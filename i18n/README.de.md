# Encipherr-CLI

Encipherr-CLI ist ein lokales Verschluesselungs-/Entschluesselungs-Tool fuer die Konsole.

[English README](../README.md)

## Funktionen
- Authentifizierte AES-256-GCM-Verschluesselung
- Text- und Dateiverschluesselung/-entschluesselung
- Schluessel nur ueber Umgebungsvariable (`ENCIPHERR_KEY`)
- Dateiverschluesselung erstellt neue `.enc` Datei (kein Ueberschreiben)
- Dateientschluesselung erzeugt neue Ausgabedatei (falls noetig mit `.dec`)
- `--output PATH` / `-o PATH`: Expliziter Ausgabepfad (nur Dateimodus)
- `--overwrite`: Vorhandene Ausgabedatei erzwungen ueberschreiben

## Voraussetzungen
- Python 3.8+
- Paket `cryptography`

## Installation

**Empfohlen (globales CLI-Tool):**
```bash
pip install encipherr-cli
```

oder mit [uv](https://github.com/astral-sh/uv):
```bash
uv tool install encipherr-cli
```

## Schnellstart
```bash
encipherr genkey
export ENCIPHERR_KEY="YOUR_KEY"
encipherr encrypt text "hello world"
encipherr decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Datei-Nutzung
```bash
encipherr encrypt file /path/to/data.txt
encipherr decrypt file /path/to/data.txt.enc

# Vorhandene Ausgabedatei erzwungen ueberschreiben
encipherr encrypt file /path/to/data.txt --overwrite
encipherr decrypt file /path/to/data.txt.enc --overwrite

# Expliziter Ausgabepfad (--output / -o)
encipherr encrypt file /path/to/data.txt --output /tmp/encrypted.enc
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

## Hilfe
```bash
encipherr -h
encipherr --version
```

## Sicherheit
- Nutze den von `genkey` erzeugten Schluessel direkt.
- Schluessel nicht in Shell-Historie, Screenshots oder oeffentlichen Logs speichern.
- Diese Version unterstuetzt bewusst kein `-k/--key`.
- Schluessel und verschluesselte Dateien getrennt aufbewahren.
- Dieses Tool ist fuer lokalen Datenschutz konzipiert, kein Schluessel-Management-System.
