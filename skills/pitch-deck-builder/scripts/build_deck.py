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

    deck_mode = str(meta.get("deckMode", "problem-solution")).lower()
    if deck_mode == "teaser":
        if len(slides) < 3 or len(slides) > 5:
            issues.append(
                {
                    "slide": "deck",
                    "severity": "warning",
                    "rule": "fi-slide-count",
                    "message": f"Teaser deck has {len(slides)} slides; VC Lab recommends 3–5 tight slides.",
                }
            )
    elif len(slides) < 8 or len(slides) > 15:
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


def _format_num(val: float, prefix: str = "", suffix: str = "") -> str:
    if abs(val) >= 1_000_000:
        num = f"{val / 1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        num = f"{val / 1_000:.1f}K" if val % 1000 != 0 else f"{int(val // 1000)}K"
    else:
        num = f"{int(val)}" if float(val).is_integer() else f"{val:.1f}"
    return f"{prefix}{num}{suffix}"


def _render_svg_chart(slide: dict[str, Any], kind: str) -> str:
    """Render a zero-dependency responsive inline SVG line or bar chart."""
    series = slide.get("series") or []
    prefix = str(slide.get("unitPrefix", ""))
    suffix = str(slide.get("unitSuffix", ""))
    title = _format_badges_html(str(slide.get("chartTitle", "")))
    if not series:
        return '<div class="visual-card"><p>No chart series data provided.</p></div>'

    w, h = 860, 320
    pad_l, pad_r, pad_t, pad_b = 64, 36, 36, 48
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b
    vals = [float(p.get("value", 0)) for p in series]
    max_v = max(max(vals), 1.0) * 1.15
    n = len(series)

    # Horizontal gridlines (4 steps)
    grid_parts: list[str] = []
    for step in range(5):
        y = pad_t + plot_h - (plot_h * step / 4.0)
        gv = max_v * step / 4.0
        grid_parts.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" '
            f'stroke="var(--border)" stroke-width="1" stroke-dasharray="4 4"/>'
            f'<text x="{pad_l - 10}" y="{y + 4:.1f}" text-anchor="end" fill="var(--muted)" '
            f'font-size="12" font-family="var(--font-mono)">{html.escape(_format_num(gv, prefix, suffix))}</text>'
        )

    chart_parts: list[str] = []
    if kind == "chart-bar":
        slot_w = plot_w / max(n, 1)
        bar_w = min(64.0, slot_w * 0.56)
        for i, p in enumerate(series):
            v = float(p.get("value", 0))
            lbl = html.escape(str(p.get("label", "")))
            cx = pad_l + slot_w * (i + 0.5)
            bh = (v / max_v) * plot_h
            bx = cx - bar_w / 2.0
            by = pad_t + plot_h - bh
            v_str = html.escape(_format_num(v, prefix, suffix))
            chart_parts.append(
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{max(bh, 2):.1f}" '
                f'rx="6" fill="var(--accent)" opacity="0.9"/>'
                f'<text x="{cx:.1f}" y="{by - 8:.1f}" text-anchor="middle" fill="var(--text)" '
                f'font-size="13" font-weight="700">{v_str}</text>'
                f'<text x="{cx:.1f}" y="{h - 14}" text-anchor="middle" fill="var(--muted)" '
                f'font-size="13">{lbl}</text>'
            )
    else:
        coords: list[tuple[float, float, str, float]] = []
        for i, p in enumerate(series):
            v = float(p.get("value", 0))
            lbl = str(p.get("label", ""))
            x = pad_l + (plot_w * i / max(n - 1, 1)) if n > 1 else pad_l + plot_w / 2.0
            y = pad_t + plot_h - (v / max_v) * plot_h
            coords.append((x, y, lbl, v))

        poly_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in coords)
        area_pts = (
            f"{coords[0][0]:.1f},{pad_t + plot_h:.1f} "
            + poly_pts
            + f" {coords[-1][0]:.1f},{pad_t + plot_h:.1f}"
        )
        chart_parts.append(
            '<defs><linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%" stop-color="var(--accent)" stop-opacity="0.32"/>'
            '<stop offset="100%" stop-color="var(--accent)" stop-opacity="0.02"/>'
            "</linearGradient></defs>"
            f'<polygon points="{area_pts}" fill="url(#areaGrad)"/>'
            f'<polyline points="{poly_pts}" fill="none" stroke="var(--accent)" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for x, y, lbl, v in coords:
            v_str = html.escape(_format_num(v, prefix, suffix))
            chart_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="var(--bg)" stroke="var(--accent)" stroke-width="3.5"/>'
                f'<text x="{x:.1f}" y="{y - 12:.1f}" text-anchor="middle" fill="var(--text)" '
                f'font-size="13" font-weight="700">{v_str}</text>'
                f'<text x="{x:.1f}" y="{h - 14}" text-anchor="middle" fill="var(--muted)" '
                f'font-size="13">{html.escape(lbl)}</text>'
            )

    title_html = (
        f'<div style="font-size:14px;font-weight:700;color:var(--muted);">{title}</div>'
        if title
        else ""
    )
    return (
        f'<div class="visual-card">{title_html}'
        f'<svg class="visual-svg" viewBox="0 0 {w} {h}" role="img" aria-label="Chart">'
        f'{"".join(grid_parts)}{"".join(chart_parts)}</svg></div>'
    )


