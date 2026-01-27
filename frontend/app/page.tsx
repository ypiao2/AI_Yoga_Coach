'use client';

import { useState } from 'react';
import Link from 'next/link';
import { generateYogaFlow, type YogaFlowResponse, TRAINING_FOCUS_OPTIONS } from '@/lib/api';

const ENERGY_LABELS: Record<number, string> = {
  1: 'Very low',
  2: 'Low',
  3: 'Moderate',
  4: 'Good',
  5: 'High',
};

const PAIN_LABELS: Record<number, string> = {
  1: 'None',
  2: 'Mild',
  3: 'Moderate',
  4: 'Noticeable',
  5: 'High',
};

export default function Home() {
  const [lastPeriodDate, setLastPeriodDate] = useState('');
  const [cycleLength, setCycleLength] = useState(28);
  const [energy, setEnergy] = useState(3);
  const [pain, setPain] = useState(1);
  const [duration, setDuration] = useState(20);
  const [trainingFocus, setTrainingFocus] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flow, setFlow] = useState<YogaFlowResponse | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);
  const [feedbackNotes, setFeedbackNotes] = useState('');
  const [feedbackSent, setFeedbackSent] = useState(false);

  const toggleTrainingFocus = (value: string) => {
    setTrainingFocus((prev) =>
      prev.includes(value) ? prev.filter((x) => x !== value) : [...prev, value]
    );
  };

  const today = new Date().toISOString().slice(0, 10);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setFlow(null);
    setLoading(true);
    try {
      const result = await generateYogaFlow({
        last_period_date: lastPeriodDate,
        cycle_length: cycleLength,
        energy,
        pain,
        duration,
        training_focus: trainingFocus.length > 0 ? trainingFocus : undefined,
      });
      setFlow(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = () => {
    setFeedbackSent(true);
    // In production, call backend to save feedback
  };

  return (
    <div className="min-h-screen bg-[#fff5f7] text-[#1f2937]">
      <header
        className="relative min-h-[200px] border-b border-[#fce7f3] px-6 py-8 flex flex-col justify-center items-center bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: 'url(/yoga_postures_1.avif)' }}
      >
        <div className="absolute inset-0 bg-white/70" aria-hidden="true" />
        <div className="relative z-10 text-center">
          <h1 className="text-3xl font-semibold text-[#ec4899]">AI Yoga Coach</h1>
          <p className="text-base text-[#6b7280] mt-1">
            Body-Aware · Rule-Guided · RAG-Enhanced
          </p>
          <Link
            href="/chat"
            className="inline-block mt-4 rounded-full bg-[#ec4899]/20 text-[#be185d] font-medium px-4 py-2 text-sm hover:bg-[#ec4899]/30 transition"
          >
            Ask about yoga →
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8">
        <section className="bg-white rounded-xl border border-[#fce7f3] shadow-sm p-6 mb-8">
          <h2 className="text-lg font-medium mb-4 text-[#1f2937]">Today&apos;s state</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-[#6b7280] mb-1">
                Last period date
              </label>
              <input
                type="date"
                value={lastPeriodDate}
                onChange={(e) => setLastPeriodDate(e.target.value)}
                max={today}
                required
                className="w-full rounded-lg border border-[#fce7f3] bg-white px-3 py-2 text-[#1f2937] focus:outline-none focus:ring-2 focus:ring-[#ec4899]/50 focus:border-[#ec4899]"
              />
            </div>
            <div>
              <label className="block text-sm text-[#6b7280] mb-1">
                Cycle length (days)
              </label>
              <input
                type="number"
                min={21}
                max={45}
                value={cycleLength}
                onChange={(e) => setCycleLength(Number(e.target.value))}
                className="w-full rounded-lg border border-[#fce7f3] bg-white px-3 py-2 text-[#1f2937] focus:outline-none focus:ring-2 focus:ring-[#ec4899]/50 focus:border-[#ec4899]"
              />
            </div>
            <div>
              <label className="block text-sm text-[#6b7280] mb-1">
                Energy (1–5): {ENERGY_LABELS[energy]}
              </label>
              <input
                type="range"
                min={1}
                max={5}
                value={energy}
                onChange={(e) => setEnergy(Number(e.target.value))}
                className="w-full accent-[#ec4899]"
              />
            </div>
            <div>
              <label className="block text-sm text-[#6b7280] mb-1">
                Pain / discomfort (1–5): {PAIN_LABELS[pain]}
              </label>
              <input
                type="range"
                min={1}
                max={5}
                value={pain}
                onChange={(e) => setPain(Number(e.target.value))}
                className="w-full accent-[#ec4899]"
              />
            </div>
            <div>
              <label className="block text-sm text-[#6b7280] mb-1">
                Session duration (minutes)
              </label>
              <input
                type="number"
                min={5}
                max={90}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full rounded-lg border border-[#fce7f3] bg-white px-3 py-2 text-[#1f2937] focus:outline-none focus:ring-2 focus:ring-[#ec4899]/50 focus:border-[#ec4899]"
              />
            </div>
            <div>
              <label className="block text-sm text-[#6b7280] mb-2">
                Training focus (optional, multi-select; leave empty for body-state & cycle-based suggestions)
              </label>
              <div className="flex flex-wrap gap-2">
                {TRAINING_FOCUS_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => toggleTrainingFocus(opt.value)}
                    className={`rounded-full px-3 py-1.5 text-sm transition ${
                      trainingFocus.includes(opt.value)
                        ? 'bg-[#ec4899] text-white shadow-sm'
                        : 'bg-white border border-[#fce7f3] text-[#6b7280] hover:border-[#ec4899] hover:text-[#ec4899]'
                    }`}
                    title={opt.label}
                  >
                    {opt.value.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
              <p className="mt-1 text-xs text-[#9ca3af]">
                Seated · Forward fold · Backbend · Twist · Side bend · Balance · Inversion
              </p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-[#ec4899] text-white font-medium py-3 px-4 hover:bg-[#db2777] disabled:opacity-60 disabled:cursor-not-allowed transition shadow-sm"
            >
              {loading ? 'Generating flow…' : 'Generate yoga flow'}
            </button>
          </form>
        </section>

        {error && (
          <div className="mb-6 rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-red-600">
            {error}
          </div>
        )}

        {flow && (
          <div className="space-y-6">
            <section className="bg-white rounded-xl border border-[#fce7f3] shadow-sm p-6">
              <h2 className="text-lg font-medium mb-3 text-[#1f2937]">Body state</h2>
              <div className="flex flex-wrap gap-2 text-sm">
                <span className="rounded-full bg-[#ec4899]/15 text-[#ec4899] px-3 py-1 font-medium">
                  {flow.body_state.cycle_phase}
                </span>
                <span className="rounded-full bg-[#10b981]/15 text-[#10b981] px-3 py-1 font-medium">
                  {flow.body_state.intensity} intensity
                </span>
                <span className="text-[#6b7280]">
                  {flow.body_state.duration_minutes} min
                </span>
                {flow.body_state.training_focus && flow.body_state.training_focus.length > 0 && (
                  <span className="rounded-full bg-[#fce7f3] text-[#be185d] px-3 py-1 font-medium">
                    Training focus: {flow.body_state.training_focus.map((t) => t.replace(/_/g, ' ')).join(' · ')}
                  </span>
                )}
              </div>
            </section>

            <section className="bg-white rounded-xl border border-[#fce7f3] shadow-sm p-6">
              <h2 className="text-lg font-medium mb-3 text-[#1f2937]">Structure</h2>
              <ul className="space-y-2">
                {flow.structure.structure?.map((s, i) => (
                  <li key={i} className="flex justify-between text-sm">
                    <span className="capitalize text-[#1f2937]">{s.section.replace(/_/g, ' ')}</span>
                    <span className="text-[#6b7280]">{s.minutes} min</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="bg-white rounded-xl border border-[#fce7f3] shadow-sm p-6">
              <h2 className="text-lg font-medium mb-3 text-[#1f2937]">Yoga flow</h2>
              <div className="space-y-4">
                {flow.sequence.sequence?.map((sec, i) => (
                  <div key={i}>
                    <h3 className="text-sm font-medium text-[#6b7280] capitalize mb-2">
                      {sec.section.replace(/_/g, ' ')}
                    </h3>
                    <ul className="space-y-2 pl-4 border-l-2 border-[#fce7f3]">
                      {sec.poses?.map((p, j) => (
                        <li key={j} className="text-sm">
                          <span className="text-[#ec4899] font-medium">
                            {p.pose.replace(/_/g, ' ')}
                          </span>
                          {p.duration && ` · ${p.duration}`}
                          {p.reps && ` · ${p.reps} reps`}
                          {p.notes && (
                            <span className="text-[#6b7280] block mt-0.5">
                              {p.notes}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-white rounded-xl border border-[#fce7f3] shadow-sm p-6">
              <h2 className="text-lg font-medium mb-3 text-[#1f2937]">Cues & guidance</h2>
              <div className="space-y-4">
                {flow.cues.cues?.map((c, i) => (
                  <div
                    key={i}
                    className="rounded-lg bg-[#fff5f7] border border-[#fce7f3] p-4"
                  >
                    <h4 className="font-medium text-[#ec4899] capitalize mb-2">
                      {c.pose.replace(/_/g, ' ')}
                    </h4>
                    {c.alignment_cues?.length > 0 && (
                      <ul className="text-sm text-[#6b7280] list-disc list-inside space-y-1 mb-2">
                        {c.alignment_cues.slice(0, 3).map((a, j) => (
                          <li key={j}>{a}</li>
                        ))}
                      </ul>
                    )}
                    <p className="text-sm text-[#1f2937]">{c.breathing}</p>
                    {c.encouragement && (
                      <p className="text-sm text-[#10b981] mt-2 italic">
                        {c.encouragement}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-white rounded-xl border border-[#fce7f3] shadow-sm p-6">
              <h2 className="text-lg font-medium mb-3 text-[#1f2937]">Feedback</h2>
              {feedbackSent ? (
                <p className="text-sm text-[#10b981]">
                  Thanks for your feedback.
                </p>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-[#6b7280] mb-1">
                      How was this flow?
                    </label>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((r) => (
                        <button
                          key={r}
                          type="button"
                          onClick={() => setFeedbackRating(r)}
                          className={`rounded-lg px-3 py-1 text-sm transition ${
                            feedbackRating === r
                              ? 'bg-[#ec4899] text-white shadow-sm'
                              : 'bg-white border border-[#fce7f3] text-[#6b7280] hover:border-[#ec4899] hover:text-[#ec4899]'
                          }`}
                        >
                          {r}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-[#6b7280] mb-1">
                      Notes (optional)
                    </label>
                    <textarea
                      value={feedbackNotes}
                      onChange={(e) => setFeedbackNotes(e.target.value)}
                      rows={3}
                      className="w-full rounded-lg border border-[#fce7f3] bg-white px-3 py-2 text-[#1f2937] focus:outline-none focus:ring-2 focus:ring-[#ec4899]/50 focus:border-[#ec4899] resize-none"
                      placeholder="Anything to adjust for next time?"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleFeedback}
                    className="rounded-lg bg-[#10b981]/20 text-[#10b981] font-medium py-2 px-4 hover:bg-[#10b981]/30 transition"
                  >
                    Send feedback
                  </button>
                </div>
              )}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
