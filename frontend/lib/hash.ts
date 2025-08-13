export function stableHash(obj: unknown): string {
  // Simple JSON stringify with sorted keys
  const seen = new WeakSet();
  const s = JSON.stringify(obj, function (k, v) {
    if (v && typeof v === "object") {
      if (seen.has(v)) return;
      seen.add(v);
      return Object.keys(v).sort().reduce((o: any, key) => (o[key] = (v as any)[key], o), {});
    }
    return v;
  });
  // FNV-1a
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ("0000000" + (h >>> 0).toString(16)).slice(-8);
}
