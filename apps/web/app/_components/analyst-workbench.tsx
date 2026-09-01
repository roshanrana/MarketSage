"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Database,
  FileText,
  RefreshCw,
  Search,
  ShieldCheck
} from "lucide-react";
import { type ReactNode, useEffect, useMemo, useState, useTransition } from "react";

type Envelope<T> = {
  request_id: string;
  mode: "seeded" | "live" | "hybrid";
  generated_at: string;
  source: string;
  data: T;
  warnings: string[];
  caveats: string[];
};

type DependencyStatus = {
  name: string;
  status: "ok" | "degraded" | "unavailable";
  detail: string;
};

type HealthData = {
  service: string;
  status: "ok" | "degraded" | "unavailable";
  version: string;
  dependencies: DependencyStatus[];
};

type DatasetEntry = {
  dataset_id: string;
  config: string;
  split: string;
  rows_count: number;
  license: string;
  role: string;
  local_status: string;
};

type DatasetStatusData = {
  count: number;
  datasets: DatasetEntry[];
};

type MarketSnapshotData = {
  ticker: string;
  name: string;
  as_of: string;
  price: number;
  currency: string;
  change: number;
  change_percent: number;
  volume: number;
  sector: string;
  source_name: string;
};

type PriceHistoryData = {
  ticker: string;
  observations: Array<{ date: string; close: number; volume?: number }>;
};

type EvidenceSnippet = {
  id: string;
  ticker: string;
  title: string;
  text: string;
  score: number;
  dataset_id: string;
  license: string;
};

type EvidenceSearchData = {
  count: number;
  retrieval_mode: string;
  results: EvidenceSnippet[];
};

type SentimentData = {
  label: "positive" | "negative" | "neutral";
  confidence: number;
  model_id: string;
  fallback: boolean;
  matched_terms: string[];
};

type ResearchBriefData = {
  run_id: string;
  title: string;
  sections: Array<{ title: string; bullets: string[] }>;
  market_snapshots: MarketSnapshotData[];
  sentiment: SentimentData | null;
  evidence: EvidenceSnippet[];
};

const modeOptions = ["seeded", "hybrid", "live"] as const;

