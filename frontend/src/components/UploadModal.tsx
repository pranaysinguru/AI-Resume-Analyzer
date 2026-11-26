import React, { useState } from "react";
import { FileText, ShieldCheck, UploadCloud, X, AlertCircle, Loader2 } from "lucide-react";
import { api } from "../api/client";
import type { ResumeDetail, ResumeSummary } from "../types/api";

interface UploadModalProps {
  open: boolean;
  onClose: () => void;
  existingResumes: ResumeSummary[];
  onUploaded: (resume: ResumeDetail) => void;
}

const ROLE_OPTIONS = [
  "",
  "AI / Machine Learning Engineer",
  "Full Stack Software Engineer",
  "Backend & API Engineer",
  "Frontend Engineer",
  "Data Scientist",
  "Data Engineer",
  "DevOps / Cloud Platform Engineer",
  "Applied LLM / AI Product Engineer",
];

export const UploadModal: React.FC<UploadModalProps> = ({
  open,
  onClose,
  existingResumes,
  onUploaded,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [versionLabel, setVersionLabel] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [attachProfileId, setAttachProfileId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const uniqueProfiles = Array.from(
    new Map(existingResumes.map((r) => [r.profile_id, r])).values()
  );

  const handleFilePick = (picked: File | null) => {
    setError(null);
    if (!picked) return;
    const lower = picked.name.toLowerCase();
    if (!lower.endsWith(".pdf") && !lower.endsWith(".docx")) {
      setError("Please select a .pdf or .docx resume file.");
      return;
    }
    setFile(picked);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Select a PDF or DOCX resume to analyze.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const uploaded = await api.uploadResume(file, {
        profileId: attachProfileId ? Number(attachProfileId) : undefined,
        versionLabel: versionLabel.trim() || undefined,
        targetRole: targetRole || undefined,
      });
      setFile(null);
      setVersionLabel("");
      onUploaded(uploaded);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Analyze New Resume
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Supports text-selectable PDF & DOCX up to 10 MB
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close upload modal"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragActive(false);
              handleFilePick(e.dataTransfer.files?.[0] ?? null);
            }}
            className={`relative rounded-xl border-2 border-dashed p-6 text-center transition-colors ${
              dragActive
                ? "border-indigo-500 bg-indigo-500/10"
                : "border-slate-300 dark:border-slate-700 hover:border-indigo-400"
            }`}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              aria-label="Resume file input"
              onChange={(e) => handleFilePick(e.target.files?.[0] ?? null)}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileText className="w-9 h-9 text-indigo-500" />
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                  {file.name}
                </p>
                <p className="text-xs text-slate-500">
                  {(file.size / 1024).toFixed(1)} KB — Click or drop to replace
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <UploadCloud className="w-10 h-10 text-indigo-500" />
                <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                  Drag & drop your resume here, or click to browse
                </p>
                <p className="text-xs text-slate-500">PDF or DOCX only</p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
                Version Label (optional)
              </label>
              <input
                type="text"
                value={versionLabel}
                onChange={(e) => setVersionLabel(e.target.value)}
                placeholder="e.g., v2 AI Engineer"
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
                Target Role (optional)
              </label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Auto-detect best role</option>
                {ROLE_OPTIONS.filter(Boolean).map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {uniqueProfiles.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
                Track Under Candidate Profile (for Version Diff)
              </label>
              <select
                value={attachProfileId}
                onChange={(e) => setAttachProfileId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Create new candidate profile</option>
                {uniqueProfiles.map((r) => (
                  <option key={r.profile_id} value={r.profile_id}>
                    Profile #{r.profile_id} (Latest: {r.version_label})
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex items-start gap-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-700 dark:text-emerald-300">
            <ShieldCheck className="w-4 h-4 mt-0.5 shrink-0" />
            <span>
              <strong>Privacy-First Processing:</strong> Raw files are parsed in memory and never saved to disk. Email and phone PII are automatically masked.
            </span>
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-xl bg-rose-500/10 border border-rose-500/25 p-3 text-xs text-rose-600 dark:text-rose-300">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Parsing & Analyzing...
                </>
              ) : (
                "Run AI Analysis"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
