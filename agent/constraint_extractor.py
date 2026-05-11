"""
agent/constraint_extractor.py
LLM-based constraint extraction with regex fallback.
Same return shape as before, plus max_duration.
"""

import os
import re
import json
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from groq import Groq

try:
    _api_key = os.environ.get("GROQ_API_KEY", "")
    if not _api_key:
        raise ValueError("GROQ_API_KEY not set")
    _client = OpenAI(
        api_key=_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    HAS_LLM = True
except Exception as e:
    print(f"[constraint_extractor] LLM disabled: {e}")
    _client = None
    HAS_LLM = False


# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM = """You are a constraint extractor for an SHL assessment recommendation system.

Given a conversation, extract hiring constraints and return ONLY a JSON object with these keys:

{
  "role": "<job title as a short phrase, or null>",
  "skills": ["<skill1>", "<skill2>"],
  "seniority": "<entry level | junior | mid-level | senior | manager | executive | graduate | null>",
  "personality_required": <true | false>,
  "max_duration": <integer minutes or null>,
  "comparison_targets": ["<assessment1>", "<assessment2>"]
}

Rules:
- Extract role from phrases like "hiring a Java developer", "for a data scientist role"
- Skills: technical (Java, Python, SQL, Excel, C++) AND soft (communication, leadership, problem solving)
- personality_required = true if user mentions personality, behavioural, culture fit, soft skills, OPQ, MQ
- max_duration: extract from "under 30 minutes", "no more than 20 min", "short test", etc.
  "short" = 20, "quick" = 15, "long" = null (don't guess)
- comparison_targets: only fill when user explicitly asks to compare named assessments
- Return ONLY valid JSON. No explanation, no markdown, no code fences.
"""


# ── LLM extraction ────────────────────────────────────────────────────────────

def _extract_with_llm(messages: list) -> Optional[dict]:

    if not HAS_LLM or _client is None:
        return None

    try:
        conversation = "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in messages
        )

        response = _client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM
                },
                {
                    "role": "user",
                    "content": conversation
                }
            ],
            temperature=0,
            max_tokens=200,
        )

        content = response.choices[0].message.content

        if not content:
            return None

        raw = content.strip()

        # Remove accidental markdown fences
        raw = re.sub(
            r"^```json|^```|```$",
            "",
            raw,
            flags=re.MULTILINE
        ).strip()

        data = json.loads(raw)

        return {
            "role":                 data.get("role"),
            "skills":               data.get("skills", []),
            "seniority":            data.get("seniority"),
            "personality_required": bool(data.get("personality_required", False)),
            "max_duration":         data.get("max_duration"),
            "comparison_targets":   data.get("comparison_targets", []),
        }

    except Exception as e:
        print(f"[constraint_extractor] LLM error: {e}")
        return None


# ── Keyword / regex fallback ──────────────────────────────────────────────────

KNOWN_SKILLS = [
    # Technical
    "java", "python", "sql", "javascript", "typescript", "c++", "c#",
    "react", "angular", "node", "excel", "r ", "scala", "go",
    "data analysis", "machine learning", "software development",
    "devops", "cloud", "aws", "azure",
    # Soft
    "communication", "leadership", "problem solving", "teamwork",
    "sales", "customer service", "negotiation", "presentation",
    "critical thinking", "attention to detail",
]

SENIORITY_LEVELS = [
    "entry level", "entry-level", "junior", "mid-level", "mid level",
    "senior", "manager", "executive", "graduate", "intern",
]

ROLE_PATTERNS = [
    r"([\w\s]+?\s(?:developer|engineer|manager|analyst|designer|scientist|"
    r"consultant|architect|specialist|lead|director|officer|executive|intern))",
]

PERSONALITY_KEYWORDS = [
    "personality", "behavioral", "behavioural", "soft skills",
    "culture fit", "opq", " mq ", "motivation",
]

DURATION_PATTERNS = [
    (r"under\s+(\d+)\s*min",        lambda m: int(m.group(1))),
    (r"less than\s+(\d+)\s*min",    lambda m: int(m.group(1))),
    (r"no more than\s+(\d+)\s*min", lambda m: int(m.group(1))),
    (r"(\d+)\s*min(?:utes?)?\s*(?:max|maximum|or less|limit)", lambda m: int(m.group(1))),
    (r"\bshort\b",                  lambda m: 20),
    (r"\bquick\b",                  lambda m: 15),
]


def _extract_with_keywords(messages: list) -> dict:
    conversation = " ".join(m["content"] for m in messages).lower()

    constraints = {
        "role":                 None,
        "skills":               [],
        "seniority":            None,
        "personality_required": False,
        "max_duration":         None,
        "comparison_targets":   [],
    }

    # Skills
    for skill in KNOWN_SKILLS:
        if skill in conversation:
            constraints["skills"].append(skill.strip())

    # Seniority
    for level in SENIORITY_LEVELS:
        if level in conversation:
            constraints["seniority"] = level
            break

    # Personality
    if any(k in conversation for k in PERSONALITY_KEYWORDS):
        constraints["personality_required"] = True

    # Role
    for pattern in ROLE_PATTERNS:
        match = re.search(pattern, conversation)
        if match:
            constraints["role"] = match.group(1).strip()
            break

    # Duration
    for pattern, extractor in DURATION_PATTERNS:
        match = re.search(pattern, conversation)
        if match:
            constraints["max_duration"] = extractor(match)
            break

    # Comparison targets
    compare_match = re.search(r"compare (.+?) and (.+?)(?:\?|$)", conversation)
    if compare_match:
        constraints["comparison_targets"] = [
            compare_match.group(1).strip(),
            compare_match.group(2).strip(),
        ]

    return constraints


# ── Public API ────────────────────────────────────────────────────────────────

def extract_constraints(messages: list) -> dict:
    result = _extract_with_llm(messages)
    if result:
        print(f"[constraint_extractor] LLM → {result}")
        return result

    result = _extract_with_keywords(messages)
    print(f"[constraint_extractor] Keyword fallback → {result}")
    return result


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        [{"role": "user", "content": "Need assessment for mid-level Java developer with communication skills and personality testing"}],
        [{"role": "user", "content": "Hiring a senior data scientist with Python and SQL, under 30 minutes please"}],
        [{"role": "user", "content": "I'm looking for tests for a graduate sales executive role, culture fit is important"}],
        [{"role": "user", "content": "Compare OPQ32 and MQ for a leadership role"}],
        [{"role": "user", "content": "Something quick for a DevOps engineer, no more than 15 min"}],
    ]
    for msgs in test_cases:
        print(f"\nInput: {msgs[0]['content']}")
        print(f"Output: {extract_constraints(msgs)}")