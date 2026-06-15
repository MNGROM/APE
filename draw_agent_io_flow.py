"""Draw the four-agent input/output flow as an SVG.

This script is documentation-only. It does not call the LLM, read run logs, or
modify prompts. Run it from the repository root:

    python draw_agent_io_flow.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import textwrap


OUT = Path(__file__).with_name("agent_io_flow.svg")
WIDTH = 1800
HEIGHT = 980


AGENTS = [
    {
        "title": "1. failure_analysis",
        "system": "prompt_workspace/failure_analysis.md",
        "code": "analysis/failure_analysis.py::analyze_failures",
        "input_file": "iteration_NNN/failure_analysis_input.json",
        "input": [
            "requirements[]",
            "predictions[]",
            "ground_truths[]",
            "failure_types.guide",
            "failure_types.by_case[]",
        ],
        "output_file": "iteration_NNN/failure_analysis_output.json",
        "output": [
            "error_patterns",
            "error_patterns[].possible_causes",
        ],
    },
    {
        "title": "2. error_localization",
        "system": "prompt_workspace/error_localization.md",
        "code": "analysis/error_localization.py::localize_errors",
        "input_file": "iteration_NNN/error_localization_input.json",
        "input": [
            "current_prompt_sections",
            "failure_analysis",
        ],
        "output_file": "iteration_NNN/error_localization_output.json",
        "output": [
            "section_diagnoses",
        ],
    },
    {
        "title": "3. prompt_editor",
        "system": "prompt_workspace/prompt_editor.md",
        "code": "analysis/prompt_editor.py::propose_prompt_revision",
        "input_file": "iteration_NNN/prompt_edit_input.json",
        "input": [
            "current_prompt_sections",
            "failure_analysis",
            "error_localization",
        ],
        "output_file": "iteration_NNN/prompt_edit_output.json",
        "output": [
            "revision_plan",
        ],
    },
    {
        "title": "4. prompt_rewriter",
        "system": "prompt_workspace/prompt_rewriter.md",
        "code": "analysis/prompt_rewriter.py::rewrite_prompt",
        "input_file": "iteration_NNN/prompt_rewrite_input.json",
        "input": [
            "current_prompt",
            "revision_plan",
        ],
        "output_file": "iteration_NNN/prompt_rewrite_output.json",
        "output": [
            "candidate_prompt",
        ],
    },
]


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def text_block(x: int, y: int, lines: list[str], *, size: int = 20, color: str = "#172033") -> str:
    parts = []
    for index, line in enumerate(lines):
        parts.append(
            f'<text x="{x}" y="{y + index * (size + 8)}" '
            f'font-family="Segoe UI, Arial, sans-serif" font-size="{size}" fill="{color}">{escape(line)}</text>'
        )
    return "\n".join(parts)


def rounded_rect(x: int, y: int, w: int, h: int, *, fill: str, stroke: str = "#253047") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="#253047" stroke-width="3" marker-end="url(#arrow)"/>'
    )


def agent_box(agent: dict[str, object], x: int, y: int) -> str:
    w = 385
    h = 760
    title = str(agent["title"])
    system = str(agent["system"])
    code = str(agent["code"])
    input_file = str(agent["input_file"])
    output_file = str(agent["output_file"])
    input_items = [str(item) for item in agent["input"]]
    output_items = [str(item) for item in agent["output"]]

    parts = [rounded_rect(x, y, w, h, fill="#f8fafc")]
    parts.append(rounded_rect(x + 18, y + 18, w - 36, 54, fill="#e8f2ff", stroke="#8ab4f8"))
    parts.append(text_block(x + 34, y + 54, [title], size=24, color="#0b376d"))

    cy = y + 105
    sections = [
        ("System prompt", [system]),
        ("Code call", wrap(code, 34)),
        ("User input file", wrap(input_file, 34)),
        ("User payload", [f"- {item}" for item in input_items]),
        ("Output file", wrap(output_file, 34)),
        ("Parsed output", [f"- {item}" for item in output_items]),
    ]
    for label, lines in sections:
        parts.append(text_block(x + 24, cy, [label], size=17, color="#5f2434"))
        cy += 28
        parts.append(text_block(x + 36, cy, lines, size=16, color="#172033"))
        cy += max(46, len(lines) * 24 + 24)
    return "\n".join(parts)


def main() -> None:
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#253047"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text_block(36, 54, ["APE four-agent prompt evolution I/O flow"], size=30, color="#172033"),
        text_block(
            36,
            90,
            ["The top line shows data dependency. Each box shows system prompt, user payload, and parsed output."],
            size=18,
            color="#4b5563",
        ),
    ]

    xs = [36, 470, 904, 1338]
    y = 145
    for agent, x in zip(AGENTS, xs):
        svg.append(agent_box(agent, x, y))

    mid_y = y + 384
    for x in xs[:-1]:
        svg.append(arrow(x + 385, mid_y, x + 434, mid_y))

    svg.append(text_block(75, 940, ["Generated by draw_agent_io_flow.py"], size=16, color="#64748b"))
    svg.append("</svg>")
    OUT.write_text("\n".join(svg), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
