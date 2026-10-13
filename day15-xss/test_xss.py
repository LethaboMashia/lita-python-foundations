"""Proves the exploit works against the unsafe renderer and fails against the safe one."""
import pytest
from setup_comments import setup
from demo_attack import post_attacker_comment, ATTACK_BODY
from render_unsafe import render_comment_unsafe
from render_safe import render_comment_safe

@pytest.fixture(autouse=True)
def fresh_db():
    setup()

def test_unsafe_render_contains_live_img_tag():
    comment_id = post_attacker_comment()
    html_out = render_comment_unsafe(comment_id)
    assert "<img src=x onerror=" in html_out

def test_safe_render_escapes_the_tag():
    comment_id = post_attacker_comment()
    html_out = render_comment_safe(comment_id)
    assert "&lt;img" in html_out
    assert "<img src=x onerror=" not in html_out

def test_safe_render_still_shows_the_text_content():
    comment_id = post_attacker_comment()
    html_out = render_comment_safe(comment_id)
    # The visible words survive escaping -- only the markup characters change.
    assert "onerror" in html_out