#!/usr/bin/python3

# Encipherr-cli

from __future__ import annotations

import argparse
import base64
import binascii
import os
import sys
import tempfile
from typing import Any
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError
    try:
        VERSION = _pkg_version("encipherr-cli")
    except PackageNotFoundError:
        VERSION = "0.0.0+local"
except ImportError:
    VERSION = "0.0.0+local"


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def get_key(args: argparse.Namespace) -> bytes:
    """Get encryption key from environment variable only.

    Strips surrounding whitespace (newline, space, NBSP, etc.) before use —
    pasted keys frequently carry a trailing newline or the leading space
    that pre-v1.3.1 `genkey`'s "your random generated key :\\n <key>" output
    produced.

    v1.3.2: after read, the variable is removed from os.environ so any
    fork/exec the process does later cannot inherit the key. Linux
    /proc/PID/environ is a frozen snapshot taken at exec(2) time and
    cannot be scrubbed from userspace — that's bounded by the same-uid
    trust boundary.
    """
    env_key = os.environ.get('ENCIPHERR_KEY')
    if env_key:
        # Pop immediately after read so subprocesses don't inherit the key.
        # The original shell that exported it still has its own copy.
        os.environ.pop('ENCIPHERR_KEY', None)
        return env_key.strip().encode()

    eprint("Error: No encryption key provided!")
    eprint("Please provide a key via:")
    eprint("  Environment variable only: export ENCIPHERR_KEY='your_key'")
    sys.exit(1)


def decode_key(key: bytes | str) -> bytes:
    """Decode urlsafe base64 key into raw 32-byte AES-256 key."""
    if isinstance(key, str):
        key = key.encode()
    try:
        decoded = base64.urlsafe_b64decode(key)
    except (binascii.Error, ValueError):
        raise ValueError("Key must be urlsafe-base64 encoded.")
    if len(decoded) != 32:
        raise ValueError("Decoded key must be exactly 32 bytes for AES-256.")
    return decoded


def gen_key(args: argparse.Namespace) -> None:
    key = os.urandom(32)
    encoded_key = base64.urlsafe_b64encode(key).decode()
    # Header on stderr, key alone on stdout — so `encipherr genkey | clip` /
    # `encipherr genkey | tail -1` capture the bare key with no leading
    # space or banner. (`print("foo:\n", key)` would emit a leading space
    # because print's default sep=' '.)
    eprint("your random generated key:")
    print(encoded_key)


def encrypted_output_path(path: str) -> str:
    """Return encrypted file path without overwriting source file."""
    return path + ".enc"


def decrypted_output_path(path: str) -> str:
    """Return decrypted file path without overwriting source file."""
    if path.endswith(".enc"):
        candidate = path[:-4]
        if os.path.exists(candidate):
            return candidate + ".dec"
        return candidate
    return path + ".dec"


def assert_output_not_exists(path: str) -> None:
    """Fail fast to avoid accidental overwrite of existing files."""
    if os.path.exists(path):
        eprint("Error: Output file already exists:", path)
        sys.exit(1)


def _filename_aad(path: str) -> bytes:
    """Build the AAD value for --bind-filename: the basename, UTF-8 encoded.

    Using basename (not full path) means moving the file to a different
    directory keeps it decryptable; only RENAMING (basename change) breaks
    the GCM tag. That matches the threat model: defend against
    same-extension swap attacks (`secrets.enc` ↔ `passwords.enc`) while
    not punishing benign relocation.
    """
    return os.path.basename(path).encode("utf-8")


def encrypt_bytes(data: bytes, raw_key: bytes, aad: bytes | None = None) -> bytes:
    """Encrypt bytes as nonce(12) + ciphertext_and_tag.

    `aad` is optional Additional Authenticated Data (RFC 5116). When set,
    decryption MUST supply the same value or GCM raises InvalidTag.
    Wire format is unchanged — AAD lives only in the tag computation.
    """
    nonce = os.urandom(12)
    aesgcm = AESGCM(raw_key)
    ciphertext = aesgcm.encrypt(nonce, data, aad)
    return nonce + ciphertext


