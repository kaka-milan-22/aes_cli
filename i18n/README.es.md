# Encipherr-CLI

Encipherr-CLI es una herramienta local de cifrado/descifrado para terminal.

[English README](../README.md)

## Caracteristicas
- Cifrado autenticado AES-256-GCM
- Cifrado y descifrado de texto y archivos
- Clave solo por variable de entorno (`ENCIPHERR_KEY`)
- El cifrado de archivos crea un nuevo archivo `.enc` (no sobrescribe el original)
- El descifrado crea un nuevo archivo de salida (usa `.dec` si hace falta)
- `--output PATH` / `-o PATH`: ruta de salida explícita (solo modo archivo)
- `--overwrite`: fuerza la sobreescritura del archivo de salida si ya existe

## Requisitos
- Python 3.8+
- Paquete `cryptography`

## Instalacion
```bash
pip install -r requirements.txt
```

## Inicio rapido
```bash
python3 encipherr.py genkey
export ENCIPHERR_KEY="YOUR_KEY"
python3 encipherr.py encrypt text "hello world"
python3 encipherr.py decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Uso con archivos
```bash
python3 encipherr.py encrypt file /path/to/data.txt
python3 encipherr.py decrypt file /path/to/data.txt.enc

# Forzar sobreescritura del archivo de salida existente
python3 encipherr.py encrypt file /path/to/data.txt --overwrite
python3 encipherr.py decrypt file /path/to/data.txt.enc --overwrite

# Ruta de salida explícita (--output / -o)
python3 encipherr.py encrypt file /path/to/data.txt --output /tmp/encrypted.enc
python3 encipherr.py decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
python3 encipherr.py decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

## Ayuda
```bash
python3 encipherr.py -h
python3 encipherr.py --version
```

## Seguridad
- Usa directamente la clave generada por `genkey`.
- No guardes la clave en historial de shell, capturas o logs publicos.
- Esta version no admite `-k/--key`.
- Separa las claves de los archivos cifrados.
