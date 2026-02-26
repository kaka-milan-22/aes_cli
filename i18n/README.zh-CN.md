# Encipherr-CLI

Encipherr-CLI 是一个用于终端环境的本地加密/解密工具。

[English README](../README.md)

## 功能特性
- 使用 AES-256-GCM 进行认证加密
- 支持文本和文件的加密/解密
- 仅支持通过环境变量 `ENCIPHERR_KEY` 提供密钥
- 文件加密输出新的 `.enc` 文件（不覆盖原文件）
- 文件解密输出新文件（必要时自动回退为 `.dec`）
- `--output PATH` / `-o PATH`：指定显式输出文件路径（仅文件模式）
- `--overwrite` 参数：强制覆盖已存在的输出文件
- 对无效密钥/密文提供清晰报错信息

## 运行要求
- Python 3.8+
- `cryptography` 包

## 安装

**推荐（全局 CLI 工具）：**
```bash
pip install encipherr-cli
```

或使用 [uv](https://github.com/astral-sh/uv)：
```bash
uv tool install encipherr-cli
```

<details>
<summary>从源码运行（开发用）</summary>

```bash
pip install -r requirements.txt
python3 encipherr.py ...
```
</details>

## 快速开始
### 1. 生成密钥
```bash
encipherr genkey
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
encipherr encrypt text "hello world"
```

### 4. 解密文本
```bash
encipherr decrypt text "PASTE_BASE64_CIPHERTEXT_HERE"
```

## 文件用法
### 加密文件
```bash
encipherr encrypt file /path/to/data.txt
```

结果：
- 输入：`/path/to/data.txt`
- 输出：`/path/to/data.txt.enc`

### 解密文件
```bash
encipherr decrypt file /path/to/data.txt.enc
```

结果：
- 首选输出：`/path/to/data.txt`
- 如果 `/path/to/data.txt` 已存在，则输出为 `/path/to/data.txt.dec`

### 强制覆盖已存在的输出文件
使用 `--overwrite` 参数，输出文件已存在时直接覆盖，而不是报错退出：
```bash
encipherr encrypt file /path/to/data.txt --overwrite
encipherr decrypt file /path/to/data.txt.enc --overwrite
```

### 指定输出路径（`--output` / `-o`）
使用 `--output PATH`（或 `-o PATH`）可将结果写入指定路径，而非自动推导的文件名。
若目标路径已存在，命令会报错退出——加上 `--overwrite` 可强制覆盖：
```bash
encipherr encrypt file /path/to/data.txt --output /tmp/encrypted.enc
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt
encipherr decrypt file /tmp/encrypted.enc --output /path/to/restored.txt --overwrite
```

**规则：**
- `--output` 仅在**文件**模式下生效；在文本模式中使用会报错。
- 若指定 `--output` 且路径已存在，未加 `--overwrite` 时直接报错。
- `--output` 不影响任何密文结构或密钥处理逻辑。

## 命令帮助
```bash
encipherr -h
encipherr --version
encipherr encrypt -h
encipherr decrypt -h
```

## CLI 语法
```bash
encipherr genkey
encipherr encrypt {text|file} <input...> [--output PATH] [--overwrite]
encipherr decrypt {text|file} <input...> [--output PATH] [--overwrite]
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
- 本工具专为本地数据保护设计，不是密钥管理系统。

## Nonce 策略
对于 AES-GCM，同一密钥下 nonce 唯一性非常重要。

当前 CLI 采用：
- 12 字节高强度随机 nonce（`os.urandom(12)`）
- 不在本地保存 nonce 状态文件
- Nonce 唯一性完全依赖安全随机数；本工具设计用于本地适度使用，不适用于高频自动化批量加密场景。

## 兼容性说明
当前版本使用 AES-256-GCM 格式，不兼容旧版 Fernet 密文。
本工具保证同一主版本号内生成的密文向后兼容。

## 许可证
[MIT](https://choosealicense.com/licenses/mit/)
