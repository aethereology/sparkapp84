import { Card, CardContent } from "@/components/ui/card";
export default async function Briefing({ params }: { params: { org: string }}) {
  const org = params.org || "spark";
  return (<div className="grid gap-4">
    <Card><CardContent>
      <h1 className="text-xl font-semibold mb-1 capitalize">{org} — Reviewer Briefing</h1>
      <p className="opacity-75">Mission, logic model, shipment metrics, and impact highlights.</p>
    </CardContent></Card>
    <div className="grid md:grid-cols-2 gap-4">
      <Card><CardContent><div className="text-sm opacity-70">Boxes Shipped (YTD)</div><div className="text-3xl font-semibold">128</div></CardContent></Card>
      <Card><CardContent><div className="text-sm opacity-70">On-time Delivery %</div><div className="text-3xl font-semibold">93%</div></CardContent></Card>
      <Card><CardContent><div className="text-sm opacity-70">Beneficiaries Served</div><div className="text-3xl font-semibold">412</div></CardContent></Card>
      <Card><CardContent><div className="text-sm opacity-70">Funds by Designation</div>
        <ul className="mt-2 space-y-1"><li className="flex justify-between"><span>Shipping Fund</span><span>$18,250</span></li><li className="flex justify-between"><span>School Kits</span><span>$12,600</span></li><li className="flex justify-between"><span>General Fund</span><span>$8,400</span></li></ul>
      </CardContent></Card>
    </div>
  </div>);
}