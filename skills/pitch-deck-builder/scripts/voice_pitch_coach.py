#!/usr/bin/env python3
"""Live Voice Pitch Coach & VC Lab / FI Partner Q&A Grilling Engine.

Analyzes spoken 3-minute pitch transcripts for WPM pace, filler words, FI banned
buzzwords, quantified proof, and generates tailored investor grilling questions.
"""

from __future__ import annotations

import json
import re
from typing import Any

FILLER_WORDS = ("um", "uh", "like", "basically", "actually", "literally", "kind of", "sort of", "you know")
BUZZWORDS = ("revolutionary", "disruptive", "world-class", "game-changing", "synergy", "unprecedented", "cutting-edge", "best-in-class")

PARTNER_QA_BANK = [
    {
        "role": "FI Mentor",
        "question": "If you stripped away every buzzword, who is the exact person signing the check in Week 1 and what painful workaround are they replacing?",
    },
    {
        "role": "VC Lab Partner",
        "question": "Walk me through your bottom-up TAM math and gross margin at scale—how do you stay above 75% margin as AI inference volume grows?",
    },
    {
        "role": "PMF Truth Auditor",
        "question": "What percentage of your active users said they would be 'Very Disappointed' if your product disappeared tomorrow, and why haven't the rest churned?",
    },
    {
        "role": "Lean CTO",
        "question": "What is your defensible Secret Sauce that a well-funded incumbent or weekend AI wrapper cannot clone in 30 days?",
    },
    {
        "role": "Mensarius Ethics Partner",
        "question": "How does your pricing, data hygiene, and For-Progress iKPI prove that profit and customer trust compound together?",
    },
]


def analyze_voice_pitch(
    transcript: str,
    duration_seconds: float = 180.0,
    target_seconds: float = 180.0,
) -> dict[str, Any]:
    text = (transcript or "").strip()
    if not text:
        raise ValueError("'transcript' is required for voice pitch analysis.")

    words = re.findall(r"\b[\w'-]+\b", text)
    word_count = len(words)
    dur = max(1.0, float(duration_seconds or 180.0))
    wpm = round((word_count / dur) * 60.0, 1)
    lower = text.lower()

    filler_hits: dict[str, int] = {}
    for fw in FILLER_WORDS:
        cnt = len(re.findall(rf"\b{re.escape(fw)}\b", lower))
        if cnt:
            filler_hits[fw] = cnt
    total_fillers = sum(filler_hits.values())

    buzz_hits = [bw for bw in BUZZWORDS if re.search(rf"\b{re.escape(bw)}\b", lower)]
    has_money = bool(re.search(r"\$\s*\d", text))
    has_pct = bool(re.search(r"\d+\s*%", text))
    has_ask = bool(re.search(r"\b(raising|pre-seed|seed|safe|round|ask)\b", lower))

    score = 100
    feedback: list[str] = []

    if wpm > 165:
        score -= 12
        feedback.append(f"Pace is rushed ({wpm} WPM). Aim for 130–155 WPM so investors absorb your numbers.")
    elif wpm < 105:
        score -= 10
        feedback.append(f"Pace is slow ({wpm} WPM). Tighten transitions to hit 130–155 WPM.")
    else:
        feedback.append(f"Strong delivery pace ({wpm} WPM — right in the 130–155 WPM executive sweet spot).")

    if dur > target_seconds + 15:
        score -= 12
        feedback.append(f"Over 3-minute FI limit ({round(dur)}s vs {round(target_seconds)}s). Cut 1–2 tangent sentences.")

    if total_fillers > 0:
        score -= min(20, total_fillers * 3)
        feedback.append(f"Detected {total_fillers} filler words ({', '.join(f'{k}×{v}' for k, v in filler_hits.items())}). Pause silently instead.")

    if buzz_hits:
        score -= min(25, len(buzz_hits) * 8)
        feedback.append(f"Remove FI banned buzzwords: {', '.join(buzz_hits)}. Replace with verified metrics.")

    if not (has_money or has_pct):
        score -= 15
        feedback.append("Zero quantified metrics ($ or %) detected. Add concrete customer pain, MRR, or margin proof.")

    if not has_ask:
        score -= 8
        feedback.append("No clear Ask detected. End with exact round size, milestones, and next step.")

    score = max(0, min(100, score))
    verdict = "DEMO_DAY_READY" if score >= 85 else ("SHARPEN_BEFORE_PITCHING" if score >= 65 else "NEEDS_REWRITE")

    return {
        "ok": True,
        "clarityScore": score,
        "verdict": verdict,
        "wordCount": word_count,
        "durationSeconds": round(dur, 1),
        "wordsPerMinute": wpm,
        "fillerWords": filler_hits,
        "totalFillers": total_fillers,
        "buzzwordsFound": buzz_hits,
        "hasQuantifiedProof": has_money or has_pct,
        "hasClearAsk": has_ask,
        "coachingFeedback": feedback,
        "partnerGrillingQuestions": PARTNER_QA_BANK,
    }


if __name__ == "__main__":
    import sys

    sample = sys.argv[1] if len(sys.argv) > 1 else "My company ClaimPulse helps dental practices cut denials to 3% with $14,400 MRR and 84% margin. We are raising $750K Pre-Seed."
    print(json.dumps(analyze_voice_pitch(sample, 45), indent=2))
