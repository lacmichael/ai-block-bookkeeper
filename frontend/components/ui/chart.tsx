"use client";

import * as React from "react";
import * as RechartsPrimitive from "recharts";
import { cn } from "@/lib/utils";

// Re-export all recharts primitives
export * from "recharts";

// Chart container component
const ChartContainer = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<"div"> & {
    config: any;
  }
>(({ id, className, children, config, ...props }, ref) => {
  const uniqueId = React.useId();
  const chartId = `chart-${id || uniqueId.replace(/:/g, "")}`;

  return (
    <div
      data-chart={chartId}
      ref={ref}
      className={cn(
        "flex aspect-video justify-center text-xs [&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground [&_.recharts-cartesian-grid_line[stroke='#ccc']]:stroke-border/50 [&_.recharts-curve.recharts-tooltip-cursor]:stroke-border [&_.recharts-dot[stroke='#fff']]:stroke-transparent [&_.recharts-layer]:outline-none [&_.recharts-polar-grid_[stroke='#ccc']]:stroke-border [&_.recharts-radial-bar-background-sector]:fill-muted [&_.recharts-rectangle.recharts-tooltip-cursor]:fill-muted [&_.recharts-reference-line_[stroke='#ccc']]:stroke-border [&_.recharts-sector[stroke='#fff']]:stroke-transparent [&_.recharts-sector]:outline-none [&_.recharts-surface]:outline-none",
        className
      )}
      {...props}
    >
      <ChartStyle id={chartId} config={config} />
      {children}
    </div>
  );
});
ChartContainer.displayName = "Chart";

const ChartStyle = ({ id, config }: { id: string; config: any }) => {
  const colorConfig = React.useMemo(() => {
    if (!config) return "";

    const colorMap: Record<string, string> = {
      primary: "hsl(var(--chart-1))",
      secondary: "hsl(var(--chart-2))",
      tertiary: "hsl(var(--chart-3))",
      quaternary: "hsl(var(--chart-4))",
      quinary: "hsl(var(--chart-5))",
    };

    const cssVars = Object.entries(config)
      .filter(([_, value]) => value !== undefined)
      .map(([key, value]) => {
        const color = colorMap[value as string] || value;
        return `  --${id}-${key}: ${color};`;
      })
      .join("\n");

    return cssVars;
  }, [config, id]);

  if (!colorConfig) return null;

  return (
    <style
      dangerouslySetInnerHTML={{
        __html: `[data-chart="${id}"] {\n${colorConfig}\n}`,
      }}
    />
  );
};

// Chart tooltip component
const ChartTooltip = RechartsPrimitive.Tooltip;

// Chart legend component
const ChartLegend = RechartsPrimitive.Legend;

export { ChartContainer, ChartTooltip, ChartLegend };
