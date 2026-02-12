# Encipherr-CLI

Encipherr-CLI 是一个用于终端环境的本地加密/解密工具。

[English README](../README.md)

## 功能特性
- 使用 AES-256-GCM 进行认证加密
- 支持文本和文件的加密/解密
- 仅支持通过环境变量 `ENCIPHERR_KEY` 提供密钥
- 文件加密输出新的 `.enc` 文件（不覆盖原文件）
- 文件解密输出新文件（必要时自动回退为 `.dec`）
- 对无效密钥/密文提供清晰报错信息

## 运行要求
- Python 3.8+
- `cryptography` 包

## 安装
```bash
pip install -r requirements.txt
```

## 快速开始
### 1. 生成密钥
```bash
python3 encipherr.py genkey
```

示例输出：
```text
your random generated key :
 sPWlTYYiVpxOzY-7qvFX5EIBP3HfNNpwMkPXRkVjXV4=
```

### 2. 设置密钥（推荐：环境变量）
```bash
export ENCIPHERR_KEY="sPWlTYYiVpxOzY-7qvFX5EIBP3HfNNpwMkPXRkVjXV4="
```

### 3. 加密文本
```bash
python3 encipherr.py encrypt text "hello world"
```

### 4. 解密文本
```bash
python3 encipherr.py decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## 文件用法
### 加密文件
```bash
python3 encipherr.py encrypt file /path/to/data.txt
```

结果：
- 输入：`/path/to/data.txt`
- 输出：`/path/to/data.txt.enc`

### 解密文件
```bash
python3 encipherr.py decrypt file /path/to/data.txt.enc
```

结果：
- 首选输出：`/path/to/data.txt`
- 如果 `/path/to/data.txt` 已存在，则输出为 `/path/to/data.txt.dec`

## 命令帮助
```bash
python3 encipherr.py -h
python3 encipherr.py --version
python3 encipherr.py encrypt -h
python3 encipherr.py decrypt -h
```

## CLI 语法
```bash
python3 encipherr.py genkey
python3 encipherr.py encrypt {text|file} <input...>
python3 encipherr.py decrypt {text|file} <input...>
```

## 自测脚本
```bash
bash scripts/selftest.sh
```

## 安全说明
- 请直接使用 `genkey` 生成的密钥。密钥必须是 URL-safe Base64，解码后为 32 字节。
- 不要把密钥保存到 shell 历史、截图或公开日志中。
- 当前版本刻意不支持 `-k/--key`。
- 建议将密钥与加密文件分开保存，并放在受保护位置。

## Nonce 策略
对于 AES-GCM，同一密钥下 nonce 唯一性非常重要。

当前 CLI 采用：
- 12 字节高强度随机 nonce（`os.urandom(12)`）
- 不在本地保存 nonce 状态文件

## 兼容性说明
当前版本使用 AES-256-GCM 格式，不兼容旧版 Fernet 密文。

## 许可证
[MIT](https://choosealicense.com/licenses/mit/)
