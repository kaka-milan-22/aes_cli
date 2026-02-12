#!/usr/bin/python3

# Encipherr-cli v1.0.0

# Cli version of the open source web app encipherr.Visit https://encipherr.pythonanywhere.com/.
# Made by Oussama Ben Sassi https://github.com/Oussama1403

# Contribute to the development of Encipherr-cli https://github.com/Oussama1403/Encipherr-CLI.
# Star the repo of Encipherr-cli if you like it :).

import argparse
import base64
import binascii
import hashlib
import os
import sys
import fcntl
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_key(args):
    """Get encryption key from args or environment variable."""
    if args.key:
        return args.key.encode() if isinstance(args.key, str) else args.key
    
    env_key = os.environ.get('ENCIPHERR_KEY')
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key
    
    print("Error: No encryption key provided!")
    print("Please provide a key via:")
    print("  1. Command line argument: python3 encipherr.py encrypt TEXT your_text -k your_key")
    print("  2. Environment variable: export ENCIPHERR_KEY='your_key'")
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

def nonce_state_path(raw_key):
    """Return per-key nonce state file path."""
    key_id = hashlib.sha256(raw_key).hexdigest()[:16]
    state_dir = os.environ.get("ENCIPHERR_NONCE_DIR", "/tmp")
    return os.path.join(state_dir, "encipherr_nonce_" + key_id + ".bin")

def next_nonce(raw_key):
    """
    Build a 96-bit nonce as 4-byte random prefix + 8-byte counter.
    Counter is persisted per key to reduce nonce reuse risk across runs.
    """
    path = nonce_state_path(raw_key)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(fd, "r+b") as state_file:
        fcntl.flock(state_file.fileno(), fcntl.LOCK_EX)
        state_file.seek(0)
        data = state_file.read()

        if len(data) == 12:
            prefix = data[:4]
            counter = int.from_bytes(data[4:], "big")
        else:
            prefix = os.urandom(4)
            counter = 0

        nonce = prefix + counter.to_bytes(8, "big")
        next_counter = (counter + 1) & ((1 << 64) - 1)
        if next_counter == 0:
            # Extremely unlikely rollover; rotate prefix defensively.
            prefix = os.urandom(4)

        state_file.seek(0)
        state_file.truncate()
        state_file.write(prefix + next_counter.to_bytes(8, "big"))
        state_file.flush()
        os.fsync(state_file.fileno())
        fcntl.flock(state_file.fileno(), fcntl.LOCK_UN)

    return nonce

def encrypt_bytes(data, raw_key):
    """Encrypt bytes as nonce(12) + ciphertext_and_tag."""
    nonce = next_nonce(raw_key)
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

def Encrypt(args):
    key = get_key(args)
    if args.mode in ['file','FILE']:
        try:
            raw_key = decode_key(key)
            path = " ".join(args.input)
            print("specified path:",path)
            
            if is_valid_file(path):
                with open(path,'rb') as f:
                    data = f.read()
            else:
                print("Error in provided path !") 
                sys.exit(1)       
            
            output_path = encrypted_output_path(path)
            assert_output_not_exists(output_path)
            encryptedfile = encrypt_bytes(data, raw_key)
            with open(output_path,'wb') as f:
                f.write(encryptedfile)
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
            print()
            print('-'*5,"Encrypted text",'-'*5)
            print()
            print(encoded)
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
                with open(path,'rb') as f:
                    data = f.read()
            else:
                print("Error in provided path !") 
                sys.exit(1)
            
            output_path = decrypted_output_path(path)
            assert_output_not_exists(output_path)
            decryptedfile = decrypt_bytes(data, raw_key)
            with open(output_path,'wb') as f:
                f.write(decryptedfile)
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
            print()
            print('-'*5,"decrypted text",'-'*5)
            print()
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


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description="Encipherr-CLI 1.0.0 (https://github.com/Oussama1403/Encipherr-CLI)",
epilog='Exemple:\n\n python3 encipherr.py genkey\n export ENCIPHERR_KEY="your_generated_key"\n python3 encipherr.py encrypt TEXT encipherr is awesome!\n ---or with key argument---\n python3 encipherr.py encrypt TEXT "hello world" -k ueVEtmfzr8d...\n python3 encipherr.py decrypt FILE path/to/file -k ueVEtmfzr8d...\n\nan issue or a feature request ? contribute to the development of Encipherr-cli https://github.com/Oussama1403/Encipherr-CLI:)')
subparsers = parser.add_subparsers()

GenKey_parser = subparsers.add_parser('genkey',help="Generate a random key for encrypting/decrypting.")
GenKey_parser.set_defaults(func=GenKey)
 
Encrypt_parser = subparsers.add_parser('encrypt',help="encrypt mode input [key]")
Encrypt_parser.add_argument('mode',type=str,choices=['text','TEXT','file','FILE'],help="TEXT or FILE")
Encrypt_parser.add_argument('input',type=str,nargs="+",help="A text if in text mode or path/to/file if in file mode")
Encrypt_parser.add_argument('-k','--key',type=str,help="your key for encrypting/decrypting (or use ENCIPHERR_KEY env variable)")
Encrypt_parser.set_defaults(func=Encrypt)


Decrypt_parser = subparsers.add_parser('decrypt',help="decrypt mode input [key]")
Decrypt_parser.add_argument('mode',type=str,choices=['text','TEXT','file','FILE'],help="TEXT or FILE")
Decrypt_parser.add_argument('input',type=str,nargs="+",help="A text if in text mode or path/to/file if in file mode")
Decrypt_parser.add_argument('-k','--key',type=str,help="your key for encrypting/decrypting (or use ENCIPHERR_KEY env variable)")
Decrypt_parser.set_defaults(func=Decrypt)

if __name__ == '__main__':
    args = parser.parse_args()
    #if no args,show help and exit.
    if len(sys.argv)==1:
       parser.print_help(sys.stderr)
       sys.exit(1)
    
    args.func(args)
