# Stored XSS: Attack and Cure

A hands-on demonstration of stored cross-site scripting (XSS) against a Python comment renderer, and the output-escaping fix that closes it.

## What the payload is, and why it fires with no `<script>` tag

**The attack string used here:** `<img src=x onerror="document.title='XSS'">`

A browser parses HTML character by character and has no way to know which parts the programmer wrote and which parts arrived from a stranger's input. `<img src=x>` is a real, valid image tag whose source (`x`) doesn't exist, so the browser fails to load it and fires the `onerror` event — and whatever JavaScript sits inside `onerror="..."` runs. No `<script>` tag is needed; `onerror`, `onload`, `onclick` and dozens of other event-handler attributes are all equally valid triggers. This is why blocklisting the literal word "script" is not a real defence (see below).

## Why render_comment_unsafe is vulnerable

The database fetch itself is parameterised and safe (D14's lesson, already applied). The vulnerability is entirely in the final return line: `author` and `body` come straight from a stored comment and are glued directly into an f-string that becomes real HTML, `f"<p><strong>{author}:</strong> {body}</p>"`. When `body` is the attack string, the function returns a live, functioning `<img>` tag in the HTML source. A browser rendering this page runs the `onerror` JavaScript exactly as if the developer had written it.

Real output from this build, confirmed by `demo_attack.py`:

```
--- render_comment_unsafe ---
<p><strong>mallory:</strong> <img src=x onerror="document.title='XSS'"></p>
```

## How html.escape() fixes it

`render_comment_safe` calls `html.escape()` on `author` and `body` before building the same HTML string: `safe_author = html.escape(author)`, `safe_body = html.escape(body)`. This converts the characters HTML treats as structural into their harmless text equivalents, before they ever reach the markup string: `<` becomes `&lt;`, `>` becomes `&gt;`, `"` becomes `&quot;`, `'` becomes `&#x27;`. The browser's parser then sees literal escape sequences, not a tag — it prints the angle brackets as visible text on screen instead of treating them as markup.

Real output from this build:

```
--- render_comment_safe ---
<p><strong>mallory:</strong> &lt;img src=x onerror=&quot;document.title=&#x27;XSS&#x27;&quot;&gt;</p>
```

The words "img", "src", "onerror" are all still visible — only the structural characters (`<`, `>`, `"`, `'`) changed. The content survives; the ability to execute as markup does not.

This fix only works because `html.escape()` and the output it's protecting agree on context: both are plain HTML text. It's not the same mechanism as D14's `?` placeholders. A placeholder keeps the attacker's data in a completely separate channel from the SQL, sent after the grammar is already locked. `html.escape()` doesn't separate anything — it transforms the data in place so the HTML parser reads the dangerous characters as printable text instead of markup. Both fixes stop user input from becoming grammar, but they do it by different means, and that difference matters for knowing where each one applies.

It also means `html.escape()` isn't a universal fix, only a context-correct one. It protects text between tags and inside quoted attribute values, which is exactly what this build needed. It does **not** protect a URL context: `html.escape('javascript:document.title=1')` returns the string completely unchanged, because none of `< > " '` appear in it. An attacker-controlled `href` doesn't need any of those characters to run code. A real comment system also needs to validate that any user-supplied URL starts with `http://` or `https://` before using it in a link, and a Content-Security-Policy header as a second layer of defence.

## Why blocklisting "<script>" is not a real fix

Filtering input for the literal string `<script>` and stripping it is the same mistake as D14's quote-escaping patch: it guesses at dangerous patterns instead of removing the ambiguity structurally. It's trivially bypassed — `<ScRiPt>` (case variation), or simply using a different tag entirely like `<img onerror=...>` or `<svg onload=...>`, both of which this build's own attack string proves work with zero `<script>` anywhere. A blocklist keeps growing forever and is always one tag behind. Escaping removes that entire category of attack for a given context — but only for the context it's applied to, as the URL case above shows.

## Tests

Three pytest tests, all confirmed passing:
- `test_unsafe_render_contains_live_img_tag` — proves the exploit lands in the unsafe renderer's output (documents the vulnerability exists)
- `test_safe_render_escapes_the_tag` — proves the identical payload is escaped and inert in the safe renderer's output
- `test_safe_render_still_shows_the_text_content` — proves escaping doesn't destroy the visible content, only neutralises the markup

## How to run

1. `pip install pytest`
2. `python demo_attack.py`
3. `pytest -v`