def decrypt_bytes(data: bytes, raw_key: bytes, aad: bytes | None = None) -> bytes:
    """Decrypt bytes encoded as nonce(12) + ciphertext_and_tag.

    `aad` must exactly match what was passed at encrypt time (or both
    must be None) — otherwise GCM raises InvalidTag.
    """
    if len(data) < 12 + 16:
        raise ValueError("Cipher data too short: need at least nonce(12)+tag(16) bytes.")
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(raw_key)
    return aesgcm.decrypt(nonce, ciphertext, aad)


def encrypt_file_stream(
    input_path: str,
    output_path: str,
    raw_key: bytes,
    *,
    aad: bytes | None = None,
    chunk_size: int = 1024 * 1024,
) -> None:
    """Stream-encrypt file as nonce(12) + ciphertext + tag(16).

    Optional `aad` is bound into the GCM tag — decrypt must supply the
    same value. Wire format unchanged.
    """
    nonce = os.urandom(12)
    encryptor = Cipher(algorithms.AES(raw_key), modes.GCM(nonce)).encryptor()
    if aad:
        encryptor.authenticate_additional_data(aad)

    out_dir = os.path.dirname(output_path) or "."
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=out_dir, prefix=".encipherr_tmp_") as tmp_file:
            tmp_path = tmp_file.name
            with open(input_path, "rb") as in_file:
                tmp_file.write(nonce)
                while True:
                    chunk = in_file.read(chunk_size)
                    if not chunk:
                        break
                    tmp_file.write(encryptor.update(chunk))
                tmp_file.write(encryptor.finalize())
                tmp_file.write(encryptor.tag)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
        os.replace(tmp_path, output_path)
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


# Files at or below this size decrypt fully in memory: the GCM tag is
# verified BEFORE any plaintext is written to disk, so a wrong key or a
# tampered ciphertext never lands unverified plaintext on the filesystem
# (no "release of unverified plaintext"). Larger files fall back to the
# streaming path, where update() output is written before finalize()
# checks the tag — unavoidable without buffering the whole file. Peak
# memory for the in-memory path is ~2x the file size.
INMEM_VERIFY_MAX = 64 * 1024 * 1024  # 64 MiB


def _atomic_write(output_path: str, data: bytes) -> None:
    """Write `data` to output_path atomically via a fsync'd temp + os.replace."""
    out_dir = os.path.dirname(output_path) or "."
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=out_dir, prefix=".encipherr_tmp_") as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(data)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_path, output_path)
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _decrypt_file_in_memory(
    input_path: str,
    output_path: str,
    raw_key: bytes,
    *,
    aad: bytes | None = None,
) -> None:
    """Decrypt a whole file in memory, verifying the tag before any write.

    decrypt_bytes() runs AESGCM.decrypt, which raises InvalidTag on a wrong
    key / tampered data BEFORE we ever open the output temp file — so no
    unverified plaintext reaches disk.
    """
    with open(input_path, "rb") as in_file:
        blob = in_file.read()
    plaintext = decrypt_bytes(blob, raw_key, aad)
    _atomic_write(output_path, plaintext)


def decrypt_file_stream(
    input_path: str,
    output_path: str,
    raw_key: bytes,
    *,
    aad: bytes | None = None,
    chunk_size: int = 1024 * 1024,
    inmem_max: int | None = None,
) -> None:
    """Decrypt file encoded as nonce(12) + ciphertext + tag(16).

    Files at or below the in-memory threshold (in bytes) are verified in
    memory before any write; larger files stream chunk-by-chunk. The
    threshold is `inmem_max` when given, else the module default
    INMEM_VERIFY_MAX.
    """
    total_size = os.path.getsize(input_path)
    min_size = 12 + 16
    if total_size < min_size:
        raise ValueError("Cipher file is too short.")

    threshold = INMEM_VERIFY_MAX if inmem_max is None else inmem_max
    if total_size <= threshold:
        _decrypt_file_in_memory(input_path, output_path, raw_key, aad=aad)
        return

    out_dir = os.path.dirname(output_path) or "."
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=out_dir, prefix=".encipherr_tmp_") as tmp_file:
            tmp_path = tmp_file.name
            with open(input_path, "rb") as in_file:
                nonce = in_file.read(12)
                in_file.seek(total_size - 16)
                tag = in_file.read(16)
                in_file.seek(12)

                decryptor = Cipher(algorithms.AES(raw_key), modes.GCM(nonce, tag)).decryptor()
                if aad:
                    decryptor.authenticate_additional_data(aad)
                remaining = total_size - 12 - 16

                while remaining > 0:
                    to_read = chunk_size if remaining > chunk_size else remaining
                    chunk = in_file.read(to_read)
                    if not chunk:
                        break
                    tmp_file.write(decryptor.update(chunk))
                    remaining -= len(chunk)

                tmp_file.write(decryptor.finalize())
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
        os.replace(tmp_path, output_path)
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _file_mode_path(args: argparse.Namespace) -> str:
    """Validate file-mode input and return the single path arg."""
    if len(args.input) != 1:
        eprint("Error: file mode expects exactly one path argument. "
               "If your path contains spaces, quote it.")
        sys.exit(2)
    return args.input[0]


