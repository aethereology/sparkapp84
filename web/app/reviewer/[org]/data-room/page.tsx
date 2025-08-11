import { Card, CardContent } from "@/components/ui/card";
import dynamic from "next/dynamic";
const DataRoom = dynamic(() => import("@/components/DataRoom"), { ssr: false });
export default async function DataRoomPage({ params }: { params: { org: string }}) {
  const org = params.org || "spark";
  return (<div className="grid gap-4">
    <Card><CardContent><h1 className="text-xl font-semibold mb-1 capitalize">{org} — Data Room</h1>
    <p className="opacity-75">Secure reviewer access (signed URLs).</p></CardContent></Card>
    <DataRoom org={org} /></div>);
}