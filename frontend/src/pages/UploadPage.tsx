import { useState, useRef, useCallback, useEffect } from "react";
import {
  Upload,
  FileImage,
  CheckCircle2,
  AlertCircle,
  Loader2,
  X,
  Save,
  RotateCcw,
  Eye,
  Calendar,
  User,
  MapPin,
  ChevronLeft,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

type Step = "list" | "uploading" | "review" | "saved" | "error" | "viewing";

interface DocumentSummary {
  id: number;
  filename: string;
  report_category: string | null;
  report_date: string | null;
  shift: string | null;
  panel: string | null;
  submitted_by: string | null;
  confidence: number | null;
  status: string;
  created_at: string | null;
}

interface DocumentDetail {
  id: number;
  filename: string;
  file_type: string;
  report_category: string | null;
  report_date: string | null;
  shift: string | null;
  panel: string | null;
  submitted_by: string | null;
  extracted_data: Record<string, any> | null;
  confidence: number | null;
  status: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  shift_statutory_report: "Shift Statutory Report",
  longwall_production_report: "Longwall Production Report",
  strata_assessment: "Strata Assessment",
  gas_monitoring: "Gas Monitoring",
  ventilation_reading: "Ventilation Reading",
  hazard_report: "Hazard Report",
  incident_report: "Incident Report",
  tarp_activation: "TARP Activation",
  equipment_log: "Equipment Log",
  prestart_checklist: "Pre-start Checklist",
};

const CATEGORY_COLORS: Record<string, string> = {
  shift_statutory_report: "bg-blue-500/20 text-blue-400",
  longwall_production_report: "bg-emerald-500/20 text-emerald-400",
  strata_assessment: "bg-purple-500/20 text-purple-400",
  gas_monitoring: "bg-amber-500/20 text-amber-400",
  hazard_report: "bg-red-500/20 text-red-400",
  incident_report: "bg-rose-500/20 text-rose-400",
  tarp_activation: "bg-orange-500/20 text-orange-400",
};

function formatFieldName(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/Ch4/g, "CH4")
    .replace(/Co /g, "CO ")
    .replace(/Co2/g, "CO2")
    .replace(/O2/g, "O2")
    .replace(/No2/g, "NO2")
    .replace(/H2s/g, "H2S")
    .replace(/Tarp/g, "TARP")
    .replace(/Afc/g, "AFC")
    .replace(/Bsl/g, "BSL");
}

function renderValue(value: any): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return JSON.stringify(value, null, 2);
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

