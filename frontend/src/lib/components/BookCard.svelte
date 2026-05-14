<script lang="ts">
  import { selectedBookId } from "$lib/store/library";
  import type { Book } from "$lib/types";

  interface Props {
    book: Book;
    base: string;
  }

  let { book, base }: Props = $props();
  let coverFailed = $state(false);
</script>

<button type="button" class="card" onclick={() => selectedBookId.set(book.id)}>
  <div class="cover">
    {#if coverFailed}
      <span>Book</span>
    {:else}
      <img
        src={`${base}/library/books/${book.id}/cover`}
        alt=""
        loading="lazy"
        onerror={() => (coverFailed = true)}
      />
    {/if}
  </div>
  <strong>{book.title}</strong>
  <span>{book.authors.join(", ")}</span>
</button>

<style>
  .card {
    min-width: 0;
    border: 1px solid #2f3437;
    border-radius: 8px;
    background: #171a1c;
    color: inherit;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    font: inherit;
    padding: 0.75rem;
    text-align: left;
  }

  .card:hover {
    border-color: #51605d;
    background: #1d2224;
  }

  .cover {
    width: 100%;
    aspect-ratio: 2 / 3;
    border-radius: 6px;
    background: #30363a;
    display: grid;
    place-items: center;
    overflow: hidden;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover span,
  span {
    color: #aab2ae;
    font-size: 0.82rem;
  }

  strong,
  span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  strong {
    color: #f7f2e7;
    font-size: 0.92rem;
    font-weight: 650;
  }
</style>