async function api<T>(path: string, init?: RequestInit): Promise<Envelope<T>> {
  const response = await fetch(`/api/marketsage${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<Envelope<T>>;
}

function numberFormat(value: number) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);
}

export function AnalystWorkbench() {
  const [ticker, setTicker] = useState("AAPL");
  const [mode, setMode] = useState<(typeof modeOptions)[number]>("seeded");
  const [query, setQuery] = useState("Apple services revenue margin");
  const [health, setHealth] = useState<Envelope<HealthData> | null>(null);
  const [datasets, setDatasets] = useState<Envelope<DatasetStatusData> | null>(null);
  const [snapshot, setSnapshot] = useState<Envelope<MarketSnapshotData> | null>(null);
  const [history, setHistory] = useState<Envelope<PriceHistoryData> | null>(null);
  const [evidence, setEvidence] = useState<Envelope<EvidenceSearchData> | null>(null);
  const [brief, setBrief] = useState<Envelope<ResearchBriefData> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  async function refreshStatus() {
    const [healthResult, datasetResult] = await Promise.all([
      api<HealthData>("/health"),
      api<DatasetStatusData>("/datasets")
    ]);
    setHealth(healthResult);
    setDatasets(datasetResult);
  }

  function runWorkflow() {
    setError(null);
    startTransition(async () => {
      try {
        const [snapshotResult, historyResult, evidenceResult] = await Promise.all([
          api<MarketSnapshotData>("/market/snapshot", {
            method: "POST",
            body: JSON.stringify({ ticker, provider_mode: mode })
          }),
          api<PriceHistoryData>("/market/history", {
            method: "POST",
            body: JSON.stringify({ ticker, provider_mode: mode })
          }),
          api<EvidenceSearchData>("/evidence/search", {
            method: "POST",
            body: JSON.stringify({ query, ticker, top_k: 4 })
          })
        ]);
        const briefResult = await api<ResearchBriefData>("/briefs/research", {
          method: "POST",
          body: JSON.stringify({ tickers: [ticker], horizon: "1w", provider_mode: mode })
        });

        setSnapshot(snapshotResult);
        setHistory(historyResult);
        setEvidence(evidenceResult);
        setBrief(briefResult);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : String(caught));
      }
    });
  }

  useEffect(() => {
    refreshStatus().catch((caught) => {
      setError(caught instanceof Error ? caught.message : String(caught));
    });
  }, []);

  const latestWarnings = useMemo(
    () =>
      [health, datasets, snapshot, evidence, brief]
        .flatMap((item) => item?.warnings ?? [])
        .filter(Boolean)
        .slice(0, 4),
    [health, datasets, snapshot, evidence, brief]
  );

  return (
    <main className="shell">
      <section className="topbar" aria-label="MarketSage command surface">
        <div>
          <p className="eyebrow">MarketSage</p>
          <h1>Analyst Workbench</h1>
        </div>
        <button className="iconButton" type="button" onClick={refreshStatus} aria-label="Refresh">
          <RefreshCw size={18} />
        </button>
      </section>

      <section className="controls" aria-label="Research controls">
        <label>
          <span>Ticker</span>
          <input value={ticker} onChange={(event) => setTicker(event.target.value.toUpperCase())} />
        </label>
        <label className="wide">
          <span>Evidence Query</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </label>
        <div className="segmented" aria-label="Mode">
          {modeOptions.map((option) => (
            <button
              className={mode === option ? "selected" : ""}
              key={option}
              onClick={() => setMode(option)}
              type="button"
            >
              {option}
            </button>
          ))}
        </div>
        <button className="primary" type="button" onClick={runWorkflow} disabled={isPending}>
          <Search size={18} />
          {isPending ? "Running" : "Run Brief"}
        </button>
      </section>

      {error ? (
        <section className="notice error" role="alert">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </section>
      ) : null}

      <section className="grid statusGrid" aria-label="Status summary">
        <Metric
          icon={<Activity size={20} />}
          label="Core"
          value={health?.data.status ?? "unknown"}
          detail={health?.data.version ?? "waiting"}
        />
        <Metric
          icon={<Database size={20} />}
          label="Datasets"
          value={datasets?.data.count ? String(datasets.data.count) : "0"}
          detail="tracked assets"
        />
        <Metric
          icon={<ShieldCheck size={20} />}
          label="Mode"
          value={mode}
          detail={snapshot?.source ?? "seeded default"}
        />
      </section>

      <section className="grid workGrid" aria-label="Analysis results">
        <Panel title="Market Snapshot" icon={<BarChart3 size={18} />}>
          {snapshot ? <SnapshotView snapshot={snapshot.data} /> : <Empty label="No snapshot yet" />}
          {history ? <PriceChart points={history.data.observations} /> : null}
        </Panel>

        <Panel title="Evidence" icon={<FileText size={18} />}>
          {evidence?.data.results.length ? (
            <div className="evidenceList">
              {evidence.data.results.map((item) => (
                <article className="evidenceItem" key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <span>{item.dataset_id}</span>
                  </div>
                  <p>{item.text}</p>
                  <footer>
                    <span>{item.license}</span>
                    <span>{Math.round(item.score * 100)}%</span>
                  </footer>
                </article>
              ))}
            </div>
          ) : (
            <Empty label="No evidence yet" />
          )}
        </Panel>

        <Panel title="Research Brief" icon={<FileText size={18} />} wide>
          {brief ? (
            <div className="brief">
              <div className="briefHeader">
                <h2>{brief.data.title}</h2>
                <span>{brief.data.run_id.slice(0, 8)}</span>
              </div>
              <div className="sectionGrid">
                {brief.data.sections.map((section) => (
                  <section className="briefSection" key={section.title}>
                    <h3>{section.title}</h3>
                    <ul>
                      {section.bullets.map((bullet) => (
                        <li key={bullet}>{bullet}</li>
                      ))}
                    </ul>
                  </section>
                ))}
              </div>
            </div>
          ) : (
            <Empty label="No brief yet" />
          )}
        </Panel>

        <Panel title="Dataset And Caveat Log" icon={<Database size={18} />}>
          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>Dataset</th>
                  <th>Rows</th>
                  <th>License</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {(datasets?.data.datasets ?? []).slice(0, 6).map((item) => (
                  <tr key={`${item.dataset_id}-${item.config}-${item.split}`}>
                    <td>{item.dataset_id}</td>
                    <td>{numberFormat(item.rows_count)}</td>
                    <td>{item.license}</td>
                    <td>{item.local_status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {latestWarnings.length ? (
            <ul className="warnings">
              {latestWarnings.map((warning, index) => (
                <li key={`${warning}-${index}`}>{warning}</li>
              ))}
            </ul>
          ) : null}
        </Panel>
      </section>
    </main>
  );
}

function Metric({
  icon,
  label,
  value,
  detail
}: {
  icon: ReactNode;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="metric">
      <div className="metricIcon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <p>{detail}</p>
      </div>
    </article>
  );
}

function Panel({
  children,
  icon,
  title,
  wide = false
}: {
  children: ReactNode;
  icon: ReactNode;
  title: string;
  wide?: boolean;
}) {
  return (
    <section className={wide ? "panel widePanel" : "panel"}>
      <header>
        <div className="panelIcon">{icon}</div>
        <h2>{title}</h2>
      </header>
      {children}
    </section>
  );
}

function SnapshotView({ snapshot }: { snapshot: MarketSnapshotData }) {
  const positive = snapshot.change_percent >= 0;
  return (
    <div className="snapshot">
      <div>
        <p>{snapshot.ticker}</p>
        <h2>{snapshot.name}</h2>
        <span>{snapshot.sector}</span>
      </div>
      <div className="priceBlock">
        <strong>
          {snapshot.price.toFixed(2)} {snapshot.currency}
        </strong>
        <span className={positive ? "up" : "down"}>
          {snapshot.change_percent > 0 ? "+" : ""}
          {snapshot.change_percent.toFixed(2)}%
        </span>
      </div>
    </div>
  );
}

function PriceChart({ points }: { points: Array<{ date: string; close: number }> }) {
  if (points.length < 2) {
    return null;
  }

  const width = 420;
  const height = 130;
  const min = Math.min(...points.map((point) => point.close));
  const max = Math.max(...points.map((point) => point.close));
  const span = max - min || 1;
  const coordinates = points
    .map((point, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - ((point.close - min) / span) * (height - 20) - 10;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Price trend">
      <polyline points={coordinates} fill="none" stroke="currentColor" strokeWidth="4" />
      {points.map((point, index) => {
        const x = (index / (points.length - 1)) * width;
        const y = height - ((point.close - min) / span) * (height - 20) - 10;
        return <circle cx={x} cy={y} key={point.date} r="4" />;
      })}
    </svg>
  );
}

function Empty({ label }: { label: string }) {
  return <div className="empty">{label}</div>;
}