def _render_svg_quadrant(slide: dict[str, Any]) -> str:
    """Render a classic VC 2x2 competitive positioning SVG quadrant."""
    w, h = 860, 340
    pad_x, pad_y = 140, 40
    box_w, box_h = w - 2 * pad_x, h - 2 * pad_y
    mid_x, mid_y = pad_x + box_w / 2.0, pad_y + box_h / 2.0

    x_left = html.escape(str(slide.get("xAxisLeft", "Low Speed / Legacy")))
    x_right = html.escape(str(slide.get("xAxisRight", "High Speed / Automated")))
    y_bottom = html.escape(str(slide.get("yAxisBottom", "Low Margin / Generic")))
    y_top = html.escape(str(slide.get("yAxisTop", "High ROI & Ethical Moat")))

    parts = [
        f'<rect x="{pad_x}" y="{pad_y}" width="{box_w}" height="{box_h}" rx="10" fill="rgba(255,255,255,0.02)" stroke="var(--border)" stroke-width="1.5"/>',
        f'<rect x="{mid_x}" y="{pad_y}" width="{box_w / 2.0}" height="{box_h / 2.0}" fill="var(--accent)" opacity="0.08"/>',
        f'<line x1="{mid_x}" y1="{pad_y}" x2="{mid_x}" y2="{pad_y + box_h}" stroke="var(--border)" stroke-width="2" stroke-dasharray="6 5"/>',
        f'<line x1="{pad_x}" y1="{mid_y}" x2="{pad_x + box_w}" y2="{mid_y}" stroke="var(--border)" stroke-width="2" stroke-dasharray="6 5"/>',
        f'<text x="{mid_x}" y="{pad_y - 12}" text-anchor="middle" fill="var(--accent)" font-size="13" font-weight="700">{y_top}</text>',
        f'<text x="{mid_x}" y="{pad_y + box_h + 24}" text-anchor="middle" fill="var(--muted)" font-size="12">{y_bottom}</text>',
        f'<text x="{pad_x - 14}" y="{mid_y + 4}" text-anchor="end" fill="var(--muted)" font-size="12">{x_left}</text>',
        f'<text x="{pad_x + box_w + 14}" y="{mid_y + 4}" text-anchor="start" fill="var(--accent)" font-size="13" font-weight="700">{x_right}</text>',
    ]

    for pt in slide.get("points", []):
        px = max(5.0, min(95.0, float(pt.get("x", 50))))
        py = max(5.0, min(95.0, float(pt.get("y", 50))))
        cx = pad_x + (px / 100.0) * box_w
        cy = pad_y + box_h - (py / 100.0) * box_h
        name = html.escape(str(pt.get("name", "")))
        hi = bool(pt.get("highlight", False))
        if hi:
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="18" fill="var(--accent)" opacity="0.22"/>'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="var(--accent)" stroke="var(--text)" stroke-width="2.5"/>'
                f'<text x="{cx:.1f}" y="{cy - 18:.1f}" text-anchor="middle" fill="var(--text)" font-size="14" font-weight="800">{name}</text>'
            )
        else:
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="var(--muted)" opacity="0.8"/>'
                f'<text x="{cx:.1f}" y="{cy + 20:.1f}" text-anchor="middle" fill="var(--muted)" font-size="12">{name}</text>'
            )

    return (
        f'<div class="visual-card"><svg class="visual-svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="Competitive 2x2 Quadrant">{"".join(parts)}</svg></div>'
    )


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

    elif stype in ("chart-line", "chart-bar"):
        body_parts.append(_render_svg_chart(slide, stype))

    elif stype == "quadrant-2x2":
        body_parts.append(_render_svg_quadrant(slide))

    elif stype == "product-frame":
        url_label = html.escape(str(slide.get("appUrl", "app.yourcompany.com")))
        img_path = str(slide.get("imagePath", "")).strip()
        if img_path:
            frame_inner = f'<img src="{html.escape(img_path, quote=True)}" alt="{html.escape(str(slide.get("caption", "Product screenshot")), quote=True)}"/>'
        else:
            steps = slide.get("mockupSteps") or [
                "1. Connect data source in 2 minutes",
                "2. Secret Sauce engine automates core job",
                "3. Instant verified ROI output",
            ]
            frame_inner = "".join(
                f'<div class="wireframe-step">{_format_badges_html(str(st))}</div>'
                for st in steps
            )
        highlights = "".join(
            f"<li>{_format_badges_html(str(h))}</li>" for h in slide.get("highlights", [])
        )
        hl_title = html.escape(str(slide.get("highlightsTitle", "Why Customers Switch")))
        body_parts.append(
            f'<div class="product-grid">'
            f'  <div class="browser-frame">'
            f'    <div class="browser-bar"><span class="browser-dot r"></span><span class="browser-dot y"></span>'
            f'      <span class="browser-dot g"></span><span class="browser-url">{url_label}</span></div>'
            f'    <div class="browser-body">{frame_inner}</div>'
            f'  </div>'
            f'  <div class="col-card"><h3>{hl_title}</h3><ul>{highlights}</ul></div>'
            f'</div>'
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
        elif stype in ("chart-line", "chart-bar"):
            prefix = str(slide.get("unitPrefix", ""))
            suffix = str(slide.get("unitSuffix", ""))
            if slide.get("chartTitle"):
                lines.append(f"### {slide['chartTitle']}")
            lines.append("| Period | Value |")
            lines.append("| :--- | ---: |")
            for pt in slide.get("series", []):
                lines.append(
                    f"| {pt.get('label', '')} | {_format_num(float(pt.get('value', 0)), prefix, suffix)} |"
                )
        elif stype == "quadrant-2x2":
            lines.append(
                f"**Axes:** X = `{slide.get('xAxisLeft', '')}` -> `{slide.get('xAxisRight', '')}` | "
                f"Y = `{slide.get('yAxisBottom', '')}` -> `{slide.get('yAxisTop', '')}`"
            )
            lines.append("")
            lines.append("| Player | X (0-100) | Y (0-100) |")
            lines.append("| :--- | ---: | ---: |")
            for pt in slide.get("points", []):
                mark = " ★" if pt.get("highlight") else ""
                lines.append(f"| **{pt.get('name', '')}{mark}** | {pt.get('x', 50)} | {pt.get('y', 50)} |")
        elif stype == "product-frame":
            if slide.get("imagePath"):
                lines.append(f"![{slide.get('caption', 'Product')}]({slide['imagePath']})")
                lines.append("")
            for st in slide.get("mockupSteps", []):
                lines.append(f"- {st}")
            if slide.get("highlights"):
                lines.append("")
                lines.append(f"### {slide.get('highlightsTitle', 'Highlights')}")
                for hl in slide.get("highlights", []):
                    lines.append(f"- {hl}")
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
        elif stype in ("chart-line", "chart-bar"):
            prefix = str(slide_data.get("unitPrefix", ""))
            suffix = str(slide_data.get("unitSuffix", ""))
            for pt in slide_data.get("series", []):
                body_lines.append(
                    f"• {pt.get('label', '')}: {_format_num(float(pt.get('value', 0)), prefix, suffix)}"
                )
        elif stype == "quadrant-2x2":
            for pt in slide_data.get("points", []):
                body_lines.append(
                    f"• {pt.get('name', '')}: X={pt.get('x', 50)}, Y={pt.get('y', 50)}"
                )
        elif stype == "product-frame":
            body_lines.extend(f"• {st}" for st in slide_data.get("mockupSteps", []))
            body_lines.extend(f"- {hl}" for hl in slide_data.get("highlights", []))
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


def export_design_briefs(
    deck_json_path: str | Path,
    output_dir: str | Path | None = None,
    target: str = "both",
) -> dict[str, Any]:
    """Generate structured Canva & Figma Slides production briefs + W3C Design Tokens."""
    src = Path(deck_json_path).resolve()
    deck_data = json.loads(src.read_text(encoding="utf-8"))
    out_dir = Path(output_dir).resolve() if output_dir else (src.parent / "design-handoff")
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = deck_data.get("meta", {})
    company = meta.get("companyName", "Startup")
    deck_mode = meta.get("deckMode", "problem-solution")
    raw_theme = deck_data.get("theme", {})
    preset = raw_theme.get("preset", "midnight-emerald")
    theme = {**THEME_PRESETS.get(preset, THEME_PRESETS["midnight-emerald"]), **raw_theme}
    slides = deck_data.get("slides", [])
    lint_report = lint_deck(deck_data)

    def _slide_summary_lines(slide: dict[str, Any], idx: int) -> list[str]:
        stype = slide.get("type", "bullets")
        out = [
            f"### Slide {idx}: {slide.get('headline', '')}",
            f"- **ID / Layout Type:** `{slide.get('id', f'slide-{idx}')}` (`{stype}`)",
            f"- **Kicker:** `{slide.get('kicker', '')}`",
        ]
        if stype == "cover":
            out.append(f"- **Subheadline:** {_strip_tags(str(slide.get('subheadline', '')))}")
            out.append(f"- **Footer:** {slide.get('footer', '')}")
        elif stype == "bullets":
            for b in slide.get("bullets", []):
                if isinstance(b, dict):
                    out.append(f"- **Bullet — {b.get('label', '')}:** {_strip_tags(str(b.get('text', '')))}")
                else:
                    out.append(f"- **Bullet:** {_strip_tags(str(b))}")
        elif stype == "metrics":
            for m in slide.get("metrics", []):
                out.append(f"- **KPI Card:** `{m.get('value', '')}` — {_strip_tags(str(m.get('label', '')))}")
        elif stype == "two-column":
            out.append(f"- **Left Column ({slide.get('leftTitle', '')}):** " + " | ".join(_strip_tags(str(x)) for x in slide.get("leftItems", [])))
            out.append(f"- **Right Column ({slide.get('rightTitle', '')}):** " + " | ".join(_strip_tags(str(x)) for x in slide.get("rightItems", [])))
        elif stype == "comparison":
            out.append(f"- **Table Columns:** {', '.join(str(h) for h in slide.get('headers', []))}")
            for row in slide.get("rows", []):
                out.append(f"  - {' | '.join(_strip_tags(str(c)) for c in row)}")
        elif stype in ("chart-line", "chart-bar"):
            prefix = str(slide.get("unitPrefix", ""))
            suffix = str(slide.get("unitSuffix", ""))
            pts = ", ".join(
                f"{p.get('label', '')}={_format_num(float(p.get('value', 0)), prefix, suffix)}"
                for p in slide.get("series", [])
            )
            out.append(f"- **Chart ({stype}):** {slide.get('chartTitle', '')} -> `{pts}`")
        elif stype == "quadrant-2x2":
            out.append(
                f"- **2x2 Axes:** X (`{slide.get('xAxisLeft', '')}` -> `{slide.get('xAxisRight', '')}`), "
                f"Y (`{slide.get('yAxisBottom', '')}` -> `{slide.get('yAxisTop', '')}`)"
            )
            for p in slide.get("points", []):
                star = " [HIGHLIGHT]" if p.get("highlight") else ""
                out.append(f"  - `{p.get('name', '')}`: X={p.get('x', 50)}, Y={p.get('y', 50)}{star}")
        elif stype == "product-frame":
            out.append(f"- **Product URL / Screenshot:** `{slide.get('appUrl', '')}` (image: `{slide.get('imagePath', 'wireframe')}`)")
            for st in slide.get("mockupSteps", []):
                out.append(f"  - Step: {_strip_tags(str(st))}")
            for hl in slide.get("highlights", []):
                out.append(f"  - Outcome: {_strip_tags(str(hl))}")
        elif stype == "ask":
            out.append(f"- **Ask:** `{slide.get('askAmount', '')}` ({_strip_tags(str(slide.get('instrument', '')))})")
            allocs = ", ".join(f"{a.get('label', '')}: {a.get('percent', '')}" for a in slide.get("allocations", []))
            out.append(f"- **Use of Funds:** {allocs}")
            for m in slide.get("milestones", []):
                out.append(f"  - Milestone: {_strip_tags(str(m))}")
            if slide.get("impactMetric"):
                out.append(f"- **For-Progress iKPI:** {_strip_tags(str(slide['impactMetric']))}")

        if slide.get("callout"):
            out.append(f"- **Callout Banner:** {_strip_tags(str(slide['callout']))}")
        if slide.get("notes"):
            out.append(f"- **Speaker Notes:** {slide['notes']}")
        out.append("")
        return out

    result: dict[str, Any] = {
        "source": str(src),
        "companyName": company,
        "deckMode": deck_mode,
        "slideCount": len(slides),
        "lintReadinessScore": lint_report["readinessScore"],
        "files": {},
    }

    if target in ("both", "canva"):
        canva_lines = [
            f"# {company} — Canva Presentation Production Brief",
            "",
            "> Generated by Startup Antigravity (`design-studio-canva-figma`) from FI-linted `pitch-deck/deck.json`.",
            "",
            "## Canva MCP Execution Recipe",
            "1. Call `canva_canva` -> `list-brand-kits` to check if the founder already has a Brand Kit.",
            "2. Call `canva_canva` -> `generate-design` (design type: `presentation`, 16:9) or `create-design` using the exact slide copy and hex palette below.",
            "3. Refine individual slide text, KPI cards, and visual hierarchy with the `canva-edit-design` skill (`edit-design`).",
            "4. Run `canva-brand-check` & `canva-design-feedback` to verify contrast, spacing, and FI <=10-word headline discipline.",
            "5. Export investor-ready PDF / PPTX via `get-export-formats` + `export-design`.",
            "",
            "## Brand Palette & Typography",
            f"- **Theme Preset:** `{preset}`",
            f"- **Background:** `{theme['bg']}` | **Card Surface:** `{theme['surface']}` | **Border:** `{theme['border']}`",
            f"- **Primary Text:** `{theme['text']}` | **Muted Text:** `{theme['muted']}`",
            f"- **Primary Accent:** `{theme['accent']}` | **Secondary Accent:** `{theme['accent2']}`",
            "- **Typography:** Clean geometric sans-serif (Inter / Plus Jakarta Sans), bold 42–56pt headlines, 18–22pt body, generous whitespace.",
            "- **Strict FI Copy Rule:** Do NOT add buzzwords or extra paragraphs. Preserve exact linted headlines and max-3-bullet density.",
            "",
            "## Slide-by-Slide Content Specification",
            "",
        ]
        for idx, s in enumerate(slides, start=1):
            canva_lines.extend(_slide_summary_lines(s, idx))
        canva_path = out_dir / "CANVA_DECK_BRIEF.md"
        canva_path.write_text("\n".join(canva_lines), encoding="utf-8")
        result["files"]["canvaBrief"] = str(canva_path)

    if target in ("both", "figma"):
        tokens = {
            "$schema": "https://tr.designtokens.org/format/",
            "meta": {"company": company, "preset": preset, "slideDimensions": {"width": 1920, "height": 1080}},
            "color": {
                "background": {"$type": "color", "$value": theme["bg"]},
                "surface": {"$type": "color", "$value": theme["surface"]},
                "textPrimary": {"$type": "color", "$value": theme["text"]},
                "textMuted": {"$type": "color", "$value": theme["muted"]},
                "accentPrimary": {"$type": "color", "$value": theme["accent"]},
                "accentSecondary": {"$type": "color", "$value": theme["accent2"]},
                "border": {"$type": "color", "$value": theme["border"]},
            },
            "typography": {
                "fontFamily": {"$type": "fontFamily", "$value": "Inter"},
                "kickerSize": {"$type": "dimension", "$value": "16px"},
                "headlineSize": {"$type": "dimension", "$value": "48px"},
                "bodySize": {"$type": "dimension", "$value": "22px"},
                "metricValueSize": {"$type": "dimension", "$value": "56px"},
            },
            "spacing": {
                "slidePaddingX": {"$type": "dimension", "$value": "120px"},
                "slidePaddingY": {"$type": "dimension", "$value": "96px"},
                "cardGap": {"$type": "dimension", "$value": "24px"},
                "cardRadius": {"$type": "dimension", "$value": "16px"},
            },
        }
        tokens_path = out_dir / "FIGMA_TOKENS.json"
        tokens_path.write_text(json.dumps(tokens, indent=2) + "\n", encoding="utf-8")

        figma_lines = [
            f"# {company} — Figma Slides & Design System Production Brief",
            "",
            "> Generated by Startup Antigravity (`design-studio-canva-figma`) from FI-linted `pitch-deck/deck.json`.",
            "",
            "## Figma MCP Execution Recipe",
            "1. Load the mandatory prerequisite skills first: `figma-create-new-file`, `figma-use`, and `figma-use-slides`.",
            "2. Call `figma_figma` -> `create_new_file` to create a new **Figma Slides** file (1920x1080 16:9 canvas).",
            "3. Bind all variables from `FIGMA_TOKENS.json` (`color.*`, `spacing.*`) via `use_figma` so re-theming the entire deck takes 1 click.",
            "4. Build slides incrementally via `use_figma` (using auto-layout frames, reusable KPI card components, and vector paths for `chart-line`/`quadrant-2x2` slides).",
            "5. Visually inspect finished slides with `get_screenshot` to confirm zero text clipping or overlap.",
            "",
            "## Canvas & Token Specs",
            f"- **Slide Frame Size:** `1920 x 1080` (16:9), Padding `120px` horizontal / `96px` vertical",
            f"- **Tokens File:** `{tokens_path.name}` (Preset: `{preset}`)",
            f"- **Colors:** BG `{theme['bg']}`, Surface `{theme['surface']}`, Accent `{theme['accent']}`, Accent2 `{theme['accent2']}`, Text `{theme['text']}`",
            "",
            "## Slide-by-Slide Frame Specification",
            "",
        ]
        for idx, s in enumerate(slides, start=1):
            figma_lines.extend(_slide_summary_lines(s, idx))
        figma_path = out_dir / "FIGMA_SLIDES_BRIEF.md"
        figma_path.write_text("\n".join(figma_lines), encoding="utf-8")
        result["files"]["figmaBrief"] = str(figma_path)
        result["files"]["figmaTokens"] = str(tokens_path)

    return result


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
    parser.add_argument(
        "--design-brief",
        choices=["both", "canva", "figma"],
        help="Generate Canva/Figma production briefs & W3C design tokens into pitch-deck/design-handoff/",
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

    if args.design_brief:
        print(json.dumps(export_design_briefs(src, args.out, target=args.design_brief), indent=2))
        return 0

    result = build_deck(src, args.out, export_pptx=args.pptx)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
