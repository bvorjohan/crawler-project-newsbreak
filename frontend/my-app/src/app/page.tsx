"use client";

import { StoryDeck } from "@/components/StoryDeck";
import { StoreGrid } from "@/components/StoreGrid";

export default function Page() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="px-6 pt-10 pb-16">
        <h1 className="text-3xl font-bold tracking-tight mb-6">Bradley Vorjohan's Web Crawler</h1>
        <StoryDeck />
      </section>

      <section className="px-6 py-10">
        <h2 className="text-2xl font-semibold mb-4">Crawl Results</h2>
        <StoreGrid />
      </section>
    </main>
  );
}
