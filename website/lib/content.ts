import fs from "fs";
import path from "path";
import matter from "gray-matter";
import readingTime from "reading-time";

const contentDir = path.join(process.cwd(), "content");

export type ContentType = "blog" | "papers";

export interface PostMeta {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  tags: string[];
  readingTime: string;
  type: ContentType;
  authors?: string[];
  venue?: string; // for papers: journal/conference
  doi?: string;
}

export interface Post extends PostMeta {
  content: string;
}

export function getPostSlugs(type: ContentType): string[] {
  const dir = path.join(contentDir, type);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md") || f.endsWith(".mdx"))
    .map((f) => f.replace(/\.mdx?$/, ""));
}

export function getPostBySlug(type: ContentType, slug: string): Post {
  const dir = path.join(contentDir, type);
  const mdxPath = path.join(dir, `${slug}.mdx`);
  const mdPath = path.join(dir, `${slug}.md`);
  const filePath = fs.existsSync(mdxPath) ? mdxPath : mdPath;
  const raw = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(raw);
  const rt = readingTime(content);

  return {
    slug,
    type,
    title: data.title ?? "Untitled",
    date: data.date ?? "",
    excerpt: data.excerpt ?? "",
    tags: data.tags ?? [],
    readingTime: rt.text,
    authors: data.authors ?? [],
    venue: data.venue ?? "",
    doi: data.doi ?? "",
    content,
  };
}

export function getAllPosts(type: ContentType): PostMeta[] {
  return getPostSlugs(type)
    .map((slug) => {
      const post = getPostBySlug(type, slug);
      const { content: _, ...meta } = post;
      return meta;
    })
    .sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getAllTags(type: ContentType): string[] {
  const posts = getAllPosts(type);
  const tags = new Set(posts.flatMap((p) => p.tags));
  return Array.from(tags).sort();
}
