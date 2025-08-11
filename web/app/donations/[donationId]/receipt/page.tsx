'use client'; import { useEffect, useState } from "react"; const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
export default function ReceiptViewer({ params }: { params: { donationId: string }}) {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(()=>{ setSrc(`${API_URL}/api/v1/donations/${params.donationId}/receipt.pdf`); },[params.donationId]);
  return (<div className="card p-4"><div className="font-semibold mb-2">Receipt for {params.donationId}</div>{src ? <iframe className="w-full h-[80vh] border rounded-xl" src={src} /> : <div>Loading…</div>}</div>);
}