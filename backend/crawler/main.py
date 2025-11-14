"""
Shopify Store Crawler
---------------------

This script:
  • Loads a list of domains
  • Detects whether each domain is a Shopify store
  • Uses Shopify’s public JSON APIs (meta.json, products.json, collections.json)
  • Summarizes product data and metadata
  • Extracts keywords, social links, and Buy-with-Prime signals
  • Saves results to:
        backend/shopify_data.json
        frontend/my-app/public/data/shopify_data.json

Design notes:
  • Only Shopify stores with valid products.json output are included.
  • Non-Shopify domains or stores that hide products.json are skipped.
  • No fallback scraper is used — intentionally kept simple.
"""

import re, json, time, httpx, os, trafilatura, yake
from urllib.parse import urljoin
from lxml import html as lxml_html
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

# -----------------------------
# GLOBAL CONSTANTS & MODEL LOAD
# -----------------------------

UA = "NB-Crawler/1.0 (+assignment)"
TIMEOUT = 15

print("Loading embedding model (this happens once)…")
EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Model ready.")

# Target categories for simple semantic classification
CATEGORIES = [
    "clothing", "footwear", "jewelry", "watches", "home decor",
    "furniture", "beauty products", "sports gear", "electronics",
    "food and beverages", "pet supplies", "toys and games",
    "art and prints", "outdoor equipment", "stationery"
]

# Pre-compute category embeddings
CAT_EMB = EMBED_MODEL.encode(CATEGORIES, normalize_embeddings=True)


# -----------------------------------
# SEMANTIC DESCRIPTION GENERATOR
# -----------------------------------

def describe_store_semantic(domain, meta, offerings, keywords):
    """
    Generate a short natural-language description of the store
    by embedding extracted keywords and comparing them to known categories.
    """
    # Determine store display name
    name = (
        (meta or {}).get("shop", {}).get("name")
        or domain.split(".")[0].title()
    )

    # Combine meaningful text signals
    text = " ".join(
        keywords
        + [t for t, _ in offerings.get("product_types_top", [])]
        + offerings.get("title_terms_top", [])
        + [t for t, _ in offerings.get("tags_top", [])]
    ) or "products"

    # Embed and classify to nearest category
    emb = EMBED_MODEL.encode([text], normalize_embeddings=True)
    sims = util.cos_sim(emb, CAT_EMB)[0].tolist()
    best_cat = CATEGORIES[sims.index(max(sims))]

    return f"{name} sells {best_cat} and related products."



# -----------------------------------
# DOMAIN LOADING & BASIC FETCH UTILS
# -----------------------------------

def load_domains(filename="domains.txt"):
    """Load and normalize domain list from a file."""
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


def fetch(url, headers=None):
    """HTTP GET wrapper using httpx with redirects and timeout."""
    h = {"User-Agent": UA, "Accept": "application/json, text/html"}
    if headers:
        h.update(headers)

    with httpx.Client(follow_redirects=True, timeout=TIMEOUT) as c:
        return c.get(url, headers=h)


def is_shopify_store(html_str, headers):
    """
    Detect Shopify storefronts using simple markers.
    Not bulletproof, but reliable enough for stores that use standard Shopify themes.
    """
    low = html_str.lower()

    # Very strong Shopify signals
    if "cdn.shopify.com" in low:
        return True
    if "shopify-features" in low:
        return True

    # Shopify script bundles
    if "shopify" in low and "script" in low:
        return True

    # Shopify-set headers
    if any("shopify" in k.lower() for k in headers.keys()):
        return True

    # Indirect heuristic: cart + products routing
    if "/cart" in low and "/products/" in low:
        return True

    return False


# ---------------------------
# KEYWORD & TEXT PROCESSING
# ---------------------------

def extract_keywords(text, topk=15):
    """Use YAKE to extract keywords from landing-page text."""
    if not text:
        return []

    extractor = yake.KeywordExtractor(lan="en", n=2, top=topk)
    keywords = extractor.extract_keywords(text)

    cleaned = []
    for term, score in sorted(keywords, key=lambda x: x[1]):
        term = term.strip(" .,:;|/\\-").lower()
        if (
            len(term) >= 3
            and not any(bad in term for bad in ["cookie", "privacy", "policy", "login"])
        ):
            cleaned.append(term)

    return cleaned[:topk]


# --------------------------
# SHOPIFY API FETCH HELPERS
# --------------------------

def fetch_shopify_meta(base_url):
    """Fetch Shopify meta.json if available."""
    try:
        r = fetch(urljoin(base_url, "/meta.json"))
        if r.status_code == 200 and "json" in r.headers.get("Content-Type", ""):
            return r.json()
    except:
        pass
    return None


def fetch_shopify_products(base_url, limit=250, page_limit=2):
    """
    Fetch products via Shopify's public products.json pagination.
    Only published/visible products are typically returned, but not guaranteed.
    """
    products = []
    for page in range(1, page_limit + 1):
        try:
            r = fetch(urljoin(base_url, f"/products.json?limit={limit}&page={page}"))
            if r.status_code != 200 or "json" not in r.headers.get("Content-Type", ""):
                break

            batch = r.json().get("products") or []
            if not batch:
                break

            products.extend(batch)
            if len(batch) < limit:
                break
        except:
            break
    return products


def fetch_shopify_collections(base_url):
    """Fetch collections via Shopify collections.json."""
    try:
        r = fetch(urljoin(base_url, "/collections.json"))
        if r.status_code == 200 and "json" in r.headers.get("Content-Type", ""):
            return r.json().get("collections", [])
    except:
        pass
    return []


