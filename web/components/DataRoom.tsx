'use client';
import useSWR from 'swr';
import { DataRoomProps, DataRoomResponse, Document } from '@/lib/types';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export default function DataRoom({ org = 'spark' }: DataRoomProps) {
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
  const { data, error, isLoading } = useSWR<DataRoomResponse>(
    `${base}/api/v1/data-room/documents?org=${org}&reviewer=true`, 
    fetcher
  );

  if (isLoading) return <div>Loading documents…</div>;
  if (error) return <div>Error loading documents</div>;
  if (!data?.documents) return <div>No documents available</div>;

  return (
    <div className="grid gap-3">
      {data.documents.map((document: Document) => (
        <a 
          key={document.url} 
          href={document.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="card p-3 hover:opacity-90"
        >
          <div className="font-medium">{document.name}</div>
          <div className="text-xs opacity-70 break-all">{document.url}</div>
        </a>
      ))}
    </div>
  );
}