import random
import tempfile
from typing import Dict, List, Union, Optional
from pydantic import BaseModel, Field, field_validator

from langchain_core.prompts import ChatPromptTemplate
import music21
import pygame

from music import MusicState, active_llm, primary_llm, fallback_llm


# =====================================================================
# 1. Pydantic Schemas with Strict Validation Bounds
# =====================================================================
class NoteItem(BaseModel):
    pitch: str = Field(description="Scientific pitch, e.g., 'D5', 'F#5', 'A4', 'G4', 'E5', or 'rest'")
    duration: float = Field(
        default=1.0,
        description="Duration in quarterLength (e.g. 0.5 for eighth, 0.75 for dotted eighth, 1.0 for quarter, 1.5 for dotted quarter, 2.0 for half note)"
    )

class ChordItem(BaseModel):
    pitches: List[str] = Field(description="Pitches forming the chord, e.g. ['D3', 'F#3', 'A3', 'D4']")
    duration: float = Field(default=2.0, description="Duration in quarterLength (e.g. 2.0, 4.0)")

class CompositionSchema(BaseModel):
    key: str = Field(
        description="Musical scale/key, e.g. 'D major', 'G major', 'C minor', 'F Dorian', 'A minor'"
    )
    target_seconds: float = Field(
        default=12.0,
        ge=5.0,
        le=60.0,
        description="Duration in seconds (5.0 to 60.0)"
    )
    tempo_bpm: int = Field(default=84, ge=50, le=180, description="Tempo in BPM matching the genre")
    time_signature: str = Field(default="4/4", description="Time signature, e.g. '4/4' or '3/4'")
    melody_instrument: str = Field(
        default="Flute",
        description="Primary lead instrument from General MIDI list (e.g. 'Flute', 'Violin', 'Sitar', 'Acoustic Grand', 'Trumpet', 'Alto Sax', 'Steel String Guitar', 'Cello'). MUST strictly match user request!"
    )
    harmony_instrument: str = Field(
        default="None",
        description="Accompaniment instrument from General MIDI list (e.g. 'Nylon String Guitar', 'String Ensemble 1', 'Acoustic Grand', 'Violin', 'Flute'), or 'None' if user requested a solo piece / single instrument."
    )
    melody: List[NoteItem] = Field(description="12-24 expressive, rhythmically diverse melody notes tailored to the chosen instrument.")
    harmony: List[ChordItem] = Field(
        default_factory=list,
        description="Harmonic accompaniment chords complementing the melody. Set to empty list [] if solo piece."
    )

    @field_validator("target_seconds", mode="before")
    @classmethod
    def clamp_duration(cls, v: float) -> float:
        try:
            val = float(v)
            return max(5.0, min(60.0, val))
        except (ValueError, TypeError):
            return 12.0


