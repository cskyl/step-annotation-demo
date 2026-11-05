#!/usr/bin/env python3
"""Build the two demo annotation pages from demo_units.json (made-up dialogues only).

  templates/gold_template.html.tpl   two-question page shell (placeholders __UNITS__ etc.)
  templates/audit48_shell.html.tpl   three-label page shell (placeholders __UNITS__ etc.)
  display_clean.py                   display-only cleanup of pasted-math artifacts

Writes gold/index.html and audit48/index.html. The pages keep the shells' HTML/CSS/JS; this
script fills in the unit data, a packet id that starts with "DEMO-", the data-derived counts
of the three-label page (glossary counts, message characters, reading minutes, unit count)
and a demo banner at the top.

Message text goes through the same display steps as the real packets:
  dec()          restore Unicode escapes that lost their backslash ("u00b2" -> "²")
  nn rule        restore a lost paragraph break: "[.!?:] ?nn" before a capital, digit or $*-(
  display_clean  pasted-math artifacts (per-character copies, stray "n" separators)
The two-question page also strips one pair of wrapping quotes, as its builder does.

Usage: python3 build_demo.py        (Python 3.8+, standard library only)
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import display_clean as DCL
from lang_toggle import add_lang_toggle

HERE = Path(__file__).resolve().parent
TPL = HERE / 'templates'
BANNER = ('<div id="demoBanner" role="note" style="background:#fff4d6;color:#4a3800;border-bottom:1px solid #e3c46a;'
          'padding:6px 16px;text-align:center;font:14px/1.4 system-ui,-apple-system,\'Segoe UI\',sans-serif">'
          'Demo with made-up dialogues — for testing the interface only / 演示版：对话均为虚构，仅用于测试界面</div>')
GOLD_BATCH = 0  # a batch number no real packet uses
GLOSSARY = [  # word list of the three-label page; counts are recomputed on the demo messages
    ('sonuç', 'result'), ('verilen', 'given'), ('değer', 'value'), ('değeri', 'value (possessive)'),
    ('bulmak', 'to find'), ('bulunur', 'is found'), ('şimdi', 'now'), ('çözüm', 'solution'),
    ('olur', 'becomes / is'), ('ve', 'and'), ('ile', 'with / and'), ('için', 'for'), ('ancak', 'however'),
    ('yani', 'that is'), ('toplam', 'total'), ('küme', 'set')]

# ---------------------------------------------------------------- display steps
_UNI = re.compile(r"u(2[0-9a-f]{3}|00[0-9a-f]{2}|01[0-9a-f]{2}|03[0-9a-f]{2}|fffd)")
_NN = re.compile(r'([.!?:])( ?)nn(?=( ?)(\S))')


def dec(t: str) -> str:
    t = _UNI.sub(lambda m: chr(int(m.group(1), 16)), t)
    return t.replace("\\'", "'").replace('\\"', '"').replace('ı', 'i').replace('İ', 'I')


def nn_fix(t: str) -> str:
    def fix(m):
        nxt = m.group(4)
        if nxt.isupper() or nxt.isdigit() or nxt in '$*-(':
            return m.group(1) + '\n\n'
        return m.group(0)
    return _NN.sub(fix, t).strip()


def clean(t: str) -> str:
    out, rep = DCL.audit(t)
    assert rep['ok'], rep['problems']
    return out


def display_gold(t: str) -> str:
    t = dec(t)
    if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
        t = t[1:-1]
    return clean(nn_fix(t)).strip()


def display_audit(t: str) -> str:
    return clean(nn_fix(dec(t)))


def unchanged(t: str) -> str:
    assert DCL.display_clean(t) == t and dec(t) == t, f'display cleanup would change {t!r}'
    return t


# ---------------------------------------------------------------- practice units of the two-question page
def practice_units():
    return [
        {'no': 'P1', 'problem': 'A box has 4 green and 6 yellow cards. Two cards are drawn without replacement. What is the probability that both are green?',
         'steps': [{'n': 1, 'text': 'first card green = 4/10 = 2/5'}, {'n': 2, 'text': 'second card green, given the first was green = 3/9 = 1/3'}],
         'final': '2/15',
         'messages': [{'role': 'Student', 'reply': None, 'chat_start': True, 'text': "I don't know how to start."},
                      {'role': 'AI', 'reply': 1, 'chat_start': False, 'text': 'What fraction of the cards is green at the start?'},
                      {'role': 'Student', 'reply': None, 'chat_start': False, 'text': '4/10'},
                      {'role': 'AI', 'reply': 2, 'chat_start': False, 'text': 'Good. After one green card is removed, 3 of the remaining 9 cards are green, so the second draw is 3/9. Now combine the two.'},
                      {'role': 'Student', 'reply': None, 'chat_start': False, 'text': '4/10 × 3/9 = 12/90 = 2/15'},
                      {'role': 'AI', 'reply': 3, 'chat_start': False, 'text': 'Correct!'}],
         'answer': {'q1': 'later', 'q2': 'Student'},
         'reason': 'Q1 = In a later AI reply: AI reply 1 only asks a question, and the Student says 4/10 first; AI reply 2 then states step 2 (3/9) before the Student does. Q2 = Student: the Student is first to give 2/15. / Q1 = 在之后的 AI 回复里：AI 第 1 条回复只是提问，4/10 是学生先说的；AI 第 2 条回复先说出步骤 2（3/9）。Q2 = Student：2/15 是学生先给出的。'},
        {'no': 'P2', 'problem': 'A rectangle is 7 cm long and 3 cm wide. Find its area and its perimeter.',
         'steps': [{'n': 1, 'text': 'length + width = 7 + 3 = 10 cm'}],
         'final': 'area = 21 cm² and perimeter = 20 cm',
         'messages': [{'role': 'Student', 'reply': None, 'chat_start': True, 'text': 'the area is 21?'},
                      {'role': 'AI', 'reply': 1, 'chat_start': False, 'text': 'Yes, 7 × 3 = 21 cm². For the perimeter, first add the length and the width.'},
                      {'role': 'Student', 'reply': None, 'chat_start': False, 'text': '10, so the perimeter is 20'},
                      {'role': 'AI', 'reply': 2, 'chat_start': False, 'text': 'Right: the area is 21 cm² and the perimeter is 20 cm.'}],
         'answer': {'q1': 'none', 'q2': 'AI'},
         'reason': 'Q1 = No: the only listed step (10) is said by the Student first; 21 is part of the final answer, not a listed step, and the Student said it first anyway; “add the length and the width” is only a method. Q2 = AI: the final has two parts. The Student gave them in two different messages; the first single message with both parts is AI reply 2. / Q1 = 没有：唯一的步骤 10 是学生先说的；21 属于最终答案且学生先说；“先把长和宽相加”只是方法。Q2 = AI：答案有两部分，学生分两条消息说出；第一条同时包含两部分的消息是 AI reply 2。'},
    ]


# ---------------------------------------------------------------- unit builders (same field schema as the real packets)
def steps_of(u):
    return [s if isinstance(s, list) else [s] for s in u['steps']]


def gold_units(src):
    out = []
    for u in src:
        steps = [{'n': i + 1, 'text': unchanged(' or '.join(x.strip() for x in alts))} for i, alts in enumerate(steps_of(u))]
        final = u['final'].strip()
        final = re.sub(r'^The correct (solution|answer) is[:\s]*', '', final, flags=re.I).strip() or final
        msgs, reply = [], 0
        for m in u['messages']:
            if m['role'] == 'AI':
                reply += 1
                msgs.append({'role': 'AI', 'reply': reply, 'chat_start': bool(m['chat_start']), 'text': display_gold(m['text'])})
            else:
                msgs.append({'role': 'Student', 'reply': None, 'chat_start': bool(m['chat_start']), 'text': display_gold(m['text'])})
        out.append({'unit_no': u['unit_no'], 'unit_key_hash': u['unit_key_hash'], 'problem': unchanged(u['problem'].strip()),
                    'steps': steps, 'final': unchanged(final), 'n_replies': reply, 'messages': msgs})
    for x in out:
        assert set(x) == {'unit_no', 'unit_key_hash', 'problem', 'steps', 'final', 'n_replies', 'messages'}
        assert all(set(m) == {'role', 'reply', 'chat_start', 'text'} for m in x['messages'])
    return out


def audit_units(src):
    out = []
    for u in src:
        msgs, reply = [], 0
        for m in u['messages']:
            if m['role'] == 'AI':
                reply += 1
                msgs.append({'role': 'AI', 'reply': reply, 'text': display_audit(m['text'])})
            else:
                msgs.append({'role': 'Student', 'reply': None, 'text': display_audit(m['text'])})
        out.append({'unit_no': u['unit_no'], 'audit_key_hash': u['audit_key_hash'], 'problem': unchanged(u['problem']),
                    'steps': [clean(x.strip()) for alts in steps_of(u) for x in alts],
                    'correct_final': unchanged(u['final']), 'n_replies': reply, 'messages': msgs})
    return out


def glossary(units):
    words = [w for u in units for m in u['messages'] for w in re.findall(r'[^\W\d_]+', m['text'].lower())]
    return [{'word': w, 'meaning': meaning, 'count': words.count(w)} for w, meaning in GLOSSARY]


# Demo-only wording: the real shells describe real chats; the demo says they are made up.
DEMO_TEXT = [
    ('这里是真实学生对话。不要上传、复制或分享消息文本；在所有标注者都返回文件前，不要和其他标注者讨论单位。导出 JSON 后删除这个 HTML。 / '
     'These are real student chats. Do not upload, copy, or share message text. Do not discuss units with other annotators '
     'until all have returned files. Delete this HTML after returning the JSON.',
     '演示版：这里的对话都是虚构的。正式标注时不要复制、上传或分享对话文字，全部交回前不要和其他标注者讨论。 / '
     'Demo: these chats are made up. In the real study, do not copy, upload or share message text, and do not discuss '
     'units with other annotators until all files are returned.'),
    ('这些是真实学生对话：不要复制、上传或分享文字；全部交回前不要和其他标注者讨论。 / These are real student chats: '
     'do not copy, upload or share text; do not discuss units with other annotators until all files are returned.',
     '演示版：这里的对话都是虚构的。正式标注时不要复制、上传或分享文字，全部交回前不要和其他标注者讨论。 / '
     'Demo: these chats are made up. In the real study, do not copy, upload or share text, and do not discuss units '
     'with other annotators until all files are returned.'),
]


def finish(html: str, n: int) -> str:
    assert not re.search(r'__[A-Z_]+__', html), 'unfilled placeholder'
    assert html.count('<body>') == 1
    hits = 0
    for old, new in DEMO_TEXT:
        hits += html.count(old)
        html = html.replace(old, new)
    assert hits == 1, 'demo wording: expected one real-chat sentence per page'
    html = (html.replace('expected 48 labels', f'expected {n} labels')
                .replace('expected exactly 48 units', f'expected exactly {n} units')
                .replace('about 1 minutes', 'about 1 minute'))
    html = html.replace('<body>', '<body>' + BANNER, 1)
    # Display-only language switch, the same one the real pages get.
    html, _ = add_lang_toggle(html)
    return html


def write(rel, text):
    p = HERE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return p


def main():
    src = json.loads((HERE / 'demo_units.json').read_text(encoding='utf-8'))['units']
    assert [u['unit_no'] for u in src] == list(range(1, len(src) + 1))
    assert all(u['audit_key_hash'].startswith('demo-') and u['unit_key_hash'].startswith('demo-') for u in src)

    # two-question page
    gu = gold_units(src)
    gc = json.dumps(gu, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    gpid = 'DEMO-' + hashlib.sha256(gc.encode('utf-8')).hexdigest()
    tpl = (TPL / 'gold_template.html.tpl').read_text(encoding='utf-8')
    gold = (tpl.replace('__UNITS__', gc.replace('</', '<\\/'))
            .replace('__PRACTICE__', json.dumps(practice_units(), ensure_ascii=False).replace('</', '<\\/'))
            .replace('__PACKET_ID__', gpid).replace('__BATCH__', str(GOLD_BATCH)).replace('__N__', str(len(gu))))
    write('gold/index.html', finish(gold, len(gu)))

    # three-label page
    au = audit_units(src)
    ac = json.dumps(au, ensure_ascii=False, separators=(',', ':'))
    apid = 'DEMO-' + hashlib.sha256(ac.encode('utf-8')).hexdigest()
    chars = sum(len(m['text']) for u in au for m in u['messages'])
    shell = (TPL / 'audit48_shell.html.tpl').read_text(encoding='utf-8')
    audit = (shell.replace('__UNITS__', ac.replace('</', '<\\/'))
             .replace('__GLOSSARY__', json.dumps(glossary(au), ensure_ascii=False, separators=(',', ':')))
             .replace('__PACKET_ID__', apid).replace('__MSG_CHARS__', f'{chars:,}')
             .replace('__READ_MIN__', str(max(1, round(chars / 1500)))).replace('__N__', str(len(au))))
    write('audit48/index.html', finish(audit, len(au)))

    print(json.dumps({'gold/index.html': {'units': len(gu), 'packet_id': gpid, 'batch': GOLD_BATCH},
                      'audit48/index.html': {'units': len(au), 'packet_id': apid, 'message_chars': chars}}, indent=1))


if __name__ == '__main__':
    main()
