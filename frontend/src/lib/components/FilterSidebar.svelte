<script lang="ts">
  import { filters, languages, resetFilters, tags } from "$lib/store/library";
  import type { Filters } from "$lib/types";

  const toggleValue = (key: "tags" | "languages", value: string): void => {
    filters.update((current) => {
      const selected = current[key];
      return {
        ...current,
        [key]: selected.includes(value)
          ? selected.filter((item) => item !== value)
          : [...selected, value],
      };
    });
  };

  const updateSearch = (search: string): void => {
    filters.update((current) => ({ ...current, search }));
  };

  const updateTagMode = (tagMode: Filters["tagMode"]): void => {
    filters.update((current) => ({ ...current, tagMode }));
  };
</script>

<aside class="sidebar" aria-label="Library filters">
  <div class="section">
    <label for="library-search">Search</label>
    <input
      id="library-search"
      type="search"
      value={$filters.search}
      oninput={(event) => updateSearch(event.currentTarget.value)}
    />
  </div>

  <div class="section">
    <div class="section-heading">
      <span>Tags</span>
      <div class="mode" aria-label="Tag filter mode">
        <button
          type="button"
          class:active={$filters.tagMode === "OR"}
          onclick={() => updateTagMode("OR")}
        >
          OR
        </button>
        <button
          type="button"
          class:active={$filters.tagMode === "AND"}
          onclick={() => updateTagMode("AND")}
        >
          AND
        </button>
      </div>
    </div>
    <div class="chips">
      {#each $tags as tag}
        <button
          type="button"
          class:active={$filters.tags.includes(tag)}
          onclick={() => toggleValue("tags", tag)}
        >
          {tag}
        </button>
      {/each}
    </div>
  </div>

  <div class="section">
    <div class="section-heading">
      <span>Languages</span>
    </div>
    <div class="chips">
      {#each $languages as language}
        <button
          type="button"
          class:active={$filters.languages.includes(language)}
          onclick={() => toggleValue("languages", language)}
        >
          {language}
        </button>
      {/each}
    </div>
  </div>

  <button type="button" class="clear" onclick={resetFilters}>Clear filters</button>
</aside>

<style>
  .sidebar {
    width: 280px;
    min-width: 240px;
    border-right: 1px solid #2f3437;
    background: #171a1c;
    padding: 1rem;
    overflow: auto;
  }

  .section {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    margin-bottom: 1.25rem;
  }

  label,
  .section-heading {
    color: #cfd6d3;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
  }

  .section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
  }

  input {
    width: 100%;
    border: 1px solid #3a4145;
    border-radius: 6px;
    background: #101214;
    color: #f5f2e8;
    font: inherit;
    padding: 0.65rem 0.75rem;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
  }

  button {
    border: 1px solid #3a4145;
    border-radius: 999px;
    background: #202528;
    color: #d8dedb;
    cursor: pointer;
    font: inherit;
    font-size: 0.78rem;
    padding: 0.35rem 0.6rem;
  }

  button:hover {
    border-color: #5a6669;
  }

  button.active {
    border-color: #a8c3b1;
    background: #314139;
    color: #ffffff;
  }

  .mode {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    border: 1px solid #3a4145;
    border-radius: 6px;
    overflow: hidden;
  }

  .mode button {
    border: 0;
    border-radius: 0;
    padding: 0.28rem 0.5rem;
  }

  .clear {
    width: 100%;
    border-radius: 6px;
    padding: 0.6rem 0.75rem;
  }

  @media (max-width: 760px) {
    .sidebar {
      width: 100%;
      max-height: 42vh;
      border-right: 0;
      border-bottom: 1px solid #2f3437;
    }
  }
</style>
