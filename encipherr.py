#!/usr/bin/python3

# Encipherr-cli v1.0.0

# Cli version of the open source web app encipherr.Visit https://encipherr.pythonanywhere.com/.
# Made by Oussama Ben Sassi https://github.com/Oussama1403

# Contribute to the development of Encipherr-cli https://github.com/Oussama1403/Encipherr-CLI.
# Star the repo of Encipherr-cli if you like it :).

import argparse
import base64
import binascii
import os
import sys
import tempfile
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VERSION = "1.2.0"

def get_key(args):
    """Get encryption key from environment variable only."""
    env_key = os.environ.get('ENCIPHERR_KEY')
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key
    
    print("Error: No encryption key provided!")
    print("Please provide a key via:")
    print("  Environment variable only: export ENCIPHERR_KEY='your_key'")
    sys.exit(1)

def decode_key(key):
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

def GenKey(args):
    key = os.urandom(32)
    encoded_key = base64.urlsafe_b64encode(key).decode()
    print("your random generated key :\n",encoded_key)

def is_valid_file(path):
    if not os.path.isfile(path):
        return False
    else:
        return True

def encrypted_output_path(path):
    """Return encrypted file path without overwriting source file."""
    return path + ".enc"

def decrypted_output_path(path):
    """Return decrypted file path without overwriting source file."""
    if path.endswith(".enc"):
        candidate = path[:-4]
        if os.path.exists(candidate):
            return candidate + ".dec"
        return candidate
    return path + ".dec"

def assert_output_not_exists(path):
    """Fail fast to avoid accidental overwrite of existing files."""
    if os.path.exists(path):
        print("Error: Output file already exists:", path)
        sys.exit(1)

