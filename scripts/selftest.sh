#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/6] Generating a temporary AES-256 key..."
KEY="$(python3 encipherr.py genkey | awk 'NF{line=$0} END{gsub(/^ +| +$/, "", line); print line}')"
export ENCIPHERR_KEY="$KEY"
echo "      Key generated and exported to ENCIPHERR_KEY for this test session."

echo "[2/6] Encrypting a test text payload..."
TEXT_CIPHER="$(python3 encipherr.py encrypt text "selftest_text" | sed -n '2p')"
echo "      Text encryption completed."

echo "[3/6] Decrypting the test text payload..."
TEXT_PLAIN="$(python3 encipherr.py decrypt text "$TEXT_CIPHER" | tail -n1)"
if [[ "$TEXT_PLAIN" != "selftest_text" ]]; then
  echo "Text test failed: decrypted text does not match the original."
  exit 1
fi
echo "      Text round-trip verification passed."

echo "[4/6] Encrypting and decrypting a temporary test file..."
TEST_FILE="$(mktemp /tmp/encipherr_selftest.XXXXXX)"
printf "selftest_file_content" > "$TEST_FILE"
python3 encipherr.py encrypt file "$TEST_FILE" >/dev/null
python3 encipherr.py decrypt file "$TEST_FILE.enc" >/dev/null

if [[ ! -f "$TEST_FILE.dec" ]]; then
  echo "File test failed: decrypted file not found."
  rm -f "$TEST_FILE" "$TEST_FILE.enc"
  exit 1
fi

echo "[5/6] Verifying decrypted file content matches original..."
if ! cmp -s "$TEST_FILE" "$TEST_FILE.dec"; then
  echo "File test failed: decrypted content mismatch."
  rm -f "$TEST_FILE" "$TEST_FILE.enc" "$TEST_FILE.dec"
  exit 1
fi
echo "      File round-trip verification passed."

echo "[6/6] Cleaning up temporary test artifacts..."
rm -f "$TEST_FILE" "$TEST_FILE.enc" "$TEST_FILE.dec"
echo "Self-test passed: text and file encryption/decryption checks succeeded."
