"""Main interactive CLI interface for AI Music Compositor."""

import sys
from music import compose_music
from component import play_midi


def format_composition_summary(comp_data: dict, target_seconds: float) -> None:
    bpm = comp_data.get("tempo_bpm", 120)
    meter = comp_data.get("time_signature", "4/4")
    mel_inst = comp_data.get("melody_instrument", "Piano")
    harm_inst = comp_data.get("harmony_instrument", "Strings")
    melody = comp_data.get("melody", [])
    harmony = comp_data.get("harmony", [])

    print(f"Tempo:          {bpm} BPM")
    print(f"Time Signature: {meter}")
    print(f"Instruments:    Melody: [{mel_inst}] | Harmony: [{harm_inst}]")
    print(f"Target Length:  {target_seconds:.1f}s ({(target_seconds / 60.0) * bpm:.1f} beats)")

    melody_str = " -> ".join([f"{n.get('pitch')}[{n.get('duration')}q]" for n in melody[:8]])
    if len(melody) > 8:
        melody_str += f" ... (+{len(melody) - 8} more)"
    print(f"Melody Motive:  {melody_str if melody_str else 'None'}")

    harmony_str = " | ".join([f"[{','.join(c.get('pitches', []))}]:{c.get('duration')}q" for c in harmony[:6]])
    if len(harmony) > 6:
        harmony_str += f" ... (+{len(harmony) - 6} more)"
    print(f"Chord Progress: {harmony_str if harmony_str else 'None'}")


def run_compositor():
    print("=" * 60)
    print("           AI MUSIC COMPOSITOR (Agent Interface)")
    print("=" * 60)
    print("Enter a musical description to compose and generate a MIDI file.")
    print("Type 'exit' or 'q' to quit.\n")

    while True:
        try:
            query = input("Describe the music you want to compose:\n> ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting AI Music Compositor. Goodbye!")
                break

            style = input("Enter musical style [Default: Romantic era]: ").strip()
            if not style:
                style = "Romantic era"

            print("\nComposing music with AI agent pipeline (Gemini + Groq Fallback)...")
            result = compose_music(musician_input=query, style=style)

            if "error" in result and result["error"]:
                print(f"\n[!] Pipeline Warning: {result['error']}")

            comp_data = result.get("composition_data", {})
            target_sec = result.get("target_seconds", 10.0)

            print("\n" + "-" * 50)
            print("COMPOSITION DETAILS:")
            print("-" * 50)
            if comp_data:
                format_composition_summary(comp_data, target_sec)
            else:
                print("No structured composition data returned.")

            midi_path = result.get("midi_file")
            print(f"MIDI File:      {midi_path}")
            print("-" * 50)

            if midi_path:
                play_choice = input("\nDo you want to play the generated music? (y/n) [default: y]: ").strip().lower()
                if play_choice in ("", "y", "yes"):
                    print("Playing MIDI audio...")
                    play_midi(midi_path)
                    print("Playback completed.")

            print("\n" + "=" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            sys.exit(0)
        except Exception as e:
            print(f"\nError during composition: {e}\n")


if __name__ == "__main__":
    run_compositor()