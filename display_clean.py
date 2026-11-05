#!/usr/bin/env python3
"""display_clean(text): display-only cleanup of pasted-math artifacts (2026-11-05).

When a student (or the AI) copied rendered math, the export kept two copies of it:

  (1) a per-character copy, one glyph per line. The export lost the backslash of every
      line break, so the copy reads "n<glyph>n<glyph>n..." and its math-italic letters
      are already U+FFFD (or empty) in the study's own export; they cannot be recovered;
  (2) then, usually, a plain copy with the content, e.g. "(a∨b n′n )⇒(a n′n ∧b)",
      in which superscripts / primes still sit between stray " n...n " separators.

Rules (display only; the text given to models is never changed):

  (a) A run is a maximal "n<token>n<token>...n" sequence, token = one non-space glyph that
      is not the letter n, a number, a run of math spaces, or empty (a vanished glyph).
      * Long run (>= 5 non-empty tokens) that is math (U+FFFD, empty glyph or a math
        symbol), or that is followed by a plain copy:
          - plain copy follows  -> DROP the run, leaving one space;
          - otherwise           -> JOIN the run's glyphs, U+FFFD / empty glyph shown as "□".
      * Short run (1-4 tokens) is dropped only when it contains U+FFFD / an empty glyph or
        a math symbol, is not glued to a preceding letter or digit, and the plain copy that
        follows matches it exactly (e.g. "n\ufffdnK" -> "K", "n\ufffdn+n\ufffdna+b" -> "a+b").
      "Plain copy follows" is decided by aligning the run's glyphs (U+FFFD = any letter)
      against the text after the run. In an exact alignment, the plain copy's own stray
      separators (the "n"s that match no glyph) are removed; in a partial alignment
      (fractions / roots, whose plain copy is reordered) they become spaces.
  (b) Elsewhere: " n′n " -> "′"; " n2n " -> "²" only when clearly a superscript (base
      letter or ")" before, operator / ")" / end after), "^2" when a base is present but
      the right side is ambiguous; "n\\u200bn" -> "". Real words and variables containing
      "n" are left alone ("n!", "C(n,5)", "and", "cannot", "n(A)").

Content guarantee (checked by audit()): every character of the input other than the
letter n, whitespace and zero-width space survives in the output, except characters of
dropped per-character runs whose glyphs are covered by the plain copy that follows.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter

FFFD = '\ufffd'
BOX = '□'
WILD = None  # unknown letter (U+FFFD or a vanished glyph)
_MSP = '\u2000-\u200b\u205f\u3000'
_TOKEN = re.compile(rf'\d+(?:[.,]\d+)*|[{_MSP}]+|[^\sn\d{_MSP}]')
MATH = set('⇒⇔⟹⟺→←↔↦∧∨⊻¬′″≤≥≠≈≡∈∉∋∪∩⊂⊆⊃⊇∅×÷⋅·√∛∜∑∏∫∞±∓−+=<>()[]{}^/|∣∠°πθαβγΔ∆')
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
_SEP_SKIP = set(' \t\u00a0\u205f\u3000') | {chr(c) for c in range(0x2000, 0x200c)}
_OPS_AFTER = set('−+-=)]},.;:?!/×⋅') | {'\n'}
MIN_LONG = 5


def _norm(c: str) -> str:
    c = unicodedata.normalize('NFKC', c)
    return '-' if c in ('−', '‐', '‑', '–') else c


def _eq(cc, pc: str) -> bool:
    if cc is WILD:
        return pc.isalpha() and pc != FFFD
    return _norm(cc) == _norm(pc)


# ---------------------------------------------------------------- run parsing
def _parse_run(t: str, i: int):
    """Parse a run starting at t[i] == 'n'. Returns (tokens, end) where tokens is a list of
    (text, start, end_including_trailing_n); tokens may be '' (vanished glyph)."""
    toks = []
    j = i + 1
    while j <= len(t):
        if j < len(t) and t[j] == 'n':
            toks.append(('', j, j + 1))
            j += 1
            continue
        m = _TOKEN.match(t, j)
        if not m or m.end() >= len(t) or t[m.end()] != 'n':
            break
        toks.append((m.group(0), j, m.end() + 1))
        j = m.end() + 1
    return toks, j


def _is_msp(tok: str) -> bool:
    return bool(tok) and all(ch in _SEP_SKIP for ch in tok)


def _glyphs(toks):
    """Glyph list for alignment: WILD for U+FFFD / empty tokens, chars for others; math spaces dropped."""
    out = []
    for tok, _, _ in toks:
        if tok == '' or tok == FFFD:
            out.append(WILD)
        elif _is_msp(tok):
            continue
        else:
            out.extend(ch if ch != FFFD else WILD for ch in tok)
    return out


# ---------------------------------------------------------------- alignment
def _align_exact(C, t: str, s: int):
    """Exact alignment of glyphs C against t[s:], allowing skipped separators ('n', spaces,
    zero-width) between glyphs but no leading 'n'. Returns list of (pos, kind) for kind in
    {'m', 'sep', 'sp'} covering t[s:end], or None."""
    n_c = len(C)
    memo = {}
    limit = min(len(t), s + 4 * n_c + 40)

    def rec(i, j, first):
        if i == n_c:
            return []
        if j >= limit:
            return None
        key = (i, j, first)
        if key in memo:
            return memo[key]
        pc = t[j]
        res = None
        if _eq(C[i], pc):
            r = rec(i + 1, j + 1, False)
            if r is not None:
                res = [(j, 'm')] + r
        if res is None and pc in _SEP_SKIP:
            r = rec(i, j + 1, first)
            if r is not None:
                res = [(j, 'sp')] + r
        if res is None and pc == 'n' and not first:
            r = rec(i, j + 1, False)
            if r is not None:
                res = [(j, 'sep')] + r
        memo[key] = res
        return res

    import sys
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, 20000))
    try:
        return rec(0, s, True)
    finally:
        sys.setrecursionlimit(old)


def _prefix_exact(C, t, s, need):
    return need > 0 and _align_exact(C[:need], t, s) is not None


def _partial_span(C, t, s):
    """Partial plain copy (fractions / roots reorder the plain copy). Returns the end of the
    shortest span t[s:e] whose characters cover the run's glyphs (multiset; each unknown
    letter needs one letter other than 'n'), or None."""
    need = Counter(_norm(c) for c in C if c is not WILD)
    wild = sum(1 for c in C if c is WILD)
    have, letters = Counter(), 0
    limit = min(len(t), s + 3 * len(C) + 30)
    for j in range(s, limit):
        ch = t[j]
        if ch in _SEP_SKIP or ch == 'n':
            continue
        if ch.isalpha():
            letters += 1
        else:
            have[_norm(ch)] += 1
        if letters >= wild and all(have[c] >= v for c, v in need.items()):
            return j + 1
    return None


def _sup(prev_out: str, nxt: str, d: str):
    """Superscript for a digit wrapped by separators: unicode when clearly a superscript,
    '^d' when a base is present but the right side is ambiguous, None when no base."""
    base = prev_out.rstrip(' ')[-1:]
    if not base or not (base.isalpha() or base in ')]'):
        return None
    if nxt == '' or nxt in _OPS_AFTER or nxt == ' ':
        return d.translate(SUP)
    return '^' + d


def _render_exact(t, ops):
    """Exact plain copy: matched chars kept, separator 'n' removed, spaces next to a
    removed separator removed, zero-width removed; a digit wrapped by separators is a
    superscript."""
    kind = {p: k for p, k in ops}
    a, b = ops[0][0], ops[-1][0] + 1
    out = []
    for p in range(a, b):
        k, ch = kind.get(p), t[p]
        if k == 'm':
            if ch.isdigit() and kind.get(p - 1) == 'sep' and kind.get(p + 1) == 'sep':
                q = p + 2
                while q < len(t) and t[q] in ' \u200b':
                    q += 1
                s = _sup(''.join(out), t[q] if q < len(t) else '', ch)
                if s is not None:
                    while out and out[-1] == ' ':
                        out.pop()
                    out.append(s)
                    continue
            out.append(ch)
        elif k == 'sp':
            if ch == '\u200b' or kind.get(p - 1) == 'sep' or kind.get(p + 1) == 'sep':
                continue
            out.append(' ')
    return ''.join(out).strip(' '), a, b


_SEPDIG = re.compile(r' ?n(\d)n ?')


def _render_partial(t, a, b, C):
    """Partial plain copy: when the span has exactly as many non-'n' letters as the run has
    unknown letters, every 'n' in it is a separator and becomes a space (a digit wrapped by
    separators after a base is a superscript); otherwise the span is shown as is apart
    from the generic rules."""
    seg = t[a:b]
    wild = sum(1 for c in C if c is WILD)
    letters = sum(1 for ch in seg if ch.isalpha() and ch != 'n')
    if letters != wild:
        return _generic(seg).strip(' ')
    seg = seg.replace('\u200b', '')

    def sup(m):
        s = _sup(seg[:m.start()], seg[m.end():m.end() + 1], m.group(1))
        return s if s is not None else ' ' + m.group(1) + ' '
    seg = _SEPDIG.sub(sup, seg)
    seg = seg.replace('n', ' ')
    seg = re.sub(r'[ \u00a0\u2000-\u200a\u205f]{2,}', ' ', seg)
    return seg.strip(' ')


# ---------------------------------------------------------------- (b) generic rules
_PRIME = re.compile(r' ?n′n ?')
_ZW = re.compile(r'( *)n\u200bn( *)')
_SUPDIG = re.compile(r'(?:(?<=(?<![A-Za-z])[A-Za-z])|(?<=[)\]])) n(\d)n (?=\S)')  # base = one-letter variable or bracket


def _generic(t: str) -> str:
    t = _ZW.sub(lambda m: ' ' if (m.group(1) or m.group(2)) and t[m.end():m.end() + 1] not in tuple('.,;:?!)') else '', t)
    t = _PRIME.sub('′', t)

    def sup(m):
        q = m.end()
        nxt = t[q] if q < len(t) else ''
        return m.group(1).translate(SUP) if nxt in _OPS_AFTER else '^' + m.group(1) + ' '
    t = _SUPDIG.sub(sup, t)
    return t


# ---------------------------------------------------------------- token classes
def _kind(tok: str) -> str:
    if tok == '':
        return 'empty'
    if tok == FFFD:
        return 'wild'
    if _is_msp(tok):
        return 'msp'
    if tok[0].isdigit():
        return 'num'
    if tok.isalpha():
        return 'ascii' if tok.isascii() else 'mathletter'
    if tok in MATH:
        return 'math'
    return 'punct'


def _is_math(toks) -> bool:
    """A long run is a per-character math copy (and may be joined) only if it has a glyph
    that cannot be ordinary text: U+FFFD / a math letter, or numbers together with math
    symbols. Operators alone ("n+n+n+n+n+n") are real variables n and are left alone."""
    kinds = {_kind(x[0]) for x in toks}
    return bool(kinds & {'wild', 'mathletter'}) or ('num' in kinds and 'math' in kinds)


def _short_ok(toks, t, start, glued_word=False) -> bool:
    """Eligibility of a short run (1-4 tokens) for dropping (still needs an exact copy).
    glued_word: the run follows a word ending in 'n' whose own 'n' was skipped ("functionn…")."""
    kinds = [_kind(x[0]) for x in toks]
    prev = t[start - 1] if start > 0 else ''
    if prev.isalnum() and not glued_word:
        return False
    if 'ascii' in kinds:
        return False
    # a single vanished glyph before a one-letter word: " of nnA with" (only after a word)
    if kinds == ['empty']:
        return start >= 2 and prev == ' ' and t[start - 2].isalpha() and t[start - 2].islower()
    if 'empty' in kinds and 'wild' not in kinds:
        return False
    if any(k in ('wild', 'mathletter', 'math') for k in kinds):
        return True
    # pure numbers ("n6n6", "n17n,n000n17,000"): only after a space / start / "("
    return 'num' in kinds and all(k in ('num', 'punct') for k in kinds) and prev in ('', ' ', '(')


# ---------------------------------------------------------------- main entry
_ORD = re.compile(r'(?:st|nd|rd|th)(?![A-Za-z])')


def _glued(C, t, last) -> bool:
    """True if the aligned plain copy t[..last] runs on into a longer word or number."""
    nxt = t[last + 1] if last + 1 < len(t) else ''
    if nxt == 'n':  # a separator / line break, unless a lower-case word follows ("n\ufffdnand")
        after = t[last + 2] if last + 2 < len(t) else ''
        return after.isalpha() and after.islower() and all(c is WILD for c in C)
    if not nxt.isalnum():
        return False
    if t[last].isdigit() and _ORD.match(t, last + 1):
        return False
    return t[last].isalnum()


def _find_plain(t, toks, long_run):
    """Try cutting the run after token k (k = K, K-1, ...): the plain copy starts right after
    that token's separator. Returns (cut, k, mode, ops_or_end) or None; mode 'exact' or 'partial'."""
    K = len(toks)
    partial = None
    # the plain copy may start inside the run only by one absorbed token ("…n6nn(B−A)")
    for k in range(K, max(1, K - 1) - 1, -1):
        sub = toks[:k]
        C = _glyphs(sub)
        if not C:
            continue
        cut = sub[-1][2]
        ops = _align_exact(C, t, cut)
        if ops is not None:
            last = max(p for p, kk in ops if kk == 'm')
            if not _glued(C, t, last):
                return cut, k, 'exact', ops
        if long_run and partial is None and len(C) >= MIN_LONG and _prefix_exact(C, t, cut, min(4, len(C))):
            e = _partial_span(C, t, cut)
            if e is not None:
                partial = (cut, k, 'partial', e)
    return partial


