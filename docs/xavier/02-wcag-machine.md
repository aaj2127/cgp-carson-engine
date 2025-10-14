2) WCAG Machine — Engine & Overlay

This file includes worker orchestration, the audit runner, report exporter, and overlay UI component.

2.1 Worker Orchestration (apps/workers/src/index.ts)

```ts
import { Queue, Worker } from "bullmq";
import { runAudit } from "@/services/wcag-audit/run";
import { generateReport } from "@/services/wcag-audit/report";
import { syncLastFm } from "@/services/lastfm-engine/sync";
import { interpretDream } from "@/services/dream-interpreter/interpret";
import { computeEnergyPulse } from "@/services/health-engine/pulse";
import { buildEbook } from "@/services/ebook-engine/build";
import { scanTrends } from "@/services/boe/scan";

const connection = { connection: { url: process.env.REDIS_URL! } };

export const q = {
  wcag: new Queue("wcag", connection),
  music: new Queue("music", connection),
  dreams: new Queue("dreams", connection),
  health: new Queue("health", connection),
  ebooks: new Queue("ebooks", connection),
  boe: new Queue("boe", connection),
};

new Worker(
  "wcag",
  async (job) => {
    if (job.name === "audit") return runAudit(job.data);
    if (job.name === "report") return generateReport(job.data);
  },
  connection
);

new Worker("music", (job) => syncLastFm(job.data), connection);
new Worker("dreams", (job) => interpretDream(job.data), connection);
new Worker("health", (job) => computeEnergyPulse(job.data), connection);
new Worker("ebooks", (job) => buildEbook(job.data), connection);
new Worker("boe", (job) => scanTrends(job.data), connection);
```

2.2 Audit Runner (services/wcag-audit/run.ts)

```ts
export async function runAudit({ userId, targetUrl }: { userId: string; targetUrl: string }) {
  // 1) Crawl (headless) → collect URLs
  // 2) Run axe + pa11y per page; aggregate by WCAG rule
  // 3) Run Lighthouse CI profile (accessibility/perf budget)
  // 4) Compute score & store issues; emit event
  const pages = await crawl(targetUrl);
  const issues = await runChecks(pages);
  const score = computeScore(issues);
  const runId = crypto.randomUUID();
  await saveAudit({ userId, targetUrl, issues, score, pages: pages.length, runId });
  await emit("wcag.audit.completed", { userId, targetUrl, score, runId, issuesCount: issues.length });
  return { runId, score, issuesCount: issues.length, pages: pages.length };
}
```

2.3 Report Export (services/wcag-audit/report.ts)

```ts
export async function generateReport({
  auditId,
  formats = ["md", "json"],
}: {
  auditId: string;
  formats?: ("md" | "json" | "pdf")[];
}) {
  const audit = await loadAudit(auditId);
  const md = renderMarkdown(audit);
  const json = JSON.stringify(audit, null, 2);
  const files: Record<string, string | Buffer> = { md, json };
  if (formats.includes("pdf")) files["pdf"] = await htmlToPdf(markdownToHtml(md));
  await storeReportArtifacts(auditId, files);
  await emit("wcag.report.ready", { auditId, formats });
  return { ok: true, formats };
}
```

2.4 Overlay Fix Component (packages/ui/overlay/OverlayHint.tsx)

```tsx
export function OverlayHint({
  issue,
  onApply,
}: {
  issue: { rule: string; selector: string; fix: string };
  onApply: () => void;
}) {
  return (
    <div className="rounded-md border border-blue-500 bg-white/95 p-3 shadow-lg">
      <div className="text-xs uppercase tracking-wide text-blue-600">{issue.rule}</div>
      <div className="mt-1 text-sm text-slate-900">{issue.fix}</div>
      <button className="mt-2 inline-flex items-center gap-1 rounded bg-blue-600 px-2 py-1 text-xs font-semibold text-white shadow hover:bg-blue-700"
        onClick={onApply}
      >
        Apply
      </button>
    </div>
  );
}
```

WCAG Rule library excerpt

- Perceivable: 1.1.1 Non-text Content (alt text), 1.4.3 Contrast
- Operable: 2.1.1 Keyboard, 2.4.1 Skip links
- Understandable: 3.3.1 Error Identification
- Robust: 4.1.2 Name, Role, Value

CI Gate

- Add `pnpm wcag:ci` to `infra/github/ci.yml`; see docs file 04 for CI snippet.
