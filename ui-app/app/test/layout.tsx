export default function TestLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen">
      <div className="flex flex-col w-full min-h-screen">
        <header className="py-4 px-6 border-b">
          <h1 className="text-xl font-bold">API Test Console</h1>
        </header>
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  );
} 