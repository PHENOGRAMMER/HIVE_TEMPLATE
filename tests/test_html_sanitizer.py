from app.services.rendering.html import sanitize_html


def test_sanitizer_preserves_safe_formatting():
    html = "<strong>Important</strong><br><em>Check this</em>"

    result = sanitize_html(html)

    assert result is not None
    assert "<strong>Important</strong>" in result
    assert "<br>" in result
    assert "<em>Check this</em>" in result


def test_sanitizer_preserves_safe_links():
    html = (
        '<a href="https://example.com">'
        "Documentation"
        "</a>"
    )

    result = sanitize_html(html)

    assert result is not None
    assert 'href="https://example.com"' in result
    assert "Documentation" in result


def test_sanitizer_removes_script():
    html = (
        "<p>Normal text</p>"
        "<script>alert('xss')</script>"
    )

    result = sanitize_html(html)

    assert result is not None
    assert "<script>" not in result
    assert "alert(" not in result
    assert "<p>Normal text</p>" in result


def test_sanitizer_removes_javascript_links():
    html = (
        '<a href="javascript:alert(1)">'
        "Click"
        "</a>"
    )

    result = sanitize_html(html)

    assert result is not None
    assert "javascript:" not in result
