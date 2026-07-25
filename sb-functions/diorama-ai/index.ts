// ============================================================
// Supabase Edge Function: diorama-ai
// ステークホルダー・ジオラマの「AIで下ごしらえ」の中継役。
//
// ブラウザにAPIキーを置かないために、この関数がキーを預かる。
// キーは必ず Supabase の Secrets（環境変数）に入れること。
// デプロイ手順は同じフォルダの README.md を読む。
// ============================================================

const ALLOWED_ORIGINS = new Set([
  "https://kizukikumitate.com",
  "https://www.kizukikumitate.com",
  "https://kizukikumitate-stack.github.io",
  "http://localhost:8000",
  "http://127.0.0.1:8000",
]);

const MODEL = Deno.env.get("ANTHROPIC_MODEL") || "claude-sonnet-4-6";

function corsHeaders(origin: string | null) {
  const allow = origin && ALLOWED_ORIGINS.has(origin) ? origin : "https://kizukikumitate.com";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

function prompt(business: string) {
  return `あなたはバリューチェーン分析とマルチステークホルダー対話の専門家です。次のビジネスを分析してください:「${business}」

以下のJSON形式のみで回答してください。前置き・説明・コードブロック記法は一切書かないこと。
{"primary":["主活動を上流から下流の順に5〜6個。各10字以内"],"support":["支援活動を3〜4個。各10字以内"],"stakeholders":[{"name":"関係者名8字以内","emoji":"絵文字1つ","situation":"その関係者が置かれている状況を35字以内で"}],"themes":["このビジネスの関係者間で対話する価値のある論点を3個。各22字以内"]}

stakeholdersは6個。顧客・従業員・取引先だけでなく、地域社会・環境・将来世代など見落とされがちな関係者も含めること。`;
}

Deno.serve(async (req: Request) => {
  const origin = req.headers.get("origin");
  const cors = corsHeaders(origin);

  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), {
      status: 405,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }
  if (origin && !ALLOWED_ORIGINS.has(origin)) {
    return new Response(JSON.stringify({ error: "origin not allowed" }), {
      status: 403,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  const apiKey = Deno.env.get("ANTHROPIC_API_KEY");
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "server not configured" }), {
      status: 500,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  let business = "";
  try {
    const body = await req.json();
    business = String(body.business || "").trim().slice(0, 200);
  } catch (_e) {
    business = "";
  }
  if (!business) {
    return new Response(JSON.stringify({ error: "business is required" }), {
      status: 400,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1000,
        messages: [{ role: "user", content: prompt(business) }],
      }),
    });
    const json = await res.json();
    if (json.error) throw new Error(json.error.message || "api error");

    const text = (json.content || [])
      .filter((i: { type: string }) => i.type === "text")
      .map((i: { text: string }) => i.text)
      .join("\n");
    const parsed = JSON.parse(text.replace(/```json|```/g, "").trim());

    return new Response(JSON.stringify({ result: parsed }), {
      headers: { ...cors, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error(e);
    return new Response(JSON.stringify({ error: "generation failed" }), {
      status: 502,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }
});
