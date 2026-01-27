'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import { chatYoga } from '@/lib/api';

// ReactMarkdown component for rendering assistant markdown (type cast for React 18 / strict JSX)
const Markdown = ReactMarkdown as React.ComponentType<{ children?: string }>;

type Message = { role: 'user' | 'assistant'; content: string };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setError(null);
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);

    try {
      const { reply } = await chatYoga(text);
      setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setMessages((prev) => prev.slice(0, -1));
      setInput(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fff5f7] text-[#1f2937] flex flex-col">
      <header className="border-b border-[#fce7f3] bg-white/80 backdrop-blur px-4 py-4 flex items-center gap-4">
        <Link
          href="/"
          className="text-[#6b7280] hover:text-[#ec4899] transition text-sm"
        >
          ← Home
        </Link>
        <h1 className="text-xl font-semibold text-[#ec4899]">Ask about yoga</h1>
      </header>

      <main className="flex-1 max-w-2xl w-full mx-auto px-4 py-6 flex flex-col">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col justify-center text-center text-[#6b7280] py-8">
            <p className="text-lg font-medium text-[#1f2937] mb-2">
              Yoga Q&A
            </p>
            <p className="text-sm">
              Ask about poses, alignment, breathing, philosophy, or safety.
              Answers use your yoga knowledge base when relevant.
            </p>
          </div>
        )}

        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                  m.role === 'user'
                    ? 'bg-[#ec4899] text-white'
                    : 'bg-white border border-[#fce7f3] text-[#1f2937]'
                }`}
              >
                {m.role === 'assistant' ? (
                  <div className="chat-markdown [&_h2]:text-base [&_h2]:font-semibold [&_h2]:mt-3 [&_h2]:mb-2 [&_h2]:text-[#1f2937] [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:mt-2 [&_h3]:mb-1 [&_p]:my-2 [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:my-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:my-0.5 [&_strong]:font-semibold [&_strong]:text-[#1f2937] [&_blockquote]:border-l-4 [&_blockquote]:border-[#ec4899] [&_blockquote]:bg-[#fdf2f8]/50 [&_blockquote]:pl-3 [&_blockquote]:py-1 [&_blockquote]:my-2 [&_blockquote]:rounded-r [&_code]:bg-[#f3f4f6] [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-sm">
                    <Markdown>{m.content}</Markdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{m.content}</p>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-[#fce7f3] rounded-2xl px-4 py-3 text-[#6b7280] text-sm">
                …
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="mb-3 rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-red-600 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about yoga…"
            disabled={loading}
            className="flex-1 rounded-xl border border-[#fce7f3] bg-white px-4 py-3 text-[#1f2937] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-[#ec4899]/50 focus:border-[#ec4899] disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-xl bg-[#ec4899] text-white font-medium px-5 py-3 hover:bg-[#db2777] disabled:opacity-60 disabled:cursor-not-allowed transition"
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
