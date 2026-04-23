"use client";

import { AvatarStage } from "@/components/AvatarStage";
import { useEffect, useMemo, useRef, useState } from "react";

type Emotion = "neutral" | "happy" | "sad" | "angry" | "surprised";
type Role = "system" | "user" | "assistant";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
};

type ChatResponse = {
  reply: string;
  emotion?: Emotion;
};

const emotions: Emotion[] = ["neutral", "happy", "sad", "angry", "surprised"];
const samplePrompts = [
  "Flirty but kind, like a cozy shrine maiden with a wicked sense of humor.",
  "Soft, helpful, playful. Low drama, high warmth.",
  "Tsundere energy, but never actually mean.",
];

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

function guessEmotion(text: string): Emotion {
  const value = text.toLowerCase();
  if (/(sorry|sad|lonely|bad|upset|hurt)/.test(value)) return "sad";
  if (/(angry|mad|annoyed|grr|hate)/.test(value)) return "angry";
  if (/(wow|surprise|shocked|wow!|wow\?|!|\?)/.test(value)) return "surprised";
  if (/(love|cute|yay|happy|nice|sweet|good)/.test(value)) return "happy";
  return "neutral";
}

async function readAudioBlob(blob: Blob) {
  const form = new FormData();
  form.append("file", blob, "recording.webm");
  return form;
}

