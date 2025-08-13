"use client";
import React from "react";

export function WakeBanner({ show, text, onCancel }:{ show:boolean; text:string; onCancel:()=>void }) {
  if (!show) return null;
  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 rounded-xl px-4 py-2 shadow-lg bg-neutral-900 text-white text-sm flex items-center gap-3 z-50">
      <span>{text}</span>
      <button onClick={onCancel} className="rounded-md px-2 py-1 bg-neutral-700 hover:bg-neutral-600">
        Cancel
      </button>
    </div>
  );
}
