3) Services: APIs, E-Book, Dreams, Music, Health, Rituals, BOE

3.1 API — Next.js App Router (apps/web/app/api)

- WCAG enqueue: apps/web/app/api/wcag/audits/route.ts

```ts
import { NextRequest, NextResponse } from "next/server";
import { q } from "@/apps/workers/src/index";

export async function POST(req: NextRequest) {
  const { targetUrl } = await req.json();
  const userId = "session-user"; // inject via auth
  await q.wcag.add("audit", { userId, targetUrl });
  return NextResponse.json({ status: "queued" }, { status: 202 });
}
```

- Ebooks enqueue: apps/web/app/api/ebooks/route.ts

```ts
import { NextRequest, NextResponse } from "next/server";
import { q } from "@/apps/workers/src/index";

export async function POST(req: NextRequest) {
  const { slug, targets = ["epub", "pdf"] } = await req.json();
  const userId = "session-user";
  await q.ebooks.add("build", { userId, slug, targets });
  return NextResponse.json({ status: "queued", slug });
}
```

- Dreams enqueue: apps/web/app/api/dreams/route.ts

```ts
import { NextRequest, NextResponse } from "next/server";
import { q } from "@/apps/workers/src/index";

export async function POST(req: NextRequest) {
  const { text, tags = [] } = await req.json();
  const userId = "session-user";
  const job = await q.dreams.add("interpret", { userId, text, tags });
  return NextResponse.json({ status: "queued", jobId: job.id }, { status: 202 });
}
```

3.2 E-Book Engine (services/ebook-engine/build.ts)

```ts
export async function buildEbook({
  userId,
  slug,
  targets = ["epub", "pdf"],
}: {
  userId: string;
  slug: string;
  targets?: ("epub" | "pdf")[];
}) {
  const book = await loadBook(slug);
  const lint = await lintBook(book); // alt-text, heading order, links
  const epub = targets.includes("epub") ? await renderEpub(book) : null;
  const pdf = targets.includes("pdf") ? await renderPdf(book) : null;
  await saveEbookArtifact({ userId, slug, lint, epub, pdf });
  await emit("ebook.built", { userId, slug, targets, warnings: lint?.warnings?.length ?? 0 });
  return { slug, targets };
}
```

3.3 Dream Interpreter (services/dream-interpreter/interpret.ts)

```ts
export async function interpretDream({
  userId,
  text,
  tags = [],
}: {
  userId: string;
  text: string;
  tags?: string[];
}) {
  const symbols = extractSymbols(text);
  const sentiment = scoreSentiment(text);
  const motifs = motifFrequencies(symbols);
  const interpretations = threeTierInterpretation({ text, symbols, sentiment, motifs });
  const ritual = composeRitual({ motifs, sentiment });
  const id = await saveDream({
    userId,
    text,
    tags,
    symbols,
    motifs,
    sentiment,
    interpretation: interpretations,
    ritual,
  });
  await emit("dream.interpreted", { userId, id, motifs });
  return { id, symbols, motifs, interpretations, ritual };
}
```

3.4 Music Identity (services/lastfm-engine/sync.ts)

```ts
export async function syncLastFm({ userId }: { userId: string }) {
  const scrobbles = await fetchRecent(userId);
  const fe = await featureExtract(scrobbles);
  const embs = await embedTracks(fe);
  const archetypes = clusterArchetypes(embs);
  await saveTracks({ userId, scrobbles, fe, embs, archetypes });
  await emit("music.archetypes.ready", { userId, archetypes });
  return { imported: scrobbles.length, archetypes };
}
```

3.5 Health Pulse (services/health-engine/pulse.ts)

```ts
export async function computeEnergyPulse({
  userId,
  date = new Date(),
}: {
  userId: string;
  date?: Date;
}) {
  const metrics = await getDailyHealth(userId, date);
  const energy = Math.round(
    clamp(
      0,
      100,
      0.4 * (metrics.hrv ?? 50) +
        0.3 * (metrics.sleepScore ?? 60) +
        0.2 * ((metrics.activityMinutes ?? 30) / 2) +
        0.1 * (100 - (metrics.rpe ?? 50))
    )
  );
  const band = energy >= 70 ? "Do" : energy >= 45 ? "Defer" : "Avoid";
  const suggestions = suggestProtocol({ energy, metrics });
  await emit("health.pulse.computed", { userId, date, energy, band });
  return { energy, band, suggestions };
}
```

3.6 Ritual Engine (services/ritual-engine/generate.ts)

```ts
export async function generateRitual({
  userId,
  context,
}: {
  userId: string;
  context: {
    music?: string[];
    motifs?: Record<string, number>;
    energy?: number;
    crmPressure?: number;
  };
}) {
  const tone = chooseTone(context);
  const steps = buildSteps(context, tone);
  const id = await saveRitual({ userId, name: tone.name, inputs: context, steps });
  await emit("ritual.generated", { userId, id, tone });
  return { id, tone, steps };
}
```

3.7 Blue Ocean Explorer (services/boe/scan.ts)

```ts
export async function scanTrends({
  userId,
  sources = ["hn", "ph", "substack", "arxiv"],
}: {
  userId: string;
  sources?: string[];
}) {
  const feed = await fetchFeeds(sources);
  const clusters = clusterTopics(feed);
  const opportunities = clusters.map((c) => toOpportunityCard(c));
  const artifactId = await saveBoeArtifact({ userId, sources, opportunities });
  await emit("boe.opportunities.ready", { userId, artifactId, count: opportunities.length });
  return { artifactId, count: opportunities.length };
}
```

Opportunity Card (Type)

```ts
export type Opportunity = {
  id: string;
  theme: string;
  signals: { source: string; url: string; score: number }[];
  productIdea: string;
  automationHooks: string[];
  pricing: { model: "b2c" | "b2b" | "hybrid"; suggestion: string };
  speedToLaunch: "weekend" | "2weeks" | "1month";
  moat: string;
};
```
