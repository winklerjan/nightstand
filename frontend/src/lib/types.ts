export interface Book {
  id: number;
  title: string;
  authors: string[];
  tags: string[];
  series: string | null;
  series_index: number | null;
  languages: string[];
  pubdate: string | null;
  formats: string[];
}

export interface BookDetail extends Book {
  comments: string | null;
  extras: {
    subgenres: string[];
    themes: string[];
  };
}

export interface Filters {
  search: string;
  tags: string[];
  languages: string[];
  tagMode: "AND" | "OR";
}

export type ViewMode = "table" | "grid";