# =====================================================================
# 2. General MIDI 128 Instrument Resolution Map (0-127 Program Index)
# =====================================================================
# Complete 128 General MIDI instrument list (0-indexed = user list number - 1)
GM_128_INSTRUMENTS: Dict[int, str] = {
    # PIANO (0-7)
    0: "Acoustic Grand",
    1: "Bright Acoustic",
    2: "Electric Grand",
    3: "Honky-Tonk",
    4: "Electric Piano 1",
    5: "Electric Piano 2",
    6: "Harpsichord",
    7: "Clavinet",
    # CHROMATIC PERCUSSION (8-15)
    8: "Celesta",
    9: "Glockenspiel",
    10: "Music Box",
    11: "Vibraphone",
    12: "Marimba",
    13: "Xylophone",
    14: "Tubular Bells",
    15: "Dulcimer",
    # ORGAN (16-23)
    16: "Drawbar Organ",
    17: "Percussive Organ",
    18: "Rock Organ",
    19: "Church Organ",
    20: "Reed Organ",
    21: "Accordion",
    22: "Harmonica",
    23: "Tango Accordion",
    # GUITAR (24-31)
    24: "Nylon String Guitar",
    25: "Steel String Guitar",
    26: "Electric Jazz Guitar",
    27: "Electric Clean Guitar",
    28: "Electric Muted Guitar",
    29: "Overdriven Guitar",
    30: "Distortion Guitar",
    31: "Guitar Harmonics",
    # BASS (32-39)
    32: "Acoustic Bass",
    33: "Electric Bass (finger)",
    34: "Electric Bass (pick)",
    35: "Fretless Bass",
    36: "Slap Bass 1",
    37: "Slap Bass 2",
    38: "Synth Bass 1",
    39: "Synth Bass 2",
    # SOLO STRINGS (40-47)
    40: "Violin",
    41: "Viola",
    42: "Cello",
    43: "Contrabass",
    44: "Tremolo Strings",
    45: "Pizzicato Strings",
    46: "Orchestral Strings",
    47: "Timpani",
    # ENSEMBLE (48-55)
    48: "String Ensemble 1",
    49: "String Ensemble 2",
    50: "SynthStrings 1",
    51: "SynthStrings 2",
    52: "Choir Aahs",
    53: "Voice Oohs",
    54: "Synth Voice",
    55: "Orchestra Hit",
    # BRASS (56-63)
    56: "Trumpet",
    57: "Trombone",
    58: "Tuba",
    59: "Muted Trumpet",
    60: "French Horn",
    61: "Brass Section",
    62: "SynthBrass 1",
    63: "SynthBrass 2",
    # REED (64-71)
    64: "Soprano Sax",
    65: "Alto Sax",
    66: "Tenor Sax",
    67: "Baritone Sax",
    68: "Oboe",
    69: "English Horn",
    70: "Bassoon",
    71: "Clarinet",
    # PIPE (72-79)
    72: "Piccolo",
    73: "Flute",
    74: "Recorder",
    75: "Pan Flute",
    76: "Blown Bottle",
    77: "Shakuhachi",
    78: "Whistle",
    79: "Ocarina",
    # SYNTH LEAD (80-87)
    80: "Square Wave",
    81: "Saw Wave",
    82: "Syn. Calliope",
    83: "Chiffer Lead",
    84: "Charang",
    85: "Solo Vox",
    86: "5th Saw Wave",
    87: "Bass & Lead",
    # SYNTH PAD (88-95)
    88: "Fantasia",
    89: "Warm Pad",
    90: "Polysynth",
    91: "Space Voice",
    92: "Bowed Glass",
    93: "Metal Pad",
    94: "Halo Pad",
    95: "Sweep Pad",
    # SYNTH EFFECTS (96-103)
    96: "Ice Rain",
    97: "Soundtrack",
    98: "Crystal",
    99: "Atmosphere",
    100: "Brightness",
    101: "Goblin",
    102: "Echo Drops",
    103: "Star Theme",
    # ETHNIC (104-111)
    104: "Sitar",
    105: "Banjo",
    106: "Shamisen",
    107: "Koto",
    108: "Kalimba",
    109: "Bagpipe",
    110: "Fiddle",
    111: "Shanai",
    # PERCUSSIVE (112-119)
    112: "Tinkle Bell",
    113: "Agogo",
    114: "Steel Drums",
    115: "Woodblock",
    116: "Taiko Drum",
    117: "Melodic Tom",
    118: "Synth Drum",
    119: "Reverse Cymbal",
    # SOUND EFFECTS (120-127)
    120: "Guitar Fret Noise",
    121: "Breath Noise",
    122: "Seashore",
    123: "Bird Tweet",
    124: "Telephone Ring",
    125: "Helicopter",
    126: "Applause",
    127: "Gunshot",
}

# Fast lookup map with normalized search aliases
GM_NAME_TO_PROGRAM: Dict[str, int] = {}
for prog, name in GM_128_INSTRUMENTS.items():
    GM_NAME_TO_PROGRAM[name.lower()] = prog

