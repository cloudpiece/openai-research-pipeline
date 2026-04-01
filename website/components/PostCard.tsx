import Link from "next/link";
import type { PostMeta } from "@/lib/content";

export default function PostCard({ post }: { post: PostMeta }) {
  const href = `/${post.type}/${post.slug}`;

  return (
    <article className="border-b border-gray-100 py-6 last:border-0">
      <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
        <time dateTime={post.date}>{post.date}</time>
        <span>·</span>
        <span>{post.readingTime}</span>
        {post.venue && (
          <>
            <span>·</span>
            <span className="italic">{post.venue}</span>
          </>
        )}
      </div>
      <h2 className="text-lg font-semibold leading-snug mb-1">
        <Link href={href} className="hover:underline">
          {post.title}
        </Link>
      </h2>
      <p className="text-sm text-gray-600 mb-2 line-clamp-2">{post.excerpt}</p>
      <div className="flex flex-wrap gap-1">
        {post.tags.map((tag) => (
          <span
            key={tag}
            className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>
    </article>
  );
}