export default function UploadPage() {
  const [step, setStep] = useState<Step>("list");
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [uploadResult, setUploadResult] = useState<DocumentDetail | null>(null);
  const [viewingDoc, setViewingDoc] = useState<DocumentDetail | null>(null);
  const [editedFields, setEditedFields] = useState<Record<string, any>>({});
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch("/api/documents/");
      if (res.ok) setDocuments(await res.json());
    } catch {}
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const [uploadProgress, setUploadProgress] = useState<{ total: number; done: number; current: string }>({ total: 0, done: 0, current: "" });

  const handleUpload = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    if (fileArray.length === 0) return;

    // Single file: show review after
    // Multiple files: batch upload, go back to list
    const isBatch = fileArray.length > 1;

    setStep("uploading");
    setError("");
    setUploadProgress({ total: fileArray.length, done: 0, current: fileArray[0].name });

    const formData = new FormData();
    for (const f of fileArray) {
      formData.append("files", f);
    }

    try {
      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        const msg = body?.detail || body?.message || JSON.stringify(body) || `HTTP ${res.status}`;
        throw new Error(msg);
      }

      const results = await res.json();

      // Handle if response is not an array (single error response)
      if (!Array.isArray(results)) {
        throw new Error(results?.detail || results?.message || JSON.stringify(results));
      }

      const errors = results.filter((r: any) => r.status === "error");
      const successes = results.filter((r: any) => r.status !== "error");

      await fetchDocuments();

      if (errors.length > 0 && successes.length === 0) {
        throw new Error(errors.map((e: any) => `${e.filename}: ${e.error}`).join("\n"));
      }

      if (isBatch || successes.length === 0) {
        setStep("saved");
        setUploadProgress({ total: fileArray.length, done: successes.length, current: "" });
      } else {
        // Single file — show review
        const data = successes[0];
        setUploadResult(data);
        setEditedFields({ ...(data.extracted_data || {}) });
        setStep("review");
      }
    } catch (err: any) {
      const msg = err instanceof Error ? err.message : typeof err === "string" ? err : JSON.stringify(err);
      setError(msg);
      setStep("error");
    }
  }, [fetchDocuments]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files.length > 0) handleUpload(e.dataTransfer.files);
    },
    [handleUpload]
  );

  const handleSaveReview = async () => {
    if (!uploadResult) return;
    try {
      await fetch(`/api/documents/${uploadResult.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          extracted_data: editedFields,
          status: "reviewed",
        }),
      });
      setStep("saved");
      fetchDocuments();
    } catch (err: any) {
      setError(err.message);
      setStep("error");
    }
  };

  const openDocument = async (id: number) => {
    try {
      const res = await fetch(`/api/documents/${id}`);
      if (!res.ok) return;
      const data = await res.json();
      setViewingDoc(data);
      setStep("viewing");
    } catch {}
  };

  const deleteDocument = async (id: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      await fetch(`/api/documents/${id}`, { method: "DELETE" });
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (viewingDoc?.id === id || uploadResult?.id === id) reset();
    } catch {}
  };

  const reset = () => {
    setStep("list");
    setUploadResult(null);
    setViewingDoc(null);
    setEditedFields({});
    setError("");
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="flex flex-col h-full">
      <header className="h-14 border-b border-border flex items-center justify-between px-4 bg-surface-raised shrink-0">
        <div className="flex items-center gap-2">
          {(step === "viewing" || step === "review") && (
            <button
              onClick={reset}
              className="p-1.5 rounded-lg text-text-secondary hover:bg-surface-overlay hover:text-text-primary transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          )}
          <Upload className="w-5 h-5 text-text-secondary" />
          <h1 className="text-sm font-semibold">
            {step === "viewing"
              ? "Document Viewer"
              : step === "review"
                ? "Review Extraction"
                : "Upload Reports"}
          </h1>
        </div>
        {step === "viewing" && viewingDoc && (
          <button
            onClick={() => deleteDocument(viewingDoc.id)}
            className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-danger px-3 py-1.5 rounded-lg hover:bg-danger/10 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
            Delete
          </button>
        )}
        {step === "list" && (
          <span className="text-xs text-text-muted bg-surface-overlay px-2 py-0.5 rounded-full">
            {documents.length} documents
          </span>
        )}
      </header>

      <div className="flex-1 overflow-hidden">
        {/* === LIST VIEW === */}
        {step === "list" && (
          <div className="h-full overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Drop zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileRef.current?.click()}
                className={cn(
                  "border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all",
                  dragOver
                    ? "border-mine-500 bg-mine-600/10"
                    : "border-border hover:border-border-hover hover:bg-surface-raised"
                )}
              >
                <input
                  ref={fileRef}
                  type="file"
                  multiple
                  accept=".jpg,.jpeg,.png,.pdf,.tiff,.tif,.webp"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) handleUpload(e.target.files);
                  }}
                  className="hidden"
                />
                <FileImage className="w-8 h-8 text-text-muted mx-auto mb-2" />
                <div className="text-sm text-text-primary">
                  Drop any scanned mine report here
                </div>
                <div className="text-xs text-text-muted mt-1">
                  AI will classify it and extract all data automatically
                </div>
              </div>

              {/* Document list */}
              {documents.length > 0 && (
                <div className="space-y-2">
                  {documents.map((d) => (
                    <button
                      key={d.id}
                      onClick={() => openDocument(d.id)}
                      className="w-full bg-surface-raised border border-border rounded-xl p-4 hover:border-border-hover transition-colors text-left group"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1.5">
                            <span
                              className={cn(
                                "text-xs px-2 py-0.5 rounded-md font-medium",
                                CATEGORY_COLORS[d.report_category || ""] ||
                                  "bg-surface-overlay text-text-secondary"
                              )}
                            >
                              {CATEGORY_LABELS[d.report_category || ""] ||
                                d.report_category ||
                                "Unclassified"}
                            </span>
                            <span
                              className={cn(
                                "text-[10px] px-1.5 py-0.5 rounded",
                                d.status === "reviewed"
                                  ? "bg-success/20 text-success"
                                  : d.status === "processed"
                                    ? "bg-mine-600/20 text-mine-400"
                                    : "bg-surface-overlay text-text-muted"
                              )}
                            >
                              {d.status}
                            </span>
                          </div>
                          <div className="text-sm text-text-primary truncate">
                            {d.filename}
                          </div>
                          <div className="flex items-center gap-4 text-xs text-text-secondary mt-1.5">
                            {d.report_date && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {d.report_date}
                              </span>
                            )}
                            {d.submitted_by && (
                              <span className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                {d.submitted_by}
                              </span>
                            )}
                            {d.panel && (
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                {d.panel}
                              </span>
                            )}
                            {d.confidence != null && (
                              <span
                                className={cn(
                                  "font-medium",
                                  d.confidence > 0.7
                                    ? "text-success"
                                    : d.confidence > 0.4
                                      ? "text-warning"
                                      : "text-danger"
                                )}
                              >
                                {Math.round(d.confidence * 100)}%
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity mt-1">
                          <Eye className="w-4 h-4 text-text-muted" />
                          <button
                            onClick={(e) => deleteDocument(d.id, e)}
                            className="p-1 rounded hover:bg-danger/20 hover:text-danger text-text-muted transition-colors"
                            title="Delete document"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* === UPLOADING === */}
        {step === "uploading" && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="w-12 h-12 text-mine-500 animate-spin" />
            <div className="text-sm text-text-secondary">
              AI is reading {uploadProgress.total > 1 ? `${uploadProgress.total} documents` : "the document"}...
            </div>
            <div className="text-xs text-text-muted">
              Classifying report type, extracting all fields
            </div>
          </div>
        )}

        {/* === SIDE-BY-SIDE REVIEW (after upload) === */}
        {step === "review" && uploadResult && (
          <SideBySideView
            documentId={uploadResult.id}
            category={uploadResult.report_category}
            confidence={uploadResult.confidence}
            fields={editedFields}
            onFieldChange={(k, v) =>
              setEditedFields((f) => ({ ...f, [k]: v }))
            }
            actions={
              <div className="flex gap-3">
                <button
                  onClick={reset}
                  className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary rounded-lg border border-border hover:bg-surface-overlay transition-colors"
                >
                  Discard
                </button>
                <button
                  onClick={handleSaveReview}
                  className="px-4 py-2 text-sm bg-mine-600 text-white rounded-lg hover:bg-mine-700 transition-colors flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  Confirm & Save
                </button>
              </div>
            }
          />
        )}

        {/* === SIDE-BY-SIDE VIEWING (clicking existing doc) === */}
        {step === "viewing" && viewingDoc && (
          <SideBySideView
            documentId={viewingDoc.id}
            category={viewingDoc.report_category}
            confidence={viewingDoc.confidence}
            fields={viewingDoc.extracted_data || {}}
            readOnly
          />
        )}

        {/* === SAVED === */}
        {step === "saved" && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <CheckCircle2 className="w-12 h-12 text-success" />
            <h2 className="text-lg font-semibold">
              {uploadProgress.total > 1
                ? `${uploadProgress.done} of ${uploadProgress.total} Documents Processed`
                : "Document Saved"}
            </h2>
            <p className="text-sm text-text-secondary">
              You can now ask about this data in Chat.
            </p>
            <button
              onClick={reset}
              className="px-4 py-2 text-sm bg-mine-600 text-white rounded-lg hover:bg-mine-700 transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Upload Another
            </button>
          </div>
        )}

        {/* === ERROR === */}
        {step === "error" && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <AlertCircle className="w-12 h-12 text-danger" />
            <h2 className="text-lg font-semibold">Something went wrong</h2>
            <p className="text-sm text-text-secondary">{error}</p>
            <button
              onClick={reset}
              className="px-4 py-2 text-sm bg-surface-overlay text-text-primary rounded-lg border border-border hover:bg-surface-raised transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Side-by-side comparison component ─── */

interface SideBySideViewProps {
  documentId: number;
  category: string | null;
  confidence: number | null;
  fields: Record<string, any>;
  readOnly?: boolean;
  onFieldChange?: (key: string, value: any) => void;
  actions?: React.ReactNode;
}

function SideBySideView({
  documentId,
  category,
  confidence,
  fields,
  readOnly,
  onFieldChange,
  actions,
}: SideBySideViewProps) {
  return (
    <div className="flex h-full">
      {/* Left: Original scan */}
      <div className="w-1/2 border-r border-border flex flex-col bg-black/20">
        <div className="h-10 border-b border-border flex items-center px-4 bg-surface-raised shrink-0">
          <FileImage className="w-3.5 h-3.5 text-text-muted mr-2" />
          <span className="text-xs text-text-secondary">Original Scan</span>
        </div>
        <div className="flex-1 overflow-auto p-2 flex items-start justify-center">
          <img
            src={`/api/documents/${documentId}/file`}
            alt="Original scan"
            className="max-w-full h-auto rounded-lg shadow-lg"
          />
        </div>
      </div>

      {/* Right: Extracted data */}
      <div className="w-1/2 flex flex-col">
        <div className="h-10 border-b border-border flex items-center justify-between px-4 bg-surface-raised shrink-0">
          <div className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-text-muted" />
            <span className="text-xs text-text-secondary">Extracted Data</span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded-md font-medium",
                CATEGORY_COLORS[category || ""] ||
                  "bg-surface-overlay text-text-secondary"
              )}
            >
              {CATEGORY_LABELS[category || ""] || category || "Unknown"}
            </span>
            {confidence != null && (
              <span
                className={cn(
                  "text-xs font-medium",
                  confidence > 0.7
                    ? "text-success"
                    : confidence > 0.4
                      ? "text-warning"
                      : "text-danger"
                )}
              >
                {Math.round(confidence * 100)}% confidence
              </span>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-3">
            {Object.entries(fields).map(([key, value]) => {
              const isComplex =
                typeof value === "object" && value !== null;
              const isLongText =
                typeof value === "string" && value.length > 80;

              return (
                <div key={key} className="flex gap-3">
                  <label className="w-40 shrink-0 text-xs text-text-secondary pt-2 text-right">
                    {formatFieldName(key)}
                  </label>
                  <div className="flex-1">
                    {readOnly ? (
                      isComplex ? (
                        <pre className="bg-surface-overlay border border-border rounded-lg px-3 py-2 text-xs text-text-primary overflow-x-auto whitespace-pre-wrap">
                          {JSON.stringify(value, null, 2)}
                        </pre>
                      ) : (
                        <div className="bg-surface-overlay border border-border rounded-lg px-3 py-2 text-sm text-text-primary min-h-[36px]">
                          {renderValue(value)}
                        </div>
                      )
                    ) : isComplex ? (
                      <textarea
                        value={JSON.stringify(value, null, 2)}
                        onChange={(e) => {
                          try {
                            onFieldChange?.(key, JSON.parse(e.target.value));
                          } catch {
                            // let them keep typing
                          }
                        }}
                        rows={Math.min(
                          JSON.stringify(value, null, 2).split("\n").length,
                          8
                        )}
                        className="w-full bg-surface-overlay border border-border rounded-lg px-3 py-2 text-xs text-text-primary font-mono resize-none focus:outline-none focus:border-mine-600"
                      />
                    ) : typeof value === "boolean" ? (
                      <select
                        value={String(value)}
                        onChange={(e) =>
                          onFieldChange?.(key, e.target.value === "true")
                        }
                        className="bg-surface-overlay border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-mine-600"
                      >
                        <option value="true">Yes</option>
                        <option value="false">No</option>
                      </select>
                    ) : isLongText ? (
                      <textarea
                        value={String(value ?? "")}
                        onChange={(e) => onFieldChange?.(key, e.target.value)}
                        rows={3}
                        className="w-full bg-surface-overlay border border-border rounded-lg px-3 py-2 text-sm text-text-primary resize-none focus:outline-none focus:border-mine-600"
                      />
                    ) : (
                      <input
                        type="text"
                        value={String(value ?? "")}
                        onChange={(e) => onFieldChange?.(key, e.target.value)}
                        className="w-full bg-surface-overlay border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-mine-600"
                      />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Actions footer */}
        {actions && (
          <div className="border-t border-border p-4 flex justify-end bg-surface-raised shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
