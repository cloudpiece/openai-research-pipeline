import PostCard from "@/components/PostCard";
import { getAllPosts } from "@/lib/content";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Blog — Research Blog" };

export default function BlogPage() {
  const posts = getAllPosts("blog");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Blog</h1>
      <p className="text-gray-500 text-sm mb-8">
        {posts.length} post{posts.length !== 1 ? "s" : ""}
      </p>
      {posts.length === 0 ? (
        <p className="text-gray-500">No posts yet.</p>
      ) : (
        posts.map((post) => <PostCard key={post.slug} post={post} />)
      )}
    </div>
  );
}
