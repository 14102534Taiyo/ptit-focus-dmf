"use client";

/**
 * Viewer-defined groups ("กลุ่มของฉัน"): any set of DMF field names under a name the viewer picks.
 * Personal by design — stored only in this browser, shareable as a link. Never changes the official mapping.
 */
export interface CustomGroup {
  id: string;
  name: string;
  members: string[];
}

const STORAGE_KEY = "ptit.fieldTracker.customGroups.v1";
const HASH_KEY = "groups";

export function loadCustomGroups(): CustomGroup[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter(isValidGroup) : [];
  } catch {
    return [];
  }
}

export function saveCustomGroups(groups: CustomGroup[]) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(groups));
  } catch {
    // Private mode / blocked storage: groups still work for this visit
  }
}

function isValidGroup(value: unknown): value is CustomGroup {
  const g = value as CustomGroup;
  return (
    !!g &&
    typeof g.name === "string" &&
    g.name.trim().length > 0 &&
    Array.isArray(g.members) &&
    g.members.every((m) => typeof m === "string")
  );
}

export function newGroupId() {
  return `g${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

function toBase64Url(text: string) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(text: string) {
  const base64 = text.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(base64 + "===".slice((base64.length + 3) % 4));
  return new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0)));
}

/** Link that recreates these groups in someone else's browser. */
export function shareLink(groups: CustomGroup[]) {
  const payload = groups.map((g) => ({ n: g.name, m: g.members }));
  const url = new URL(window.location.href);
  url.hash = `${HASH_KEY}=${toBase64Url(JSON.stringify(payload))}`;
  return url.toString();
}

/** Groups carried in the current URL hash (from a shared link), or [] when there are none. */
export function groupsFromHash(): CustomGroup[] {
  try {
    const match = window.location.hash.match(new RegExp(`${HASH_KEY}=([^&]+)`));
    if (!match) return [];
    const payload = JSON.parse(fromBase64Url(match[1]));
    if (!Array.isArray(payload)) return [];
    return payload
      .map((p: { n?: unknown; m?: unknown }) => ({ id: newGroupId(), name: String(p.n || ""), members: Array.isArray(p.m) ? p.m.map(String) : [] }))
      .filter(isValidGroup)
      .slice(0, 20);
  } catch {
    return [];
  }
}

export function clearHash() {
  try {
    window.history.replaceState(null, "", window.location.pathname + window.location.search);
  } catch {
    // ignore
  }
}

export const sameGroup = (a: CustomGroup, b: CustomGroup) =>
  a.name === b.name && a.members.length === b.members.length && a.members.every((m) => b.members.includes(m));
