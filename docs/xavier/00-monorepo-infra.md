0) Monorepo & Infra (Drop-in)

Version: v1.0 — "Build with Power, Not Pressure"

Prereqs

- Node 20+
- pnpm 9
- Docker / docker-compose

Quick start

```
git clone  xavier && cd xavier
pnpm i
cp .env.example .env
docker compose up -d
pnpm db:push
pnpm dev
```

Recommended layout (drop into repo root)

```
xavier/
├─ apps/
│  ├─ web/                    # Next.js 14 (App Router) – user UI
│  ├─ admin/                  # Ops & QA dashboards
│  └─ workers/                # BullMQ workers
├─ services/
│  ├─ wcag-audit/             # axe/pa11y/Lighthouse orchestration
│  ├─ dream-interpreter/
│  ├─ lastfm-engine/
│  ├─ health-engine/
│  ├─ ritual-engine/
│  ├─ ebook-engine/
│  ├─ boe/
│  └─ automations/
├─ packages/
│  ├─ ui/
│  ├─ db/
│  ├─ prompts/
│  ├─ config/
│  ├─ analytics/
│  └─ sdk/
├─ infra/
│  ├─ compose.yml
│  └─ github/ci.yml
└─ docs/
   └─ xavier/
      ├─ 00-monorepo-infra.md
      ├─ 01-schema.md
      ├─ 02-wcag-machine.md
      ├─ 03-services.md
      └─ 04-automation-layer.md
```

.env.example (excerpt)

```
DATABASE_URL=postgres://postgres:postgres@localhost:5432/xavier
REDIS_URL=redis://localhost:6379
NEXTAUTH_SECRET=...
NEXTAUTH_URL=http://localhost:3000

OPENAI_API_KEY=...
LASTFM_API_KEY=...
BIKA_API_URL=https://api.bika.ai
BIKA_API_KEY=...
AUTOMATIONS_SIGNING_SECRET=...
```

Integrations notes

- Keep Bika adapter config in infra or secret store.
- Provide fallback webhooks for Zapier / n8n / Make via env toggles.
