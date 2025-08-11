import "./globals.css"; export const metadata = { title: process.env.NEXT_PUBLIC_BRAND_NAME || "SparkCreatives", description: "Reviewer briefing, data room, and donor transparency", };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (<html lang="en"><body className="min-h-screen">
    <header className="bg-tamarind-orange text-white px-6 py-4"><div className="max-w-6xl mx-auto flex items-center gap-3">
      <div className="w-7 h-7 bg-white/90 rounded-lg"></div>
      <div className="font-semibold">{process.env.NEXT_PUBLIC_BRAND_NAME || "SparkCreatives"}</div>
      <nav className="ml-auto flex gap-4 text-sm">
        <a href="/reviewer/spark/briefing" className="hover:underline">Reviewer Briefing</a>
        <a href="/reviewer/spark/data-room" className="hover:underline">Data Room</a>
        <a href="/dashboard/spark" className="hover:underline">Org Dashboard</a>
      </nav></div></header>
    <main className="max-w-6xl mx-auto p-6">{children}</main></body></html>);
}