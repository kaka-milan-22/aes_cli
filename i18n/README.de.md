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
```bash
pip install -r requirements.txt
```

## Schnellstart
```bash
python3 encipherr.py genkey
export ENCIPHERR_KEY="YOUR_KEY"
python3 encipherr.py encrypt text "hello world"
python3 encipherr.py decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Datei-Nutzung
```bash
python3 encipherr.py encrypt file /path/to/data.txt
python3 encipherr.py decrypt file /path/to/data.txt.enc

# Vorhandene Ausgabedatei erzwungen ueberschreiben
python3 encipherr.py encrypt file /path/to/data.txt --overwrite
python3 encipherr.py decrypt file /path/to/data.txt.enc --overwrite

# Expliziter Ausgabepfad (--output / -o)
python3 encipherr.py encrypt file /path/to/data.txt --output /tmp/encrypted.enc
python3 encipherr.py decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
python3 encipherr.py decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

## Hilfe
```bash
python3 encipherr.py -h
python3 encipherr.py --version
```

## Sicherheit
- Nutze den von `genkey` erzeugten Schluessel direkt.
- Schluessel nicht in Shell-Historie, Screenshots oder oeffentlichen Logs speichern.
- Diese Version unterstuetzt bewusst kein `-k/--key`.
- Schluessel und verschluesselte Dateien getrennt aufbewahren.
