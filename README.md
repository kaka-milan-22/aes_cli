# Encipherr-CLI

Encipherr-CLI is a local encryption/decryption tool for terminal usage.

## Features
- AES-256-GCM authenticated encryption
- Text and file encryption/decryption
- Key via environment variable (`ENCIPHERR_KEY`) or `-k/--key`
- File encryption writes a new `.enc` file (does not overwrite original)
- File decryption writes a new output file (auto-fallback to `.dec` when needed)
- Clear error messages for invalid key/cipher data

## Requirements
- Python 3.8+
- `cryptography` package

## Install
```bash
pip install cryptography
```

## Quick Start
### 1. Generate key
```bash
python3 encipherr.py genkey
```

Example output:
```text
your random generated key :
 sPWlTYYiVpxOzY-7qvFX5EIBP3HfNNpwMkPXRkVjXV4=
```

### 2. Set key (recommended: environment variable)
```bash
export ENCIPHERR_KEY="sPWlTYYiVpxOzY-7qvFX5EIBP3HfNNpwMkPXRkVjXV4="
```

### 3. Encrypt text
```bash
python3 encipherr.py encrypt text "hello world"
```

### 4. Decrypt text
```bash
python3 encipherr.py decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## File Usage
### Encrypt file
```bash
python3 encipherr.py encrypt file /path/to/data.txt
```

Result:
- Input: `/path/to/data.txt`
- Output: `/path/to/data.txt.enc`

### Decrypt file
```bash
python3 encipherr.py decrypt file /path/to/data.txt.enc
```

Result:
- Preferred output: `/path/to/data.txt`
- If `/path/to/data.txt` already exists, output becomes `/path/to/data.txt.dec`

## Command Help
```bash
python3 encipherr.py -h
python3 encipherr.py encrypt -h
python3 encipherr.py decrypt -h
```

## CLI Syntax
```bash
python3 encipherr.py genkey
python3 encipherr.py encrypt {text|file} <input...> [-k KEY]
python3 encipherr.py decrypt {text|file} <input...> [-k KEY]
```

## Security Notes
- Use `genkey` output directly. Key must be URL-safe Base64 and decode to 32 bytes.
- Do not store key in shell history, screenshots, or public logs.
- Prefer `ENCIPHERR_KEY` over `-k` to reduce exposure in process list/history.
- Keep encrypted files and keys in separate secure locations.

## Nonce Strategy
For AES-GCM, nonce uniqueness per key is critical.

This CLI uses:
- 12-byte nonce format: `4-byte random prefix + 8-byte counter`
- Per-key persisted counter state file (default in `/tmp`)
- File locking to reduce collision risk across concurrent processes

## Compatibility Notice
This version uses AES-256-GCM format and is not compatible with older Fernet ciphertexts.

## License
[MIT](https://choosealicense.com/licenses/mit/)
