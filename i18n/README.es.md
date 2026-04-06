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

> **Nota:** Este proyecto no está publicado en PyPI. Instalar directamente desde GitHub.

**Recomendado (herramienta CLI global):**
```bash
uv tool install git+https://github.com/kaka-milan-22/aes_cli.git
```

**Verificar instalacion:**
```bash
encipherr --help
```

<details>
<summary>Desarrollador / instalacion local</summary>

```bash
git clone https://github.com/kaka-milan-22/aes_cli.git
cd aes_cli
uv tool install .
# o bien
pip install -e .
```
</details>

**Correspondencia de nombres:**
- Comando CLI: `encipherr`
- Paquete Python: `encipherr-cli`
- Repositorio: `aes_cli`

## Inicio rapido
```bash
encipherr genkey
export ENCIPHERR_KEY="YOUR_KEY"
encipherr encrypt text "hello world"
encipherr decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## Uso con archivos
```bash
encipherr encrypt file /path/to/data.txt
encipherr decrypt file /path/to/data.txt.enc

# Forzar sobreescritura del archivo de salida existente
encipherr encrypt file /path/to/data.txt --overwrite
encipherr decrypt file /path/to/data.txt.enc --overwrite

# Ruta de salida explícita (--output / -o)
encipherr encrypt file /path/to/data.txt --output /tmp/encrypted.enc
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

## Ayuda
```bash
encipherr -h
encipherr --version
```

## Seguridad
- Usa directamente la clave generada por `genkey`.
- No guardes la clave en historial de shell, capturas o logs publicos.
- Esta version no admite `-k/--key`.
- Separa las claves de los archivos cifrados.
- Esta herramienta esta disenada para proteccion de datos local. No es un sistema de gestion de claves.
