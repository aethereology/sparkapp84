import * as React from "react";
export function Card({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) { return <div className={`card ${className}`}>{children}</div>; }
export function CardHeader({ children }: React.PropsWithChildren) { return <div className="px-4 pt-4 font-semibold">{children}</div>; }
export function CardContent({ children }: React.PropsWithChildren) { return <div className="p-4">{children}</div>; }