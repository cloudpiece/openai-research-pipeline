import PostCard from "@/components/PostCard";
import { getAllPosts } from "@/lib/content";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Papers — Research Blog" };

export default function PapersPage() {
  const papers = getAllPosts("papers");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Papers</h1>
      <p className="text-gray-500 text-sm mb-8">
        {papers.length} paper{papers.length !== 1 ? "s" : ""}
      </p>
      {papers.length === 0 ? (
        <p className="text-gray-500">No papers yet.</p>
      ) : (
        papers.map((post) => <PostCard key={post.slug} post={post} />)
      )}
    </div>
  );
}
