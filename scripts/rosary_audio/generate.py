"""Make the guided-Rosary voice clips (runs in GitHub Actions, see .github/workflows/rosary-audio.yml).

Every voice here is free to use on the site:
  en  Piper en_US-ljspeech-high   LJ Speech dataset, public domain
  es  Piper es_MX-ald-medium      Ald Mexican Spanish dataset, Unlicense (public domain)
  pt  Piper pt_BR-faber-medium    OHF voice datasets, CC0
  tl  Meta MMS-TTS tgl            CC BY-NC 4.0 (non-commercial, attribution on the page)

Output: site/audio/rosary/<lang>/<clip>.mp3, a silent "hush_" twin of each response
half (so "take turns" mode can wait for you even when the phone screen is locked),
and manifest.json with every clip's length in seconds.
"""
import json, os, re, subprocess, sys, tempfile, urllib.request, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lines import clips  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "site", "audio", "rosary")
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
PIPER = {
    "en": ("en/en_US/ljspeech/high/en_US-ljspeech-high", 1.12),
    "es": ("es/es_MX/ald/medium/es_MX-ald-medium", 1.08),
    "pt": ("pt/pt_BR/faber/medium/pt_BR-faber-medium", 1.08),
}
CACHE = os.path.join(tempfile.gettempdir(), "piper-voices")


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def piper_wav(lang, text, wav):
    path, scale = PIPER[lang]
    os.makedirs(CACHE, exist_ok=True)
    onnx = os.path.join(CACHE, os.path.basename(path) + ".onnx")
    for ext in (".onnx", ".onnx.json"):
        if not os.path.exists(onnx.replace(".onnx", ext)):
            urllib.request.urlretrieve(HF + path + ext, onnx.replace(".onnx", ext))
    run(["piper", "-m", onnx, "-f", wav, "--length-scale", str(scale),
         "--sentence-silence", "0.35", "--noise-scale", "0.6"], input=text.encode("utf-8"))


_mms = None


def mms_wav(text, wav):
    """MMS drops punctuation, so speak phrase by phrase and put the pauses back."""
    global _mms
    import numpy as np
    import torch
    from transformers import AutoTokenizer, VitsModel
    if _mms is None:
        _mms = (VitsModel.from_pretrained("facebook/mms-tts-tgl"), AutoTokenizer.from_pretrained("facebook/mms-tts-tgl"))
        _mms[0].speaking_rate = 0.92
    model, tok = _mms
    rate = model.config.sampling_rate
    parts = [p for p in re.split(r"(?<=[.;:!?,])\s+", text) if p.strip()]
    audio = []
    for p in parts:
        torch.manual_seed(7)
        with torch.no_grad():
            y = model(**tok(p, return_tensors="pt")).waveform[0].numpy()
        audio.append(y)
        pause = 0.45 if re.search(r"[.;:!?]$", p) else 0.18
        audio.append(np.zeros(int(rate * pause), dtype=np.float32))
    y = np.concatenate(audio)
    y = (np.clip(y / max(1e-6, np.abs(y).max()) * 0.9, -1, 1) * 32767).astype("<i2")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(y.tobytes())


def to_mp3(wav, mp3, tail):
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af",
         "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
         "loudnorm=I=-17:TP=-2:LRA=11,apad=pad_dur=%.2f" % tail,
         "-ac", "1", "-ar", "22050", "-c:a", "libmp3lame", "-b:a", "48k", mp3])


def silent_mp3(seconds, mp3):
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono",
         "-t", "%.2f" % seconds, "-c:a", "libmp3lame", "-b:a", "16k", mp3])


def duration(mp3):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", mp3], capture_output=True, text=True, check=True)
    return round(float(out.stdout.strip()), 2)


def main(langs):
    for lang in langs:
        d = os.path.join(OUT, lang)
        os.makedirs(d, exist_ok=True)
        manifest = {}
        for cid, text in clips(lang):
            wav = os.path.join(tempfile.gettempdir(), "%s-%s.wav" % (lang, cid))
            (mms_wav(text, wav) if lang == "tl" else piper_wav(lang, text, wav))
            mp3 = os.path.join(d, cid + ".mp3")
            to_mp3(wav, mp3, 0.3 if cid.endswith("_a") else 0.9)
            manifest[cid] = duration(mp3)
            if cid.endswith("_b"):
                # Time for you to pray the response yourself: a little slower than the voice.
                h = os.path.join(d, "hush_" + cid + ".mp3")
                silent_mp3(manifest[cid] * 1.15 + 0.4, h)
                manifest["hush_" + cid] = duration(h)
            print(lang, cid, manifest[cid], flush=True)
        silent_mp3(1.5, os.path.join(d, "pause.mp3"))
        manifest["pause"] = duration(os.path.join(d, "pause.mp3"))
        json.dump(manifest, open(os.path.join(d, "manifest.json"), "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["en", "es", "pt", "tl"])
