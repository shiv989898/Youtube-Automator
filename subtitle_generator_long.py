import math


def generate_srt_from_script(script_text: str, duration: float, output_path: str) -> None:
    """Generate a very simple .srt subtitle file from the long-form script.

    Splits the script into short phrases and assigns equal time slices across
    the full voiceover duration.
    """
    if not script_text or duration <= 0:
        return

    words = script_text.split()
    phrases = []
    current = []
    for w in words:
        current.append(w)
        if len(current) >= 7 or w.endswith((".", "!", "?")):
            phrases.append(" ".join(current))
            current = []
    if current:
        phrases.append(" ".join(current))

    if not phrases:
        return

    time_per = duration / len(phrases)

    def fmt_ts(t: float) -> str:
        if t < 0:
            t = 0
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        millis = int((t - int(t)) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

    lines = []
    current_time = 0.0
    for idx, phrase in enumerate(phrases, start=1):
        start = current_time
        end = min(duration, start + time_per)
        lines.append(str(idx))
        lines.append(f"{fmt_ts(start)} --> {fmt_ts(end)}")
        lines.append(phrase)
        lines.append("")
        current_time += time_per
        if current_time >= duration:
            break

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
