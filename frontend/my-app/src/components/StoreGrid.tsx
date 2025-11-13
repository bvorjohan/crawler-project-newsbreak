"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Globe, ShoppingBag, DollarSign, MapPin, Tags } from "lucide-react";

type StoreRecord = {
  domain: string;
  platform: string;
  meta?: {
    name?: string;
    url?: string;
    description?: string;
    country?: string;
    city?: string;
    published_products_count?: number;
  };
  description?: string;
  buy_with_prime?: boolean;
  price_summary?: {
    min_price?: number;
    max_price?: number;
    avg_price?: number;
    num_prices?: number;
  };
  offerings?: {
    title_terms_top?: string[];
  };
  landing_keywords?: string[];
};

export function StoreGrid() {
  const [stores, setStores] = useState<StoreRecord[]>([]);

  useEffect(() => {
    fetch("/data/shopify_data.json")
      .then((res) => res.json())
      .then(setStores)
      .catch((err) => console.error("Failed to load stores:", err));
  }, []);

  if (!stores.length)
    return (
      <p className="text-muted-foreground text-center py-12">
        Loading crawl results…
      </p>
    );

  return (
    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {stores.map((store) => {
        const meta = store.meta || {};
        const name = meta.name || store.domain;
        const url = meta.url || `https://${store.domain}`;
        const desc =
          store.description ||
          meta.description ||
          "No description available.";

        const keywords =
          store.offerings?.title_terms_top?.slice(0, 5) ||
          store.landing_keywords?.slice(0, 5) ||
          [];

        const price =
          store.price_summary?.avg_price &&
          `$${store.price_summary.avg_price.toFixed(2)}`;

        const products = meta.published_products_count;

        return (
          <Card
            key={store.domain}
            className="group border border-border/50 hover:border-border hover:shadow-lg transition-all duration-200 rounded-xl overflow-hidden bg-card"
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold truncate">
                  {name}
                </CardTitle>
                <Badge
                  variant={
                    store.platform === "Shopify" ? "default" : "secondary"
                  }
                  className="text-xs"
                >
                  {store.platform}
                </Badge>
              </div>
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
              >
                <Globe className="h-4 w-4 opacity-70" />
                {store.domain}
              </a>
            </CardHeader>

            <CardContent className="space-y-3 text-sm">
              <p className="text-muted-foreground line-clamp-3">{desc}</p>

              {keywords.length > 0 && (
                <div className="space-y-1">
                  <div className="flex items-center gap-1 text-xs font-medium text-muted-foreground/80">
                    <Tags className="h-3 w-3 opacity-80" />
                    Keywords
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {keywords.map((kw, k) => (
                      <Badge key={k} variant="outline" className="text-xs">
                        {kw}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between pt-2 text-xs text-muted-foreground">
                {price && (
                  <div className="flex items-center gap-1">
                    Avg {price}
                  </div>
                )}
                {products && (
                  <div className="flex items-center gap-1">
                    <ShoppingBag className="h-3 w-3" />
                    {products} products
                  </div>
                )}
                {meta.country && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {meta.country}
                  </div>
                )}
              </div>

              {store.buy_with_prime && (
                <div className="pt-2">
                  <Badge className="bg-blue-600 hover:bg-blue-700 text-white">
                    Buy with Prime
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
