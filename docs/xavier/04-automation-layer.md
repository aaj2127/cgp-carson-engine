4) Automation Layer — Bika.ai Adapter + Migration-ready

Goal: vendor-agnostic automations with an adapter for Bika.ai and drop-in providers for Zapier / n8n / Make / Airflow.

4.1 Events (packages/sdk/src/events.ts)

```ts
export type XavierEvent =
  | {
      type: "wcag.audit.completed";
      userId: string;
      data: {
        runId: string;
        score: number;
        issuesCount: number;
        targetUrl: string;
      };
    }
  | {
      type: "wcag.report.ready";
      userId: string;
      data: { auditId: string; formats: string[] };
    }
  | {
      type: "dream.interpreted";
      userId: string;
      data: { id: string; motifs: Record<string, number> };
    }
  | {
      type: "music.archetypes.ready";
      userId: string;
      data: { archetypes: string[] };
    }
  | {
      type: "health.pulse.computed";
      userId: string;
      data: { date: string; energy: number; band: "Do" | "Defer" | "Avoid" };
    }
  | {
      type: "ebook.built";
      userId: string;
      data: { slug: string; targets: string[]; warnings?: number };
    }
  | {
      type: "boe.opportunities.ready";
      userId: string;
      data: { artifactId: string; count: number };
    };
```

4.2 Provider interface (packages/sdk/src/automation.ts)

```ts
export interface AutomationProvider {
  name: "bika" | "zapier" | "n8n" | "make" | "airflow" | "custom";
  send(event: XavierEvent): Promise<{ ok: boolean }>;
  poll?(cursor?: string): Promise<{ events: XavierEvent[]; next?: string }>;
}

export class AutomationBus {
  constructor(private providers: AutomationProvider[]) {}
  async emit(evt: XavierEvent) {
    return Promise.allSettled(this.providers.map((p) => p.send(evt)));
  }
}
```

4.3 Bika.ai provider (packages/sdk/src/providers/bika.ts)

```ts
import crypto from "node:crypto";
import type { AutomationProvider } from "../automation";
import type { XavierEvent } from "../events";

export function BikaProvider({
  url,
  apiKey,
  signingSecret,
}: {
  url: string;
  apiKey: string;
  signingSecret: string;
}): AutomationProvider {
  const sign = (body: string) =>
    crypto.createHmac("sha256", signingSecret).update(body).digest("hex");

  return {
    name: "bika",
    async send(event: XavierEvent) {
      const body = JSON.stringify({ event });
      const res = await fetch(`${url}/hooks/xavier`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": apiKey,
          "x-signature": sign(body),
        },
        body,
      });
      return { ok: res.ok };
    },
  };
}
```

4.4 Zapier / n8n / Make / Airflow providers (packages/sdk/src/providers)

- Zapier

```ts
export function ZapierProvider({ webhookUrl }: { webhookUrl: string }): AutomationProvider {
  return {
    name: "zapier",
    async send(event) {
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(event),
      });
      return { ok: res.ok };
    },
  };
}
```

- n8n & Make follow the same pattern. Airflow posts `{ conf: event }` to the DAG URL with auth header.

4.5 Wiring the bus (services/automations/bus.ts)

```ts
import { AutomationBus } from "@/packages/sdk/src/automation";
import { BikaProvider } from "@/packages/sdk/src/providers/bika";
import { ZapierProvider } from "@/packages/sdk/src/providers/zapier";
import { N8nProvider } from "@/packages/sdk/src/providers/n8n";
import { MakeProvider } from "@/packages/sdk/src/providers/make";

export const bus = new AutomationBus(
  [
    BikaProvider({
      url: process.env.BIKA_API_URL!,
      apiKey: process.env.BIKA_API_KEY!,
      signingSecret: process.env.AUTOMATIONS_SIGNING_SECRET!,
    }),
    process.env.ZAPIER_WEBHOOK && ZapierProvider({ webhookUrl: process.env.ZAPIER_WEBHOOK }),
    process.env.N8N_WEBHOOK && N8nProvider({ webhookUrl: process.env.N8N_WEBHOOK }),
    process.env.MAKE_WEBHOOK && MakeProvider({ webhookUrl: process.env.MAKE_WEBHOOK }),
  ].filter(Boolean) as AutomationProvider[]
);

export async function emit(type: XavierEvent["type"], data: XavierEvent["data"] & { userId: string }) {
  const evt: XavierEvent = { type, userId: data.userId, data } as XavierEvent;
  return bus.emit(evt);
}
```

4.6 Inbound webhook receiver (apps/web/app/api/automations/inbound/route.ts)

```ts
import { NextRequest, NextResponse } from "next/server";
import crypto from "node:crypto";

function verify(req: NextRequest, body: string) {
  const sig = req.headers.get("x-signature") ?? "";
  const expect = crypto
    .createHmac("sha256", process.env.AUTOMATIONS_SIGNING_SECRET!)
    .update(body)
    .digest("hex");
  return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expect));
}

export async function POST(req: NextRequest) {
  const body = await req.text();
  if (!verify(req, body)) return new NextResponse("invalid signature", { status: 401 });
  const { action, payload } = JSON.parse(body);
  // Example actions: schedule.audit, build.ebook, send.digest
  if (action === "schedule.audit") {
    // enqueue WCAG audit
  }
  if (action === "build.ebook") {
    // enqueue e-book build
  }
  return NextResponse.json({ ok: true });
}
```

4.7 Example: Emitting an event

```ts
await emit("wcag.audit.completed", {
  userId,
  runId,
  score,
  issuesCount,
  targetUrl,
});
```

Migration strategy

- Keep adapters under packages/sdk/src/providers.
- Replace BikaProvider implementation if Bika publishes an SDK/OAuth.
- Add provider config rows in automation_connections table for user-level wiring.

---- APPENDIX: CI snippet, SOPs, Admin & Use Cases ----

Add to /docs/xavier/04-automation-layer.md or a separate file:

CI / CD (infra/github/ci.yml excerpt)

```yml
name: ci
on: [push, pull_request]
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: pnpm i
      - run: pnpm -w lint && pnpm -w typecheck && pnpm -w test
  wcag-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm wcag:ci
```

SOPs (Operator Playbooks)

- Daily Ingest (08:00 ET): Music sync → Health import → BOE scan
- Daily Digest (08:30 ET): Energy Pulse + 3 Focus items + 1 ritual + fix sprint if WCAG deltas
- WCAG Release: Overlay PR -> CI axe/pa11y/LH ≥ 95 -> ship & notify bus

Quick automation examples

- After Audit Completes → Create Bika Task & Slack DM
- BOE finds opportunities → Build outline ebook
- Low energy → Rebalance focus lane, silence notifications

Admin & Privacy

- RBAC in admin app
- Artifact export & delete flows
- Event audit log
- Secrets locally via .env, KMS in production
