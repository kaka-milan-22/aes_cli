# Encipherr-CLI

Encipherr-CLI est un outil local de chiffrement/dechiffrement pour le terminal.

[English README](../README.md)

## Fonctionnalites
- Chiffrement authentifie AES-256-GCM
- Chiffrement et dechiffrement de texte et de fichiers
- Cle via variable d'environnement uniquement (`ENCIPHERR_KEY`)
- Le chiffrement de fichier cree un nouveau fichier `.enc` (sans ecraser l'original)
- Le dechiffrement cree un nouveau fichier de sortie (avec repli `.dec` si necessaire)
- `--overwrite` : force l'ecrasement du fichier de sortie s'il existe deja

## Prerequis
- Python 3.8+
- Package `cryptography`

## Installation
```bash
pip install -r requirements.txt
```

## Demarrage rapide
```bash
python3 encipherr.py genkey
export ENCIPHERR_KEY="YOUR_KEY"
python3 encipherr.py encrypt text "hello world"
python3 encipherr.py decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Utilisation fichier
```bash
python3 encipherr.py encrypt file /path/to/data.txt
python3 encipherr.py decrypt file /path/to/data.txt.enc

# Ecraser de force un fichier de sortie existant
python3 encipherr.py encrypt file /path/to/data.txt --overwrite
python3 encipherr.py decrypt file /path/to/data.txt.enc --overwrite
```

## Aide
```bash
python3 encipherr.py -h
python3 encipherr.py --version
```

## Securite
- Utilisez directement la cle generee par `genkey`.
- Ne stockez pas la cle dans l'historique shell, les captures ou les logs publics.
- Cette version ne prend pas en charge `-k/--key`.
- Conservez separement les cles et les fichiers chiffres.
