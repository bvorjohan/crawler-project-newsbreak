import re, json, time, httpx, os, tldextract, trafilatura, yake
from urllib.parse import urljoin
from lxml import html as lxml_html
from sentence_transformers import SentenceTransformer, util

UA = "NB-Crawler/1.0 (+assignment)"
TIMEOUT = 15


print("Loading embedding model (this happens once)...")
EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Model ready.")

CATEGORIES = [
    "clothing", "footwear", "jewelry", "watches", "home decor",
    "furniture", "beauty products", "sports gear", "electronics",
    "food and beverages", "pet supplies", "toys and games",
    "art and prints", "outdoor equipment", "stationery"
]
CAT_EMB = EMBED_MODEL.encode(CATEGORIES, normalize_embeddings=True)


def describe_store_semantic(domain, meta, offerings, keywords):
    """Generate one-sentence description using embedding similarity."""
    name = (meta or {}).get("shop", {}).get("name") or domain.split(".")[0].title()

    # Combine relevant text into one short string
    text = " ".join(
        keywords
        + [t for t, _ in offerings.get("product_types_top", [])]
        + offerings.get("title_terms_top", [])
        + [t for t, _ in offerings.get("tags_top", [])]
    ) or "products"

    emb = EMBED_MODEL.encode([text], normalize_embeddings=True)
    sims = util.cos_sim(emb, CAT_EMB)[0].tolist()
    best_cat = CATEGORIES[sims.index(max(sims))]

    return f"{name} sells {best_cat} and related products."

