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

> **Hinweis:** Dieses Projekt ist nicht auf PyPI veröffentlicht. Bitte direkt von GitHub installieren.

**Empfohlen (globales CLI-Tool):**
```bash
uv tool install git+https://github.com/kaka-milan-22/aes_cli.git
```

**Installation prüfen:**
```bash
encipherr --help
```

<details>
<summary>Entwickler / lokale Installation</summary>

```bash
git clone https://github.com/kaka-milan-22/aes_cli.git
cd aes_cli
uv tool install .
# oder
pip install -e .
```
</details>

**Namens-Zuordnung:**
- CLI-Befehl: `encipherr`
- Python-Paket: `encipherr-cli`
- Repository: `aes_cli`

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
