import { useState } from "react";
import { FileText, ChevronDown, Calendar, User, MapPin } from "lucide-react";
import { useReports } from "@/hooks/useReports";
import { cn } from "@/lib/utils";

const REPORT_TYPES = [
  { value: "", label: "All Reports" },
  { value: "deputy", label: "Deputy Reports" },
  { value: "shift", label: "Shift Reports" },
  { value: "gas", label: "Gas Readings" },
  { value: "hazard", label: "Hazard Reports" },
  { value: "strata", label: "Strata Assessments" },
  { value: "ventilation", label: "Ventilation" },
  { value: "incident", label: "Incidents" },
  { value: "tarp", label: "TARP Activations" },
  { value: "equipment_log", label: "Equipment Logs" },
  { value: "prestart", label: "Pre-start Checklists" },
];

const TYPE_COLORS: Record<string, string> = {
  deputy: "bg-blue-500/20 text-blue-400",
  shift: "bg-emerald-500/20 text-emerald-400",
  gas: "bg-amber-500/20 text-amber-400",
  hazard: "bg-red-500/20 text-red-400",
  strata: "bg-purple-500/20 text-purple-400",
  ventilation: "bg-cyan-500/20 text-cyan-400",
  incident: "bg-rose-500/20 text-rose-400",
  tarp: "bg-orange-500/20 text-orange-400",
  equipment_log: "bg-slate-500/20 text-slate-400",
  prestart: "bg-teal-500/20 text-teal-400",
};

export default function ReportsPage() {
  const [selectedType, setSelectedType] = useState("");
  const { reports, loading } = useReports({
    report_type: selectedType || undefined,
    limit: 100,
  });

  return (
    <div className="flex flex-col h-full">
      <header className="h-14 border-b border-border flex items-center justify-between px-4 bg-surface-raised shrink-0">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-text-secondary" />
          <h1 className="text-sm font-semibold">Reports</h1>
          <span className="text-xs text-text-muted bg-surface-overlay px-2 py-0.5 rounded-full">
            {reports.length}
          </span>
        </div>
      </header>

      <div className="p-4 border-b border-border bg-surface-raised/50">
        <div className="flex flex-wrap gap-2">
          {REPORT_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => setSelectedType(t.value)}
              className={cn(
                "text-xs px-3 py-1.5 rounded-lg transition-colors",
                selectedType === t.value
                  ? "bg-mine-600 text-white"
                  : "bg-surface-overlay text-text-secondary hover:text-text-primary"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="text-center text-text-muted py-8">Loading...</div>
        ) : reports.length === 0 ? (
          <div className="text-center text-text-muted py-8">
            No reports found
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-2">
            {reports.map((r) => (
              <div
                key={r.id}
                className="bg-surface-raised border border-border rounded-xl p-4 hover:border-border-hover transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={cn(
                          "text-xs px-2 py-0.5 rounded-md font-medium",
                          TYPE_COLORS[r.report_type] ||
                            "bg-surface-overlay text-text-secondary"
                        )}
                      >
                        {r.report_type}
                      </span>
                      <span className="text-xs text-text-muted capitalize">
                        {r.shift} shift
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-text-secondary mt-2">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {r.report_date}
                      </span>
                      {r.submitted_by && (
                        <span className="flex items-center gap-1">
                          <User className="w-3 h-3" />
                          {r.submitted_by}
                        </span>
                      )}
                      {r.panel && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {r.panel}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-text-muted">#{r.id}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
