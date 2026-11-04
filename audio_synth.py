"""Production Audio Synthesizer: Renders MIDI to studio-grade WAV using SoundFont samples."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import numpy as np

SOUNDFONT_PATH = os.getenv("SOUNDFONT_PATH", "soundfonts/default.sf2")


def get_soundfont_path() -> Optional[Path]:
    """Finds the best available SoundFont file across environment, local, and system paths."""
    candidates = [
        os.getenv("SOUNDFONT_PATH"),
        "soundfonts/default.sf2",
        "soundfonts/TimGM6mb.sf2",
        "/usr/share/sounds/sf2/TimGM6mb.sf2",
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/share/sounds/sf2/default.sf2",
        "/usr/share/soundfonts/default.sf2",
    ]
    for p in candidates:
        if p:
            candidate_path = Path(p)
            if candidate_path.exists() and candidate_path.is_file():
                return candidate_path

    # Automatic fallback to pretty_midi's bundled General MIDI soundfont
    try:
        import pretty_midi
        pm_sf2 = Path(pretty_midi.__file__).parent / "TimGM6mb.sf2"
        if pm_sf2.exists():
            return pm_sf2
    except Exception:
        pass
    return None


def render_midi_to_wav(midi_path: str, output_wav_path: str) -> bool:
    """
    Renders MIDI to 44.1kHz studio-grade WAV audio.
    Priority 1: Headless FluidSynth CLI binary (Official Linux production engine, isolated subprocess).
    Priority 2: Embedded TinySoundFont DSP engine (Local development fallback).
    Priority 3: Harmonic timbre DSP synthesizer fallback.
    """
    soundfont = get_soundfont_path()
    if soundfont:
        print(f"[AudioSynth] Using SoundFont: {soundfont}")
    else:
        print("[AudioSynth] Notice: No SoundFont file found. Using DSP timbre fallback.")

    # =========================================================================
    # Priority 1: System FluidSynth CLI binary (Linux Production Standard)
    # =========================================================================
    if shutil.which("fluidsynth") and soundfont and soundfont.exists():
        try:
            cmd = [
                "fluidsynth",
                "-n",
                "-i",
                "-r", "44100",
                "-F", str(output_wav_path),
                str(soundfont),
                str(midi_path),
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
            if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 1000:
                print(f"[AudioSynth] Successfully rendered audio via FluidSynth CLI.")
                return True
            else:
                print(f"[Warning] FluidSynth CLI did not produce audio: {res.stderr}")
        except Exception as e:
            print(f"[Warning] FluidSynth CLI render error: {e}")

    # =========================================================================
    # Priority 2: Embedded TinySoundFont (Local Development Fallback)
    # =========================================================================
    if soundfont and soundfont.exists():
        try:
            import tinysoundfont
            import soundfile as sf

            synth = tinysoundfont.Synth()
            synth.sfload(str(soundfont))
            seq = tinysoundfont.Sequencer(synth)
            seq.midi_load(str(midi_path))

            chunk_size = 4096
            chunks = []
            max_chunks = 2000  # Safety guard (~180 seconds max)
            count = 0

            while not seq.is_empty() and count < max_chunks:
                chunk = synth.generate(chunk_size)
                chunks.append(np.frombuffer(chunk, dtype=np.float32).reshape(-1, 2))
                count += 1

            # 0.5s acoustic tail for natural reverb and chord decay
            for _ in range(6):
                tail_chunk = synth.generate(chunk_size)
                chunks.append(np.frombuffer(tail_chunk, dtype=np.float32).reshape(-1, 2))

            if chunks:
                audio = np.concatenate(chunks, axis=0)

                # Soft peak normalization to prevent distortion
                peak = float(np.max(np.abs(audio)))
                if peak > 0.001:
                    audio = (audio / peak) * 0.94

                sf.write(output_wav_path, audio, 44100)

                if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 1000:
                    print(f"[AudioSynth] Successfully rendered audio via TinySoundFont.")
                    return True

        except Exception as e:
            print(f"[Warning] SoundFont engine render error: {e}")

    # =========================================================================
    # Priority 3: Fallback Multi-Instrument Timbre DSP
    # =========================================================================
    try:
        import pretty_midi
        import soundfile as sf

        pm = pretty_midi.PrettyMIDI(str(midi_path))
        fs = 44100
        total_time = pm.get_end_time()
        total_samples = int((total_time + 0.5) * fs)
        audio_buffer = np.zeros(total_samples, dtype=np.float32)

        for instrument in pm.instruments:
            if instrument.is_drum:
                continue

            prog = int(instrument.program)

            for note in instrument.notes:
                start_sample = int(note.start * fs)
                dur = float(note.end - note.start)
                if dur <= 0:
                    continue

                sig = _synthesize_instrument_timbre(
                    program=prog,
                    pitch=int(note.pitch),
                    duration=dur,
                    velocity=int(note.velocity),
                    fs=fs
                )

                end_sample = start_sample + len(sig)
                if end_sample > total_samples:
                    sig = sig[:total_samples - start_sample]
                    end_sample = total_samples

                if len(sig) > 0:
                    audio_buffer[start_sample:end_sample] += sig

        peak = float(np.max(np.abs(audio_buffer)))
        if peak > 0.001:
            audio_buffer = (audio_buffer / peak) * 0.92

        sf.write(output_wav_path, audio_buffer, fs)
        return True

    except Exception as e:
        print(f"[Error] Fallback audio synthesis failed: {e}")
        return False


def _synthesize_instrument_timbre(program: int, pitch: int, duration: float, velocity: int, fs: int = 44100) -> np.ndarray:
    """Synthesizes an acoustic waveform with characteristics of the given General MIDI program."""
    n_samples = int(duration * fs)
    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)

    t = np.linspace(0, duration, n_samples, endpoint=False)
    freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
    vol = min(1.0, max(0.1, (velocity / 127.0)))

    env = np.ones(n_samples, dtype=np.float32)
    attack_samples = min(int(0.04 * fs), n_samples // 4)
    release_samples = min(int(0.05 * fs), n_samples // 4)

    # 1. PIPE & FLUTES (GM 72-79)
    if 72 <= program <= 79:
        vib = 0.012 * np.sin(2.0 * np.pi * 5.5 * t)
        phase = 2.0 * np.pi * freq * (t + vib * (t > 0.08))
        wave = (
            1.00 * np.sin(phase) +
            0.24 * np.sin(2.0 * phase) +
            0.08 * np.sin(3.0 * phase) +
            0.03 * np.random.randn(n_samples)
        )
        if attack_samples > 0:
            env[:attack_samples] = np.sin(np.linspace(0, np.pi / 2, attack_samples))
        if release_samples > 0:
            env[-release_samples:] = np.cos(np.linspace(0, np.pi / 2, release_samples))

    # 2. REEDS & SAXOPHONES (GM 64-71)
    elif 64 <= program <= 71:
        vib = 0.014 * np.sin(2.0 * np.pi * 5.2 * t)
        phase = 2.0 * np.pi * freq * (t + vib * (t > 0.06))
        wave = (
            1.00 * np.sin(phase) +
            0.60 * np.sin(2.0 * phase) +
            0.75 * np.sin(3.0 * phase) +
            0.40 * np.sin(4.0 * phase) +
            0.30 * np.sin(5.0 * phase)
        )
        sax_attack = min(int(0.025 * fs), n_samples // 4)
        if sax_attack > 0:
            env[:sax_attack] = np.linspace(0, 1, sax_attack)
        if release_samples > 0:
            env[-release_samples:] = np.linspace(1, 0, release_samples)

    # 3. SOLO STRINGS & ENSEMBLE (GM 40-55)
    elif 40 <= program <= 55 or program == 110:
        vib = 0.015 * np.sin(2.0 * np.pi * 6.0 * t)
        phase = 2.0 * np.pi * freq * (t + vib * (t > 0.1))
        wave = (
            1.00 * np.sin(phase) +
            0.50 * np.sin(2.0 * phase) +
            0.33 * np.sin(3.0 * phase) +
            0.22 * np.sin(4.0 * phase) +
            0.14 * np.sin(5.0 * phase)
        )
        if attack_samples > 0:
            env[:attack_samples] = np.linspace(0, 1, attack_samples)
        if release_samples > 0:
            env[-release_samples:] = np.linspace(1, 0, release_samples)

    # 4. ETHNIC & PLUCKED (GM 104-111: Sitar, Banjo, Shamisen, Koto, Kalimba, Bagpipe, Shanai)
    elif 104 <= program <= 111:
        phase = 2.0 * np.pi * freq * t
        wave = (
            1.00 * np.sin(phase) * np.exp(-t * 2.0) +
            0.70 * np.sin(2.0 * phase) * np.exp(-t * 3.5) +
            0.55 * np.sin(3.0 * phase) * np.exp(-t * 5.0) +
            0.40 * np.sin(4.0 * phase) * np.exp(-t * 7.0) +
            0.25 * np.sin(5.0 * phase) * np.exp(-t * 9.0)
        )
        pluck_attack = min(int(0.004 * fs), n_samples)
        if pluck_attack > 0:
            env[:pluck_attack] = np.linspace(0, 1, pluck_attack)

    # 5. GUITARS (GM 24-31)
    elif 24 <= program <= 31:
        phase = 2.0 * np.pi * freq * t
        wave = (
            1.00 * np.sin(phase) * np.exp(-t * 2.0) +
            0.60 * np.sin(2.0 * phase) * np.exp(-t * 3.8) +
            0.30 * np.sin(3.0 * phase) * np.exp(-t * 6.0)
        )
        pluck_attack = min(int(0.005 * fs), n_samples)
        if pluck_attack > 0:
            env[:pluck_attack] = np.linspace(0, 1, pluck_attack)

    # 6. BASS (GM 32-39)
    elif 32 <= program <= 39:
        phase = 2.0 * np.pi * freq * t
        wave = (
            1.00 * np.sin(phase) * np.exp(-t * 1.6) +
            0.45 * np.sin(2.0 * phase) * np.exp(-t * 3.0) +
            0.15 * np.sin(3.0 * phase) * np.exp(-t * 5.0)
        )
        bass_attack = min(int(0.008 * fs), n_samples)
        if bass_attack > 0:
            env[:bass_attack] = np.linspace(0, 1, bass_attack)

    # 7. BRASS (GM 56-63)
    elif 56 <= program <= 63:
        phase = 2.0 * np.pi * freq * t
        wave = (
            1.00 * np.sin(phase) +
            0.75 * np.sin(2.0 * phase) +
            0.55 * np.sin(3.0 * phase) +
            0.35 * np.sin(4.0 * phase)
        )
        brass_attack = min(int(0.06 * fs), n_samples // 3)
        if brass_attack > 0:
            env[:brass_attack] = np.linspace(0, 1, brass_attack) ** 1.5
        if release_samples > 0:
            env[-release_samples:] = np.linspace(1, 0, release_samples)

    # 8. ORGAN & ACCORDION (GM 16-23)
    elif 16 <= program <= 23:
        phase = 2.0 * np.pi * freq * t
        wave = (
            0.80 * np.sin(phase) +
            0.60 * np.sin(2.0 * phase) +
            0.40 * np.sin(3.0 * phase) +
            0.30 * np.sin(4.0 * phase)
        )
        org_attack = min(int(0.015 * fs), n_samples // 4)
        if org_attack > 0:
            env[:org_attack] = np.linspace(0, 1, org_attack)
        if release_samples > 0:
            env[-release_samples:] = np.linspace(1, 0, release_samples)

    # 9. CHROMATIC PERCUSSION (GM 8-15, 112-119)
    elif 8 <= program <= 15 or 112 <= program <= 119:
        phase = 2.0 * np.pi * freq * t
        wave = (
            1.00 * np.sin(phase) * np.exp(-t * 3.5) +
            0.40 * np.sin(2.76 * phase) * np.exp(-t * 5.0) +
            0.20 * np.sin(5.40 * phase) * np.exp(-t * 8.0)
        )
        perc_attack = min(int(0.003 * fs), n_samples)
        if perc_attack > 0:
            env[:perc_attack] = np.linspace(0, 1, perc_attack)

    # 10. SYNTH LEAD & PADS (GM 80-103)
    elif 80 <= program <= 103:
        phase = 2.0 * np.pi * freq * t
        wave = (
            0.80 * np.sin(phase) +
            0.40 * np.sin(2.0 * phase) +
            0.30 * np.sin(3.0 * phase) +
            0.20 * np.sin(5.0 * phase)
        )
        pad_attack = min(int(0.08 * fs), n_samples // 3)
        if pad_attack > 0:
            env[:pad_attack] = np.linspace(0, 1, pad_attack)
        if release_samples > 0:
            env[-release_samples:] = np.linspace(1, 0, release_samples)

    # 11. PIANO / DEFAULT (GM 0-7)
    else:
        phase = 2.0 * np.pi * freq * t
        wave = (
            1.00 * np.sin(phase) * np.exp(-t * 1.5) +
            0.55 * np.sin(2.0 * phase) * np.exp(-t * 2.5) +
            0.28 * np.sin(3.0 * phase) * np.exp(-t * 3.8) +
            0.15 * np.sin(4.0 * phase) * np.exp(-t * 5.0)
        )
        piano_attack = min(int(0.006 * fs), n_samples)
        if piano_attack > 0:
            env[:piano_attack] = np.linspace(0, 1, piano_attack)

    signal = wave * env * vol
    return signal.astype(np.float32)