# User-friendly aliases
ALIASES: Dict[str, int] = {
    "piano": 0,
    "grand piano": 0,
    "acoustic piano": 0,
    "electric piano": 4,
    "harpsichord": 6,
    "music box": 10,
    "marimba": 12,
    "xylophone": 13,
    "tubular bells": 14,
    "organ": 16,
    "rock organ": 18,
    "church organ": 19,
    "accoridan": 21,
    "accordion": 21,
    "harmonica": 22,
    "guitar": 24,
    "acoustic guitar": 24,
    "classical guitar": 24,
    "spanish guitar": 24,
    "steel guitar": 25,
    "electric guitar": 27,
    "jazz guitar": 26,
    "clean guitar": 27,
    "distortion guitar": 30,
    "bass": 33,
    "acoustic bass": 32,
    "electric bass": 33,
    "synth bass": 38,
    "violin": 40,
    "violine": 40,
    "viola": 41,
    "cello": 42,
    "contrabass": 43,
    "double bass": 43,
    "strings": 48,
    "string ensemble": 48,
    "stringinstrument": 48,
    "orchestral strings": 46,
    "orchestra": 48,
    "timpani": 47,
    "choir": 52,
    "trumpet": 56,
    "trombone": 57,
    "tuba": 58,
    "french horn": 60,
    "horn": 60,
    "brass": 61,
    "brass section": 61,
    "saxophone": 65,
    "saxaphone": 65,
    "sax": 65,
    "soprano sax": 64,
    "alto sax": 65,
    "tenor sax": 66,
    "baritone sax": 67,
    "oboe": 68,
    "english horn": 69,
    "bassoon": 70,
    "clarinet": 71,
    "piccolo": 72,
    "flute": 73,
    "flut": 73,
    "bansuri": 73,
    "indian flute": 73,
    "recorder": 74,
    "pan flute": 75,
    "shakuhachi": 77,
    "skakuhachi": 77,
    "whistle": 78,
    "ocarina": 79,
    "synth lead": 80,
    "square lead": 80,
    "saw lead": 81,
    "synth pad": 89,
    "warm pad": 89,
    "sitar": 104,
    "banjo": 105,
    "shamisen": 106,
    "koto": 107,
    "kalimba": 108,
    "bagpipe": 109,
    "fiddle": 110,
    "shanai": 111,
    "shehnai": 111,
    "steel drums": 114,
}
GM_NAME_TO_PROGRAM.update(ALIASES)


# Corresponding music21 instrument classes
def get_music21_instrument_class(program: int):
    """Maps a GM program number to the closest music21 Instrument class."""
    if 0 <= program <= 7:
        if program == 6:
            return music21.instrument.Harpsichord
        return music21.instrument.Piano
    elif 8 <= program <= 15:
        if program in (9, 10, 11, 12, 13):
            return music21.instrument.Marimba
        return music21.instrument.Percussion
    elif 16 <= program <= 23:
        if program in (21, 23):
            return music21.instrument.Accordion
        elif program == 22:
            return music21.instrument.Harmonica
        return music21.instrument.Organ
    elif 24 <= program <= 31:
        if program >= 26:
            return music21.instrument.ElectricGuitar
        return music21.instrument.AcousticGuitar
    elif 32 <= program <= 39:
        if program >= 33:
            return music21.instrument.ElectricBass
        return music21.instrument.AcousticBass
    elif 40 <= program <= 47:
        if program == 40:
            return music21.instrument.Violin
        elif program == 41:
            return music21.instrument.Viola
        elif program == 42:
            return music21.instrument.Violoncello
        elif program == 43:
            return music21.instrument.Contrabass
        elif program == 47:
            return music21.instrument.Timpani
        return music21.instrument.StringInstrument
    elif 48 <= program <= 55:
        if program in (52, 53):
            return music21.instrument.Choir
        return music21.instrument.StringInstrument
    elif 56 <= program <= 63:
        if program in (56, 59):
            return music21.instrument.Trumpet
        elif program == 57:
            return music21.instrument.Trombone
        elif program == 58:
            return music21.instrument.Tuba
        elif program == 60:
            return music21.instrument.Horn
        return music21.instrument.BrassInstrument
    elif 64 <= program <= 71:
        if program in (64, 65, 66, 67):
            return music21.instrument.Saxophone
        elif program == 68:
            return music21.instrument.Oboe
        elif program == 69:
            return music21.instrument.EnglishHorn
        elif program == 70:
            return music21.instrument.Bassoon
        elif program == 71:
            return music21.instrument.Clarinet
        return music21.instrument.Woodwind
    elif 72 <= program <= 79:
        if program == 72:
            return music21.instrument.Piccolo
        elif program in (73, 75, 77, 78, 79):
            return music21.instrument.Flute
        elif program == 74:
            return music21.instrument.Recorder
        return music21.instrument.Flute
    elif 104 <= program <= 111:
        if program in (104, 105, 106, 107):
            return music21.instrument.Lute
        elif program == 110:
            return music21.instrument.Violin
        return music21.instrument.AcousticGuitar
    return music21.instrument.Instrument


