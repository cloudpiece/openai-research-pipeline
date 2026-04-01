import type { Metadata } from "next";

export const metadata: Metadata = { title: "About — Research Blog" };

export default function AboutPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">About</h1>
      <div className="prose prose-gray">
        <p>
          This is a research blog for sharing articles, ideas, and academic
          papers. Edit <code>app/about/page.tsx</code> to update this page.
        </p>
      </div>
    </div>
  );
}
