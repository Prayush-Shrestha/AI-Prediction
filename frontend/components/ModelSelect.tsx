"use client";
import { useRouter, useSearchParams } from "next/navigation";

export const MODEL_OPTIONS = [
  { key: "random_forest", label: "Random Forest" },
  { key: "logistic_regression", label: "Logistic Regression" },
  { key: "gradient_boosting", label: "Gradient Boosting" },
];

export function ModelSelect({ value }: { value: string }) {
  const router = useRouter();
  const params = useSearchParams();
  return (
    <select
      value={value}
      onChange={(e) => {
        const q = new URLSearchParams(params.toString());
        q.set("model", e.target.value);
        router.push(`?${q.toString()}`);
      }}
      className="rounded-lg border border-line bg-surface px-2.5 py-2 text-[13px] text-body"
      aria-label="Select model"
    >
      {MODEL_OPTIONS.map((m) => (
        <option key={m.key} value={m.key}>
          {m.label}
        </option>
      ))}
    </select>
  );
}
