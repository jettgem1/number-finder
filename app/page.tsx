import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to Number Finder
        </h1>
        <p className="text-xl text-center mb-12">
          Upload a PDF to find the largest numbers within it
        </p>

        <div className="flex justify-center">
          <Link
            href="/pdf-finder"
            className="group rounded-lg border border-transparent px-6 py-4 text-lg font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          >
            Try PDF Number Finder
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none ml-2">
              -&gt;
            </span>
          </Link>
        </div>
      </div>
    </main>
  )
}
