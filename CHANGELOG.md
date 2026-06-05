# Change Log

## [1.3.3] 2026-06-05 — verify-before-write decryption

On-disk ciphertext format unchanged; existing `.enc` files decrypt exactly as before.

### Security

- **Verify-before-write for small files**: decryption of files at or below `INMEM_VERIFY_MAX` (64 MiB) now happens fully in memory — `AESGCM.decrypt` verifies the GCM tag *before* any plaintext is written to disk. Previously all files used the streaming path, which writes `decryptor.update()` output to a temp file before `finalize()` checks the tag, transiently landing unverified plaintext on disk (a "release of unverified plaintext" / RUP property). Files above the threshold still stream (verifying the whole file in memory would cost ~2x its size in RAM); the temp file is still removed on tag failure and never replaces the target. Encryption is unchanged (it has no RUP concern).
- **`--inmem-max MIB` (new, decrypt only)**: override the in-memory verify threshold per invocation (default 64 MiB). `--inmem-max 0` forces the streaming path for all files; a large value forces verify-before-write regardless of size (at ~2x-file-size RAM cost). File mode only; text mode rejects the flag (text always decrypts in memory).

### Fixes

- Text-mode decrypt exception ordering: `except (binascii.Error, UnicodeEncodeError)` now precedes the bare `except ValueError`. `binascii.Error` is a `ValueError` subclass, so it was previously unreachable — malformed-base64 input got the generic "Invalid input format" message instead of "Cipher text must be base64 encoded." No security impact; error precision only.

### Tests

- Added `tests/test_inmemory_verify.py` (pytest): small-file round-trip (with and without AAD), large-file streaming round-trip, the core guarantee that a tampered small file is rejected **before any temp file is opened**, and the `--inmem-max` override / CLI wiring. Added `tests/test_text_mode_errors.py` for the base64 error-message ordering. `pyproject.toml` gains `[tool.pytest.ini_options] pythonpath = ["."]`.

## [1.3.2] 2026-05-31 — security + UX hardening from internal review

On-disk ciphertext format unchanged unless `--bind-filename` is used; existing `.enc` files still decrypt as before.

### Security

- **`--bind-filename` (new)**: opt-in flag that binds the ciphertext to the output filename's basename via GCM AAD (RFC 5116). Decrypt then requires `--bind-filename` + the same basename or the GCM tag verification fails. Defends against same-extension swap attacks (`secrets.enc` ↔ `passwords.enc`) where an attacker with write access to a vault directory can substitute one ciphertext for another and the user wouldn't notice on decrypt. **File mode only**; text mode rejects the flag (no filename to bind). Moving the file to a different directory still works — only renaming the basename breaks the tag.
- **`ENCIPHERR_KEY` env-var hardening**: `get_key()` now `os.environ.pop('ENCIPHERR_KEY', None)` immediately after read, so any subprocess `encipherr` may fork/exec later cannot inherit the key. Defense-in-depth; the original shell still has its own copy. Linux `/proc/PID/environ` is a frozen snapshot at exec(2) time and remains a same-uid trust-boundary concern.

### UX

- Help-text epilog now references the installed `encipherr` command (not `python3 encipherr.py`) and fixes the long-standing "Exemple" typo.
- `input` argument help now documents the `--` separator for inputs starting with a dash.
- `--bind-filename` is rejected in text mode with a clear error rather than silently doing nothing.
- Type hints added on all 11 core / API-surface functions (`encrypt_bytes`, `decrypt_bytes`, `encrypt_file_stream`, `decrypt_file_stream`, `decode_key`, `get_key`, `_filename_aad`, `gen_key`, `encrypt_cmd`, `decrypt_cmd`, `main`).

### Hygiene

- `build/` was tracked in git as a stale wheel artifact. `.gitignore` now excludes `build/`, `dist/`, `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/` and the file is untracked.
- `cryptography==46.0.3` pin relaxed to `cryptography>=46,<47` so PyCA security patches land without manual bumps; major version still locked (47 may break the AESGCM API surface).
- `scripts/selftest.sh` step number `[9/10]` → `[9/9]`; added `[extra-3]` test case for `--bind-filename` round-trip + rename-rejection + flag-missing-on-bound-file + text-mode rejection.

### Notes

- v1.3.1 (paste-friendly key handling — `genkey` stderr/stdout split + `get_key.strip()`) was developed but never tagged; it is rolled into this release as the [1.3.1] entry below.

## [1.3.1] 2026-05-30 — paste-friendly key handling
On-disk ciphertext format unchanged; all prior `.enc` files still decrypt.
- `genkey` no longer emits a leading space before the key (`print("header:\n", key)` adds a space because `print` defaults to `sep=' '`). The header goes to stderr and the bare key alone goes to stdout, so `encipherr genkey | pbcopy` and `encipherr genkey | tail -1` capture the key cleanly. **Behavior change** for anyone parsing stdout for the header — the header is on stderr now.
- `get_key()` now `.strip()`s `ENCIPHERR_KEY` before use, so a stray trailing newline or surrounding whitespace from copy-paste no longer produces a misleading `Invalid encryption key format` error. (Python's `str.strip()` covers ASCII whitespace and NBSP ` `; truly invisible chars like ZWSP `​` still need to be cleaned externally.)

## [1.3.0] 2026-04-18 — engineering cleanup
On-disk ciphertext format unchanged; all prior `.enc` files still decrypt.
- Single source of version truth: `pyproject.toml` drives `--version` via `importlib.metadata`.
- Removed stray `DEBUG BUILD ACTIVE` debug print from the entry point.
- Removed unreachable stdin (`-`) placeholder branch; no user-visible feature change.
- Tightened `decrypt_bytes` minimum length check from 13 to 28 bytes (nonce + tag); legal ciphertexts are always >= 28.
- All error messages now go to stderr; file-mode encrypt/decrypt print a single concise success line.
- File mode now rejects multi-argument input explicitly (quote paths that contain spaces).
- Internal cleanup: PEP 8 function names (`gen_key`/`encrypt_cmd`/`decrypt_cmd`), removed `is_valid_file` wrapper, dropped `except Exception` catch-alls in text mode.

## [released] 2021-12-27 first stable version
- A lot of bugs have been fixed
- Optimized code.
- Simple usage;big change in the way encipherr-cli is operated and well documented in help section.
