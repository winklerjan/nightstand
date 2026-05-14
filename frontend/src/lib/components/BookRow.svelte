<script lang="ts">
  import { selectedBookId } from "$lib/store/library";
  import type { Book } from "$lib/types";

  interface Props {
    book: Book;
    base: string;
  }

  let { book, base }: Props = $props();
  let coverFailed = $state(false);

  const year = $derived(book.pubdate ? book.pubdate.slice(0, 4) : "");
</script>

<button type="button" class="row" onclick={() => selectedBookId.set(book.id)}>
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
  <div class="title">
    <strong>{book.title}</strong>
    <span>{book.authors.join(", ")}</span>
  </div>
  <div class="year">{year}</div>
  <div class="tags">
    {#each book.tags.slice(0, 4) as tag}
      <span>{tag}</span>
    {/each}
  </div>
  <div class="formats">
    {#each book.formats as format}
      <span>{format}</span>
    {/each}
  </div>
</button>

<style>
  .row {
    width: 100%;
    display: grid;
    grid-template-columns: 48px minmax(180px, 1.5fr) 64px minmax(160px, 1fr) minmax(90px, 0.5fr);
    align-items: center;
    gap: 0.85rem;
    border: 0;
    border-bottom: 1px solid #2b3134;
    background: transparent;
    color: inherit;
    cursor: pointer;
    font: inherit;
    padding: 0.65rem 0.75rem;
    text-align: left;
  }

  .row:hover {
    background: #202528;
  }

  .cover {
    width: 48px;
    height: 64px;
    border-radius: 4px;
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

  .cover span {
    color: #aeb7b3;
    font-size: 0.65rem;
  }

  .title {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  strong,
  .title span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  strong {
    color: #f7f2e7;
    font-weight: 650;
  }

  .title span,
  .year {
    color: #aab2ae;
    font-size: 0.84rem;
  }

  .tags,
  .formats {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }

  .tags span,
  .formats span {
    border: 1px solid #3b4346;
    border-radius: 999px;
    color: #cbd3cf;
    font-size: 0.72rem;
    padding: 0.16rem 0.45rem;
  }

  .formats span {
    border-color: #4a5c53;
    color: #d8ecdc;
  }

  @media (max-width: 900px) {
    .row {
      grid-template-columns: 48px minmax(0, 1fr) 52px;
    }

    .tags,
    .formats {
      display: none;
    }
  }
</style>
