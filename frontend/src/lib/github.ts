"use client";

/**
 * Minimal GitHub REST client used by the web mapping editor. The static site has no server, so an admin
 * saves by committing straight to the repo with their own fine-grained token (kept only in their browser).
 */
export const REPO = { owner: "14102534Taiyo", name: "ptit-focus-dmf", branch: "main" };
const API = `https://api.github.com/repos/${REPO.owner}/${REPO.name}`;
const TOKEN_KEY = "ptit.github.token.v1";

export function loadToken(): string {
  try {
    return window.localStorage.getItem(TOKEN_KEY) || "";
  } catch {
    return "";
  }
}

export function storeToken(token: string | null) {
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // storage blocked — token lives only for this visit
  }
}

async function gh<T>(token: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path.startsWith("http") ? path : `${API}${path}`, {
    ...init,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
    },
  });
  if (!response.ok) {
    let message = `${response.status}`;
    try {
      message += ` ${(await response.json()).message || ""}`;
    } catch {
      // ignore
    }
    throw new Error(message.trim());
  }
  return (await response.json()) as T;
}

/** Who the token belongs to and whether it can write to the repo. */
export async function checkAccess(token: string) {
  const [user, repo] = await Promise.all([
    gh<{ login: string }>(token, "https://api.github.com/user"),
    gh<{ permissions?: { push?: boolean } }>(token, ""),
  ]);
  return { login: user.login, canWrite: !!repo.permissions?.push };
}

function decodeBase64Utf8(b64: string) {
  const binary = atob(b64.replace(/\n/g, ""));
  return new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0)));
}

function bytesToBase64(bytes: Uint8Array) {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode.apply(null, Array.from(bytes.subarray(i, i + 0x8000)));
  }
  return btoa(binary);
}

/** Current file text + blob sha on the branch (sha is used to detect concurrent edits). */
export async function readFile(token: string, path: string) {
  const file = await gh<{ content: string; sha: string }>(token, `/contents/${encodeURIComponent(path)}?ref=${REPO.branch}`);
  return { text: decodeBase64Utf8(file.content), sha: file.sha };
}

export interface FileChange {
  path: string;
  /** UTF-8 text, or raw bytes for binary files such as .xlsx */
  content: string | Uint8Array;
}

/** Commit several files at once on top of the branch head (one commit → one ETL run). */
export async function commitFiles(token: string, message: string, files: FileChange[]) {
  for (let attempt = 0; attempt < 2; attempt++) {
    const ref = await gh<{ object: { sha: string } }>(token, `/git/ref/heads/${REPO.branch}`);
    const head = await gh<{ tree: { sha: string } }>(token, `/git/commits/${ref.object.sha}`);
    const blobs = await Promise.all(
      files.map((f) =>
        gh<{ sha: string }>(token, "/git/blobs", {
          method: "POST",
          body: JSON.stringify(
            typeof f.content === "string"
              ? { content: f.content, encoding: "utf-8" }
              : { content: bytesToBase64(f.content), encoding: "base64" },
          ),
        }),
      ),
    );
    const tree = await gh<{ sha: string }>(token, "/git/trees", {
      method: "POST",
      body: JSON.stringify({
        base_tree: head.tree.sha,
        tree: files.map((f, i) => ({ path: f.path, mode: "100644", type: "blob", sha: blobs[i].sha })),
      }),
    });
    const commit = await gh<{ sha: string; html_url: string }>(token, "/git/commits", {
      method: "POST",
      body: JSON.stringify({ message, tree: tree.sha, parents: [ref.object.sha] }),
    });
    try {
      await gh(token, `/git/refs/heads/${REPO.branch}`, { method: "PATCH", body: JSON.stringify({ sha: commit.sha }) });
      return commit;
    } catch (error) {
      // The daily ETL may have pushed in between — rebuild on the new head once
      if (attempt === 1) throw error;
    }
  }
  throw new Error("commit failed");
}

export const ACTIONS_URL = `https://github.com/${REPO.owner}/${REPO.name}/actions`;
export const NEW_TOKEN_URL =
  "https://github.com/settings/personal-access-tokens/new";
