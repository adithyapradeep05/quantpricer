import { useEffect, useMemo, useRef, useState } from "react";
import { apiRequest, Req, Res } from "@/lib/api";
import { stableHash } from "@/lib/hash";

const HISTORY_KEY = "qp_history"; // array of { at, paramsHash, params, result }

function saveHistory(params:Req, result:Res) {
  try {
    const arr = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    const paramsHash = stableHash(params);
    arr.unshift({ at: Date.now(), paramsHash, params, result });
    localStorage.setItem(HISTORY_KEY, JSON.stringify(arr.slice(0, 50)));
  } catch {}
}

function getCachedByParams(params:Req): Res | null {
  try {
    const arr = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    const paramsHash = stableHash(params);
    const hit = arr.find((x:any)=> x.paramsHash === paramsHash);
    return hit ? (hit.result as Res) : null;
  } catch { return null; }
}

export function usePrice() {
  const [waking, setWaking] = useState(false);
  const [bannerText, setBannerText] = useState("Waking server… first request may take ~30–60s");
  const [lastCached, setLastCached] = useState<Res | null>(null);

  const timers = useRef<number[]>([]);

  useEffect(()=>{
    const onWake = () => {
      setWaking(true);
      setBannerText("Waking server… first request may take ~30–60s");
      // progressive messages
      timers.current.push(window.setTimeout(()=> setBannerText("Still waking… Render Free can take ~30–60s on the first hit"), 15000));
      timers.current.push(window.setTimeout(()=> setBannerText("Almost there… you can Cancel and retry anytime"), 45000));
    };
    const onFail = () => {
      setWaking(false);
      timers.current.forEach(id=>clearTimeout(id));
      timers.current = [];
    };
    window.addEventListener("qp:waking", onWake);
    window.addEventListener("qp:wake-failed", onFail);
    return ()=>{
      window.removeEventListener("qp:waking", onWake);
      window.removeEventListener("qp:wake-failed", onFail);
    };
  }, []);

  useEffect(()=>{
    // user-initiated warm ping on mount
    apiRequest("/health", undefined, { method: "GET", timeoutMs: 2000, maxAttempts: 1 }).catch(()=>{});
  }, []);

  const price = useMemo(()=> {
    return async (params: Omit<Req, "idempotencyKey">, signal?: AbortSignal): Promise<Res> => {
      // populate cached
      setLastCached(getCachedByParams(params as Req));
      const idempotencyKey = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
      const res = await apiRequest<Res>("/price", { ...params, idempotencyKey }, { timeoutMs: 30000, maxAttempts: 3, signal });
      setWaking(false);
      saveHistory(params as Req, res);
      return res;
    };
  }, []);

  const cancelAll = () => {
    setWaking(false);
    timers.current.forEach(id=>clearTimeout(id));
    timers.current = [];
  };

  return { price, waking, bannerText, lastCached, cancelAll };
}
