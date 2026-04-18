# Change Log

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
