#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/9] Generating a temporary AES-256 key..."
KEY="$(python3 encipherr.py genkey | awk 'NF{line=$0} END{gsub(/^ +| +$/, "", line); print line}')"
export ENCIPHERR_KEY="$KEY"
echo "      Key generated and exported to ENCIPHERR_KEY for this test session."

echo "[2/9] Encrypting a test text payload..."
TEXT_CIPHER="$(python3 encipherr.py encrypt text "selftest_text" | grep -v -- '-----' | grep '\S' | tail -1)"
echo "      Text encryption completed."

echo "[3/9] Decrypting the test text payload..."
TEXT_PLAIN="$(python3 encipherr.py decrypt text "$TEXT_CIPHER" | tail -n1)"
if [[ "$TEXT_PLAIN" != "selftest_text" ]]; then
  echo "Text test failed: decrypted text does not match the original."
  exit 1
fi
echo "      Text round-trip verification passed."

echo "[4/9] Encrypting and decrypting a temporary test file (default paths)..."
TEST_FILE="$(mktemp /tmp/encipherr_selftest.XXXXXX)"
printf "selftest_file_content" > "$TEST_FILE"
python3 encipherr.py encrypt file "$TEST_FILE" >/dev/null
python3 encipherr.py decrypt file "$TEST_FILE.enc" >/dev/null

if [[ ! -f "$TEST_FILE.dec" ]]; then
  echo "File test failed: decrypted file not found."
  rm -f "$TEST_FILE" "$TEST_FILE.enc"
  exit 1
fi

echo "[5/9] Verifying decrypted file content matches original..."
if ! cmp -s "$TEST_FILE" "$TEST_FILE.dec"; then
  echo "File test failed: decrypted content mismatch."
  rm -f "$TEST_FILE" "$TEST_FILE.enc" "$TEST_FILE.dec"
  exit 1
fi
echo "      File round-trip verification passed."

echo "[6/9] Testing --output flag: encrypt with explicit output path..."
TEST_FILE2="$(mktemp /tmp/encipherr_selftest2.XXXXXX)"
printf "selftest_output_flag" > "$TEST_FILE2"
CUSTOM_ENC="$(mktemp -u /tmp/encipherr_custom.XXXXXX.enc)"
python3 encipherr.py encrypt file "$TEST_FILE2" --output "$CUSTOM_ENC" >/dev/null
if [[ ! -f "$CUSTOM_ENC" ]]; then
  echo "--output encrypt test failed: output file not found at $CUSTOM_ENC"
  rm -f "$TEST_FILE2"
  exit 1
fi

echo "[7/9] Testing --output flag: decrypt with explicit output path..."
CUSTOM_DEC="$(mktemp -u /tmp/encipherr_custom_dec.XXXXXX)"
python3 encipherr.py decrypt file "$CUSTOM_ENC" --output "$CUSTOM_DEC" >/dev/null
if [[ ! -f "$CUSTOM_DEC" ]]; then
  echo "--output decrypt test failed: output file not found at $CUSTOM_DEC"
  rm -f "$TEST_FILE2" "$CUSTOM_ENC"
  exit 1
fi
if ! cmp -s "$TEST_FILE2" "$CUSTOM_DEC"; then
  echo "--output decrypt test failed: content mismatch."
  rm -f "$TEST_FILE2" "$CUSTOM_ENC" "$CUSTOM_DEC"
  exit 1
fi
echo "      --output round-trip verification passed."

echo "[8/9] Testing --overwrite conflict guard: must error without --overwrite..."
if python3 encipherr.py encrypt file "$TEST_FILE2" --output "$CUSTOM_ENC" >/dev/null 2>&1; then
  echo "Overwrite guard test failed: should have errored but did not."
  rm -f "$TEST_FILE2" "$CUSTOM_ENC" "$CUSTOM_DEC"
  exit 1
fi
echo "      Overwrite guard correctly prevented silent clobber."

echo "[9/9] Cleaning up temporary test artifacts..."
rm -f "$TEST_FILE" "$TEST_FILE.enc" "$TEST_FILE.dec"
rm -f "$TEST_FILE2" "$CUSTOM_ENC" "$CUSTOM_DEC"
echo "Self-test passed: text, file, --output, and --overwrite guard checks succeeded."
