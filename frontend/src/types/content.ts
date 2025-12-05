import { Component } from 'vue';

export interface Paper {
  paper_id: number;
  title: string;
  author: string;
  year: number;
  abstract?: string;
}

export interface Project {
  id: number;
  name: string;
  date: string;
  outputs: Paper[];
}

export interface PaperMenuOption {
  label: string;
  value: string;
  icon?: Component;
}