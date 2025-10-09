# config.py (V3.0 - 高级安全版，URL和模型名称外部化)

import os

# --- AI 模型配置 ---
# 默认的AI提供商，可以在本地运行时使用。在GitHub Actions中，此设置依然有效。
AI_PROVIDER = "openai" 

# --- 敏感信息配置 (从环境变量读取) ---
# 邮件发送配置
EMAIL_HOST = "smtp.qq.com"
EMAIL_PORT = 465
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'YOUR_SENDER_EMAIL@qq.com') 
SENDER_AUTH_CODE = os.environ.get('SENDER_AUTH_CODE', 'YOUR_SENDER_AUTH_CODE') 
receiver_emails_str = os.environ.get('RECEIVER_EMAILS', 'YOUR_RECEIVER_EMAIL@example.com')
RECEIVER_EMAILS = [email.strip() for email in receiver_emails_str.split(',') if email.strip()]

# API密钥管理
ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY', 'YOUR_ZHIPU_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', 'YOUR_ANTHROPIC_API_KEY')

gemini_keys_str = os.environ.get('GEMINI_API_KEYS')
if gemini_keys_str:
    GEMINI_API_KEYS = [key.strip() for key in gemini_keys_str.split(',') if key.strip()]
else:
    GEMINI_API_KEYS = ["YOUR_GEMINI_API_KEY_1"]

# --- 【核心修改 1】URL 配置外部化 ---
# 优先从环境变量读取，如果不存在 (本地运行)，则使用后面的默认值或空字符串
BASE_URL_ZHIPU = os.environ.get('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')
BASE_URL_OPENAI = os.environ.get('OPENAI_BASE_URL', '') 
BASE_URL_GEMINI = os.environ.get('GEMINI_BASE_URL', '')
BASE_URL_CLAUDE = os.environ.get('CLAUDE_BASE_URL', 'https://api.anthropic.com')

# --- 【核心修改 2】模型名称配置外部化 ---
# 优先从环境变量读取，如果不存在 (本地运行)，则使用后面的默认值
MODEL_ZHIPU = os.environ.get('MODEL_ZHIPU', 'glm-4')
MODEL_OPENAI = os.environ.get('MODEL_OPENAI', 'gpt-4-turbo')
MODEL_GEMINI = os.environ.get('MODEL_GEMINI', 'gemini-1.5-pro-latest')
MODEL_CLAUDE = os.environ.get('MODEL_CLAUDE', 'claude-3-opus-20240229')

# --- 书籍与文件配置 ---
BOOK_FILENAME = "毛泽东选集.epub"
TOC_CACHE_FILE = "toc_cache.json"
PROGRESS_FILE = "progress.json"
READING_PLAN_FILE = "reading_plan.json"

# --- 解析器配置  ---
EXCLUDED_KEYWORDS = ["说明", "目录", "扉页", "出版"]
MIN_PDF_TOC_LEVEL = 3
