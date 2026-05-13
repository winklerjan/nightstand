<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { onMount } from "svelte";

  let health: unknown = null;
  let probe: unknown = null;
  let fetchError: string | null = null;

  onMount(async () => {
    try {
      const port: number = await invoke("get_backend_port");
      if (!port) throw new Error("Backend port not available (sidecar failed to start?)");
      const base = `http://localhost:${port}`;
      const [h, p] = await Promise.all([
        fetch(`${base}/health`).then((r) => r.json()),
        fetch(`${base}/calibre/probe`).then((r) => r.json()),
      ]);
      health = h;
      probe = p;
    } catch (e) {
      fetchError = String(e);
    }
  });
</script>

<main>
  <h1>Nightstand</h1>

  {#if fetchError}
    <div class="card error">
      <h2>Error</h2>
      <pre>{fetchError}</pre>
    </div>
  {:else}
    <div class="card">
      <h2>Sidecar</h2>
      <pre>{health ? JSON.stringify(health, null, 2) : "loading…"}</pre>
    </div>
    <div class="card">
      <h2>Calibre</h2>
      <pre>{probe ? JSON.stringify(probe, null, 2) : "loading…"}</pre>
    </div>
  {/if}
</main>

<style>
  :global(*, *::before, *::after) {
    box-sizing: border-box;
  }
  :global(html, body) {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    background: #1a1a1a;
    color: #e0e0e0;
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
  }
  main {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  h1 {
    margin: 0 0 0.25rem;
    font-size: 1.4rem;
    font-weight: 600;
    color: #fff;
  }
  .card {
    background: #262626;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
  }
  .card.error {
    border-color: #7f1d1d;
    background: #1c0a0a;
  }
  h2 {
    margin: 0 0 0.75rem;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #666;
  }
  pre {
    margin: 0;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace;
    font-size: 0.875rem;
    white-space: pre-wrap;
    word-break: break-all;
  }
</style>
