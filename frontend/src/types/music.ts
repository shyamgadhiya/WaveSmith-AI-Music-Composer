export interface NoteSummary {
  pitch: string;
  duration: number;
}

export interface ChordSummary {
  pitches: string[];
  duration: number;
}

export interface CompositionDetails {
  tempo_bpm: number;
  time_signature: string;
  melody_instrument: string;
  harmony_instrument: string;
  melody: NoteSummary[];
  harmony: ChordSummary[];
}

export interface ComposeResponse {
  session_id: string;
  target_seconds: number;
  composition: CompositionDetails;
  midi_download_url: string;
  audio_stream_url: string | null;
}

export type PipelineStage =
  | "idle"
  | "extracting_key"
  | "generating_notes"
  | "compiling_midi"
  | "rendering_wav"
  | "completed"
  | "error";

export interface StreamEventPayload {
  stage: PipelineStage;
  message: string;
  session_id?: string;
  target_seconds?: number;
  composition?: CompositionDetails;
  midi_download_url?: string;
  audio_stream_url?: string | null;
}

export type StreamTransport = "eventsource" | "fetch";