def _lead(out, t, start):
    """What replaces the run's leading separator: a line break if it was glued to the
    previous text ("follows:n…", "2×n(A∩B)n…"), one space after a word, nothing after a
    space / opening bracket / quote / line start."""
    prev_out = out[-1][-1:] if out and out[-1] else ''
    if not prev_out or prev_out in ' \n\t([{"\'':
        return ''
    prev_src = t[start - 1] if start > 0 else ''
    return '\n' if prev_src not in ' ' else ' '


def _clean_segments(text: str):
    """Returns the list of output segments (kind, src_start, src_end, out_text, info)."""
    t = text
    segs = []
    keep_from = 0
    out_tail = ['']
    i, n = 0, len(t)
    glued_at = -1

    def flush(upto):
        nonlocal keep_from
        if upto > keep_from:
            s = _generic(t[keep_from:upto])
            segs.append(('keep', keep_from, upto, s, None))
            out_tail[0] = s
        keep_from = upto

    while i < n:
        if t[i] != 'n':
            i += 1
            continue
        toks, end = _parse_run(t, i)
        if not toks:
            i += 1
            continue
        if toks[0][0] == '' and i > 0 and t[i - 1].isalpha():
            glued_at = i + 1  # "functionn…": the word keeps its 'n', the run starts next
            i += 1
            continue
        start = i
        nonempty = [x for x in toks if _kind(x[0]) not in ('empty', 'msp')]
        long_run = len(nonempty) >= MIN_LONG
        if not long_run and not _short_ok(toks, t, start, glued_word=(start == glued_at)):
            i = end  # maximal runs only: never re-scan from inside a rejected run
            continue
        res = _find_plain(t, toks, long_run)
        if res is not None and (long_run or res[2] == 'exact'):
            cut, k, mode, x = res
            flush(start)
            if mode == 'exact':
                shown, a, b = _render_exact(t, x)
            else:
                a, b = cut, x
                shown = _render_partial(t, a, b, _glyphs(toks[:k]))
            lead = _lead([out_tail[0]], t, start)
            segs.append(('drop', start, cut, lead, {'mode': mode, 'glyphs': _glyphs(toks[:k])}))
            segs.append(('span', cut, b, shown, {'mode': mode, 'glyphs': _glyphs(toks[:k])}))
            out_tail[0] = shown or lead
            i = keep_from = b
            # the formula's own trailing separator(s)
            m = re.match(r'([.?!,;:)]*)(n+)(?="?\s*$)', t[i:])
            m2 = re.match(r'([.?!,;:]?)n(?=[A-Z])', t[i:])
            if m:
                segs.append(('trim', i, i + m.end(), m.group(1), None))
                i = keep_from = i + m.end()
            elif m2:
                segs.append(('nl', i, i + m2.end(), m2.group(1) + '\n', None))
                i = keep_from = i + m2.end()
            elif i < n and t[i] == 'n' and i + 1 < n and t[i + 1].isalpha() and t[i + 1] != 'n':
                segs.append(('nl', i, i + 1, '\n', None))
                i = keep_from = i + 1
            elif i < n and t[i] == 'n' and i + 1 < n and t[i + 1] == 'n' and i + 2 < n and t[i + 2].isalpha():
                segs.append(('nl', i, i + 2, '\n\n', None))
                i = keep_from = i + 2
            continue
        if (long_run and _is_math(toks)) or (not long_run and any(_kind(x[0]) == 'wild' for x in toks)):
            flush(start)
            joined = ''.join(BOX if _kind(tok) in ('wild', 'empty') else tok.replace(FFFD, BOX) for tok, _, _ in toks)
            lead = _lead([out_tail[0]], t, start)
            tail = ' ' if end < n and t[end] not in ' \n.,;:?!)"' else ''
            segs.append(('join', start, end, lead + joined + tail, {'glyphs': _glyphs(toks)}))
            out_tail[0] = lead + joined + tail
            i = keep_from = end
            continue
        i = end
    flush(n)
    return segs


