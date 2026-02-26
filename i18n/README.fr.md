# Encipherr-CLI

Encipherr-CLI est un outil local de chiffrement/dechiffrement pour le terminal.

[English README](../README.md)

## Fonctionnalites
- Chiffrement authentifie AES-256-GCM
- Chiffrement et dechiffrement de texte et de fichiers
- Cle via variable d'environnement uniquement (`ENCIPHERR_KEY`)
- Le chiffrement de fichier cree un nouveau fichier `.enc` (sans ecraser l'original)
- Le dechiffrement cree un nouveau fichier de sortie (avec repli `.dec` si necessaire)
- `--output PATH` / `-o PATH` : chemin de sortie explicite (mode fichier uniquement)
- `--overwrite` : force l'ecrasement du fichier de sortie s'il existe deja

## Prerequis
- Python 3.8+
- Package `cryptography`

## Installation

**Recommande (outil CLI global) :**
```bash
pip install encipherr-cli
```

ou avec [uv](https://github.com/astral-sh/uv) :
```bash
uv tool install encipherr-cli
```

## Demarrage rapide
```bash
encipherr genkey
export ENCIPHERR_KEY="YOUR_KEY"
encipherr encrypt text "hello world"
encipherr decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Utilisation fichier
```bash
encipherr encrypt file /path/to/data.txt
encipherr decrypt file /path/to/data.txt.enc

# Ecraser de force un fichier de sortie existant
encipherr encrypt file /path/to/data.txt --overwrite
encipherr decrypt file /path/to/data.txt.enc --overwrite

# Chemin de sortie explicite (--output / -o)
encipherr encrypt file /path/to/data.txt --output /tmp/encrypted.enc
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

## Aide
```bash
encipherr -h
encipherr --version
```

## Securite
- Utilisez directement la cle generee par `genkey`.
- Ne stockez pas la cle dans l'historique shell, les captures ou les logs publics.
- Cette version ne prend pas en charge `-k/--key`.
- Conservez separement les cles et les fichiers chiffres.
- Cet outil est concu pour la protection des donnees locales. Ce n'est pas un systeme de gestion de cles.
