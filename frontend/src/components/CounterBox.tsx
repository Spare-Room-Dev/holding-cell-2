'use client';

import { motion } from 'motion/react';

interface CounterBoxProps {
  label: string;
  value: number;
}

const formatCount = (n: number): string => {
  if (n > 99999) return '99,999+';
  return n.toLocaleString();
};

export function CounterBox({ label, value }: CounterBoxProps) {
  return (
    <div className="flex flex-col items-center gap-xs">
      <span className="counter-label">{label}</span>
      <motion.div
        className="counter-box"
        initial={false}
        animate={{ scale: [1, 1.02, 1] }}
        transition={{ duration: 0.15 }}
        key={value}
      >
        <span className="counter-number font-mono">
          {formatCount(value)}
        </span>
      </motion.div>
    </div>
  );
}