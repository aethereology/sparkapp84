import * as React from "react";
export function Button({ children, className = "", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={`px-4 py-2 rounded-xl bg-[color:var(--chili-red)] text-white hover:opacity-90 ${className}`} {...props}>{children}</button>;
}