def resolve_instrument(name: str) -> music21.instrument.Instrument:
    """Resolves an instrument name to a music21 instrument with the exact General MIDI program."""
    clean = name.strip().lower()

    # Exact or alias match
    prog: Optional[int] = GM_NAME_TO_PROGRAM.get(clean)

    # Substring search if not found
    if prog is None:
        for alias, p in GM_NAME_TO_PROGRAM.items():
            if alias in clean or clean in alias:
                prog = p
                break

    if prog is None:
        prog = 0  # Default to Acoustic Grand Piano

    canonical_name = GM_128_INSTRUMENTS.get(prog, "Acoustic Grand")
    cls = get_music21_instrument_class(prog)
    inst = cls()
    inst.midiProgram = prog
    inst.instrumentName = canonical_name
    return inst


def extract_single_instrument(text: str) -> Optional[str]:
    """Finds the most specific instrument mentioned in text."""
    t = text.lower().replace("violine", "violin").replace("saxaphone", "saxophone").replace("accoridan", "accordion")
    matches = [
        ("pan flute", "Pan Flute"),
        ("indian flute", "Flute"),
        ("bansuri", "Flute"),
        ("shakuhachi", "Shakuhachi"),
        ("skakuhachi", "Shakuhachi"),
        ("flute", "Flute"),
        ("flut", "Flute"),
        ("recorder", "Recorder"),
        ("piccolo", "Piccolo"),
        ("ocarina", "Ocarina"),
        ("steel string guitar", "Steel String Guitar"),
        ("nylon string guitar", "Nylon String Guitar"),
        ("electric guitar", "Overdriven Guitar"),
        ("acoustic guitar", "Steel String Guitar"),
        ("guitar", "Steel String Guitar"),
        ("electric piano", "Electric Piano 1"),
        ("acoustic grand", "Acoustic Grand"),
        ("grand piano", "Acoustic Grand"),
        ("piano", "Acoustic Grand"),
        ("harpsichord", "Harpsichord"),
        ("violin", "Violin"),
        ("fiddle", "Violin"),
        ("viola", "Viola"),
        ("cello", "Cello"),
        ("contrabass", "Contrabass"),
        ("string ensemble", "String Ensemble 1"),
        ("orchestral strings", "Orchestral Strings"),
        ("strings", "String Ensemble 1"),
        ("trumpet", "Trumpet"),
        ("french horn", "French Horn"),
        ("trombone", "Trombone"),
        ("tuba", "Tuba"),
        ("brass section", "Brass Section"),
        ("brass", "Brass Section"),
        ("soprano sax", "Soprano Sax"),
        ("alto sax", "Alto Sax"),
        ("tenor sax", "Tenor Sax"),
        ("baritone sax", "Baritone Sax"),
        ("saxophone", "Alto Sax"),
        ("sax", "Alto Sax"),
        ("clarinet", "Clarinet"),
        ("oboe", "Oboe"),
        ("bassoon", "Bassoon"),
        ("harmonica", "Harmonica"),
        ("accordion", "Accordion"),
        ("acoustic bass", "Acoustic Bass"),
        ("electric bass", "Electric Bass (finger)"),
        ("synth bass", "Synth Bass 1"),
        ("bass", "Acoustic Bass"),
        ("sitar", "Sitar"),
        ("koto", "Koto"),
        ("kalimba", "Kalimba"),
        ("harp", "Harp"),
        ("marimba", "Marimba"),
        ("vibraphone", "Vibraphone"),
        ("music box", "Music Box"),
        ("steel drums", "Steel Drums"),
    ]
    for key, name in matches:
        if key in t:
            return name
    return None


