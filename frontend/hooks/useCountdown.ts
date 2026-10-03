"use client";
import { useEffect, useState } from "react";

/** Ticks every `intervalSec` and exposes seconds remaining. Used for the
 * clearly-labelled 60s demo-simulation refresh. */
export function useCountdown(intervalSec: number, onTick: () => void) {
  const [left, setLeft] = useState(intervalSec);
  useEffect(() => {
    const id = setInterval(() => {
      setLeft((v) => {
        if (v <= 1) {
          onTick();
          return intervalSec;
        }
        return v - 1;
      });
    }, 1000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intervalSec]);
  return left;
}