def encrypt_bytes(data, raw_key):
    """Encrypt bytes as nonce(12) + ciphertext_and_tag."""
    nonce = os.urandom(12)
    aesgcm = AESGCM(raw_key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_bytes(data, raw_key):
    """Decrypt bytes encoded as nonce(12) + ciphertext_and_tag."""
    if len(data) < 13:
        raise ValueError("Cipher data is too short.")
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(raw_key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def encrypt_file_stream(input_path, output_path, raw_key, chunk_size=1024 * 1024):
    """Stream-encrypt file as nonce(12) + ciphertext + tag(16)."""
    nonce = os.urandom(12)
    encryptor = Cipher(algorithms.AES(raw_key), modes.GCM(nonce)).encryptor()

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

def decrypt_file_stream(input_path, output_path, raw_key, chunk_size=1024 * 1024):
    """Stream-decrypt file encoded as nonce(12) + ciphertext + tag(16)."""
    total_size = os.path.getsize(input_path)
    min_size = 12 + 16
    if total_size < min_size:
        raise ValueError("Cipher file is too short.")

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

def Encrypt(args):
    key = get_key(args)
    if args.mode in ['file','FILE']:
        try:
            raw_key = decode_key(key)
            path = " ".join(args.input)
            print("specified path:",path)
            
            if is_valid_file(path):
                pass
            else:
                print("Error in provided path !") 
                sys.exit(1)       
            
            output_path = encrypted_output_path(path)
            if not getattr(args, 'overwrite', False):
                assert_output_not_exists(output_path)
            encrypt_file_stream(path, output_path, raw_key)
            print("the file at ",path," is encrypted")
            print("encrypted output:", output_path)
        except ValueError:
            print("Error: Invalid encryption key format. Use genkey output (base64 32-byte key).")
            sys.exit(1)
        except PermissionError:
            print("Error: Permission denied while reading/writing file.")
            sys.exit(1)
        except OSError as exc:
            print("Error: File operation failed:", exc)
            sys.exit(1)

    else:
        try:
            raw_key = decode_key(key)
            #text encryption mode
            value = " ".join(args.input)
            plaintext = value.encode()
            encryptedtext = encrypt_bytes(plaintext, raw_key)
            encoded = base64.urlsafe_b64encode(encryptedtext).decode()
            print("----- Encrypted start -----")
            print(encoded)
            print("----- Encrypted end -----")
        except ValueError:
            print("Error: Invalid encryption key format. Use genkey output (base64 32-byte key).")
            sys.exit(1)
        except Exception as exc:
            print("Error in Encryption:", exc)
            sys.exit(1)

def Decrypt(args):
    key = get_key(args)
    if args.mode in ['file',"FILE"]:
        try:
            raw_key = decode_key(key)
            path = " ".join(args.input)
            print("specified path:",path)
            
            if is_valid_file(path):
                pass
            else:
                print("Error in provided path !") 
                sys.exit(1)
            
            output_path = decrypted_output_path(path)
            if not getattr(args, 'overwrite', False):
                assert_output_not_exists(output_path)
            decrypt_file_stream(path, output_path, raw_key)
            print("the file at ",path," is decrypted")
            print("decrypted output:", output_path)
        except ValueError:
            print("Error: Invalid input format. Key or cipher data is invalid.")
            sys.exit(1)
        except InvalidTag:
            print("Error: Decryption failed. Key is wrong or file content is invalid/corrupted.")
            sys.exit(1)
        except PermissionError:
            print("Error: Permission denied while reading/writing file.")
            sys.exit(1)
        except OSError as exc:
            print("Error: File operation failed:", exc)
            sys.exit(1)
   
    
    else:
        try:
            raw_key = decode_key(key)
            #text decryption mode
            value = " ".join(args.input)
            token = value.encode()
            cipher_bytes = base64.urlsafe_b64decode(token)
            decryptedtext = decrypt_bytes(cipher_bytes, raw_key)
            print('-'*5,"decrypted text",'-'*5)
            print(decryptedtext.decode())
        except ValueError:
            print("Error: Invalid input format. Key or cipher text is invalid.")
            sys.exit(1)
        except (binascii.Error, UnicodeEncodeError):
            print("Error: Cipher text must be base64 encoded.")
            sys.exit(1)
        except InvalidTag:
            print("Error: Decryption failed. Key is wrong or cipher text is invalid/corrupted.")
            sys.exit(1)
        except Exception as exc:
            print("Error in Decryption:", exc)
            sys.exit(1)


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description=f"Encipherr-CLI {VERSION} (https://github.com/Oussama1403/Encipherr-CLI)",
epilog='Exemple:\n\n python3 encipherr.py genkey\n export ENCIPHERR_KEY="your_generated_key"\n python3 encipherr.py encrypt TEXT encipherr is awesome!\n python3 encipherr.py decrypt FILE path/to/file.enc\n\nan issue or a feature request ? contribute to the development of Encipherr-cli https://github.com/Oussama1403/Encipherr-CLI:)')
parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
subparsers = parser.add_subparsers()

GenKey_parser = subparsers.add_parser('genkey',help="Generate a random key for encrypting/decrypting.")
GenKey_parser.set_defaults(func=GenKey)
 
Encrypt_parser = subparsers.add_parser('encrypt',help="encrypt mode input")
Encrypt_parser.add_argument('mode',type=str,choices=['text','TEXT','file','FILE'],help="TEXT or FILE")
Encrypt_parser.add_argument('input',type=str,nargs="+",help="A text if in text mode or path/to/file if in file mode")
Encrypt_parser.add_argument('--overwrite', action='store_true', help="Overwrite output file if it already exists")
Encrypt_parser.set_defaults(func=Encrypt)


Decrypt_parser = subparsers.add_parser('decrypt',help="decrypt mode input")
Decrypt_parser.add_argument('mode',type=str,choices=['text','TEXT','file','FILE'],help="TEXT or FILE")
Decrypt_parser.add_argument('input',type=str,nargs="+",help="A text if in text mode or path/to/file if in file mode")
Decrypt_parser.add_argument('--overwrite', action='store_true', help="Overwrite output file if it already exists")
Decrypt_parser.set_defaults(func=Decrypt)

def main(argv=None):
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
    print("DEBUG BUILD ACTIVE")
    raise SystemExit(main())