# ---------- LOAD DOMAINS ----------
def load_domains(filename="domains.txt"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    domains = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = line.strip()
            if not d or d.startswith("#"):
                continue
            d = re.sub(r"^https?://", "", d).strip("/")
            domains.append(d)
    return domains


# ---------- FETCH HELPERS ----------
def fetch(url, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json, text/html"}
    if headers:
        h.update(headers)
    with httpx.Client(follow_redirects=True, timeout=TIMEOUT) as c:
        r = c.get(url, headers=h)
        return r

def is_shopify_store(html_str, headers):
    low = html_str.lower()
    return (
        "cdn.shopify.com" in low
        or "shopify-features" in low
        or any("shopify" in k.lower() for k in headers.keys())
    )


# ---------- TEXT EXTRACTION ----------
def extract_keywords(text, topk=15):
    if not text:
        return []
    extractor = yake.KeywordExtractor(lan="en", n=2, top=topk)
    keywords = extractor.extract_keywords(text)
    out = []
    for term, score in sorted(keywords, key=lambda x: x[1]):
        term = term.strip(" .,:;|/\\-").lower()
        if len(term) >= 3 and not any(bad in term for bad in ["cookie", "privacy", "policy", "login"]):
            out.append(term)
    return out[:topk]


# ---------- SHOPIFY DATA FETCH ----------
def fetch_shopify_meta(base_url):
    try:
        r = fetch(urljoin(base_url, "/meta.json"))
        if r.status_code == 200 and "json" in r.headers.get("Content-Type", ""):
            return r.json()
    except Exception:
        pass
    return None

def fetch_shopify_products(base_url, limit=250, page_limit=2):
    all_products = []
    for page in range(1, page_limit + 1):
        url = urljoin(base_url, f"/products.json?limit={limit}&page={page}")
        try:
            r = fetch(url)
            if r.status_code != 200 or "json" not in r.headers.get("Content-Type", ""):
                break
            data = r.json()
            products = data.get("products") or []
            if not products:
                break
            all_products.extend(products)
            if len(products) < limit:
                break
        except Exception:
            break
    return all_products

def fetch_shopify_collections(base_url):
    """Fetch visible collections/categories."""
    try:
        r = fetch(urljoin(base_url, "/collections.json"))
        if r.status_code == 200 and "json" in r.headers.get("Content-Type", ""):
            data = r.json()
            return data.get("collections", [])
    except Exception:
        pass
    return []


# ---------- PRODUCT SUMMARY ----------
def summarize_products(products):
    types, vendors, tags, titles = [], [], [], []
    for p in products:
        types.append(p.get("product_type", "").strip())
        vendors.append(p.get("vendor", "").strip())
        tags.extend(p.get("tags") or [])
        titles.append(p.get("title", ""))

    def top(items, k=10):
        freq = {}
        for i in items:
            if not i:
                continue
            freq[i] = freq.get(i, 0) + 1
        return sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

    # compute frequent words from titles
    words = []
    for t in titles:
        for w in re.split(r"[^A-Za-z0-9+&'-]+", t.lower()):
            if 3 <= len(w) <= 20 and not re.match(r"^\d+$", w):
                words.append(w)
    common_title_terms = [w for w, _ in sorted(
        {w: words.count(w) for w in set(words)}.items(),
        key=lambda kv: (-kv[1], kv[0])
    )[:20]]

    return {
        "product_types_top": top(types, 8),
        "vendors_top": top(vendors, 5),
        "tags_top": top(tags, 10),
        "title_terms_top": common_title_terms,
        "total_products_sampled": len(products),
        "example_titles": titles[:8]
    }

def summarize_prices(products):
    prices = []
    for p in products:
        for v in p.get("variants", []):
            try:
                price = float(v.get("price", 0))
                if price > 0:
                    prices.append(price)
            except (TypeError, ValueError):
                pass
    if not prices:
        return None
    return {
        "min_price": min(prices),
        "max_price": max(prices),
        "avg_price": round(sum(prices) / len(prices), 2),
        "num_prices": len(prices)
    }

def extract_social_links(html):
    socials = {}
    for platform in ["instagram", "facebook", "tiktok", "youtube", "twitter", "x.com"]:
        pattern = rf'https?://(?:www\.)?{platform}\.com/[A-Za-z0-9_.\-/%]+'
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            socials[platform] = list(set(matches))
    return socials

def detect_buy_with_prime(html):
    low = html.lower()
    indicators = [
        "buywithprime.amazon",      # official Amazon endpoint
        "buy-with-prime",           # used in script names
        "bwp.js",                   # internal SDK filename
        "bwp-client",               # used in script URLs
        "data-bwp",                 # HTML attributes
        "amazonpay"                 # sometimes co-injected
    ]
    for token in indicators:
        if token in low:
            return True
    return False

# ---------- MAIN ANALYZER ----------
def analyze_shopify_store(domain):
    base = f"https://{domain}"
    print(f"Analyzing {domain} ...")
    # Get homepage HTML
    try:
        r = fetch(base)
    except Exception as e:
        return {"domain": domain, "error": f"fetch_home_failed: {e}"}

    if not is_shopify_store(r.text, r.headers):
        print(f"  ⚠️  Skipping non-Shopify: {domain}")
        return {"domain": domain, "platform": "Not Shopify"}

    meta = fetch_shopify_meta(base)
    products = fetch_shopify_products(base)
    collections = fetch_shopify_collections(base)
    offerings = summarize_products(products)

    # Get keywords from homepage
    text = trafilatura.extract(r.text, include_comments=False) or ""
    keywords = extract_keywords(text, topk=15)
    description = describe_store_semantic(domain, meta, offerings, keywords)

    # Detect socials and Buy with Prime from homepage
    social_links = extract_social_links(r.text)
    has_bwp = detect_buy_with_prime(r.text)

    # Price summary from product list
    price_summary = summarize_prices(products)

    return {
        "domain": domain,
        "platform": "Shopify",
        "meta": meta,
        "description": description,
        "collections": [
            {"title": c.get("title"), "handle": c.get("handle")}
            for c in (collections or [])
        ],
        "offerings": offerings,
        "price_summary": price_summary,   
        "social_links": social_links,     
        "buy_with_prime": has_bwp,      
        "landing_keywords": keywords,
        "timestamp": int(time.time())
    }


# ---------- RUNNER ----------
if __name__ == "__main__":
    DOMAINS = load_domains("domains.txt")
    print(f"Loaded {len(DOMAINS)} domains")

    results = []
    for d in DOMAINS:
        try:
            store = analyze_shopify_store(d)
            if (store.platform == "Shopify"):
                results.append(store)
        except Exception as e:
            results.append({"domain": d, "error": str(e)})
            print(f"  ❌ {d}: {e}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify_data.json")
    frontend_output_path = Path(__file__).resolve().parents[2] / "frontend" / "my-app" / "public" / "data" / "shopify_data.json"
    frontend_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    with frontend_output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Done! Results written to {out_path}")
