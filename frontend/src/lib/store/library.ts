import { derived, writable } from "svelte/store";
import type { Book, Filters, ViewMode } from "$lib/types";

const defaultFilters: Filters = {
  search: "",
  tags: [],
  languages: [],
  tagMode: "OR",
};

const initialViewMode = (): ViewMode => {
  if (typeof localStorage === "undefined") return "table";
  return localStorage.getItem("nightstand:viewMode") === "grid" ? "grid" : "table";
};

export const books = writable<Book[]>([]);
export const tags = writable<string[]>([]);
export const filters = writable<Filters>({ ...defaultFilters });
export const viewMode = writable<ViewMode>(initialViewMode());
export const selectedBookId = writable<number | null>(null);
export const loading = writable<boolean>(true);
export const error = writable<string | null>(null);
export const backendBase = writable<string | null>(null);

if (typeof localStorage !== "undefined") {
  viewMode.subscribe((value) => {
    localStorage.setItem("nightstand:viewMode", value);
  });
}

export const languages = derived(books, ($books) => {
  const values = new Set<string>();
  for (const book of $books) {
    for (const language of book.languages) values.add(language);
  }
  return [...values].sort((a, b) => a.localeCompare(b));
});

export const filteredBooks = derived([books, filters], ([$books, $filters]) => {
  const query = $filters.search.trim().toLocaleLowerCase();
  return $books.filter((book) => {
    const haystack = `${book.title} ${book.authors.join(" ")}`.toLocaleLowerCase();
    const matchesSearch = query === "" || haystack.includes(query);
    const matchesTags =
      $filters.tags.length === 0 ||
      ($filters.tagMode === "AND"
        ? $filters.tags.every((tag) => book.tags.includes(tag))
        : $filters.tags.some((tag) => book.tags.includes(tag)));
    const matchesLanguages =
      $filters.languages.length === 0 ||
      $filters.languages.some((language) => book.languages.includes(language));
    return matchesSearch && matchesTags && matchesLanguages;
  });
});

export const resetFilters = (): void => {
  filters.set({ ...defaultFilters });
};
