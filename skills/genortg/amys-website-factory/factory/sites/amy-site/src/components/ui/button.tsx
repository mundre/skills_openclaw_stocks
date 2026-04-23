import * as React from "react";
import { cn } from "@/lib/utils";

type ButtonVariant = "default" | "outline" | "secondary" | "ghost";
type ButtonSize = "default" | "sm" | "lg";

const variantStyles: Record<ButtonVariant, string> = {
  default:
    "bg-cyan-300 text-slate-950 hover:bg-cyan-200 focus-visible:ring-cyan-300",
  outline:
    "border border-slate-300/60 bg-transparent text-slate-100 hover:bg-slate-800/70 focus-visible:ring-slate-300",
  secondary:
    "bg-violet-300 text-slate-950 hover:bg-violet-200 focus-visible:ring-violet-300",
  ghost:
    "bg-transparent text-slate-100 hover:bg-slate-800/60 focus-visible:ring-slate-300",
};

const sizeStyles: Record<ButtonSize, string> = {
  default: "h-11 px-5 py-2",
  sm: "h-9 px-3",
  lg: "h-12 px-6 text-base",
};

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-md font-semibold transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950",
          "disabled:pointer-events-none disabled:opacity-60",
          variantStyles[variant],
          sizeStyles[size],
          className,
        )}
        {...props}
      />
    );
  },
);

Button.displayName = "Button";
