export interface Paper {
  paper_id: number;
  title: string;
  author: string;
  year: number;
  url: string;
  abstract?: string;
}

export interface Project {
  id: number;
  name: string;
  date: string;
  outputs: Paper[];
}