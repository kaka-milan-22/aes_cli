"""Tests for in-memory (verify-before-write) decryption of small files.

The security property under test: for a file at or below INMEM_VERIFY_MAX,
the GCM tag MUST be verified before any plaintext touches the disk. The
streaming path (used for large files) writes decryptor.update() output to a
temp file *before* finalize() checks the tag — that transiently lands
unverified plaintext on disk. The in-memory path must not.
"""

import base64
import os
import tempfile

import pytest
from cryptography.exceptions import InvalidTag

import encipherr

KEY = os.urandom(32)
KEY_B64 = base64.urlsafe_b64encode(KEY).decode()


def _encrypt(tmp_path, data: bytes, *, aad: bytes | None = None):
    src = tmp_path / "plain.bin"
    src.write_bytes(data)
    out = tmp_path / "plain.bin.enc"
    encipherr.encrypt_file_stream(str(src), str(out), KEY, aad=aad)
    return out


def test_small_file_roundtrip(tmp_path):
    out = _encrypt(tmp_path, b"hello small payload")
    dec = tmp_path / "out.dec"
    encipherr.decrypt_file_stream(str(out), str(dec), KEY)
    assert dec.read_bytes() == b"hello small payload"


def test_small_file_roundtrip_with_aad(tmp_path):
    out = _encrypt(tmp_path, b"bound payload", aad=b"plain.bin.enc")
    dec = tmp_path / "out.dec"
    encipherr.decrypt_file_stream(str(out), str(dec), KEY, aad=b"plain.bin.enc")
    assert dec.read_bytes() == b"bound payload"


def test_tampered_small_file_never_opens_temp_file(tmp_path, monkeypatch):
    """The core RUP guarantee: a tampered small file is rejected BEFORE any
    temp file is opened, so unverified plaintext never reaches the disk."""
    out = _encrypt(tmp_path, b"sensitive small payload")

    raw = bytearray(out.read_bytes())
    raw[20] ^= 0x01  # flip a ciphertext byte (past nonce(12), before tag)
    out.write_bytes(raw)

    opened = []
    real = tempfile.NamedTemporaryFile

    def spy(*args, **kwargs):
        opened.append(kwargs.get("dir"))
        return real(*args, **kwargs)

    monkeypatch.setattr(encipherr.tempfile, "NamedTemporaryFile", spy)

    dec = tmp_path / "out.dec"
    with pytest.raises(InvalidTag):
        encipherr.decrypt_file_stream(str(out), str(dec), KEY)

    assert opened == [], "temp file opened before tag verification (RUP leak)"
    assert not dec.exists()
    residue = [p for p in os.listdir(tmp_path) if p.startswith(".encipherr_tmp_")]
    assert residue == []


def test_large_file_roundtrip_uses_streaming(tmp_path, monkeypatch):
    """Files above the threshold keep using the streaming path and round-trip."""
    monkeypatch.setattr(encipherr, "INMEM_VERIFY_MAX", 1024)
    data = os.urandom(4096)
    out = _encrypt(tmp_path, data)
    dec = tmp_path / "big.dec"
    encipherr.decrypt_file_stream(str(out), str(dec), KEY)
    assert dec.read_bytes() == data


def test_inmem_max_param_overrides_global(tmp_path, monkeypatch):
    """A per-call inmem_max of 0 (bytes) forces the streaming path even for a
    tiny file — proving the parameter, not just the global, drives the choice."""
    out = _encrypt(tmp_path, b"sensitive small payload")
    raw = bytearray(out.read_bytes())
    raw[20] ^= 0x01
    out.write_bytes(raw)

    opened = []
    real = tempfile.NamedTemporaryFile

    def spy(*args, **kwargs):
        opened.append(kwargs.get("dir"))
        return real(*args, **kwargs)

    monkeypatch.setattr(encipherr.tempfile, "NamedTemporaryFile", spy)

    dec = tmp_path / "out.dec"
    with pytest.raises(InvalidTag):
        encipherr.decrypt_file_stream(str(out), str(dec), KEY, inmem_max=0)

    assert opened, "inmem_max=0 should force the streaming path (temp opened)"


def test_cli_inmem_max_flag_roundtrip(tmp_path, monkeypatch):
    """The --inmem-max flag is wired through decrypt and the file round-trips."""
    src = tmp_path / "f.bin"
    src.write_bytes(b"cli flag payload")
    enc = tmp_path / "f.bin.enc"
    dec = tmp_path / "f.dec"

    monkeypatch.setenv("ENCIPHERR_KEY", KEY_B64)
    encipherr.main(["encrypt", "file", str(src), "-o", str(enc)])
    # get_key() pops ENCIPHERR_KEY after read, so set it again for decrypt.
    monkeypatch.setenv("ENCIPHERR_KEY", KEY_B64)
    encipherr.main(["decrypt", "file", str(enc), "-o", str(dec), "--inmem-max", "0"])

    assert dec.read_bytes() == b"cli flag payload"
