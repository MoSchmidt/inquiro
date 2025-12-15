import { defineStore } from 'pinia';
import { summarisePaper } from '@/services/papers';
import { reactive } from 'vue';

export type SummaryStatus = "idle" | "loading" | "success" | "error";

export interface StructuredSummary {
  title: string;
  executive_summary: string;
  relevance_to_query?: string;
  methodology_points: string[];
  results_points: string[];
  limitations: string;
}

export type SummaryEntry = {
  status: SummaryStatus;
  summaryMarkdown: string | null;
  structuredData: StructuredSummary | null;
  error: string | null;
  updatedAt: number | null;
};

type SummaryStoreState = {
  entries: Record<string, SummaryEntry>;
  inFlight: Record<string, Promise<void> | undefined>;
}

function ensureEntry(state: SummaryStoreState, paperId: number): SummaryEntry {
  if (!state.entries[paperId]) {
    state.entries[paperId] = {
      status: "idle",
      summaryMarkdown: null,
      structuredData: null,
      error: null,
      updatedAt: null,
    };
  }
  return state.entries[paperId];
}

function formatSummaryToMarkdown(data: StructuredSummary): string {
  const parts = [
    `### Executive Summary\n${data.executive_summary}`,
  ];

  if (data.relevance_to_query) {
    parts.push(`### Relevance to Query\n${data.relevance_to_query}`);
  }

  parts.push(`### Core Methodology\n${data.methodology_points.map(p => `* ${p}`).join('\n')}`);
  parts.push(`### Key Findings & Results\n${data.results_points.map(p => `* ${p}`).join('\n')}`);
  parts.push(`### Critical Analysis & Limitations\n${data.limitations}`);

  return parts.join('\n\n');
}

export const usePaperSummariesStore = defineStore("paperSummaries", () => {
  const state = reactive<SummaryStoreState>({
    entries: {},
    inFlight: {},
  });

  const entry = (paperId: number) => ensureEntry(state, paperId);

  const hasSummary = (paperId: number): boolean => {
    const e = state.entries[paperId];
    return e?.status === "success" && !!e?.summaryMarkdown;
  };

  const summarise = async (
    paperId: number,
    opts?: { force?: boolean, query?: string }
  ) => {
    const e = ensureEntry(state, paperId);

    if (!opts?.force && e.status === "success" && e.summaryMarkdown) return;

    if (state.inFlight[paperId]) return state.inFlight[paperId];

    e.status = "loading";
    e.error = null;

    const p = (async () => {
      try {
        const result = (await summarisePaper(paperId, opts?.query || "")) as unknown as StructuredSummary;

        if (!result || !result.executive_summary) {
          throw new Error("Invalid summary format returned.");
        }

        e.structuredData = result;
        e.summaryMarkdown = formatSummaryToMarkdown(result);
        e.status = "success";
        e.updatedAt = Date.now();
      } catch (err: unknown) {
        e.status = "error";
        e.error = err instanceof Error ? err.message : "Failed to summarise paper.";
      } finally {
        state.inFlight[paperId] = undefined;
      }
    })();

    state.inFlight[paperId] = p;
    return p;
  };

  const clear = (paperId: number) => {
    delete state.entries[paperId];
    delete state.inFlight[paperId];
  };

  const clearAll = () => {
    state.entries = {};
    state.inFlight = {};
  };

  return {
    entry,
    hasSummary,

    summarise,
    clear,
    clearAll,
  };
});
