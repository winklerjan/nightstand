<script lang="ts">
  import BookCard from "$lib/components/BookCard.svelte";
  import { backendBase, filteredBooks } from "$lib/store/library";
</script>

<section class="grid" aria-label="Books grid">
  {#if !$backendBase}
    <p class="empty">Loading library...</p>
  {:else if $filteredBooks.length === 0}
    <p class="empty">No books match the current filters.</p>
  {:else}
    {#each $filteredBooks as book (book.id)}
      <BookCard {book} base={$backendBase} />
    {/each}
  {/if}
</section>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 0.85rem;
  }

  .empty {
    color: #aeb7b3;
    margin: 0;
  }
</style>
