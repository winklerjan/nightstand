<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { onMount } from "svelte";
  import BookDetail from "$lib/components/BookDetail.svelte";
  import BookGrid from "$lib/components/BookGrid.svelte";
  import BookTable from "$lib/components/BookTable.svelte";
  import FilterSidebar from "$lib/components/FilterSidebar.svelte";
  import {
    backendBase,
    books,
    error,
    filteredBooks,
    loading,
    selectedBookId,
    tags,
    viewMode,
  } from "$lib/store/library";
  import type { Book } from "$lib/types";

  const loadLibrary = async (): Promise<void> => {
    loading.set(true);
    error.set(null);
    selectedBookId.set(null);

    try {
      const port: number = await invoke("get_backend_port");
      if (!port) throw new Error("Backend port not available.");
      const base = `http://localhost:${port}`;
      backendBase.set(base);

      const [booksResponse, tagsResponse] = await Promise.all([
        fetch(`${base}/library/books`),
        fetch(`${base}/library/tags`),
      ]);

      if (booksResponse.status === 423 || tagsResponse.status === 423) {
        throw new Error("Calibre is open - close it and refresh.");
      }
      if (!booksResponse.ok) {
        throw new Error(`Books request failed with HTTP ${booksResponse.status}`);
      }
      if (!tagsResponse.ok) {
        throw new Error(`Tags request failed with HTTP ${tagsResponse.status}`);
      }

      books.set((await booksResponse.json()) as Book[]);
      tags.set((await tagsResponse.json()) as string[]);
    } catch (loadError: unknown) {
      error.set(String(loadError));
      books.set([]);
      tags.set([]);
    } finally {
      loading.set(false);
    }
  };

  onMount(() => {
    void loadLibrary();
  });
</script>

<main>
  <FilterSidebar />

  <section class="content" aria-label="Library browser">
    <header>
      <div>
        <h1>Nightstand</h1>
        <p>{$filteredBooks.length} books</p>
      </div>
      <div class="actions" aria-label="View mode">
        <button
          type="button"
          class:active={$viewMode === "table"}
          onclick={() => viewMode.set("table")}
        >
          Table
        </button>
        <button
          type="button"
          class:active={$viewMode === "grid"}
          onclick={() => viewMode.set("grid")}
        >
          Grid
        </button>
      </div>
    </header>

    {#if $error}
      <div class="banner" role="alert">
        <span>{$error}</span>
        <button type="button" onclick={loadLibrary}>Retry</button>
      </div>
    {/if}

    {#if $loading}
      <p class="status">Loading library...</p>
    {:else if $viewMode === "table"}
      <BookTable />
    {:else}
      <BookGrid />
    {/if}
  </section>

  <BookDetail />
</main>

<style>
  :global(*, *::before, *::after) {
    box-sizing: border-box;
  }

  :global(html, body) {
    margin: 0;
    min-height: 100vh;
    background: #101214;
    color: #e7ece9;
    font-family:
      Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.5;
  }

  :global(button) {
    letter-spacing: 0;
  }

  main {
    min-height: 100vh;
    display: flex;
    background: #101214;
  }

  .content {
    min-width: 0;
    flex: 1;
    padding: 1rem;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  h1 {
    color: #f7f2e7;
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0;
  }

  p {
    margin: 0;
  }

  header p,
  .status {
    color: #aeb7b3;
  }

  .actions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    border: 1px solid #3a4145;
    border-radius: 6px;
    overflow: hidden;
  }

  .actions button,
  .banner button {
    border: 0;
    background: #202528;
    color: #d8dedb;
    cursor: pointer;
    font: inherit;
    padding: 0.55rem 0.8rem;
  }

  .actions button.active {
    background: #314139;
    color: #ffffff;
  }

  .banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    border: 1px solid #7b3d32;
    border-radius: 8px;
    background: #281917;
    color: #ffd8cf;
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
  }

  .banner button {
    border: 1px solid #8a554c;
    border-radius: 6px;
    background: #3a211d;
    color: #ffe4dd;
  }

  @media (max-width: 760px) {
    main {
      flex-direction: column;
    }

    header {
      align-items: flex-start;
      flex-direction: column;
    }
  }
</style>