def detect_requested_instruments(prompt: str) -> tuple[Optional[str], Optional[str], str]:
    """
    Intelligently analyzes user prompt for instrument intent:
    - mode 'both': same instrument requested in both harmony and melody tracks
    - mode 'solo': user strictly requested only one instrument (no accompaniment)
    - mode 'specified': user gave distinct melody and harmony instruments
    - mode 'krishna': devotional Indian flute
    - mode 'melody_only': single lead requested without accompaniment preference
    - mode 'free': no specific instruments mentioned
    """
    p = prompt.lower().replace("violine", "violin").replace("saxaphone", "saxophone").replace("accoridan", "accordion")

    # 1. Check if user requested the SAME instrument for BOTH tracks
    is_both = any(phrase in p for phrase in [
        "in both harmony and melody",
        "in both melody and harmony",
        "both harmony and melody",
        "both melody and harmony",
        "in both tracks",
        "for both tracks",
        "both tracks",
        "in both",
        "for both",
        "use violin in both",
        "use violine in both",
        "use flute in both",
        "same instrument in both",
        "same instrument for both",
        "both harmony and lead"
    ])
    if is_both:
        inst = extract_single_instrument(p) or "Violin"
        return inst, inst, "both"

    # 2. Check if user requested a SOLO piece or ONLY one instrument
    is_solo = any(phrase in p for phrase in [
        "only",
        "solo",
        "pure",
        "just",
        "single instrument",
        "one instrument",
        "no other instrument",
        "no accompaniment",
        "no chords",
        "without chords",
        "without accompaniment"
    ])
    if is_solo:
        inst = extract_single_instrument(p) or "Flute"
        return inst, "None", "solo"

    # 3. Check for specific accompaniment / harmony keywords
    mel_inst = extract_single_instrument(p)
    harm_inst = None

    if any(k in p for k in ["deep string chords", "orchestral strings", "string chords", "sweeping orchestral strings"]):
        harm_inst = "String Ensemble 1"
    elif "piano chords" in p or "with piano" in p:
        harm_inst = "Acoustic Grand"
    elif "guitar chords" in p or "with guitar" in p:
        harm_inst = "Nylon String Guitar"
    elif "cello" in p and mel_inst != "Cello":
        harm_inst = "Cello"
    elif "harp" in p and mel_inst != "Harp":
        harm_inst = "Harp"
    elif "brass" in p and mel_inst != "Brass Section":
        harm_inst = "Brass Section"

    if mel_inst and harm_inst:
        return mel_inst, harm_inst, "specified"

    # 4. Check for Krishna / Indian style
    if any(k in p for k in ["krishna", "bansuri", "indian flute", "raga", "bhajan"]):
        return "Flute", "Nylon String Guitar", "krishna"

    if mel_inst:
        return mel_inst, None, "melody_only"

    return None, None, "free"


# =====================================================================
# 3. Dynamic Velocity & Humanization Engine
# =====================================================================
def apply_velocity_dynamics(
    element: Union[music21.note.Note, music21.chord.Chord],
    beat_position: float,
    base_velocity: int = 82,
    time_sig_numerator: int = 4
) -> None:
    beat_in_measure = (beat_position % time_sig_numerator)

    if beat_in_measure == 0.0:
        accent = 12
    elif time_sig_numerator == 4 and beat_in_measure == 2.0:
        accent = 6
    elif beat_in_measure % 1.0 != 0.0:
        accent = -5
    else:
        accent = 0

    jitter = random.randint(-3, 4)
    calculated_velocity = max(35, min(115, base_velocity + accent + jitter))
    element.volume.velocity = calculated_velocity


