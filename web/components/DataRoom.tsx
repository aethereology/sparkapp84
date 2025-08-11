'use client'; import useSWR from 'swr';
const fetcher = (url: string) => fetch(url).then(r => r.json());
export default function DataRoom({ org = 'spark' }: { org?: string }) {
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
  const { data, error, isLoading } = useSWR(`${base}/api/v1/data-room/documents?org=${org}&reviewer=true`, fetcher);
  if (isLoading) return <div>Loading documents…</div>;
  if (error) return <div>Error loading</div>;
  return (<div className="grid gap-3">{data.documents.map((d:any) => (
    <a key={d.url} href={d.url} target="_blank" className="card p-3 hover:opacity-90">
      <div className="font-medium">{d.name}</div>
      <div className="text-xs opacity-70 break-all">{d.url}</div>
    </a>))}</div>);
}