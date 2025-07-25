import Chat from "@/components/chat";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-items-center min-h-screen">
      <main className="flex flex-col items-center w-full">
        <Chat />
      </main>
    </div>
  );
}
