# Encipherr-CLI

Encipherr-CLI e uno strumento locale di cifratura/decifratura per terminale.

[English README](../README.md)

## Funzionalita
- Cifratura autenticata AES-256-GCM
- Cifratura e decifratura di testo e file
- Chiave solo tramite variabile d'ambiente (`ENCIPHERR_KEY`)
- La cifratura file crea un nuovo `.enc` (non sovrascrive l'originale)
- La decifratura crea un nuovo file di output (usa `.dec` se necessario)
- `--output PATH` / `-o PATH`: percorso di output esplicito (solo modalità file)
- `--overwrite`: sovrascrive forzatamente il file di output se gia esistente

## Requisiti
- Python 3.8+
- Pacchetto `cryptography`

## Installazione

**Consigliato (strumento CLI globale):**
```bash
pip install encipherr-cli
```

oppure con [uv](https://github.com/astral-sh/uv):
```bash
uv tool install encipherr-cli
```

## Avvio rapido
```bash
encipherr genkey
export ENCIPHERR_KEY="YOUR_KEY"
encipherr encrypt text "hello world"
encipherr decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Uso file
```bash
encipherr encrypt file /path/to/data.txt
encipherr decrypt file /path/to/data.txt.enc

# Sovrascrittura forzata del file di output esistente
encipherr encrypt file /path/to/data.txt --overwrite
encipherr decrypt file /path/to/data.txt.enc --overwrite

# Percorso di output esplicito (--output / -o)
encipherr encrypt file /path/to/data.txt --output /tmp/encrypted.enc
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

## Aiuto
```bash
encipherr -h
encipherr --version
```

## Sicurezza
- Usa direttamente la chiave prodotta da `genkey`.
- Non salvare la chiave in cronologia shell, screenshot o log pubblici.
- Questa versione non supporta `-k/--key`.
- Conserva separati chiavi e file cifrati.
- Questo strumento e progettato per la protezione dei dati locali. Non e un sistema di gestione delle chiavi.