def encrypt_cmd(args: argparse.Namespace) -> None:
    key = get_key(args)
    if args.mode in ['file', 'FILE']:
        try:
            raw_key = decode_key(key)
            path = _file_mode_path(args)

            if not os.path.isfile(path):
                eprint("Error: input file not found:", path)
                sys.exit(1)

            output_path = args.output if args.output else encrypted_output_path(path)
            if not args.overwrite:
                assert_output_not_exists(output_path)
            # --bind-filename: AAD = basename of the output (.enc) file. Decrypt
            # must pass --bind-filename + same basename or GCM rejects. Defends
            # against same-extension swap attacks (`secrets.enc` ↔ `pwds.enc`).
            aad = _filename_aad(output_path) if args.bind_filename else None
            encrypt_file_stream(path, output_path, raw_key, aad=aad)
            print(f"Encrypted: {path} -> {output_path}")
            if args.bind_filename:
                print(f"  (bound to filename {os.path.basename(output_path)!r}; "
                      "decrypt requires --bind-filename + same basename)")
        except ValueError:
            eprint("Error: Invalid encryption key format. Use genkey output (base64 32-byte key).")
            sys.exit(1)
        except PermissionError:
            eprint("Error: Permission denied while reading/writing file.")
            sys.exit(1)
        except OSError as exc:
            eprint("Error: File operation failed:", exc)
            sys.exit(1)

    else:
        try:
            if args.output:
                eprint("Error: --output is only valid in file mode.")
                sys.exit(1)
            if args.bind_filename:
                eprint("Error: --bind-filename is only valid in file mode "
                       "(text mode has no filename to bind to).")
                sys.exit(1)
            raw_key = decode_key(key)
            value = " ".join(args.input)
            plaintext = value.encode()
            encryptedtext = encrypt_bytes(plaintext, raw_key)
            encoded = base64.urlsafe_b64encode(encryptedtext).decode()
            print("----- Encrypted start -----")
            print(encoded)
            print("----- Encrypted end -----")
        except ValueError:
            eprint("Error: Invalid encryption key format. Use genkey output (base64 32-byte key).")
            sys.exit(1)


