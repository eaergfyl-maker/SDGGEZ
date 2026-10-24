"""Find skills in CV text with keyword rules. Owner: Member 3.

Deterministic: no AI, no network, nothing stored or logged. The text is used in memory and
thrown away. Demo and tests use invented CVs only (the brief forbids real ones).

For every skill in data/skills.json the matcher looks for its `keywords` and `cv_terms`:

  found     the exact phrase appears (any case, plural allowed), e.g. "Zendesk" -> CRM tools.
            The UI ticks these automatically.
  possible  the words of a multi-word phrase all appear close together in any form, e.g.
            "handled complaints from customers" for "complaint handling"; or an exact phrase
            right after a negation ("no experience with SQL") or an intention ("currently
            learning Python", "interested in EV charging"). The UI shows these unticked for the
            person to confirm.

Every result carries the piece of the CV that triggered it, so the person can see why.

Where the AI layer plugs in (Member 3, later): call the model separately, keep only skill ids
that exist in data/skills.json and quotes that literally appear in the redacted text, then add
them as level "possible" with source "ai". Keyword results stay as they are.
"""
import re

MAX_CHARS = 20_000
WINDOW = 6                       # words: how close the words of a phrase must be for "possible"
SNIPPET = 45                     # characters of context on each side of the evidence
NEGATIONS = {"no", "not", "without", "never", "lack", "lacking", "none"}
# wanting or still learning a skill is not having it: "currently learning Python", "interested in EV"
INTENT = {"learning", "interested", "hoping", "hope", "plan", "planning", "want", "aspiring", "aspire"}
STOPWORDS = {"and", "of", "the", "for", "in", "to", "a", "an", "with", "on", "at", "by"}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NUMBERISH = re.compile(r"\+?\d[\d\s().-]{6,}\d")
WORD = re.compile(r"[a-z0-9][a-z0-9+#.-]*[a-z0-9+#]|[a-z0-9]")


def redact(text: str) -> tuple[str, dict]:
    """Blank out emails and long numbers (phone numbers, IC numbers) before anything else.

    A number is removed when it has 9 or more digits, so years and ranges like "2019 - 2023"
    stay readable.
    """
    counts = {"emails": 0, "numbers": 0}

    def drop_email(m):
        counts["emails"] += 1
        return "[email removed]"

    def drop_number(m):
        if sum(ch.isdigit() for ch in m.group()) < 9:
            return m.group()
        counts["numbers"] += 1
        return "[number removed]"

    text = EMAIL.sub(drop_email, text)
    text = NUMBERISH.sub(drop_number, text)
    return text, counts


def stem(word: str) -> str:
    """Rough word stem so "handled", "handling" and "handles" compare equal."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def _phrase_regex(term: str) -> re.Pattern:
    # whole phrase, any case, optional plural; letters or digits must not touch either end
    return re.compile(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?:e?s)?(?![a-z0-9])")


def _snippet(text: str, start: int, end: int) -> str:
    a, b = max(0, start - SNIPPET), min(len(text), end + SNIPPET)
    piece = " ".join(text[a:b].split())
    return ("…" if a > 0 else "") + piece + ("…" if b < len(text) else "")


def _qualifier(lower: str, start: int) -> str | None:
    """Why an exact mention should not count as having the skill, or None if it should."""
    before = WORD.findall(lower[max(0, start - 40):start])[-3:]
    if any(w in NEGATIONS for w in before):
        return "mentioned after a negation such as 'no' or 'without'"
    if any(w in INTENT for w in before):
        return "mentioned as something being learned or wanted, not yet used"
    return None


def _terms(skill: dict) -> list[str]:
    seen, out = set(), []
    for t in list(skill.get("keywords", [])) + list(skill.get("cv_terms", [])):
        t = t.strip().lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _exact(lower: str, term: str):
    """First plain occurrence of the exact phrase as (start, end, None); otherwise the first
    qualified one as (start, end, reason); None if the phrase never appears."""
    first_qualified = None
    for m in _phrase_regex(term).finditer(lower):
        reason = _qualifier(lower, m.start())
        if reason is None:
            return m.start(), m.end(), None
        first_qualified = first_qualified or (m.start(), m.end(), reason)
    return first_qualified


def _nearby(tokens: list[tuple[str, int, int]], term: str):
    """All words of a multi-word phrase within WINDOW words of each other, in any form."""
    wanted = {stem(w) for w in WORD.findall(term) if w not in STOPWORDS}
    if len(wanted) < 2:
        return None
    stems = [stem(t[0]) for t in tokens]
    for i, s in enumerate(stems):
        if s not in wanted:
            continue
        window = stems[i:i + WINDOW]
        if wanted <= set(window):
            last = max(i + window.index(w) for w in wanted)
            return tokens[i][1], tokens[last][2]
    return None


def match_cv(text: str, skills: list[dict]) -> dict:
    """Return the skills found in the CV text, each with level, matched term and evidence."""
    clean, redactions = redact(text)
    lower = clean.lower()
    tokens = [(m.group(), m.start(), m.end()) for m in WORD.finditer(lower)]

    results = []
    for skill in skills:
        best = None
        for term in _terms(skill):
            hit = _exact(lower, term)
            if hit and hit[2] is None:
                best = ("found", term, hit[0], hit[1], None)
                break
            if hit and best is None:
                best = ("possible", term, hit[0], hit[1], hit[2])
        if best is None:
            for term in _terms(skill):
                near = _nearby(tokens, term)
                if near:
                    best = ("possible", term, near[0], near[1], "similar wording, not the exact phrase")
                    break
        if best:
            level, term, start, end, note = best
            results.append({
                "skill": skill["id"], "name": skill["name"], "level": level, "source": "keywords",
                "term": term, "evidence": _snippet(clean, start, end), "note": note,
            })

    results.sort(key=lambda r: (r["level"] != "found", r["name"]))
    return {
        "found": [r for r in results if r["level"] == "found"],
        "possible": [r for r in results if r["level"] == "possible"],
        "redactions": redactions,
        "characters": len(text),
    }
