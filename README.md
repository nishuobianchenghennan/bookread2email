# bookread2email
使用自定义AI对书籍的内容进行解读并定时推送到指定的邮箱
## Secrets设置
参考下述表格
| Secret 名称 | 你的值 |
| :--- | :--- |
| `SENDER_EMAIL` | 你的发件人QQ邮箱 |
| `SENDER_AUTH_CODE` | 你的QQ邮箱授权码 |
| `RECEIVER_EMAILS` | `email1@qq.com,email2@gmail.com` (用逗号分隔) |
| `ZHIPU_API_KEY` | 你的智谱API Key |
| `OPENAI_API_KEY` | 你的OpenAI API Key |
| `GEMINI_API_KEYS` | `key1,key2,key3` (用逗号分隔) |
| `ANTHROPIC_API_KEY` | 你的Claude API Key |
| `ZHIPU_BASE_URL` | `https://open.bigmodel.cn/api/paas/v4/` |
| `OPENAI_BASE_URL` | `https://sdwfger.edu.kg/v1` |
| `GEMINI_BASE_URL` | *(留空即可，除非你有特定代理)* |
| `CLAUDE_BASE_URL` | `https://api.anthropic.com` |
| `MODEL_ZHIPU` | `glm-4` |
| `MODEL_OPENAI` | `gpt-4-turbo` |
| `MODEL_GEMINI` | `gemini-1.5-pro-latest` |
| `MODEL_CLAUDE` | `claude-3-opus-20240229` |