# =====================================================================
# 4. Composer Agent
# =====================================================================
def composer_agent(state: MusicState) -> Dict:
    user_input = state["musician_input"]
    mel_req, harm_req, mode = detect_requested_instruments(user_input)

    if mode == "both":
        key_hint = "C minor" if "c minor" in user_input.lower() else "D minor or G major"
        inst_instruction = (
            f"CRITICAL REQUIREMENT: User explicitly demanded {mel_req} in BOTH harmony and melody tracks!\n"
            f"You MUST set melody_instrument to '{mel_req}' AND harmony_instrument to '{mel_req}'.\n"
            f"Write lead melody notes for {mel_req} and chordal voicings/counterpoint for the accompanying {mel_req} track."
        )
    elif mode == "solo":
        key_hint = "D major or G major" if any(k in user_input.lower() for k in ["krishna", "flute", "bansuri"]) else "C minor or D minor"
        inst_instruction = (
            f"CRITICAL REQUIREMENT: User strictly requested a SOLO {mel_req} composition ONLY. No second instrument allowed!\n"
            f"You MUST set melody_instrument to '{mel_req}', harmony_instrument to 'None', and harmony to empty list [].\n"
            f"Write rich, expressive, multi-phrase solo melody notes specifically for {mel_req}."
        )
    elif mode == "specified":
        key_hint = "C minor" if "c minor" in user_input.lower() else "Eb major or D minor"
        inst_instruction = (
            f"User requested {mel_req} lead melody with {harm_req} accompaniment.\n"
            f"You MUST set melody_instrument to '{mel_req}' and harmony_instrument to '{harm_req}'."
        )
    elif mode == "krishna":
        key_hint = "D major (Raga Bhupali / Yaman scale) or G major"
        inst_instruction = (
            "IMPORTANT: Devotional Krishna / Indian style Flute music.\n"
            "You MUST set melody_instrument to 'Flute' (General MIDI #74) and harmony_instrument to 'Nylon String Guitar' or 'String Ensemble 1'.\n"
            "The melody should feature serene, devotional, ornamental flute phrasing with flowing steps, graceful leaps, and gentle pauses."
        )
    elif mode == "melody_only":
        key_hint = "D minor, G major, Eb major, or A minor"
        inst_instruction = (
            f"User specifically requested {mel_req}!\n"
            f"You MUST set melody_instrument to '{mel_req}'. Choose a tasteful accompaniment or 'None'."
        )
    else:
        key_hint = random.choice(["Eb major or C minor", "D minor or F major", "G minor or Bb major", "A minor or C major"])
        inst_instruction = "Choose distinct, expressive instruments from the General MIDI list (e.g. Flute, Violin, Sitar, Acoustic Grand, Trumpet, Alto Sax, Steel String Guitar)."

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a master composer, arranger, and multi-instrumentalist.\n"
         "Your goal is to write a compelling, non-repetitive musical composition matching the user's specific vision.\n\n"
         "Strict Composition Rules:\n"
         "1. {inst_instruction}\n"
         "2. KEY & TONALITY: Use {key_hint}. Build an evocative tonal atmosphere.\n"
         "3. MELODY: Write 12 to 24 diverse notes with varied durations (0.5, 0.75, 1.0, 1.5, 2.0) and expressive rests ('rest'). Avoid repeating the same 3 notes!\n"
         "4. HARMONY: Provide rich chord progressions (maj7, m7, sus2, add9) that harmonize beautifully with the melody (or empty list [] if solo).\n"
         "Output strictly structured data matching the schema."),
        ("user",
         "Genre / Style: {style}\n"
         "User Request: {input}\n"
         "Selected Key Palette: {key_hint}\n"
         "Generate the composition.")
    ])

    primary_chain = prompt | primary_llm.with_structured_output(CompositionSchema)
    fallback_chain = prompt | fallback_llm.with_structured_output(CompositionSchema)

    payload = {
        "style": state.get("style", "Lo-Fi"),
        "input": user_input,
        "key_hint": key_hint,
        "inst_instruction": inst_instruction
    }

    try:
        result: CompositionSchema = primary_chain.invoke(payload)
    except Exception as e:
        print(f"[Warning] Primary LLM failed ({e}), seamlessly switching to Groq fallback...")
        result: CompositionSchema = fallback_chain.invoke(payload)

    comp_dict = result.model_dump()

    # Enforce exact user constraints
    if mode == "both":
        comp_dict["melody_instrument"] = mel_req
        comp_dict["harmony_instrument"] = mel_req
    elif mode == "solo":
        comp_dict["melody_instrument"] = mel_req
        comp_dict["harmony_instrument"] = "None"
        comp_dict["harmony"] = []
    elif mode == "specified":
        if mel_req:
            comp_dict["melody_instrument"] = mel_req
        if harm_req:
            comp_dict["harmony_instrument"] = harm_req
    elif mode == "krishna":
        comp_dict["melody_instrument"] = "Flute"
    elif mel_req:
        comp_dict["melody_instrument"] = mel_req

    return {
        "composition_data": comp_dict,
        "target_seconds": result.target_seconds
    }