# ----------------------------
# PRODUCT SUMMARY + ANALYSIS
# ----------------------------

def summarize_products(products):
    """
    Extract common product types, vendors, tags, and frequent title words.
    Very useful for categorizing stores at a glance.
    """
    types, vendors, tags, titles = [], [], [], []

    for p in products:
        types.append(p.get("product_type", "").strip())
        vendors.append(p.get("vendor", "").strip())
        tags.extend(p.get("tags", []) or [])
        titles.append(p.get("title", ""))

    # Utility: top-k most frequent items
    def top(items, k=10):
        freq = {}
        for i in items:
            if i:
                freq[i] = freq.get(i, 0) + 1
        return sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

    # Extract common words from product titles
    words = []
    for t in titles:
        for w in re.split(r"[^A-Za-z0-9+&'-]+", t.lower()):
            if 3 <= len(w) <= 20 and not w.isdigit():
                words.append(w)

    title_terms = [
        w
        for w, _ in sorted(
            {w: words.count(w) for w in set(words)}.items(),
            key=lambda kv: (-kv[1], kv[0])
        )[:20]
    ]

    return {
        "product_types_top": top(types, 8),
        "vendors_top": top(vendors, 5),
        "tags_top": top(tags, 10),
        "title_terms_top": title_terms,
        "total_products_sampled": len(products),
        "example_titles": titles[:8],
    }


def summarize_prices(products):
    """Compute min, max, and average price across product variants."""
    prices = []
    for p in products:
        for v in p.get("variants", []):
            try:
                val = float(v.get("price", 0))
                if val > 0:
                    prices.append(val)
            except:
                pass

    if not prices:
        return None

    return {
        "min_price": min(prices),
        "max_price": max(prices),
        "avg_price": round(sum(prices) / len(prices), 2),
        "num_prices": len(prices),
    }


def extract_social_links(html):
    """Detect social links naïvely by matching platform URLs."""
    socials = {}
    for platform in ["instagram", "facebook", "tiktok", "youtube", "twitter", "x.com"]:
        matches = re.findall(
            rf'https?://(?:www\.)?{platform}\.com/[A-Za-z0-9_.\-/%]+',
            html,
            re.IGNORECASE
        )
        if matches:
            socials[platform] = list(set(matches))
    return socials


def detect_buy_with_prime(html):
    """Detect Buy-with-Prime integrations via script signatures."""
    low = html.lower()
    indicators = [
        "buywithprime.amazon",
        "buy-with-prime",
        "bwp.js",
        "bwp-client",
        "data-bwp",
        "amazonpay",
    ]
    return any(token in low for token in indicators)


# ------------------------
# MAIN SHOPIFY ANALYSIS
# ------------------------

def analyze_shopify_store(domain):
    """
    For a given domain:
      • Fetch homepage
      • Verify Shopify
      • Pull meta.json, products.json, collections.json
      • Extract store description and summaries
    """
    base = f"https://{domain}"
    print(f"Analyzing {domain} …")

    # Fetch homepage
    try:
        resp = fetch(base)
    except Exception as e:
        return {"domain": domain, "error": f"fetch_home_failed: {e}"}

    html = resp.text

    # 1. Shopify detection
    if not is_shopify_store(html, resp.headers):
        print(f"  ⚠️ Skipping non-Shopify: {domain}")
        return {"domain": domain, "platform": "Not Shopify"}

    # 2. Fetch Shopify data
    meta = fetch_shopify_meta(base)
    products = fetch_shopify_products(base)
    collections = fetch_shopify_collections(base)

    # If products.json is empty → treat as non-Shopify
    if not products:
        print(f"  ⚠️ No products.json data for {domain}. Skipping.")
        return {"domain": domain, "platform": "Not Shopify"}

    # 3. Summaries & semantic description
    offerings = summarize_products(products)
    text = trafilatura.extract(html, include_comments=False) or ""
    keywords = extract_keywords(text)
    description = describe_store_semantic(domain, meta, offerings, keywords)

    social_links = extract_social_links(html)
    has_bwp = detect_buy_with_prime(html)
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
        "timestamp": int(time.time()),
    }


# -----------------------
# EXECUTION / WRITE OUT
# -----------------------

if __name__ == "__main__":
    DOMAINS = load_domains("domains.txt")
    print(f"Loaded {len(DOMAINS)} domains")

    results = []
    for d in DOMAINS:
        try:
            store = analyze_shopify_store(d)
            # Only store valid Shopify results
            if store.get("platform") == "Shopify":
                results.append(store)
        except Exception as e:
            results.append({"domain": d, "error": str(e)})
            print(f"  ❌ {d}: {e}")

    # Write backend output
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify_data.json")

    # Write frontend output
    frontend_output_path = (
        Path(__file__).resolve().parents[2]
        / "frontend" / "my-app" / "public" / "data" / "shopify_data.json"
    )
    frontend_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with frontend_output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # -------------------------------------
    # Write CSV output (domain, description, keywords)
    # -------------------------------------
    import csv

    csv_output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "extremely_straightforward_deliverable.csv"
    )

    with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["domain", "description", "keywords"])

        for store in results:
            kw = store.get("landing_keywords") or []
            writer.writerow([
                store.get("domain", ""),
                store.get("description", "").replace("\n", " "),
                ", ".join(kw)
            ])

    print(f"📄 CSV output written to {csv_output_path}")

    print(f"✅ Done! Results written to {out_path}")
