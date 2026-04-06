# Encipherr-CLI

Encipherr-CLI is a local encryption/decryption tool for terminal usage.

## Languages
Default: English 🇺🇸  
🇺🇸 [English Documentation](README.md) | 🇨🇳 [中文文档](i18n/README.zh-CN.md) | 🇪🇸 [Documentacion en Espanol](i18n/README.es.md) | 🇮🇹 [Documentazione in Italiano](i18n/README.it.md)  
🇩🇪 [Deutsche Dokumentation](i18n/README.de.md) | 🇫🇷 [Documentation Francaise](i18n/README.fr.md)

## Features
- AES-256-GCM authenticated encryption
- Text and file encryption/decryption
- Key via environment variable (`ENCIPHERR_KEY`) only
- File encryption writes a new `.enc` file (does not overwrite original)
- File decryption writes a new output file (auto-fallback to `.dec` when needed)
- `--output PATH` / `-o PATH` to specify an explicit output file path (file mode only)
- `--overwrite` flag to force-overwrite existing output files
- Clear error messages for invalid key/cipher data

## Install

> **Note:** This project is not published on PyPI. Install from GitHub instead.

**Recommended (global CLI tool):**
```bash
uv tool install git+https://github.com/kaka-milan-22/aes_cli.git
```

**Verify installation:**
```bash
encipherr --help
```

<details>
<summary>Developer / local install</summary>

```bash
git clone https://github.com/kaka-milan-22/aes_cli.git
cd aes_cli
uv tool install .
# or
pip install -e .
```
</details>

**Name mapping:**
- CLI command: `encipherr`
- Python package: `encipherr-cli`
- Repository: `aes_cli`

## Quick Start
### 1. Generate key
```bash
encipherr genkey
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
encipherr encrypt text "hello world"
```

### 4. Decrypt text
```bash
encipherr decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## File Usage
### Encrypt file
```bash
encipherr encrypt file /path/to/data.txt
```

Result:
- Input: `/path/to/data.txt`
- Output: `/path/to/data.txt.enc`

### Decrypt file
```bash
encipherr decrypt file /path/to/data.txt.enc
```

Result:
- Preferred output: `/path/to/data.txt`
- If `/path/to/data.txt` already exists, output becomes `/path/to/data.txt.dec`

### Force overwrite existing output file
Use `--overwrite` to overwrite an already-existing output file instead of aborting:
```bash
encipherr encrypt file /path/to/data.txt --overwrite
encipherr decrypt file /path/to/data.txt.enc --overwrite
```

### Explicit output path (`--output` / `-o`)
Use `--output PATH` (or `-o PATH`) to write the result to a specific path instead of the auto-derived name.
If the path already exists the command aborts — add `--overwrite` to allow it:
```bash
encipherr encrypt file /path/to/data.txt --output /tmp/encrypted.enc
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

**Rules:**
- `--output` is only valid in **file** mode. Using it in text mode results in an error.
- If `--output` is set and the path already exists, the command errors unless `--overwrite` is also set.
- Using `--output` does not change the ciphertext format or key handling in any way.

## Command Help
```bash
encipherr -h
encipherr --version
encipherr encrypt -h
encipherr decrypt -h
```

## CLI Syntax
```bash
encipherr genkey
encipherr encrypt {text|file} <input...> [--output PATH] [--overwrite]
encipherr decrypt {text|file} <input...> [--output PATH] [--overwrite]
```

## Self Test
```bash
bash scripts/selftest.sh
```

## Security Notes
- Use `genkey` output directly. Key must be URL-safe Base64 and decode to 32 bytes.
- Do not store key in shell history, screenshots, or public logs.
- This version intentionally does not support `-k/--key`.
- Keep encrypted files and keys in separate secure locations.
- This tool is designed for local data protection. It is not a key management system.

## Nonce Strategy
For AES-GCM, nonce uniqueness per key is critical.

This CLI uses:
- 12-byte cryptographically secure random nonce (`os.urandom(12)`)
- No local nonce state files
- Nonce uniqueness relies solely on secure randomness; this tool is intended for local and moderate usage, not high-frequency automated batch encryption.

## Compatibility Notice
This version uses AES-256-GCM format and is not compatible with older Fernet ciphertexts.
This tool guarantees backward compatibility for ciphertexts generated within the same major version.

## License
[MIT](https://choosealicense.com/licenses/mit/)
