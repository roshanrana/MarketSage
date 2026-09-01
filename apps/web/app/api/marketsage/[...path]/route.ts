import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const analyticsURL = process.env.MARKETSAGE_ANALYTICS_URL ?? "http://127.0.0.1:8765";
const analyticsToken = process.env.MARKETSAGE_HTTP_TOKEN;

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const target = new URL(path.join("/"), `${analyticsURL.replace(/\/$/, "")}/`);
  target.search = request.nextUrl.search;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }
  if (analyticsToken) {
    headers.set("authorization", `Bearer ${analyticsToken}`);
  }

  const body =
    request.method === "GET" || request.method === "HEAD" ? undefined : await request.text();
  const upstream = await fetch(target, {
    method: request.method,
    headers,
    body,
    cache: "no-store"
  });

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") ?? "application/json"
    }
  });
}

export async function GET(request: NextRequest, context: RouteContext) {
  return proxy(request, context);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxy(request, context);
}
