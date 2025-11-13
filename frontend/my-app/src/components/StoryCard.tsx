"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";

export function StoryCard({ title, summary, details }: {
  title: string;
  summary: string;
  details: string;
}) {
  const [flipped, setFlipped] = useState(false);

  return (
    <motion.div
      className="relative w-80 h-56 cursor-pointer [perspective:1000px]"
      onClick={() => setFlipped(!flipped)}
    >
      <motion.div
        className="absolute inset-0"
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{ duration: 0.6 }}
        style={{ transformStyle: "preserve-3d" }}
      >
        {/* Front */}
        <Card className="absolute inset-0 backface-hidden flex flex-col justify-center">
          <CardHeader>
            <CardTitle>{title}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">{summary}</p>
          </CardContent>
        </Card>

        {/* Back */}
        <Card className="absolute inset-0 backface-hidden rotate-y-180 flex flex-col justify-center">
          <CardHeader>
            <CardTitle>{title}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed">{details}</p>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
