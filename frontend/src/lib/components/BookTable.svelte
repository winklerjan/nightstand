<script lang="ts">
  import BookRow from "$lib/components/BookRow.svelte";
  import { backendBase, filteredBooks } from "$lib/store/library";
</script>

<section class="table" aria-label="Books table">
  <div class="header">
    <span></span>
    <span>Title</span>
    <span>Year</span>
    <span>Tags</span>
    <span>Formats</span>
  </div>
  {#if !$backendBase}
    <p class="empty">Loading library...</p>
  {:else if $filteredBooks.length === 0}
    <p class="empty">No books match the current filters.</p>
  {:else}
    {#each $filteredBooks as book (book.id)}
      <BookRow {book} base={$backendBase} />
    {/each}
  {/if}
</section>

<style>
  .table {
    border: 1px solid #2f3437;
    border-radius: 8px;
    overflow: hidden;
    background: #171a1c;
  }

  .header {
    display: grid;
    grid-template-columns: 48px minmax(180px, 1.5fr) 64px minmax(160px, 1fr) minmax(90px, 0.5fr);
    gap: 0.85rem;
    border-bottom: 1px solid #2f3437;
    color: #8d9893;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.55rem 0.75rem;
    text-transform: uppercase;
  }

  .empty {
    color: #aeb7b3;
    margin: 0;
    padding: 1rem;
  }

  @media (max-width: 900px) {
    .header {
      grid-template-columns: 48px minmax(0, 1fr) 52px;
    }

    .header span:nth-child(4),
    .header span:nth-child(5) {
      display: none;
    }
  }
</style>
