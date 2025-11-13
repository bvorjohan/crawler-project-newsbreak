"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

const cards = [
  {
    title: "Hello!", 
    text: `I'm happy to show you my web crawler project. I made a web crawler for one of my earliest projects when I was learning to program, so this was a fun throwback.`,
  },
  {
    title: "Early Decisions",
    text: `I quickly decided to revisit Python for this project. It is easy to implement and iterate with, and has a wonderful ecosystem of libraries that make web crawling much easier.
    
    Since my richest experience is in Frontend work, I decided I would make a website to show the results of the crawler project.`,
  },
  {
    title: "Tools Used",
    text: `I used ChatGPT to help iterate over ideas more quickly. I am not really an "AI Enthusiast", but it definitely removes a lot of obstacles from prototyping!
    
    For the frontend, this project was an opportunity to experiment with some more interesting UI frameworks than I usually use, so I was very happy to get to use tailwind and framer-motion.
    
    For the crawler itself, I used a smattering of common Python libraries for http/html manipulation. More interestingly, I chose to use yake and sentence_transformers to do some light analysis on the crawler results.`,
  },
  {
    title: "Insight",
    text: `My current role involves working on an integration with Shopify. It seems like all of these stores happen to be Shopify stores! Except for 9wik.com, which looks like an inactive store.
    
    This pattern means that the crawler implementation can rely on some pretty consistent sources of data. For a general-purpose crawler, you could not rely on this. But for the purposes of the assignment, it lets us make some assumptions that simplify the implementation considerably.
    
    I spend a lot of time at work looking at Shopify stores, so this felt right-at-home!`,
  },
  {
    title: "Cheating — only a little",
    text: `While web scrapers are simple at heart, they have to deal with the profound dynamic messiness of the internet. While working on the project, there are a few challenges that came up that involved some tough choices.
    
    As I mentioned before, 9wick shut down before I started the assignment — so it gets left out of the final data. What's more, Cleanomics's website went from being its own web store to a marketing page for cleanomicessentials.com. In a real scaled-up production setting, these types of dynamic problems would require some long-term solutions. For this project, I just decided to use the updated domain.
    
    7bonkers is primarily a watch store, but also contains some "inappropriate" products. I decided not to alter the data coming in, but thankfully it does not show up on this website.`,
  },
  {
    title: "Personalization",
    text: `Some of these stores use "Buy with Prime", which is the Amazon service I work on. I've made sure to highlight those stores via the crawler data.`,
  },
  {
    title: "De-Scoping",
    text: `When I initially thought of how to approach the project, I also wanted to set up the script to run on a regular interval, and also add a button on the UI that would let you run it at-will. However, real life caught up to me (and I didn't want to have to pentest my API!) so I decided to de-scope that from this version.`,
  },
  {
    title: "Room for growth",
    text: `Web crawlers are simple in concept, but potentially complicated depending on what kind of data you're building for. Looking at this data, I have some questions. Why does this data return average price in Dollars even when that is not the primary shop currency? Is the average price a good representation of what you can expect to spend at the store? These are things that would require some further thought.`,
  },
];

export function StoryDeck() {
  const [index, setIndex] = useState(0);
  const next = () => setIndex((i) => (i + 1) % cards.length);
  const prev = () => setIndex((i) => (i - 1 + cards.length) % cards.length);

  return (
    <div className="flex items-center justify-center w-full py-12">
      {/* Left button */}
      <Button
        variant="outline"
        size="icon"
        onClick={prev}
        aria-label="Previous card"
        className="mr-4 shrink-0 rounded-full shadow-sm border-muted hover:bg-accent hover:text-accent-foreground relative z-50"
      >
        <ChevronLeft className="h-6 w-6" />
      </Button>

      {/* Card stack */}
      <div className="relative w-[36rem] h-[26rem]">
        {cards.map((c, i) => {
          const offset = ((i - index + cards.length) % cards.length);
          const zIndex = cards.length - offset;
          const isActive = i === index;

          return (
            <motion.div
              key={i}
              className="absolute inset-0"
              style={{ zIndex }}
              animate={{
                x: offset * 20,
                y: offset * 8,
                scale: isActive ? 1 : 0.96,
                opacity: isActive ? 1 : 0.7,
                rotate: isActive ? 0 : offset * 1.5, // slight tilt
                filter: isActive ? "blur(0px)" : "blur(1px)",
              }}
              transition={{ type: "spring", stiffness: 120, damping: 20 }}
            >
              <Card className="h-full shadow-xl overflow-hidden">
                <CardHeader>
                  <CardTitle className="text-xl">{c.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Instead of splitting paragraphs manually, use white-space + margins */}
                  <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                    {c.text}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Right button */}
      <Button
        variant="outline"
        size="icon"
        onClick={next}
        aria-label="Next card"
        className="ml-4 shrink-0 rounded-full shadow-sm border-muted hover:bg-accent hover:text-accent-foreground relative z-50"
      >
        <ChevronRight className="h-6 w-6" />
      </Button>
    </div>
  );
}
