<script lang="ts">
  import { backendBase, selectedBookId } from "$lib/store/library";
  import type { BookDetail } from "$lib/types";

  const cache = new Map<number, BookDetail>();
  let coverFailed = $state(false);
  let bookPromise = $state<Promise<BookDetail> | null>(null);

  const close = (): void => {
    selectedBookId.set(null);
  };

  $effect(() => {
    const id = $selectedBookId;
    const base = $backendBase;
    coverFailed = false;

    if (id === null || base === null) {
      bookPromise = null;
      return;
    }

    const cached = cache.get(id);
    if (cached) {
      bookPromise = Promise.resolve(cached);
      return;
    }

    bookPromise = fetch(`${base}/library/books/${id}`).then(async (response) => {
      if (response.status === 423) throw new Error("Calibre is open - close it and retry.");
      if (!response.ok) throw new Error(`Book detail failed with HTTP ${response.status}`);
      const book = (await response.json()) as BookDetail;
      cache.set(id, book);
      return book;
    });
  });
</script>

{#if $selectedBookId !== null}
  <aside class="panel" aria-label="Book detail">
    <button type="button" class="close" aria-label="Close detail" onclick={close}>x</button>

    {#if bookPromise !== null}
      {#await bookPromise}
        <p class="status">Loading book...</p>
      {:then book}
        <div class="cover">
          {#if coverFailed}
            <span>Book</span>
          {:else}
            <img
              src={`${$backendBase}/library/books/${book.id}/cover`}
              alt=""
              loading="lazy"
              onerror={() => (coverFailed = true)}
            />
          {/if}
        </div>

        <div class="identity">
          <h2>{book.title}</h2>
          <p>{book.authors.join(", ")}</p>
        </div>

        <dl>
          {#if book.series}
            <div>
              <dt>Series</dt>
              <dd>{book.series}{book.series_index ? ` #${book.series_index}` : ""}</dd>
            </div>
          {/if}
          {#if book.pubdate}
            <div>
              <dt>Year</dt>
              <dd>{book.pubdate.slice(0, 4)}</dd>
            </div>
          {/if}
          <div>
            <dt>Languages</dt>
            <dd>{book.languages.join(", ") || "Unknown"}</dd>
          </div>
          <div>
            <dt>Formats</dt>
            <dd>{book.formats.join(", ") || "None"}</dd>
          </div>
        </dl>

        <section>
          <h3>Tags</h3>
          <div class="chips">
            {#each book.tags as tag}
              <span>{tag}</span>
            {/each}
          </div>
        </section>

        {#if book.extras.subgenres.length > 0 || book.extras.themes.length > 0}
          <section>
            <h3>Extras</h3>
            <div class="chips">
              {#each book.extras.subgenres as subgenre}
                <span>{subgenre}</span>
              {/each}
              {#each book.extras.themes as theme}
                <span>{theme}</span>
              {/each}
            </div>
          </section>
        {/if}

        {#if book.comments}
          <section>
            <h3>Comments</h3>
            <div class="comments">{book.comments}</div>
          </section>
        {/if}

        <button type="button" class="edit" disabled>Coming in M2</button>
      {:catch err}
        <p class="status error">{err}</p>
      {/await}
    {/if}
  </aside>
{/if}

<style>
  .panel {
    position: fixed;
    inset: 0 0 0 auto;
    width: min(420px, 100vw);
    z-index: 20;
    background: #171a1c;
    border-left: 1px solid #30373a;
    box-shadow: -20px 0 45px rgb(0 0 0 / 0.35);
    color: #f7f2e7;
    overflow-y: auto;
    padding: 1rem;
  }

  .close {
    width: 2rem;
    height: 2rem;
    border: 1px solid #3a4145;
    border-radius: 6px;
    background: #202528;
    color: #f7f2e7;
    cursor: pointer;
    float: right;
    font: inherit;
  }

  .cover {
    width: 180px;
    aspect-ratio: 2 / 3;
    border-radius: 8px;
    background: #30363a;
    display: grid;
    margin: 2.4rem auto 1rem;
    overflow: hidden;
    place-items: center;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover span,
  .status,
  dd,
  .identity p {
    color: #aeb7b3;
  }

  .identity {
    text-align: center;
  }

  h2 {
    font-size: 1.35rem;
    line-height: 1.2;
    margin: 0;
  }

  .identity p {
    margin: 0.45rem 0 1.25rem;
  }

  dl {
    display: grid;
    gap: 0.65rem;
    margin: 0 0 1.25rem;
  }

  dl div {
    display: grid;
    grid-template-columns: 90px minmax(0, 1fr);
    gap: 0.75rem;
  }

  dt,
  h3 {
    color: #cfd6d3;
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
  }

  dd {
    margin: 0;
    min-width: 0;
  }

  section {
    margin-top: 1.25rem;
  }

  h3 {
    margin: 0 0 0.55rem;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }

  .chips span {
    border: 1px solid #3b4346;
    border-radius: 999px;
    color: #cbd3cf;
    font-size: 0.76rem;
    padding: 0.18rem 0.5rem;
  }

  .comments {
    color: #d8dedb;
    font-size: 0.9rem;
    line-height: 1.55;
  }

  .status {
    margin-top: 4rem;
  }

  .error {
    color: #f6b5a8;
  }

  .edit {
    width: 100%;
    border: 1px solid #3a4145;
    border-radius: 6px;
    background: #222729;
    color: #88918d;
    font: inherit;
    margin-top: 1.5rem;
    padding: 0.7rem;
  }
</style>