def decrypt_cmd(args: argparse.Namespace) -> None:
    key = get_key(args)
    if args.mode in ['file', 'FILE']:
        try:
            raw_key = decode_key(key)
            path = _file_mode_path(args)

            if not os.path.isfile(path):
                eprint("Error: input file not found:", path)
                sys.exit(1)

            output_path = args.output if args.output else decrypted_output_path(path)
            if not args.overwrite:
                assert_output_not_exists(output_path)
            # --bind-filename: AAD = basename of the input (.enc) file. Must
            # match the basename used at encrypt time, else GCM raises
            # InvalidTag and we surface "Decryption failed".
            aad = _filename_aad(path) if args.bind_filename else None
            # --inmem-max is given in MiB; convert to bytes. None -> module default.
            inmem_max = args.inmem_max * 1024 * 1024 if args.inmem_max is not None else None
            decrypt_file_stream(path, output_path, raw_key, aad=aad, inmem_max=inmem_max)
            print(f"Decrypted: {path} -> {output_path}")
        except ValueError:
            eprint("Error: Invalid input format. Key or cipher data is invalid.")
            sys.exit(1)
        except InvalidTag:
            if args.bind_filename:
                eprint("Error: Decryption failed. Key is wrong, file content is "
                       "invalid/corrupted, or the filename does not match the one "
                       "used at encrypt time (--bind-filename binds basename into the tag).")
            else:
                eprint("Error: Decryption failed. Key is wrong or file content is invalid/corrupted.")
            sys.exit(1)
        except PermissionError:
            eprint("Error: Permission denied while reading/writing file.")
            sys.exit(1)
        except OSError as exc:
            eprint("Error: File operation failed:", exc)
            sys.exit(1)

    else:
        try:
            if args.output:
                eprint("Error: --output is only valid in file mode.")
                sys.exit(1)
            if args.bind_filename:
                eprint("Error: --bind-filename is only valid in file mode "
                       "(text mode has no filename to bind to).")
                sys.exit(1)
            if args.inmem_max is not None:
                eprint("Error: --inmem-max is only valid in file mode "
                       "(text mode always decrypts in memory).")
                sys.exit(1)
            raw_key = decode_key(key)
            value = " ".join(args.input)
            token = value.encode()
            cipher_bytes = base64.urlsafe_b64decode(token)
            decryptedtext = decrypt_bytes(cipher_bytes, raw_key)
            print('-' * 5, "decrypted text", '-' * 5)
            print(decryptedtext.decode())
        # binascii.Error / UnicodeEncodeError are ValueError subclasses, so
        # this specific clause MUST precede the bare `except ValueError` below
        # — otherwise malformed-base64 input gets the generic message.
        except (binascii.Error, UnicodeEncodeError):
            eprint("Error: Cipher text must be base64 encoded.")
            sys.exit(1)
        except ValueError:
            eprint("Error: Invalid input format. Key or cipher text is invalid.")
            sys.exit(1)
        except InvalidTag:
            eprint("Error: Decryption failed. Key is wrong or cipher text is invalid/corrupted.")
            sys.exit(1)


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=f"Encipherr-CLI {VERSION} (https://github.com/kaka-milan-22/aes_cli.git)",
    epilog='Example:\n\n encipherr genkey\n export ENCIPHERR_KEY="your_generated_key"\n encipherr encrypt TEXT encipherr is awesome!\n encipherr decrypt FILE path/to/file.enc\n\nNote: for inputs that start with a dash, use "--" to end argparse flag parsing:\n   encipherr encrypt text -- -starts-with-dash')
parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
subparsers = parser.add_subparsers()

gen_key_parser = subparsers.add_parser('genkey', help="Generate a random key for encrypting/decrypting.")
gen_key_parser.set_defaults(func=gen_key)

encrypt_parser = subparsers.add_parser('encrypt', help="encrypt mode input")
encrypt_parser.add_argument('mode', type=str, choices=['text', 'TEXT', 'file', 'FILE'], help="TEXT or FILE")
encrypt_parser.add_argument('input', type=str, nargs="+",
                             help="A text if in text mode or path/to/file if in file mode (prefix with -- if input starts with a dash)")
encrypt_parser.add_argument('--output', '-o', metavar='PATH', help="Output file path (file mode only)")
encrypt_parser.add_argument('--overwrite', action='store_true', help="Overwrite output file if it already exists")
encrypt_parser.add_argument('--bind-filename', action='store_true',
                             help="Bind ciphertext to the output filename (basename) via GCM AAD; "
                                  "decrypt then requires --bind-filename + the same basename. "
                                  "Defends against same-extension swap attacks. (file mode only)")
encrypt_parser.set_defaults(func=encrypt_cmd)

decrypt_parser = subparsers.add_parser('decrypt', help="decrypt mode input")
decrypt_parser.add_argument('mode', type=str, choices=['text', 'TEXT', 'file', 'FILE'], help="TEXT or FILE")
decrypt_parser.add_argument('input', type=str, nargs="+",
                             help="A text if in text mode or path/to/file if in file mode (prefix with -- if input starts with a dash)")
decrypt_parser.add_argument('--output', '-o', metavar='PATH', help="Output file path (file mode only)")
decrypt_parser.add_argument('--overwrite', action='store_true', help="Overwrite output file if it already exists")
decrypt_parser.add_argument('--bind-filename', action='store_true',
                             help="Require the GCM AAD to match the input file's basename "
                                  "(needed only for files encrypted with --bind-filename). (file mode only)")
decrypt_parser.add_argument('--inmem-max', metavar='MIB', type=int, default=None,
                            help="Max file size (in MiB) to decrypt fully in memory, where the GCM "
                                 "tag is verified before any plaintext is written to disk. Larger "
                                 "files stream. Default 64. Use 0 to always stream. (file mode only)")
decrypt_parser.set_defaults(func=decrypt_cmd)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help(sys.stderr)
        return 1

    args.func(args)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
