"""
Anti-spoonfeeding safety layer
- Detects "solution leakage" (full solutions, final answers, full code dumps).
- Enforces hint policy (max 3 hints, Socratic style).
- Can sanitize/truncate model output to comply.

This is heuristic-based by design (fast + simple + works for MVP).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re


@dataclass
class PolicyConfig:
    # hint constraints
    hint_limit: int = 3
    max_hint_chars: int = 900  # keep hints short

    # allow showing code snippets in hints (very small only)
    allow_code_in_hints: bool = True
    max_code_chars: int = 350

    # if model output contains strong "final answer" patterns, block/transform
    block_final_answers_in_hint_mode: bool = True

    # remove long step-by-step solutions in hint mode
    block_step_by_step_in_hint_mode: bool = True

    # extra strict mode (exam mode)
    exam_mode_definitions_only: bool = False

    # aggressive sanitization if leakage detected
    replace_on_violation: bool = True


@dataclass
class PolicyResult:
    ok: bool
    text: str
    reasons: List[str]
    truncated: bool = False
    code_removed: bool = False
    violation: bool = False


_FINAL_PATTERNS = [
    r"\bfinal answer\b",
    r"\bthe answer is\b",
    r"\bhere(’|')?s the solution\b",
    r"\bcomplete solution\b",
    r"\bfull solution\b",
    r"\bhere is the full\b",
    r"\bfull code\b",
    r"\bcomplete code\b",
    r"\bentire code\b",
    r"\bhere's the code\b",
    r"\bthis will solve\b",
]

# Step-by-step / full derivation patterns
_STEP_PATTERNS = [
    r"^\s*step\s*\d+\s*[:.)-]",
    r"^\s*\d+\s*[.)-]\s+",  # numbered list
    r"\bfirst,\b.*\bsecond,\b.*\bthird,\b",
    r"\btherefore\b.*\bthus\b",
    r"\bproof\b.*\bq\.?e\.?d\.?\b",
]

# Code block patterns (triple backticks) + inline code fences
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`[^`]{20,}`")  # long inline code


def _contains_any_pattern(text: str, patterns: List[str], multiline: bool = True) -> bool:
    flags = re.IGNORECASE | (re.MULTILINE if multiline else 0)
    for p in patterns:
        if re.search(p, text, flags=flags):
            return True
    return False


def detect_solution_leakage(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if _contains_any_pattern(text, _FINAL_PATTERNS):
        reasons.append("final_answer_language")
    if _contains_any_pattern(text, _STEP_PATTERNS):
        reasons.append("step_by_step_solution")
    if _CODE_BLOCK_RE.search(text):
        reasons.append("code_block_present")
    # Very long response often indicates full solution dumping
    if len(text) > 2000:
        reasons.append("too_long")
    return (len(reasons) > 0), reasons


def _strip_code_blocks(text: str) -> Tuple[str, bool]:
    new = _CODE_BLOCK_RE.sub("", text)
    # also remove very long inline code
    new2 = _INLINE_CODE_RE.sub("`[code omitted]`", new)
    return new2, (new2 != text)


def _shrink_code_blocks(text: str, max_code_chars: int) -> Tuple[str, bool]:
    """
    Keep code blocks but truncate each to max_code_chars.
    """
    removed_any = False

    def _repl(m):
        nonlocal removed_any
        block = m.group(0)
        # Preserve fence header
        lines = block.splitlines()
        if len(lines) <= 2:
            return block
        header = lines[0]
        footer = lines[-1]
        body = "\n".join(lines[1:-1])
        if len(body) > max_code_chars:
            removed_any = True
            body = body[:max_code_chars].rstrip() + "\n# ...snippet truncated..."
        return "\n".join([header, body, footer])

    out = _CODE_BLOCK_RE.sub(_repl, text)
    return out, removed_any


def _truncate_text(text: str, max_chars: int) -> Tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    # try cut at sentence boundary
    cut = text[:max_chars]
    m = re.search(r"(.+[.!?])\s", cut[::-1])
    # if we can't find boundary, hard cut
    return cut.rstrip() + "…", True


def build_safe_hint_fallback(hint_no: int, hint_limit: int, topic: Optional[str] = None) -> str:
    """
    Used when the model output violates policy badly.
    """
    t = f" about **{topic}**" if topic else ""
    if hint_no >= hint_limit:
        return (
            f"You’ve used all {hint_limit} hints{t}. "
            "Try attempting the MCQs again, and tell me which option confused you."
        )
    return (
        f"I can’t give a full solution{t}, but I can guide you.\n\n"
        "Here’s a hint: identify the *key idea* and apply it to a small example.\n"
        "Micro-question: What is the *first step* you would take, and why?"
    )


def enforce_hint_policy(
    model_text: str,
    cfg: PolicyConfig,
    *,
    hint_no: int,
    topic: Optional[str] = None,
) -> PolicyResult:
    """
    Enforce anti-spoonfeeding policy on LLM output for HINT mode.
    """
    reasons: List[str] = []
    violation, leak_reasons = detect_solution_leakage(model_text)
    reasons.extend(leak_reasons)

    text = model_text
    truncated = False
    code_removed = False

    if cfg.exam_mode_definitions_only:
        # Very strict: only allow definitions / short conceptual notes
        # Remove code blocks and truncate aggressively.
        text, removed = _strip_code_blocks(text)
        code_removed = code_removed or removed
        text, was_trunc = _truncate_text(text, min(cfg.max_hint_chars, 500))
        truncated = truncated or was_trunc
        # Remove "answer is" style phrases
        text = re.sub(r"(?i)\b(final answer|the answer is|solution)\b.*", "", text).strip()
        if not text:
            text = build_safe_hint_fallback(hint_no, cfg.hint_limit, topic)
            return PolicyResult(ok=True, text=text, reasons=["exam_mode_sanitized"], truncated=True)
        return PolicyResult(ok=True, text=text, reasons=["exam_mode_sanitized"], truncated=truncated, code_removed=code_removed)

    # Hint mode: block full solution language
    if cfg.block_final_answers_in_hint_mode and _contains_any_pattern(text, _FINAL_PATTERNS):
        violation = True

    # Handle code
    if _CODE_BLOCK_RE.search(text):
        if not cfg.allow_code_in_hints:
            text, removed = _strip_code_blocks(text)
            code_removed = code_removed or removed
        else:
            text, shrunk = _shrink_code_blocks(text, cfg.max_code_chars)
            code_removed = code_removed or shrunk

    # Block step-by-step dumps by stripping numbered steps beyond 2-3 lines
    if cfg.block_step_by_step_in_hint_mode and _contains_any_pattern(text, _STEP_PATTERNS):
        # Keep only first ~2 paragraphs, then force micro-question
        parts = re.split(r"\n\s*\n", text)
        text = "\n\n".join(parts[:2]).strip()
        violation = True
        reasons.append("step_by_step_trimmed")

    # Truncate hint length
    text, was_trunc = _truncate_text(text.strip(), cfg.max_hint_chars)
    truncated = truncated or was_trunc

    # Ensure it ends with a micro-question style prompt
    if not re.search(r"[?]\s*$", text):
        text = text.rstrip() + "\n\nMicro-question: What do you think is the next step?"

    if violation and cfg.replace_on_violation:
        # Replace with a safe fallback if the text is still too revealing
        # (e.g., contains "final answer" even after edits)
        if _contains_any_pattern(text, _FINAL_PATTERNS) or len(text) > cfg.max_hint_chars:
            text = build_safe_hint_fallback(hint_no, cfg.hint_limit, topic)
            return PolicyResult(
                ok=True,
                text=text,
                reasons=reasons + ["replaced_due_to_violation"],
                truncated=True,
                code_removed=code_removed,
                violation=True,
            )

    return PolicyResult(
        ok=True,
        text=text,
        reasons=reasons,
        truncated=truncated,
        code_removed=code_removed,
        violation=violation,
    )


def enforce_explanation_policy(
    model_text: str,
    cfg: PolicyConfig,
) -> PolicyResult:
    """
    For FULL NOTES / EXPLANATION mode (unlocked when score < threshold).
    We still keep it readable and avoid dumping irrelevant massive content.
    """
    reasons: List[str] = []
    text = model_text.strip()
    truncated = False

    # Even in explanation mode, avoid absurdly long dumps
    text, was_trunc = _truncate_text(text, max(3000, cfg.max_hint_chars * 3))
    truncated = truncated or was_trunc

    # Keep code blocks but shrink if huge
    if _CODE_BLOCK_RE.search(text):
        text, shrunk = _shrink_code_blocks(text, max(cfg.max_code_chars * 3, 1200))
        if shrunk:
            reasons.append("code_blocks_truncated")

    return PolicyResult(ok=True, text=text, reasons=reasons, truncated=truncated, violation=False)


def can_provide_hint(hint_no: int, cfg: PolicyConfig) -> bool:
    return 1 <= hint_no <= cfg.hint_limit

