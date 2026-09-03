import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  const auth = req.headers.get("Authorization") || "";
  if (!auth.startsWith("Bearer ")) return json({ error: "Unauthorized" }, 401);

  const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
  const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  if (!supabaseUrl || !serviceRole) {
    return json({ error: "Server configuration missing" }, 500);
  }

  const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
    headers: { Authorization: auth, apikey: serviceRole },
  });
  if (!userResponse.ok) return json({ error: "Unauthorized" }, 401);

  const user = await userResponse.json();
  if (!user?.id) return json({ error: "Unauthorized" }, 401);

  const adminResponse = await fetch(
    `${supabaseUrl}/rest/v1/admin_users?select=user_id&user_id=eq.${encodeURIComponent(user.id)}&limit=1`,
    {
      headers: {
        Authorization: `Bearer ${serviceRole}`,
        apikey: serviceRole,
        Accept: "application/json",
      },
    },
  );
  if (!adminResponse.ok) {
    return json({ error: "Could not verify admin access" }, 500);
  }

  const admins = await adminResponse.json();
  if (!Array.isArray(admins) || admins.length === 0) {
    return json({ error: "Forbidden" }, 403);
  }

  const githubToken = Deno.env.get("GITHUB_ACTIONS_TOKEN") || "";
  if (!githubToken) {
    return json(
      {
        ok: true,
        dispatched: false,
        mode: "schedule_fallback",
        message:
          "Immediate GitHub dispatch is not configured; scheduled deployment remains available.",
      },
      202,
    );
  }

  const githubResponse = await fetch(
    "https://api.github.com/repos/nauda199x/smartcity-sale/actions/workflows/site-pipeline.yml/dispatches",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "smartcity-marketplace-seo-sync",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: "main" }),
    },
  );

  if (githubResponse.status === 204) {
    return json(
      { ok: true, dispatched: true, mode: "workflow_dispatch" },
      202,
    );
  }

  const detail = (await githubResponse.text()).slice(0, 300);
  return json(
    {
      error: "GitHub workflow dispatch failed",
      github_status: githubResponse.status,
      detail,
    },
    502,
  );
});
