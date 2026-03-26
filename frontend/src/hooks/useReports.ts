import { useState, useEffect, useCallback } from "react";

export interface Report {
  id: number;
  report_type: string;
  report_date: string;
  shift: string;
  panel: string | null;
  submitted_by: string | null;
  notes: string | null;
  created_at: string;
}

interface UseReportsOptions {
  report_type?: string;
  limit?: number;
}

export function useReports(options: UseReportsOptions = {}) {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (options.report_type) params.set("report_type", options.report_type);
      if (options.limit) params.set("limit", String(options.limit));

      const res = await fetch(`/api/reports?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setReports(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [options.report_type, options.limit]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  return { reports, loading, error, refetch: fetchReports };
}
