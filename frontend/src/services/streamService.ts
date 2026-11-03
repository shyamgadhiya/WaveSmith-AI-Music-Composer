import { StreamEventPayload, StreamTransport } from "@/types/music";

interface StreamOptions {
  prompt: string;
  style: string;
  transport?: StreamTransport;
  onEvent: (event: StreamEventPayload) => void;
  onError: (error: string) => void;
  onFinish?: () => void;
  signal?: AbortSignal;
}

/**
 * Connects to the FastAPI SSE endpoint using either Native EventSource or fetch ReadableStream.
 */
export async function streamComposition({
  prompt,
  style,
  transport = "eventsource",
  onEvent,
  onError,
  onFinish,
  signal,
}: StreamOptions): Promise<() => void> {
  const backendBase = process.env.NEXT_PUBLIC_BACKEND_URL || "";

  // -------------------------------------------------------------
  // Mode 1: Native EventSource (GET)
  // -------------------------------------------------------------
  if (transport === "eventsource") {
    const params = new URLSearchParams({ prompt, style });
    const url = `${backendBase}/api/v1/compose/stream?${params.toString()}`;
    const es = new EventSource(url);

    const stageEvents = [
      "extracting_key",
      "generating_notes",
      "compiling_midi",
      "rendering_wav",
      "completed",
      "error",
    ];

    stageEvents.forEach((stage) => {
      es.addEventListener(stage, (evt: MessageEvent) => {
        try {
          const payload = JSON.parse(evt.data) as StreamEventPayload;
          onEvent(payload);

          if (stage === "completed" || stage === "error") {
            es.close();
            onFinish?.();
          }
        } catch (err) {
          console.error("Failed to parse SSE payload", err);
        }
      });
    });

    es.onerror = (e) => {
      console.warn("EventSource encountered connection interruption", e);
      // Only fire error if not explicitly aborted
      if (!signal?.aborted) {
        onError("Stream connection lost or failed to reach AI server.");
      }
      es.close();
      onFinish?.();
    };

    const cleanup = () => {
      es.close();
    };

    if (signal) {
      signal.addEventListener("abort", cleanup);
    }

    return cleanup;
  }

  // -------------------------------------------------------------
  // Mode 2: fetch with ReadableStream (POST)
  // -------------------------------------------------------------
  const url = `${backendBase}/api/v1/compose/stream`;
  let active = true;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ prompt, style }),
      signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    (async () => {
      try {
        while (active) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";

          for (const block of parts) {
            if (!block.trim()) continue;

            const lines = block.split("\n");
            let eventType = "message";
            let dataStr = "";

            for (const line of lines) {
              if (line.startsWith("event:")) {
                eventType = line.slice(6).trim();
              } else if (line.startsWith("data:")) {
                dataStr = line.slice(5).trim();
              }
            }

            if (dataStr) {
              try {
                const payload = JSON.parse(dataStr) as StreamEventPayload;
                onEvent(payload);
                if (payload.stage === "completed" || payload.stage === "error") {
                  active = false;
                  break;
                }
              } catch (err) {
                console.error("Failed to parse chunk", err);
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          onError(err.message || "Failed during streaming chunk reception.");
        }
      } finally {
        onFinish?.();
      }
    })();
  } catch (err: any) {
    if (err.name !== "AbortError") {
      onError(err.message || "Unable to initiate stream connection.");
      onFinish?.();
    }
  }

  return () => {
    active = false;
  };
}

