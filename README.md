# Encipherr-CLI

<p>
  <img  src="https://img.shields.io/github/stars/Oussama1403/Encipherr-CLI" />
  <img src="https://img.shields.io/github/contributors/Oussama1403/Encipherr-CLI" />
  <img src="https://img.shields.io/github/last-commit/Oussama1403/Encipherr-CLI" />
  <img src="https://visitor-badge.laobi.icu/badge?page_id=Oussama1403.Encipherr-CLI" />
  <img src="https://img.shields.io/github/languages/count/Oussama1403/Encipherr-CLI" />
  <img src="https://img.shields.io/github/languages/top/Oussama1403/Encipherr-CLI" />

  <img src="https://img.shields.io/badge/license-MIT-blue.svg?color=f64152" />
  <img  src="https://img.shields.io/github/issues/Oussama1403/Encipherr-CLI" />
  <img  src="https://img.shields.io/github/issues-pr/Oussama1403/Encipherr-CLI" />
</p>

<b>A command line interface (CLI) version of <a href="https://Encipherr.pythonanywhere.com/" target="_blank">Encipherr</a> for the offline usage.</b>

## Why the need of a CLI version ?
- offline access
- your data will be processed locally which means more security.
- lightweight,no need for a browser.
- more features than the web version. 
## Requirements:
  - python 3.8
  - cryptography module
  - argparse
  
## Usage
 In your terminal type:
 ```
  python3 encipherr.py -h
 ```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

 ● 根据代码分析，这个项目的加密相对安全，不易被直接破解：

   安全优势：

     - 使用Fernet加密 - 基于AES-128（CBC模式）+ HMAC，是cryptography库提供的经过验证的对称加密方案
     - 包含完整性验证 - Fernet自动使用HMAC防止密文被篡改
     - 时间戳验证 - Fernet会嵌入时间戳，可防止重放攻击

   潜在风险：

     - 密钥管理 - 安全性完全依赖密钥保管，如果密钥泄露则数据可被解密
     - 密钥长度 - 使用AES-128而非AES-256（虽然AES-128目前仍被认为足够安全）
     - 无密钥派生函数 - 如果用户使用弱密钥，代码没有通过PBKDF2等强化
     - 错误处理过于宽泛 - 可能掩盖安全问题

   结论：

   对于普通使用场景，这个加密工具是安全的。暴力破解Fernet加密在计算上不可行。但需要妥善保管密钥，并且注意密钥应该使用genkey命令生成，而不是手动输入弱密码。

   主要改动：

     - 新增 get_key() 函数 - 自动从命令行参数或环境变量 ENCIPHERR_KEY 获取密钥
     - 参数调整 - 将 key 改为可选参数 -k/--key，不再是必需的位置参数
     - 使用方式更灵活 - 两种方式均可：
       - 环境变量：export ENCIPHERR_KEY="your_key"
       - 命令行参数：-k your_key
