import { Card, CardContent } from "@/components/ui/card";
export default async function OrgDashboard({ params }: { params: { org: string }}) {
  const org = params.org || "spark";
  return (<div className="grid gap-4">
    <Card><CardContent><h1 className="text-xl font-semibold mb-1 capitalize">{org} — Dashboard</h1>
    <p className="opacity-75">KPIs and operational snapshots (placeholder).</p></CardContent></Card>
    <div className="grid md:grid-cols-2 gap-4">
      <Card><CardContent><div className="text-sm opacity-70">Avg days door-to-door</div><div className="text-3xl font-semibold">42</div></CardContent></Card>
      <Card><CardContent><div className="text-sm opacity-70">On-time % (last 90d)</div><div className="text-3xl font-semibold">91%</div></CardContent></Card>
      <Card><CardContent><div className="text-sm opacity-70">Cost per shipped box</div><div className="text-3xl font-semibold">$97.30</div></CardContent></Card>
      <Card><CardContent><div className="text-sm opacity-70">Recurring donors</div><div className="text-3xl font-semibold">37</div></CardContent></Card>
    </div>
  </div>);
}