def display_clean(text: str, log: list | None = None) -> str:
    """Display-only cleanup (see module docstring). If `log` is a list, one dict per changed
    segment is appended."""
    segs = _clean_segments(text)
    if log is not None:
        for kind, a, b, s, info in segs:
            if kind != 'keep' or s != text[a:b]:
                log.append({'action': kind, 'src': text[a:b], 'out': s, **({'mode': info['mode']} if info and 'mode' in info else {})})
    return ''.join(s for _, _, _, s, _ in segs).replace(FFFD, BOX)


# ---------------------------------------------------------------- audit
_IGN = set(' \t\n\u00a0\u200b') | set(_SEP_SKIP)


def _content(s: str, keep_n: bool = False) -> Counter:
    return Counter(_norm(c) for c in s
                   if c not in _IGN and (keep_n or c != 'n') and c not in (FFFD, BOX, '^'))


def audit(text: str):
    """Independent checks of one cleaning. Returns (cleaned, report); report['ok'] is True iff
      * kept text changed only by the generic rules, which remove only 'n'/spaces/zero-width;
      * every plain-copy span keeps all its characters except separator 'n's, spaces and
        zero-width spaces, and keeps at least as many letters as the run has unknown glyphs;
      * every dropped run's known glyphs are covered by its plain-copy span (in order for an
        exact copy);
      * every joined run keeps all its glyphs;
      * only the letter 'n' is removed outside dropped runs, and only as a separator."""
    segs = _clean_segments(text)
    out = ''.join(s for _, _, _, s, _ in segs).replace(FFFD, BOX)
    problems = []
    for idx, (kind, a, b, s, info) in enumerate(segs):
        src = text[a:b]
        if kind == 'keep':
            if _content(src) != _content(s):
                problems.append(('keep content changed', src[:60]))
        elif kind == 'span':
            if _content(src) != _content(s):
                problems.append(('span content changed', src[:60], s[:60]))
            wild = sum(1 for c in info['glyphs'] if c is WILD or c.isalpha())
            if sum(1 for ch in s if ch.isalpha()) < wild:
                problems.append(('span lost letters', src[:60], s[:60]))
            known = [_norm(c) for c in info['glyphs'] if c is not WILD and not c.isalpha()]
            have = [_norm(c) for c in s if c not in _IGN and not c.isalpha() and c not in ('^',)]
            if info['mode'] == 'exact':
                it = iter(have)
                if not all(any(h == k for h in it) for k in known):
                    problems.append(('glyph order not covered', src[:60], s[:60]))
            elif Counter(known) - Counter(have):
                problems.append(('glyphs not covered', src[:60], s[:60]))
        elif kind == 'join':
            if _content(src) != _content(s):
                problems.append(('join content changed', src[:60]))
        elif kind in ('trim', 'nl'):
            if _content(src) != _content(s) or set(src) - set(s) - {'n'}:
                problems.append((kind + ' removed non-n', src))
    return out, {'ok': not problems, 'problems': problems,
                 'segments': [{'action': k, 'src': text[a:b], 'out': s} for k, a, b, s, _ in segs if k != 'keep' or s != text[a:b]]}