# =====================================================================
# 5. MIDI Converter (Deadlock-Proof & Multi-Track Instrument Assign)
# =====================================================================
def midi_converter(state: MusicState) -> Dict:
    data = state["composition_data"]
    target_seconds = float(data.get("target_seconds", state.get("target_seconds", 12.0)))
    bpm = int(data.get("tempo_bpm", 84))
    meter_str = str(data.get("time_signature", "4/4"))

    # Cap target seconds safely between 5s and 60s
    target_seconds = max(5.0, min(60.0, target_seconds))
    target_beats = (target_seconds / 60.0) * bpm

    try:
        meter_num = int(meter_str.split("/")[0])
    except Exception:
        meter_num = 4

    score = music21.stream.Score()
    score.insert(0, music21.tempo.MetronomeMark(number=bpm))
    score.insert(0, music21.meter.TimeSignature(meter_str))

    melody_part = music21.stream.Part(id="MelodyPart")
    harmony_part = music21.stream.Part(id="HarmonyPart")

    mel_name = data.get("melody_instrument", "Flute")
    harm_name = data.get("harmony_instrument", "None")

    mel_inst = resolve_instrument(mel_name)
    mel_inst.midiChannel = 0
    melody_part.insert(0, mel_inst)

    is_solo = (
        not harm_name
        or str(harm_name).strip().lower() in ("none", "null", "no", "off", "solo", "empty")
        or not data.get("harmony")
    )

    if not is_solo:
        harm_inst = resolve_instrument(harm_name)
        harm_inst.midiChannel = 1
        harmony_part.insert(0, harm_inst)

    # -------------------------------------------------------------
    # Render Melody (Deadlock-Free with Loop Guard)
    # -------------------------------------------------------------
    current_melody_beats = 0.0
    raw_melody = data.get("melody", [])
    if raw_melody:
        # Guarantee loop termination: max 300 notes total
        max_notes = 300
        notes_rendered = 0

        while current_melody_beats < (target_beats - 0.05) and notes_rendered < max_notes:
            advanced = False
            for item in raw_melody:
                remaining = target_beats - current_melody_beats
                if remaining <= 0.05:
                    break

                raw_dur = float(item.get("duration", 1.0))
                if raw_dur <= 0.05:
                    raw_dur = 0.5  # sanitize invalid duration

                dur = min(raw_dur, remaining)

                pitch_str = str(item.get("pitch", "rest")).strip()
                if pitch_str.lower() == "rest":
                    n = music21.note.Rest(quarterLength=dur)
                else:
                    try:
                        n = music21.note.Note(pitch_str, quarterLength=dur)
                    except Exception:
                        n = music21.note.Note("D5", quarterLength=dur)

                    apply_velocity_dynamics(
                        element=n,
                        beat_position=current_melody_beats,
                        base_velocity=88,
                        time_sig_numerator=meter_num
                    )

                melody_part.append(n)
                current_melody_beats += dur
                notes_rendered += 1
                advanced = True

                if current_melody_beats >= (target_beats - 0.05):
                    break

            if not advanced:
                break

    # -------------------------------------------------------------
    # Render Harmony (Deadlock-Free with Loop Guard)
    # -------------------------------------------------------------
    current_harmony_beats = 0.0
    raw_harmony = data.get("harmony", [])
    if raw_harmony:
        max_chords = 200
        chords_rendered = 0

        while current_harmony_beats < (target_beats - 0.05) and chords_rendered < max_chords:
            advanced = False
            for chord_item in raw_harmony:
                remaining = target_beats - current_harmony_beats
                if remaining <= 0.05:
                    break

                raw_dur = float(chord_item.get("duration", 2.0))
                if raw_dur <= 0.05:
                    raw_dur = 1.0

                dur = min(raw_dur, remaining)
                pitches = chord_item.get("pitches", ["D3", "A3", "D4"])

                try:
                    ch = music21.chord.Chord(pitches, quarterLength=dur)
                except Exception:
                    ch = music21.chord.Chord(["D3", "A3", "D4"], quarterLength=dur)

                apply_velocity_dynamics(
                    element=ch,
                    beat_position=current_harmony_beats,
                    base_velocity=60,
                    time_sig_numerator=meter_num
                )

                harmony_part.append(ch)
                current_harmony_beats += dur
                chords_rendered += 1
                advanced = True

                if current_harmony_beats >= (target_beats - 0.05):
                    break

            if not advanced:
                break

    score.insert(0, melody_part)
    if not is_solo and len(harmony_part.notesAndRests) > 0:
        score.insert(0, harmony_part)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_midi:
        score.write('midi', temp_midi.name)

    return {"midi_file": temp_midi.name}


# =====================================================================
# 6. Playback Utility
# =====================================================================
def play_midi(midi_file_path: str) -> None:
    """Plays generated MIDI through pygame with volume initialized."""
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(midi_file_path)
        pygame.mixer.music.set_volume(0.9)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        pygame.mixer.quit()
