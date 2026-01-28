// Same origin ('') when deployed with FastAPI; set NEXT_PUBLIC_API_URL=http://localhost:8000 when frontend runs on :3000
function getApiBase(): string {
  const env = process.env.NEXT_PUBLIC_API_URL ?? '';
  if (env) return env;
  if (typeof window !== 'undefined' && window.location?.port === '3000') return 'http://localhost:8000';
  return '';
}

/** Training focus options; values match backend TRAINING_FOCUS_MAP keys */
export const TRAINING_FOCUS_OPTIONS = [
  { value: 'seated', label: 'Seated (e.g. lotus, for pranayama & meditation)' },
  { value: 'forward_fold', label: 'Forward fold (stretch posterior chain, calm nerves)' },
  { value: 'backbend', label: 'Backbend (open chest, energize spine)' },
  { value: 'twist', label: 'Twist (compress abdomen, support detox)' },
  { value: 'side_bend', label: 'Side bend (lengthen lateral body)' },
  { value: 'balance', label: 'Balance (core & focus)' },
  { value: 'inversion', label: 'Inversion (circulation, ease fatigue)' },
] as const;

export type YogaFlowRequest = {
  last_period_date: string;
  cycle_length?: number;
  energy?: number;
  pain?: number;
  duration?: number;
  user_id?: string;
  /** Training focus, multi-select, e.g. ["forward_fold", "balance"] */
  training_focus?: string[];
};

export type YogaFlowResponse = {
  body_state: {
    cycle_phase: string;
    day_in_cycle: number;
    intensity: string;
    allowed_pose_types: string[];
    forbidden_pose_types: string[];
    energy_level: number;
    pain_level: number;
    duration_minutes: number;
    training_focus?: string[];
  };
  structure: {
    structure: Array<{ section: string; minutes: number; description?: string }>;
    total_minutes: number;
    rationale?: string;
  };
  sequence: {
    sequence: Array<{
      section: string;
      poses: Array<{ pose: string; duration?: string; reps?: number; notes?: string }>;
    }>;
    total_estimated_minutes: number;
  };
  cues: {
    cues: Array<{
      pose: string;
      section: string;
      alignment_cues: string[];
      breathing: string;
      modifications: string;
      encouragement: string;
    }>;
  };
  session_id?: string;
};

export async function generateYogaFlow(body: YogaFlowRequest): Promise<YogaFlowResponse> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/v1/yoga-flow`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to generate yoga flow');
  }
  return res.json();
}

export type ChatResponse = { reply: string };

export async function chatYoga(message: string): Promise<ChatResponse> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: message.trim() }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to get reply');
  }
  return res.json();
}

/** Stream chat: call onChunk(text) for each chunk; rejects on error. */
export async function chatYogaStream(
  message: string,
  onChunk: (chunk: string) => void
): Promise<void> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/v1/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: message.trim() }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to start stream');
  }
  const reader = res.body?.getReader();
  if (!reader) throw new Error('No response body');
  const dec = new TextDecoder();
  let buf = '';
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop() ?? '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const raw = line.slice(6).trim();
          if (raw === '[DONE]') continue;
          try {
            const o = JSON.parse(raw) as { chunk?: string; error?: string };
            if (o.error) throw new Error(o.error);
            if (typeof o.chunk === 'string') onChunk(o.chunk);
          } catch (e) {
            if (e instanceof SyntaxError) continue;
            throw e;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
