1) Core Data (Drizzle schema)

Save as: packages/db/schema.ts

```ts
import { pgTable, varchar, text, jsonb, timestamp, integer, serial, index } from "drizzle-orm/pg-core";

type JsonRecord = Record<string, unknown>;

type JsonArray = JsonRecord[];

type MotifRecord = Record<string, number>;

type EbookMeta = {
  authors: string[];
  isbn?: string;
  keywords?: string[];
  language: string;
  publisher?: string;
  edition?: string;
  coverPath?: string;
  theme?: string;
};

type EbookDistPaths = {
  epub?: string;
  pdf?: string;
};

export const users = pgTable("users", {
  id: varchar("id", { length: 36 }).primaryKey(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  name: varchar("name", { length: 120 }),
  createdAt: timestamp("created_at").defaultNow(),
});

export const events = pgTable(
  "events",
  {
    id: varchar("id", { length: 36 }).primaryKey(),
    userId: varchar("user_id", { length: 36 }).notNull(),
    type: varchar("type", { length: 80 }).notNull(),
    payload: jsonb("payload").$type<JsonRecord>(),
    at: timestamp("at").defaultNow(),
  },
  (t) => ({ byUserType: index("events_user_type_idx").on(t.userId, t.type) })
);

export const audits = pgTable("audits", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  targetUrl: text("target_url").notNull(),
  score: integer("score").default(0),
  issues: jsonb("issues").$type<JsonArray>(),
  pages: integer("pages").default(0),
  runId: varchar("run_id", { length: 36 }),
  status: varchar("status", { length: 20 }).default("queued"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const tracks = pgTable("tracks", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  artist: varchar("artist", { length: 255 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  playedAt: timestamp("played_at").notNull(),
  features: jsonb("features").$type<JsonRecord>(),
  embedding: jsonb("embedding").$type<JsonRecord>(),
});

export const dreams = pgTable("dreams", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  text: text("text").notNull(),
  tags: jsonb("tags").$type<string[]>().default([]),
  symbols: jsonb("symbols").$type<JsonArray>().default([]),
  motifs: jsonb("motifs").$type<MotifRecord>().default({}),
  sentiment: integer("sentiment"),
  interpretation: jsonb("interpretation").$type<JsonRecord>(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const healthMetrics = pgTable("health_metrics", {
  id: serial("id").primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  date: timestamp("date").notNull(),
  hrv: integer("hrv"),
  sleepScore: integer("sleep_score"),
  activityMinutes: integer("activity_minutes"),
  rpe: integer("rpe"),
});

export const rituals = pgTable("rituals", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  name: varchar("name", { length: 120 }).notNull(),
  inputs: jsonb("inputs").$type<JsonRecord>(),
  steps: jsonb("steps").$type<JsonArray>(),
  linkedArtifactId: varchar("linked_artifact_id", { length: 36 }),
  createdAt: timestamp("created_at").defaultNow(),
});

export const crmLeads = pgTable("crm_leads", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  name: varchar("name", { length: 255 }),
  email: varchar("email", { length: 255 }),
  stage: varchar("stage", { length: 50 }).default("new"),
  score: integer("score").default(0),
  nextActionAt: timestamp("next_action_at"),
});

export const ebooks = pgTable("ebooks", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  slug: varchar("slug", { length: 120 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  meta: jsonb("meta").$type<EbookMeta>(),
  a11yReport: jsonb("a11y_report").$type<JsonRecord>(),
  distPaths: jsonb("dist_paths").$type<EbookDistPaths>(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const automationConnections = pgTable("automation_connections", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull(),
  provider: varchar("provider", { length: 40 }).notNull(),
  config: jsonb("config").$type<JsonRecord>().default({}),
  createdAt: timestamp("created_at").defaultNow(),
});
```

Notes

- Keep types strict in packages/sdk to reuse DB types.
- Use drizzle-kit for migrations; db:push included in root scripts.
