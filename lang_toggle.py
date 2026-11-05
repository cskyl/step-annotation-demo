"""Add the display-only language switch (中英 / 中文 / English) to an annotation page.

The switch hides one half of each "中文 / English" pair on screen. It does not touch
unit data, PACKET_ID, labels or exports, so a page keeps its packet id.
A few strings that the runtime rule cannot split get explicit markup here.
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SNIPPET = HERE / 'templates' / 'lang_toggle.snippet.html'

# Exact UI strings (no unit data) that need explicit language markup.
EXPLICIT = [
    # gold page, made-up example ②: two pairs interleaved in one line
    ('<div class="ans">Q1 = 在之后的 AI 回复里 / In a later AI reply（reply 1 只是复述 3/8 和说方法名；reply 2 先说出 2/7 / '
     'reply 1 only echoes 3/8 and names a method; reply 2 states 2/7 first） &nbsp;·&nbsp; Q2 = Student</div>',
     '<div class="ans" data-bi-skip><span class="bi-zh">Q1 = 在之后的 AI 回复里（reply 1 只是复述 3/8 和说方法名；'
     'reply 2 先说出 2/7）</span><span class="bi-sep"> / </span><span class="bi-en">Q1 = In a later AI reply '
     '(reply 1 only echoes 3/8 and names a method; reply 2 states 2/7 first)</span> &nbsp;·&nbsp; Q2 = Student</div>'),
    # three-label page: English-only return instruction
    ('<p><strong>Click Export JSON and send the file to the person who gave you this page.</strong></p>',
     '<p><strong>点击“导出 JSON”，把文件发给给你这个页面的人。 / Click Export JSON and send the file to the person '
     'who gave you this page.</strong></p>'),
]
# three-label page: English-only footer with filled-in counts
FOOTER = re.compile(r'<footer class="muted">Estimated message characters: ([\d,]+); character-based reading estimate: '
                    r'about (\d+) (minutes?) at 1,500 characters/minute\. The form target is about 1 minute per unit\.</footer>')


def _footer(m):
    chars, mins, unit = m.groups()
    return (f'<footer class="muted"><span class="bi-zh">消息约 {chars} 字符；按每分钟 1,500 字符估算，阅读约 {mins} 分钟。'
            f'每题目标约 1 分钟。</span><span class="bi-sep"> / </span><span class="bi-en">Estimated message characters: '
            f'{chars}; character-based reading estimate: about {mins} {unit} at 1,500 characters/minute. '
            f'The form target is about 1 minute per unit.</span></footer>')


def add_lang_toggle(html: str) -> tuple:
    """Return (new_html, report). Refuses a page that already has the switch."""
    assert 'id="uiLangScript"' not in html, 'language switch already present'
    assert html.count('</body>') == 1
    report = {}
    for old, new in EXPLICIT:
        n = html.count(old)
        assert n <= 1, old[:40]
        html = html.replace(old, new)
        report[old[:48]] = n
    html, n = FOOTER.subn(_footer, html)
    report['footer'] = n
    html = html.replace('</body>', SNIPPET.read_text(encoding='utf-8') + '</body>', 1)
    return html, report
