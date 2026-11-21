#!/usr/bin/env python3
"""
Startup Antigravity — Founder Institute Pitch Deck Linter & Compiler.

Compiles `pitch-deck/deck.json` into:
  1. `pitch-deck/index.html` (zero-dependency 16:9 interactive web presentation + Print-to-PDF)
  2. `pitch-deck/DECK.md` (Marp-compatible Markdown export)
  3. Optional `pitch-deck/DECK.pptx` if `--pptx` is passed and `python-pptx` is installed.

Also provides reusable `lint_one_sentence_pitch()` and `lint_deck()` functions
imported by the bundled MCP server and lifecycle hooks.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"
DEFAULT_TEMPLATE_HTML = RESOURCES_DIR / "deck.template.html"

BANNED_BUZZWORDS = [
    "revolutionary",
    "disruptive",
    "disrupt",
    "world-class",
    "game-changing",
    "game changer",
    "cutting-edge",
    "next-gen",
    "next generation",
    "synergy",
    "best-in-class",
    "groundbreaking",
    "unprecedented",
    "magic",
    "seamless",
    "empower",
    "innovative",
    "first-ever",
    "only platform",
    "uber for",
    "airbnb for",
]

VAGUE_AUDIENCES = [
    "everyone",
    "anyone",
    "people",
    "consumers",
    "small businesses",
    "businesses",
    "companies",
    "enterprises",
    "users",
    "millennials",
    "gen z",
]

THEME_PRESETS: dict[str, dict[str, str]] = {
    "midnight-emerald": {
        "bg": "#0B1120",
        "surface": "#111C33",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "accent": "#10B981",
        "accent2": "#F59E0B",
        "border": "#1E293B",
    },
    "obsidian-gold": {
        "bg": "#090D16",
        "surface": "#131B2E",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "accent": "#F59E0B",
        "accent2": "#10B981",
        "border": "#1F2A44",
    },
    "editorial-light": {
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "text": "#0F172A",
        "muted": "#475569",
        "accent": "#059669",
        "accent2": "#D97706",
        "border": "#E2E8F0",
    },
    "cobalt-velocity": {
        "bg": "#090E1A",
        "surface": "#121B31",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "accent": "#38BDF8",
        "accent2": "#10B981",
        "border": "#1E293B",
    },
}


def _strip_tags(text: str) -> str:
    return re.sub(r"\s*\[(VALIDATED|HYPOTHESIS|TARGET)\]\s*", " ", text).strip()


def _word_count(text: str) -> int:
    clean = _strip_tags(text)
    return len([w for w in re.split(r"\s+", clean) if w])


def _format_badges_html(raw: str) -> str:
    escaped = html.escape(raw)
    escaped = escaped.replace(
        "[VALIDATED]", '<span class="badge badge-validated">VALIDATED</span>'
    )
    escaped = escaped.replace(
        "[HYPOTHESIS]", '<span class="badge badge-hypothesis">HYPOTHESIS</span>'
    )
    escaped = escaped.replace(
        "[TARGET]", '<span class="badge badge-target">TARGET</span>'
    )
    return escaped


def lint_one_sentence_pitch(pitch: str) -> dict[str, Any]:
    """Lint a Founder Institute Madlibs One-Sentence Pitch (+ Secret Sauce)."""
    issues: list[dict[str, str]] = []
    lowered = pitch.lower().strip()
    words = _word_count(pitch)

    if not lowered:
        return {
            "passed": False,
            "score": 0,
            "wordCount": 0,
            "issues": [
                {
                    "severity": "error",
                    "rule": "fi-pitch-empty",
                    "message": "FI One-Sentence Pitch is empty.",
                }
            ],
        }

    # Check template placeholders left unfilled
    if re.search(r"\[(defined|specific|secret|company|target)[^\]]*\]", lowered):
        issues.append(
            {
                "severity": "error",
                "rule": "fi-pitch-placeholder",
                "message": "Pitch still contains unfilled template brackets (e.g. [defined offering]).",
            }
        )

    # Check FI Madlibs structural anchors
    has_offering = "developing" in lowered or "building" in lowered
    has_audience = "to help" in lowered
    has_secret_sauce = " with " in lowered
    if not (has_offering and has_audience):
        issues.append(
            {
                "severity": "warning",
                "rule": "fi-madlibs-structure",
                "message": (
                    "Follow the FI Madlibs formula: 'My company, [Name], is developing "
                    "[offering] to help [specific audience] [solve problem] with [secret sauce].'"
                ),
            }
        )
    if not has_secret_sauce:
        issues.append(
            {
                "severity": "warning",
                "rule": "fi-secret-sauce",
                "message": "Missing explicit 'with [secret sauce]' differentiator at the end of the pitch.",
            }
        )

    # Banned buzzwords / superlatives
    found_buzz = [
        bw for bw in BANNED_BUZZWORDS if re.search(rf"\b{re.escape(bw)}\b", lowered)
    ]
    if found_buzz:
        issues.append(
            {
                "severity": "error",
                "rule": "fi-no-buzzwords",
                "message": f"Remove buzzwords/superlatives: {', '.join(found_buzz)}. Use concrete facts instead.",
            }
        )

    # Check vague audiences right after "to help"
    m_aud = re.search(r"to help\s+([^.,;]{2,60})", lowered)
    if m_aud:
        aud_snippet = m_aud.group(1)
        for vague in VAGUE_AUDIENCES:
            if re.search(rf"\b{re.escape(vague)}\b", aud_snippet):
                issues.append(
                    {
                        "severity": "warning",
                        "rule": "fi-specific-audience",
                        "message": (
                            f"Target audience looks too broad ('{vague}'). Narrow to a specific "
                            "buyer persona (e.g. 'Series A B2B SaaS CFOs' or 'independent dental clinics')."
                        ),
                    }
                )
                break

    if words > 38:
        issues.append(
            {
                "severity": "warning",
                "rule": "fi-pitch-length",
                "message": f"Pitch is {words} words; tighten to under 35 words so it can be spoken in one breath.",
            }
        )

    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    score = max(0, 100 - errors * 25 - warnings * 12)
    return {
        "passed": errors == 0,
        "score": score,
        "wordCount": words,
        "issues": issues,
    }


def lint_deck(deck_data: dict[str, Any]) -> dict[str, Any]:
    """Audit a pitch deck JSON against Founder Institute & Mensarius evidence standards."""
    issues: list[dict[str, Any]] = []
    meta = deck_data.get("meta", {})
    slides = deck_data.get("slides", [])

    pitch_report = lint_one_sentence_pitch(meta.get("fiOneSentencePitch", ""))
    for item in pitch_report["issues"]:
        issues.append({"slide": "meta", **item})

    if not isinstance(slides, list) or len(slides) == 0:
        return {
            "passed": False,
            "readinessScore": 0,
            "slideCount": 0,
            "validatedClaims": 0,
            "hypothesisClaims": 0,
            "issues": issues
            + [
                {
                    "slide": "deck",
                    "severity": "error",
                    "rule": "slides-required",
                    "message": "Deck must contain a non-empty 'slides' array.",
                }
            ],
        }

    if len(slides) < 8 or len(slides) > 15:
        issues.append(
            {
                "slide": "deck",
                "severity": "warning",
                "rule": "fi-slide-count",
                "message": f"Deck has {len(slides)} slides; FI recommends 10–12 core slides for a 3-minute pitch.",
            }
        )

    problem_bullets = None
    solution_bullets = None
    raw_text_dump = json.dumps(deck_data)
    validated_count = raw_text_dump.count("[VALIDATED]")
    hypothesis_count = raw_text_dump.count("[HYPOTHESIS]")
    placeholder_hits = len(
        re.findall(r"(Your Company Name|Replace (This )?With|Founder Name)", raw_text_dump)
    )

    if placeholder_hits > 0:
        issues.append(
            {
                "slide": "deck",
                "severity": "warning",
                "rule": "unfilled-placeholders",
                "message": f"Found {placeholder_hits} starter template placeholder string(s) still present.",
            }
        )

    for idx, slide in enumerate(slides, start=1):
        sid = slide.get("id", f"slide-{idx}")
        headline = slide.get("headline", "")
        hw = _word_count(headline)
        if hw == 0:
            issues.append(
                {
                    "slide": sid,
                    "severity": "error",
                    "rule": "headline-missing",
                    "message": "Slide is missing a headline.",
                }
            )
        elif hw > 12:
            issues.append(
                {
                    "slide": sid,
                    "severity": "warning",
                    "rule": "fi-headline-10-words",
                    "message": f"Headline is {hw} words (FI target: <=10 words). Tighten into a punchy takeaway.",
                }
            )

        # Buzzword scan on slide headline
        hl_low = headline.lower()
        for bw in BANNED_BUZZWORDS:
            if re.search(rf"\b{re.escape(bw)}\b", hl_low):
                issues.append(
                    {
                        "slide": sid,
                        "severity": "warning",
                        "rule": "fi-slide-buzzword",
                        "message": f"Headline uses buzzword '{bw}'. Replace with quantified proof.",
                    }
                )

        bullets = slide.get("bullets")
        if isinstance(bullets, list):
            if len(bullets) > 3:
                issues.append(
                    {
                        "slide": sid,
                        "severity": "warning",
                        "rule": "fi-max-3-bullets",
                        "message": f"Slide has {len(bullets)} bullets (FI rule: max 3 concise bullets per slide).",
                    }
                )
            if sid == "problem":
                problem_bullets = len(bullets)
            elif sid == "solution":
                solution_bullets = len(bullets)

    if (
        problem_bullets is not None
        and solution_bullets is not None
        and problem_bullets != solution_bullets
    ):
        issues.append(
            {
                "slide": "solution",
                "severity": "warning",
                "rule": "fi-problem-solution-mirror",
                "message": (
                    f"Problem slide has {problem_bullets} bullets while Solution slide has "
                    f"{solution_bullets}. FI decks mirror Problem and Solution 1-to-1."
                ),
            }
        )

    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    readiness = max(0, min(100, 100 - errors * 20 - warnings * 6))

    return {
        "passed": errors == 0,
        "readinessScore": readiness,
        "slideCount": len(slides),
        "validatedClaims": validated_count,
        "hypothesisClaims": hypothesis_count,
        "placeholderHits": placeholder_hits,
        "pitchScore": pitch_report["score"],
        "issues": issues,
    }


def _render_slide_html(slide: dict[str, Any], index: int, total: int, company: str) -> str:
    stype = slide.get("type", "bullets")
    kicker = html.escape(slide.get("kicker", ""))
    headline = _format_badges_html(slide.get("headline", ""))
    notes = html.escape(slide.get("notes", ""), quote=True)
    callout = slide.get("callout", "")
    callout_html = (
        f'<div class="callout">{_format_badges_html(callout)}</div>' if callout else ""
    )

    if stype == "cover":
        sub = _format_badges_html(slide.get("subheadline", ""))
        footer = html.escape(slide.get("footer", ""))
        return (
            f'<article class="slide slide-cover" data-notes="{notes}">'
            f'  <div>'
            f'    <div class="kicker">{kicker}</div>'
            f'    <h1 class="headline">{headline}</h1>'
            f'    <p class="subheadline">{sub}</p>'
            f'    <div class="cover-footer">{footer}</div>'
            f'  </div>'
            f'</article>'
        )

    body_parts: list[str] = []

    if stype == "bullets":
        items = []
        for b in slide.get("bullets", []):
            if isinstance(b, dict):
                lbl = _format_badges_html(str(b.get("label", "")))
                txt = _format_badges_html(str(b.get("text", "")))
                items.append(
                    f'<li class="bullet-card"><span class="bullet-label">{lbl}</span>'
                    f'<span class="bullet-text">{txt}</span></li>'
                )
            else:
                items.append(
                    f'<li class="bullet-card"><span class="bullet-text">{_format_badges_html(str(b))}</span></li>'
                )
        body_parts.append(f'<ul class="bullet-list">{"".join(items)}</ul>')

    elif stype == "metrics":
        cards = []
        for m in slide.get("metrics", []):
            val = _format_badges_html(str(m.get("value", "")))
            lbl = _format_badges_html(str(m.get("label", "")))
            cards.append(
                f'<div class="metric-card"><div class="metric-val">{val}</div>'
                f'<div class="metric-lbl">{lbl}</div></div>'
            )
        body_parts.append(f'<div class="metrics-grid">{"".join(cards)}</div>')

    elif stype == "two-column":
        lt = html.escape(slide.get("leftTitle", ""))
        rt = html.escape(slide.get("rightTitle", ""))
        l_items = "".join(
            f"<li>{_format_badges_html(str(x))}</li>" for x in slide.get("leftItems", [])
        )
        r_items = "".join(
            f"<li>{_format_badges_html(str(x))}</li>" for x in slide.get("rightItems", [])
        )
        body_parts.append(
            f'<div class="two-col">'
            f'  <div class="col-card"><h3>{lt}</h3><ul>{l_items}</ul></div>'
            f'  <div class="col-card"><h3>{rt}</h3><ul>{r_items}</ul></div>'
            f'</div>'
        )

    elif stype == "comparison":
        headers = "".join(f"<th>{html.escape(str(h))}</th>" for h in slide.get("headers", []))
        rows_html = []
        for row in slide.get("rows", []):
            tds = "".join(f"<td>{_format_badges_html(str(c))}</td>" for c in row)
            rows_html.append(f"<tr>{tds}</tr>")
        body_parts.append(
            f'<table class="comp"><thead><tr>{headers}</tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody></table>'
        )

    elif stype == "ask":
        amt = html.escape(str(slide.get("askAmount", "")))
        inst = _format_badges_html(str(slide.get("instrument", "")))
        allocs = "".join(
            f'<div class="alloc-row"><span>{html.escape(str(a.get("label", "")))}</span>'
            f'<span class="alloc-pct">{html.escape(str(a.get("percent", "")))}</span></div>'
            for a in slide.get("allocations", [])
        )
        miles = "".join(
            f"<li>{_format_badges_html(str(m))}</li>" for m in slide.get("milestones", [])
        )
        impact = slide.get("impactMetric", "")
        impact_html = (
            f'<div class="callout" style="margin-top:12px;">{_format_badges_html(impact)}</div>'
            if impact
            else ""
        )
        body_parts.append(
            f'<div class="ask-grid">'
            f'  <div class="ask-hero">'
            f'    <div><div class="ask-amount">{amt}</div><div class="ask-inst">{inst}</div></div>'
            f'    <div>{allocs}</div>'
            f'  </div>'
            f'  <div class="col-card"><h3>Key Unlock Milestones</h3><ul>{miles}</ul>{impact_html}</div>'
            f'</div>'
        )

    if callout_html:
        body_parts.append(callout_html)

    return (
        f'<article class="slide" data-notes="{notes}">'
        f'  <div>'
        f'    <div class="kicker">{kicker}</div>'
        f'    <h2 class="headline">{headline}</h2>'
        f'  </div>'
        f'  <div class="slide-body">{"".join(body_parts)}</div>'
        f'  <div class="slide-foot"><span>{html.escape(company)}</span>'
        f'  <span>{index} / {total}</span></div>'
        f'</article>'
    )


def render_html(deck_data: dict[str, Any], template_path: Path | None = None) -> str:
    """Compile deck JSON into a self-contained interactive 16:9 HTML5 deck."""
    tpl_file = template_path or DEFAULT_TEMPLATE_HTML
    template = tpl_file.read_text(encoding="utf-8")

    meta = deck_data.get("meta", {})
    company = meta.get("companyName", "Startup Pitch Deck")
    target_minutes = float(meta.get("targetPitchMinutes", 3))
    target_seconds = int(max(60, target_minutes * 60))

    raw_theme = deck_data.get("theme", {})
    preset_name = raw_theme.get("preset", "midnight-emerald")
    theme = {**THEME_PRESETS.get(preset_name, THEME_PRESETS["midnight-emerald"]), **raw_theme}

    slides = deck_data.get("slides", [])
    slides_html = "\n      ".join(
        _render_slide_html(s, i + 1, len(slides), company) for i, s in enumerate(slides)
    )

    replacements = {
        "__DECK_TITLE__": html.escape(f"{company} — Pitch Deck"),
        "__COMPANY_NAME__": html.escape(company),
        "__THEME_BG__": theme["bg"],
        "__THEME_SURFACE__": theme["surface"],
        "__THEME_TEXT__": theme["text"],
        "__THEME_MUTED__": theme["muted"],
        "__THEME_ACCENT__": theme["accent"],
        "__THEME_ACCENT2__": theme["accent2"],
        "__THEME_BORDER__": theme["border"],
        "__SLIDES_HTML__": slides_html,
        "__TARGET_SECONDS__": str(target_seconds),
    }
    for k, v in replacements.items():
        template = template.replace(k, v)
    return template


def render_markdown(deck_data: dict[str, Any]) -> str:
    """Render Marp-compatible Markdown deck from deck JSON."""
    meta = deck_data.get("meta", {})
    company = meta.get("companyName", "Startup Pitch Deck")
    lines = [
        "---",
        "marp: true",
        "theme: default",
        "paginate: true",
        f"header: '{company}'",
        "---",
        "",
    ]
    slides = deck_data.get("slides", [])
    for idx, slide in enumerate(slides):
        if idx > 0:
            lines.extend(["", "---", ""])
        kicker = slide.get("kicker", "")
        headline = slide.get("headline", "")
        if kicker:
            lines.append(f"###### {kicker}")
        lines.append(f"# {headline}" if idx == 0 else f"## {headline}")
        lines.append("")

        stype = slide.get("type", "bullets")
        if stype == "cover":
            if slide.get("subheadline"):
                lines.append(f"> {slide['subheadline']}")
                lines.append("")
            if slide.get("footer"):
                lines.append(f"*{slide['footer']}*")
        elif stype == "bullets":
            for b in slide.get("bullets", []):
                if isinstance(b, dict):
                    lines.append(f"- **{b.get('label', '')}:** {b.get('text', '')}")
                else:
                    lines.append(f"- {b}")
        elif stype == "metrics":
            lines.append("| Metric | Detail |")
            lines.append("| :--- | :--- |")
            for m in slide.get("metrics", []):
                lines.append(f"| **{m.get('value', '')}** | {m.get('label', '')} |")
        elif stype == "two-column":
            lines.append(f"### {slide.get('leftTitle', 'Left')}")
            for item in slide.get("leftItems", []):
                lines.append(f"- {item}")
            lines.append("")
            lines.append(f"### {slide.get('rightTitle', 'Right')}")
            for item in slide.get("rightItems", []):
                lines.append(f"- {item}")
        elif stype == "comparison":
            headers = slide.get("headers", [])
            if headers:
                lines.append("| " + " | ".join(str(h) for h in headers) + " |")
                lines.append("| " + " | ".join(":---" for _ in headers) + " |")
                for row in slide.get("rows", []):
                    lines.append("| " + " | ".join(str(c) for c in row) + " |")
        elif stype == "ask":
            lines.append(f"**Raise:** {slide.get('askAmount', '')} — {slide.get('instrument', '')}")
            lines.append("")
            for a in slide.get("allocations", []):
                lines.append(f"- **{a.get('percent', '')}** — {a.get('label', '')}")
            lines.append("")
            lines.append("### Milestones")
            for m in slide.get("milestones", []):
                lines.append(f"- {m}")
            if slide.get("impactMetric"):
                lines.append("")
                lines.append(f"> {slide['impactMetric']}")

        if slide.get("callout"):
            lines.append("")
            lines.append(f"> {slide['callout']}")
        if slide.get("notes"):
            lines.append("")
            lines.append(f"<!-- Speaker Notes: {slide['notes']} -->")

    return "\n".join(lines) + "\n"


def _export_optional_pptx(deck_data: dict[str, Any], out_path: Path) -> str | None:
    """Optionally build a native .pptx if python-pptx is installed."""
    try:
        from pptx import Presentation  # type: ignore
        from pptx.util import Inches, Pt  # type: ignore
    except ImportError:
        return None

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for slide_data in deck_data.get("slides", []):
        s = prs.slides.add_slide(blank_layout)
        tb = s.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{slide_data.get('kicker', '')}\n{slide_data.get('headline', '')}"
        p.font.size = Pt(28)
        p.font.bold = True

        body_lines: list[str] = []
        stype = slide_data.get("type", "bullets")
        if stype == "cover" and slide_data.get("subheadline"):
            body_lines.append(slide_data["subheadline"])
        elif stype == "bullets":
            for b in slide_data.get("bullets", []):
                body_lines.append(
                    f"• {b.get('label', '')}: {b.get('text', '')}"
                    if isinstance(b, dict)
                    else f"• {b}"
                )
        elif stype == "metrics":
            for m in slide_data.get("metrics", []):
                body_lines.append(f"• {m.get('value', '')} — {m.get('label', '')}")
        elif stype == "two-column":
            body_lines.append(slide_data.get("leftTitle", ""))
            body_lines.extend(f"  - {x}" for x in slide_data.get("leftItems", []))
            body_lines.append(slide_data.get("rightTitle", ""))
            body_lines.extend(f"  - {x}" for x in slide_data.get("rightItems", []))
        elif stype == "comparison":
            headers = slide_data.get("headers", [])
            if headers:
                body_lines.append(" | ".join(str(h) for h in headers))
            for row in slide_data.get("rows", []):
                body_lines.append(" | ".join(str(c) for c in row))
        elif stype == "ask":
            body_lines.append(
                f"Ask: {slide_data.get('askAmount', '')} ({slide_data.get('instrument', '')})"
            )
            body_lines.extend(f"• {m}" for m in slide_data.get("milestones", []))

        if body_lines:
            bb = s.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
            btf = bb.text_frame
            btf.word_wrap = True
            btf.paragraphs[0].text = "\n".join(body_lines)
            btf.paragraphs[0].font.size = Pt(18)

        if slide_data.get("notes"):
            s.notes_slide.notes_text_frame.text = slide_data["notes"]

    prs.save(str(out_path))
    return str(out_path)


def build_deck(
    deck_json_path: str | Path,
    output_dir: str | Path | None = None,
    export_pptx: bool = False,
) -> dict[str, Any]:
    """Load deck.json, lint it against FI rules, and write index.html + DECK.md."""
    src = Path(deck_json_path).resolve()
    deck_data = json.loads(src.read_text(encoding="utf-8"))
    out_dir = Path(output_dir).resolve() if output_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    lint_report = lint_deck(deck_data)
    html_out = out_dir / "index.html"
    md_out = out_dir / "DECK.md"

    html_out.write_text(render_html(deck_data), encoding="utf-8")
    md_out.write_text(render_markdown(deck_data), encoding="utf-8")

    pptx_out = None
    pptx_note = None
    if export_pptx:
        pptx_out = _export_optional_pptx(deck_data, out_dir / "DECK.pptx")
        if pptx_out is None:
            pptx_note = (
                "Optional dependency 'python-pptx' not installed. Install via "
                "'pip install python-pptx' or open index.html and click 'Export PDF'."
            )

    return {
        "source": str(src),
        "htmlPath": str(html_out),
        "markdownPath": str(md_out),
        "pptxPath": pptx_out,
        "pptxNote": pptx_note,
        "lint": lint_report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build interactive 16:9 HTML & Marp Markdown pitch deck from deck.json"
    )
    parser.add_argument("deck_json", help="Path to pitch-deck/deck.json")
    parser.add_argument("--out", help="Output directory (defaults to deck.json parent)")
    parser.add_argument(
        "--pptx", action="store_true", help="Also export DECK.pptx if python-pptx is available"
    )
    parser.add_argument(
        "--lint-only", action="store_true", help="Lint without writing output files"
    )
    args = parser.parse_args()

    src = Path(args.deck_json)
    if not src.exists():
        print(json.dumps({"error": f"File not found: {src}"}))
        return 1

    if args.lint_only:
        data = json.loads(src.read_text(encoding="utf-8"))
        print(json.dumps(lint_deck(data), indent=2))
        return 0

    result = build_deck(src, args.out, export_pptx=args.pptx)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
