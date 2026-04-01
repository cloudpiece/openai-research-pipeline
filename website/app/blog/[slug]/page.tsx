import { getPostBySlug, getPostSlugs } from "@/lib/content";
import { compileMDX } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import rehypeSlug from "rehype-slug";
import type { Metadata } from "next";
import Link from "next/link";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return getPostSlugs("blog").map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug("blog", slug);
  return { title: `${post.title} — Research Blog` };
}

export default async function BlogPost({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug("blog", slug);
  const { content } = await compileMDX({
    source: post.content,
    options: {
      mdxOptions: {
        remarkPlugins: [remarkGfm],
        rehypePlugins: [rehypeHighlight, rehypeSlug],
      },
    },
  });

  return (
    <article>
      <div className="mb-8">
        <Link href="/blog" className="text-sm text-blue-600 hover:underline">
          ← Back to Blog
        </Link>
      </div>
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-3">{post.title}</h1>
        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500">
          <time dateTime={post.date}>{post.date}</time>
          <span>·</span>
          <span>{post.readingTime}</span>
        </div>
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </header>
      <div className="prose prose-gray max-w-none">{content}</div>
    </article>
  );
}
