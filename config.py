# config.py (安全版，支持GitHub Actions Secrets)

import os

# --- AI 模型配置 ---
# 在这里选择你想使用的AI提供商: "zhipu", "openai", "gemini", "claude"
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
    GEMINI_API_KEYS = ["YOUR_GEMINI_API_KEY_1", "YOUR_GEMINI_API_KEY_2"]

# Base URL 配置 (可选)
BASE_URL_ZHIPU = "https://open.bigmodel.cn/api/paas/v4/"
BASE_URL_OPENAI = "https://sdwfger.edu.kg/v1"
BASE_URL_GEMINI = "https://api-proxy.me/gemini" # Gemini SDK通常不直接支持此项
BASE_URL_CLAUDE = "https://api.anthropic.com"

# --- 模型名称配置 ---
MODEL_ZHIPU = "glm-4"
MODEL_OPENAI = "gemini-2.5-pro(不易断流)"
MODEL_GEMINI = "gemini-1.5-pro-latest"
MODEL_CLAUDE = "claude-3-opus-20240229"

# --- 书籍配置 ---
BOOK_FILENAME = "毛泽东选集.epub"
TOC_CACHE_FILE = "toc_cache.json"
PROGRESS_FILE = "progress.json"
READING_PLAN_FILE = "reading_plan.json"

# --- 解析器配置 ---
EXCLUDED_KEYWORDS = ["说明", "目录", "扉页", "出版"]
MIN_PDF_TOC_LEVEL = 3