export function WaifuRoom() {
  const [backendUrl, setBackendUrl] = useState("http://127.0.0.1:8000");
  const [apiBaseUrl, setApiBaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("gpt-4o-mini");
  const [voice, setVoice] = useState("kore");
  const [systemPrompt, setSystemPrompt] = useState(
    "You are a charming 3D waifu in a browser chatroom. Keep replies vivid, affectionate, and game-like. Speak in short paragraphs."
  );
  const [personality, setPersonality] = useState(samplePrompts[0]);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: uid(),
      role: "assistant",
      content:
        "Hai. Upload a VRM, wire the backend, and I’ll start talking like I belong in the room.",
    },
  ]);
  const [emotion, setEmotion] = useState<Emotion>("happy");
  const [mouthOpen, setMouthOpen] = useState(0);
  const [pose, setPose] = useState(0);
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [recording, setRecording] = useState(false);
  const [ttsOn, setTtsOn] = useState(true);
  const [sttHint, setSttHint] = useState("Mic idle");
  const [connection, setConnection] = useState("Local backend not checked yet");

  const listRef = useRef<HTMLDivElement | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const meterRef = useRef<number | null>(null);

  const transcript = useMemo(
    () => messages.filter((message) => message.role !== "system"),
    [messages]
  );

  useEffect(() => {
    const timer = window.setTimeout(() => {
      listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
    }, 40);
    return () => window.clearTimeout(timer);
  }, [messages]);

  useEffect(() => {
    void fetch(`${backendUrl}/health`)
      .then(async (response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = (await response.json()) as { status?: string };
        setConnection(`Backend ${payload.status ?? "ok"}`);
      })
      .catch(() => setConnection("Backend offline, frontend still usable"));
  }, [backendUrl]);

  useEffect(() => {
    return () => {
      if (meterRef.current !== null) window.cancelAnimationFrame(meterRef.current);
    };
  }, []);

  const startTtsMeter = async (audio: HTMLAudioElement) => {
    const context = new AudioContext();
    const source = context.createMediaElementSource(audio);
    const analyser = context.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);
    analyser.connect(context.destination);

    const data = new Uint8Array(analyser.frequencyBinCount);
    const pump = () => {
      analyser.getByteFrequencyData(data);
      const total = data.reduce((sum, value) => sum + value, 0);
      const level = total / data.length / 255;
      setMouthOpen(Math.min(1, Math.max(0.05, level * 1.9)));
      meterRef.current = window.requestAnimationFrame(pump);
    };

    await context.resume();
    pump();
    audio.onended = () => {
      if (meterRef.current !== null) {
        window.cancelAnimationFrame(meterRef.current);
        meterRef.current = null;
      }
      setMouthOpen(0);
      context.close().catch(() => null);
    };
  };

  const playTts = async (text: string) => {
    if (!ttsOn || !text.trim()) return;

    try {
      const response = await fetch(`${backendUrl}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          voice,
          model,
          backend: { apiBaseUrl, apiKey },
        }),
      });

      if (!response.ok) return;
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.autoplay = true;
      audio.volume = 1;
      audio.onended = () => URL.revokeObjectURL(url);
      await audio.play();
      await startTtsMeter(audio);
    } catch (error) {
      console.error(error);
    }
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || busy) return;

    const nextMessages: ChatMessage[] = [
      ...messages,
      { id: uid(), role: "user", content: text },
    ];
    setMessages(nextMessages);
    setInput("");
    setBusy(true);

    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model,
          api_base_url: apiBaseUrl,
          api_key: apiKey,
          system_prompt: systemPrompt,
          personality,
          messages: nextMessages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status}`);
      }

      const data = (await response.json()) as ChatResponse;
      const reply = data.reply || "…";
      const replyEmotion = data.emotion ?? guessEmotion(reply);

      setEmotion(replyEmotion);
      setMessages((current) => [
        ...current,
        { id: uid(), role: "assistant", content: reply },
      ]);
      await playTts(reply);
    } catch (error) {
      console.error(error);
      setMessages((current) => [
        ...current,
        {
          id: uid(),
          role: "assistant",
          content:
            "Backend missed a step. Check the OpenAI-compatible endpoint, then I’ll talk again.",
        },
      ]);
      setEmotion("sad");
    } finally {
      setBusy(false);
    }
  };

  const stopRecording = async () => {
    const recorder = recorderRef.current;
    if (!recorder) return;
    recorder.stop();
  };

  const toggleMic = async () => {
    if (recording) {
      stopRecording();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      recorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        setRecording(false);
        setSttHint("Sending audio to Whisper...");
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());
        try {
          const form = await readAudioBlob(blob);
          const response = await fetch(`${backendUrl}/stt`, {
            method: "POST",
            body: form,
          });
          if (!response.ok) throw new Error(`STT failed: ${response.status}`);
          const data = (await response.json()) as { text?: string };
          setInput(data.text ?? "");
          setSttHint("Transcript ready");
        } catch (error) {
          console.error(error);
          setSttHint("Whisper request failed");
        }
      };
      recorder.start();
      setRecording(true);
      setSttHint("Recording...");
    } catch (error) {
      console.error(error);
      setSttHint("Mic unavailable");
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[1600px] flex-col gap-6 px-4 py-4 lg:px-6">
      <header className="glass flex flex-wrap items-center justify-between gap-4 rounded-[28px] px-5 py-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-[var(--muted)]">Waifu Room</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">
            Fullstack waifu chatroom, VRM stage, Whisper STT, Kokoro TTS
          </h1>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">{connection}</span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">{busy ? "Thinking" : "Idle"}</span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">{sttHint}</span>
        </div>
      </header>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="grid gap-6">
          <AvatarStage
            modelFile={modelFile}
            emotion={emotion}
            mouthOpen={mouthOpen}
            pose={pose}
          />

          <div className="glass rounded-[28px] p-5">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-[var(--muted)]">Character control</p>
                <h2 className="mt-1 text-xl font-semibold">Upload, prompt, mood, voice</h2>
              </div>
              <div className="flex gap-2">
                {emotions.map((value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setEmotion(value)}
                    className={`rounded-full border px-3 py-2 text-xs transition ${
                      emotion === value
                        ? "border-[var(--accent-2)] bg-white/15 text-white"
                        : "border-white/10 bg-white/5 text-[var(--muted)]"
                    }`}
                  >
                    {value}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <label className="grid gap-2 text-sm text-[var(--muted)]">
                VRM model
                <input
                  type="file"
                  accept=".vrm"
                  onChange={(event) => setModelFile(event.target.files?.[0] ?? null)}
                  className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white file:mr-4 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-black"
                />
              </label>

              <label className="grid gap-2 text-sm text-[var(--muted)]">
                Pose mood
                <input
                  type="range"
                  min={-1}
                  max={1}
                  step={0.01}
                  value={pose}
                  onChange={(event) => setPose(Number(event.target.value))}
                />
              </label>

              <label className="grid gap-2 text-sm text-[var(--muted)] lg:col-span-2">
                System prompt
                <textarea
                  value={systemPrompt}
                  onChange={(event) => setSystemPrompt(event.target.value)}
                  rows={4}
                  className="rounded-3xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white placeholder:text-white/30"
                />
              </label>

              <label className="grid gap-2 text-sm text-[var(--muted)] lg:col-span-2">
                Personality
                <textarea
                  value={personality}
                  onChange={(event) => setPersonality(event.target.value)}
                  rows={3}
                  className="rounded-3xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white placeholder:text-white/30"
                />
              </label>
            </div>
          </div>
        </div>

        <aside className="grid gap-6">
          <div className="glass rounded-[28px] p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-[var(--muted)]">Backend</p>
                <h2 className="mt-1 text-xl font-semibold">OpenAI-compatible chat, Whisper, Kokoro</h2>
              </div>
              <button
                type="button"
                onClick={() => setTtsOn((current) => !current)}
                className={`rounded-full border px-3 py-2 text-xs ${
                  ttsOn ? "border-[var(--good)] bg-[rgba(109,240,177,0.15)]" : "border-white/10 bg-white/5"
                }`}
              >
                TTS {ttsOn ? "on" : "off"}
              </button>
            </div>

            <div className="mt-5 grid gap-4">
              <label className="grid gap-2 text-sm text-[var(--muted)]">
                Backend URL
                <input
                  value={backendUrl}
                  onChange={(event) => setBackendUrl(event.target.value)}
                  className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white"
                />
              </label>
              <label className="grid gap-2 text-sm text-[var(--muted)]">
                OpenAI endpoint
                <input
                  value={apiBaseUrl}
                  onChange={(event) => setApiBaseUrl(event.target.value)}
                  placeholder="https://api.openai.com/v1"
                  className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white"
                />
              </label>
              <label className="grid gap-2 text-sm text-[var(--muted)]">
                API key
                <input
                  value={apiKey}
                  onChange={(event) => setApiKey(event.target.value)}
                  type="password"
                  placeholder="sk-..."
                  className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white"
                />
              </label>
              <label className="grid gap-2 text-sm text-[var(--muted)]">
                Model
                <input
                  value={model}
                  onChange={(event) => setModel(event.target.value)}
                  placeholder="gpt-4o-mini"
                  className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white"
                />
              </label>
              <label className="grid gap-2 text-sm text-[var(--muted)]">
                Voice
                <select
                  value={voice}
                  onChange={(event) => setVoice(event.target.value)}
                  className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white"
                >
                  <option value="kore">kore</option>
                  <option value="alloy">alloy</option>
                  <option value="shimmer">shimmer</option>
                  <option value="nova">nova</option>
                </select>
              </label>
            </div>
          </div>

          <div className="glass flex min-h-0 flex-1 flex-col rounded-[28px] p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-[var(--muted)]">Chat room</p>
                <h2 className="mt-1 text-xl font-semibold">Talk to the avatar</h2>
              </div>
              <button
                type="button"
                onClick={toggleMic}
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs"
              >
                {recording ? "Stop mic" : "Whisper mic"}
              </button>
            </div>

            <div ref={listRef} className="scrollbar mt-4 flex min-h-[420px] flex-1 flex-col gap-3 overflow-auto pr-1">
              {transcript.map((message) => (
                <article
                  key={message.id}
                  className={`max-w-[92%] rounded-[24px] border px-4 py-3 text-sm leading-6 ${
                    message.role === "user"
                      ? "ml-auto border-[rgba(120,247,255,0.22)] bg-[rgba(120,247,255,0.08)]"
                      : "border-white/10 bg-white/6"
                  }`}
                >
                  <p className="mb-1 text-[10px] uppercase tracking-[0.35em] text-[var(--muted)]">
                    {message.role}
                  </p>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </article>
              ))}
            </div>

            <div className="mt-4 grid gap-3">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Say something to your waifu..."
                rows={4}
                className="rounded-[24px] border border-white/10 bg-black/35 px-4 py-3 text-sm text-white placeholder:text-white/30"
              />
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={sendMessage}
                  disabled={busy}
                  className="rounded-full bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-black disabled:opacity-50"
                >
                  Send
                </button>
                <button
                  type="button"
                  onClick={() => setInput("What are you thinking right now?")}
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm"
                >
                  Prompt me
                </button>
                <button
                  type="button"
                  onClick={() => setInput("")}
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="glass rounded-[28px] p-5 xl:col-span-2">
          <p className="text-xs uppercase tracking-[0.35em] text-[var(--muted)]">System design</p>
          <h2 className="mt-1 text-xl font-semibold">What this project is built to do</h2>
          <ul className="mt-4 grid gap-3 text-sm leading-6 text-[var(--muted)] sm:grid-cols-2">
            <li className="rounded-2xl border border-white/10 bg-white/5 p-4 text-white/90">Upload VRM waifu or character models from the browser.</li>
            <li className="rounded-2xl border border-white/10 bg-white/5 p-4 text-white/90">Drive chat via any OpenAI-compatible LLM endpoint.</li>
            <li className="rounded-2xl border border-white/10 bg-white/5 p-4 text-white/90">Record mic audio, transcribe it with Whisper, and send it to chat.</li>
            <li className="rounded-2xl border border-white/10 bg-white/5 p-4 text-white/90">Speak replies with Kokoro TTS and animate mouth movement.</li>
          </ul>
        </div>

        <div className="glass rounded-[28px] p-5">
          <p className="text-xs uppercase tracking-[0.35em] text-[var(--muted)]">Defaults</p>
          <div className="mt-4 grid gap-3 text-sm text-[var(--muted)]">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Frontend, Next.js + Tailwind + three.js</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Backend, Python venv + FastAPI</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Chat, OpenAI-compatible completions</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Voice, Whisper + Kokoro</div>
          </div>
        </div>
      </section>
    </main>
  );
}
