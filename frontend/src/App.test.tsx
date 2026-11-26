import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

describe("ResumeX AI App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    globalThis.fetch = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/resumes")) {
        return Promise.resolve(
          new Response(JSON.stringify([]), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.includes("/dashboard/overview")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              has_data: false,
              summary_metrics: {
                total_versions: 0,
                latest_ats_score: 0,
                best_ats_score: 0,
                total_job_matches: 0,
                avg_job_match_score: 0,
                interview_sessions_count: 0,
                career_twin_health: 0,
              },
              active_resume: null,
              ats_trend: [],
              skill_distribution: [],
              recent_job_matches: [],
              top_career_recommendations: [],
              priority_recommendations: [],
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      return Promise.resolve(new Response("{}", { status: 200 }));
    }) as unknown as typeof fetch;
  });

  it("renders landing page and navigates to empty dashboard state", async () => {
    render(<App />);
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(2));

    expect(screen.getByText(/Evidence-Backed Career Twin/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Open App/i }));

    await waitFor(() => {
      expect(screen.getByText(/No Resumes Analyzed Yet/i)).toBeInTheDocument();
    });
  });

  it("opens upload modal and rejects invalid extension client-side", async () => {
    render(<App />);
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(2));

    fireEvent.click(screen.getByRole("button", { name: /Upload PDF \/ DOCX Resume/i }));
    expect(screen.getByText(/Analyze New Resume/i)).toBeInTheDocument();

    const fileInput = screen.getByLabelText(/Resume file input/i);
    const badFile = new File(["hello"], "malware.txt", { type: "text/plain" });
    fireEvent.change(fileInput, { target: { files: [badFile] } });

    expect(screen.getByText(/Please select a \.pdf or \.docx resume file/i)).toBeInTheDocument();
  });

  it("toggles dark/light theme cleanly", async () => {
    render(<App />);
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(2));

    expect(document.documentElement.classList.contains("dark")).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: /Toggle color theme/i }));
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
