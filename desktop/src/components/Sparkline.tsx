interface SparklineProps {
  points: number[];
  direction?: "up" | "down" | "flat";
}

export function Sparkline({ points, direction = "flat" }: SparklineProps) {
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = Math.max(max - min, 1);
  const width = 180;
  const height = 64;
  const path = points
    .map((point, index) => {
      const x = (index / Math.max(points.length - 1, 1)) * width;
      const y = height - ((point - min) / range) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
  const stroke = direction === "down" ? "#F05C5C" : direction === "up" ? "#36D399" : "#30D5E8";

  return (
    <svg className="h-16 w-full overflow-visible" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="trend line">
      <path d={path} fill="none" stroke={stroke} strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
      <path d={`${path} L ${width} ${height} L 0 ${height} Z`} fill={stroke} opacity="0.08" />
    </svg>
  );
}
