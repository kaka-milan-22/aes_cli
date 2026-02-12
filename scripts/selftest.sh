#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

KEY="$(python3 encipherr.py genkey | awk 'NF{line=$0} END{gsub(/^ +| +$/, "", line); print line}')"
export ENCIPHERR_KEY="$KEY"

TEXT_CIPHER="$(python3 encipherr.py encrypt text "selftest_text" | sed -n '2p')"
TEXT_PLAIN="$(python3 encipherr.py decrypt text "$TEXT_CIPHER" | tail -n1)"
if [[ "$TEXT_PLAIN" != "selftest_text" ]]; then
  echo "Text test failed"
  exit 1
fi

TEST_FILE="$(mktemp /tmp/encipherr_selftest.XXXXXX)"
printf "selftest_file_content" > "$TEST_FILE"
python3 encipherr.py encrypt file "$TEST_FILE" >/dev/null
python3 encipherr.py decrypt file "$TEST_FILE.enc" >/dev/null

if [[ ! -f "$TEST_FILE.dec" ]]; then
  echo "File test failed: decrypted file not found"
  rm -f "$TEST_FILE" "$TEST_FILE.enc"
  exit 1
fi

if ! cmp -s "$TEST_FILE" "$TEST_FILE.dec"; then
  echo "File test failed: decrypted content mismatch"
  rm -f "$TEST_FILE" "$TEST_FILE.enc" "$TEST_FILE.dec"
  exit 1
fi

rm -f "$TEST_FILE" "$TEST_FILE.enc" "$TEST_FILE.dec"
echo "Self-test passed"
