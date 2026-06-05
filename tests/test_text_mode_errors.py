"""Text-mode decrypt error-message precision.

binascii.Error is a subclass of ValueError, so the `except ValueError`
clause must come AFTER the `except (binascii.Error, ...)` clause — otherwise
a malformed-base64 input is reported with the generic "invalid input" message
instead of the precise "must be base64 encoded" one.
"""

import base64
import os

import pytest

import encipherr

KEY_B64 = base64.urlsafe_b64encode(os.urandom(32)).decode()


def test_bad_base64_ciphertext_reports_base64_error(capsys, monkeypatch):
    monkeypatch.setenv("ENCIPHERR_KEY", KEY_B64)
    # 5 alphabet chars: 1 more than a multiple of 4 → binascii.Error before
    # the length/decrypt logic is ever reached.
    with pytest.raises(SystemExit) as exc:
        encipherr.main(["decrypt", "text", "AAAAA"])
    assert exc.value.code == 1
    assert "base64" in capsys.readouterr().err.lower()
