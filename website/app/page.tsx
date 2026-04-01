import Link from "next/link";
import PostCard from "@/components/PostCard";
import { getAllPosts } from "@/lib/content";

export default function Home() {
  const recentBlog = getAllPosts("blog").slice(0, 3);
  const recentPapers = getAllPosts("papers").slice(0, 3);

  return (
    <div className="space-y-14">
      <section>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Research Blog</h1>
        <p className="text-gray-600">
          Writing on research, ideas, and experiments.
        </p>
      </section>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Posts</h2>
          <Link href="/blog" className="text-sm text-blue-600 hover:underline">
            All posts →
          </Link>
        </div>
        {recentBlog.length === 0 ? (
          <p className="text-sm text-gray-500">No posts yet.</p>
        ) : (
          recentBlog.map((post) => <PostCard key={post.slug} post={post} />)
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Papers</h2>
          <Link href="/papers" className="text-sm text-blue-600 hover:underline">
            All papers →
          </Link>
        </div>
        {recentPapers.length === 0 ? (
          <p className="text-sm text-gray-500">No papers yet.</p>
        ) : (
          recentPapers.map((post) => <PostCard key={post.slug} post={post} />)
        )}
      </section>
    </div>
  );
}
