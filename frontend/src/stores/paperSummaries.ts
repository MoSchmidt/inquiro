import { defineStore } from 'pinia';
import { summarisePaper } from '@/services/paper';
import { reactive } from 'vue';

export type SummaryStatus = "idle" | "loading" | "success" | "error";

export type SummaryEntry = {
  status: SummaryStatus;
  summary: string | null;
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
      summary: null,
      error: null,
      updatedAt: null,
    };
  }
  return state.entries[paperId];
}

export const usePaperSummariesStore = defineStore("paperSummaries", () => {
  const state = reactive<SummaryStoreState>({
    entries: {},
    inFlight: {},
  });

  const entry = (paperId: number) => ensureEntry(state, paperId);

  const hasSummary = (paperId: number): boolean => {
    const e = state.entries[paperId];
    return e?.status === "success" && !!e?.summary;
  };

  const summarise = async (
    paperId: number,
    opts?: { force?: boolean }
  ) => {
    const e = ensureEntry(state, paperId);

    if (!opts?.force && e.status === "success" && e.summary) return;

    if (state.inFlight[paperId]) return state.inFlight[paperId];

    e.status = "loading";
    e.error = null;

    const p = (async () => {
      try {
        const summary = (await summarisePaper(paperId)).summary;

        if (!summary.trim()) throw new Error("Empty summary returned from server.");

        e.summary = summary;
        e.status = "success";
        e.updatedAt = Date.now();
      } catch (err: any) {
        e.status = "error";
        e.error = err?.message ?? "Failed to summarise paper.";
      } finally {
        state.inFlight[paperId] = undefined;
      }
    })();

    state.inFlight[paperId] = p;
    return p;
  };

  const clear = (paperId: string) => {
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
