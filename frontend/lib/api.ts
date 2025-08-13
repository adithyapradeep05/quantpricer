export type Req = { S:number; K:number; r:number; q?:number; sigma:number; T:number; type:"call"|"put"; idempotencyKey?: string };
export type Res = { price:number; greeks:{delta:number;gamma:number;vega:number;theta:number;rho:number}; meta:any };

const BASE = process.env.NEXT_PUBLIC_API_BASE!;
const sleep = (ms:number)=> new Promise(r=>setTimeout(r, ms));

function withTimeout(ms:number, signal?:AbortSignal) {
  const ctl = new AbortController();
  const id = setTimeout(()=>ctl.abort(), ms);
  if (signal) signal.addEventListener("abort", ()=>ctl.abort(), { once: true });
  return { signal: ctl.signal, cancel: ()=>clearTimeout(id) };
}

async function attempt(url:string, init:RequestInit, timeoutMs:number, signal?:AbortSignal) {
  const { signal:toSignal, cancel } = withTimeout(timeoutMs, signal);
  try {
    const res = await fetch(url, { ...init, signal: toSignal, cache: "no-store" });
    return res;
  } finally { cancel(); }
}

function fireEvent(name:string, detail?:any) {
  window.dispatchEvent(new CustomEvent(name, { detail }));
}

export async function apiRequest<T=unknown>(
  path: string,
  body?: any,
  opts?: { method?: "GET"|"POST", timeoutMs?: number, maxAttempts?: number, wakeThresholdMs?: number, signal?:AbortSignal }
): Promise<T> {
  const method = opts?.method ?? (body ? "POST" : "GET");
  const timeoutMs = opts?.timeoutMs ?? 30000; // per attempt
  const maxAttempts = opts?.maxAttempts ?? 3;
  const wakeThresholdMs = opts?.wakeThresholdMs ?? 1200;
  const signal = opts?.signal;

  let showedWake = false;
  const wakeTimer = setTimeout(() => { showedWake = true; fireEvent("qp:waking"); }, wakeThresholdMs);

  // non-blocking warm ping
  attempt(`${BASE}/health`, { method: "GET" }, 3000, signal).catch(()=>{});

  let attemptNo = 0;
  let lastErr: any = null;

  while (attemptNo < maxAttempts) {
    try {
      const res = await attempt(`${BASE}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined
      }, timeoutMs, signal);

      clearTimeout(wakeTimer);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // success
      return (await res.json()) as T;
    } catch (e) {
      lastErr = e;
      attemptNo++;
      if (attemptNo >= maxAttempts) break;
      const backoff = 800 * Math.pow(2, attemptNo - 1) + Math.random() * 300; // 0.8s, 1.6s
      await sleep(backoff);
    }
  }
  clearTimeout(wakeTimer);
  if (showedWake) fireEvent("qp:wake-failed");
  throw lastErr ?? new Error("Request failed");
}
