# Encipherr-CLI

Encipherr-CLI e uno strumento locale di cifratura/decifratura per terminale.

[English README](README.md)

## Funzionalita
- Cifratura autenticata AES-256-GCM
- Cifratura e decifratura di testo e file
- Chiave solo tramite variabile d'ambiente (`ENCIPHERR_KEY`)
- La cifratura file crea un nuovo `.enc` (non sovrascrive l'originale)
- La decifratura crea un nuovo file di output (usa `.dec` se necessario)

## Requisiti
- Python 3.8+
- Pacchetto `cryptography`

## Installazione
```bash
pip install -r requirements.txt
```

## Avvio rapido
```bash
python3 encipherr.py genkey
export ENCIPHERR_KEY="YOUR_KEY"
python3 encipherr.py encrypt text "hello world"
python3 encipherr.py decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Uso file
```bash
python3 encipherr.py encrypt file /path/to/data.txt
python3 encipherr.py decrypt file /path/to/data.txt.enc
```

## Aiuto
```bash
python3 encipherr.py -h
python3 encipherr.py --version
```

## Sicurezza
- Usa direttamente la chiave prodotta da `genkey`.
- Non salvare la chiave in cronologia shell, screenshot o log pubblici.
- Questa versione non supporta `-k/--key`.
- Conserva separati chiavi e file cifrati.
