import os


def test_format_message_respects_no_color_env(monkeypatch):
    # Ensure NO_COLOR causes format_message to return the plain message
    monkeypatch.setenv('NO_COLOR', '1')
    from app.calculator_repl import format_message

    assert format_message('Plain', 'instruction') == 'Plain'


def test_format_message_unknown_type_returns_plain(monkeypatch):
    # Force _supports_color to True so we reach the unknown-type return
    import app.calculator_repl as cr
    monkeypatch.setattr(cr, '_supports_color', lambda: True)

    assert cr.format_message('X', 'not_a_real_type') == 'X'
