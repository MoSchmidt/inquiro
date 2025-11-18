export interface Paper {
    title: string;
    author: string;
    year: number;
    url: string;
}

export interface Project {
    id: string;
    name: string;
    query: string;
    date: string;
    outputs: Paper[];
}