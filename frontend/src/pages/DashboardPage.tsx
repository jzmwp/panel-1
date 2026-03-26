import { useState, useEffect } from "react";
import { BarChart3, AlertTriangle, Wind, TrendingUp, Activity } from "lucide-react";

interface Stats {
  total_reports: number;
  report_breakdown: Record<string, number>;
  open_hazards: number;
  recent_incidents: number;
  tarp_activations: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [reports, setReports] = useState<any[]>([]);

  useEffect(() => {
    // Fetch summary stats
    Promise.all([
      fetch("/api/reports?limit=200").then((r) => r.json()),
    ]).then(([allReports]) => {
      const breakdown: Record<string, number> = {};
      for (const r of allReports) {
        breakdown[r.report_type] = (breakdown[r.report_type] || 0) + 1;
      }
      setReports(allReports);
      setStats({
        total_reports: allReports.length,
        report_breakdown: breakdown,
        open_hazards: allReports.filter(
          (r: any) => r.report_type === "hazard"
        ).length,
        recent_incidents: allReports.filter(
          (r: any) => r.report_type === "incident"
        ).length,
        tarp_activations: allReports.filter(
          (r: any) => r.report_type === "tarp"
        ).length,
      });
    });
  }, []);

  if (!stats)
    return (
      <div className="flex items-center justify-center h-full text-text-muted">
        Loading dashboard...
      </div>
    );

  const cards = [
    {
      label: "Total Reports",
      value: stats.total_reports,
      icon: BarChart3,
      color: "text-mine-400",
      bg: "bg-mine-600/10",
    },
    {
      label: "Open Hazards",
      value: stats.open_hazards,
      icon: AlertTriangle,
      color: "text-warning",
      bg: "bg-warning/10",
    },
    {
      label: "Incidents",
      value: stats.recent_incidents,
      icon: Activity,
      color: "text-danger",
      bg: "bg-danger/10",
    },
    {
      label: "TARP Activations",
      value: stats.tarp_activations,
      icon: TrendingUp,
      color: "text-orange-400",
      bg: "bg-orange-500/10",
    },
  ];

  return (
    <div className="flex flex-col h-full">
      <header className="h-14 border-b border-border flex items-center px-4 bg-surface-raised shrink-0">
        <BarChart3 className="w-5 h-5 text-text-secondary mr-2" />
        <h1 className="text-sm font-semibold">Dashboard</h1>
      </header>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Stat Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cards.map((card) => (
              <div
                key={card.label}
                className="bg-surface-raised border border-border rounded-xl p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-text-secondary">
                    {card.label}
                  </span>
                  <div
                    className={`w-8 h-8 rounded-lg ${card.bg} flex items-center justify-center`}
                  >
                    <card.icon className={`w-4 h-4 ${card.color}`} />
                  </div>
                </div>
                <div className={`text-2xl font-bold ${card.color}`}>
                  {card.value}
                </div>
              </div>
            ))}
          </div>

          {/* Report Breakdown */}
          <div className="bg-surface-raised border border-border rounded-xl p-6">
            <h2 className="text-sm font-semibold mb-4">
              Reports by Type
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {Object.entries(stats.report_breakdown)
                .sort(([, a], [, b]) => b - a)
                .map(([type, count]) => (
                  <div
                    key={type}
                    className="bg-surface-overlay rounded-lg p-3 text-center"
                  >
                    <div className="text-lg font-bold text-text-primary">
                      {count}
                    </div>
                    <div className="text-xs text-text-secondary capitalize">
                      {type.replace("_", " ")}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-surface-raised border border-border rounded-xl p-6">
            <h2 className="text-sm font-semibold mb-4">
              Recent Reports
            </h2>
            <div className="space-y-2">
              {reports.slice(0, 10).map((r: any) => (
                <div
                  key={r.id}
                  className="flex items-center justify-between py-2 border-b border-border/50 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs px-2 py-0.5 rounded bg-surface-overlay text-text-secondary capitalize">
                      {r.report_type}
                    </span>
                    <span className="text-sm text-text-primary">
                      {r.submitted_by || "Unknown"}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-text-muted">
                    <span className="capitalize">{r.shift}</span>
                    <span>{r.report_date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
