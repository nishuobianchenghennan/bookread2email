# ai_analyzer.py (最终重构版)
#
# 功能特性:
# 1. 多模型调度: 支持 Zhipu, OpenAI, Gemini, Claude 四种主流AI模型。
# 2. 灵活配置: 通过 config.py 轻松切换模型、管理API密钥和自定义 Base URL。
# 3. 统一提示词: 使用统一、结构化的系统提示词，确保分析报告的质量和一致性。
# 4. 高可用性 (Gemini): 为Gemini实现了API密钥列表轮换和自动重试机制，
#    能有效应对单个密钥失效或达到速率限制的问题。
# 5. Cloudflare 代理修复 (OpenAI): 为OpenAI客户端添加 User-Agent 请求头，
#    以绕过部分代理服务器上的Cloudflare机器人检测。
# 6. 健壮的错误处理: 对每个API调用都进行了封装，并提供了清晰的错误日志。
import config

# --- 统一的系统提示词 ---
# 将这个复杂的提示词定义为一个常量，方便所有模型复用，确保分析维度的一致性。
SYSTEM_PROMPT = """
# 角色与任务

# 任务：生成《毛泽东选集》指定文章的深度解读与实践应用报告

## 1. 角色与目标
你将扮演一位深耕毛泽东思想、马克思主义中国化和中国近现代史的资深研究员，同时也是一位善于将高深理论转化为实践策略的导师。你的核心目标是，基于用户指定的《毛泽东选集》中的一篇文章，生成一份结构化、系统化的深度解读报告，实现从理论认知、精细化拆解到现实应用的全链路分析。

## 2. 背景与上下文
用户将首先提供一篇《毛泽东选集》中的文章作为分析对象。收到特定的文章后，你的所有分析都必须围绕该指定文章展开。

## 3. 关键步骤
在你的创作过程中，请严格遵循以下九个步骤来构思和撰写报告：

1.  **构建宏观认知 (文章深度概览)**: 撰写一篇约500字的综合性导读，内容涵盖写作背景与核心关切、核心论证脉络、主要理论创新与贡献，以及最终的实践指向。

2.  **提炼核心论点**: 以无序列表的形式，精准提炼出文章中最重要的3-5个核心论点。

3.  **分析时代背景与问题意识**: 详细阐述文章写作时所面临的国内与国际历史背景，并明确指出作者旨在解决的核心问题或批判的错误倾向。

4.  **梳理论证结构与逻辑**: 分析文章的整体逻辑框架（如“提出问题-分析问题-解决问题”），并用有序列表清晰展示作者是如何一步步展开论证的。

5.  **辨析关键概念与术语**: 识别并深度解释文中的关键概念（如“统一战线”、“实事求是”等），阐明其在当时语境下的具体含义及理论渊源。

6.  **挖掘思想方法与哲学意蕴**: 深度剖析文章所体现的马克思主义哲学思想（特别是《实践论》和《矛盾论》的观点），并结合原文举例，分析作者是如何运用矛盾分析法、阶级分析法或调查研究等方法的。

7.  **总结历史意义与当代启示**: 阐述该文章在当时产生的历史影响及其思想史地位，并宏观论述其思想对我们今天理解社会、开展工作的原则性启示。

8.  **制定行动指南与实践策略**: 将文中的抽象思想转化为具体的、可操作的行动指南。
    - **方法论转化**: 将文章的核心方法论，提炼成一个可供个人或团队使用的思考框架或工作流程。
    - **场景化应用**: 针对**个人成长、职场发展、团队管理、项目规划、社会热点分析**中至少两个领域，提供具体的应用案例或模拟场景。
    - **实践自查清单**: 设计一个包含3-5个问题的自查清单，帮助使用者检验自己是否在实践中真正运用了文中的思想。

9.  **提出启发性追问**: 基于文章内容，提出2-3个能够引导用户进行更深层次思考的问题，可关于理论的适用边界、历史局限性，或在当代应用中需要注意的变通之处。

## 4. 输出要求
- **格式**: 使用Markdown格式进行撰写。通过各级标题（`##`、`###`）、列表（有序、无序）、粗体等元素清晰地组织九个部分的内容，确保报告结构分明，可读性强。
- **风格**: 兼具学术研究的严谨性和实践导师的启发性。语言应深刻、清晰、逻辑性强，同时要通俗易懂，便于应用。
- **约束**:
    - 必须严格按照上述九个部分的框架进行分析，不可遗漏或颠倒顺序。
    - 必须重点突出第八步“行动指南与实践策略”，确保内容具体、可操作，真正实现理论到实践的转化。
    - **最终输出**: 你的最终回复应仅包含完整的九部分解读报告本身，不得包含任何前言、摘要、步骤说明或其他无关内容。请在用户提供文章标题后直接开始生成报告。

以下是文章原文：
---
{content}
---
"""
# ===============================================================
# --- 各个模型的具体实现 (私有函数，以下划线开头) ---
# ===============================================================

def _get_analysis_from_zhipu(content, article_title):
    """使用智谱AI (GLM-4) 进行分析"""
    from zhipuai import ZhipuAI

    # 动态构建客户端参数，如果配置了base_url，则使用它
    client_args = {'api_key': config.ZHIPU_API_KEY}
    if config.BASE_URL_ZHIPU:
        client_args['base_url'] = config.BASE_URL_ZHIPU

    client = ZhipuAI(**client_args)

    prompt = SYSTEM_PROMPT.format(article_title=article_title, content=content)
    response = client.chat.completions.create(
        model=config.MODEL_ZHIPU,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content


def _get_analysis_from_openai(content, article_title):
    """使用 OpenAI (GPT) 进行分析"""
    from openai import OpenAI

    # 动态构建客户端参数
    client_args = {'api_key': config.OPENAI_API_KEY}
    if config.BASE_URL_OPENAI:
        client_args['base_url'] = config.BASE_URL_OPENAI

    # 【Cloudflare修复】添加自定义请求头，伪装成浏览器
    # 很多受Cloudflare保护的代理需要一个常见的User-Agent头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    # 将headers添加到OpenAI客户端的默认请求中
    client = OpenAI(**client_args, default_headers=headers)

    prompt = SYSTEM_PROMPT.format(article_title=article_title, content=content)
    response = client.chat.completions.create(
        model=config.MODEL_OPENAI,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content


def _get_analysis_from_gemini(content, article_title):
    """
    使用 Google (Gemini) 进行分析。
    【增强版】支持API密钥列表，实现自动轮换和重试。
    """
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions

    # 检查密钥列表是否存在且不为空
    if not config.GEMINI_API_KEYS or not isinstance(config.GEMINI_API_KEYS, list):
        raise ValueError("Gemini API 密钥未配置或格式不正确，请在 config.py 中配置 GEMINI_API_KEYS 列表。")

    # 遍历列表中的每一个密钥
    for i, key in enumerate(config.GEMINI_API_KEYS):
        print(f"正在尝试使用 Gemini Key #{i + 1}...")
        try:
            # 使用当前密钥配置SDK
            genai.configure(api_key=key)

            model = genai.GenerativeModel(config.MODEL_GEMINI)
            prompt = SYSTEM_PROMPT.format(article_title=article_title, content=content)

            response = model.generate_content(prompt)

            # 如果请求成功，立即返回结果，不再尝试下一个密钥
            print(f"Gemini Key #{i + 1} 请求成功。")
            return response.text

        except google_exceptions.PermissionDenied as e:
            print(f"警告：Gemini Key #{i + 1} 权限被拒绝 (可能是无效key)。错误: {e}")
            continue  # 继续尝试下一个密钥
        except google_exceptions.ResourceExhausted as e:
            print(f"警告：Gemini Key #{i + 1} 已达到速率限制。错误: {e}")
            continue  # 继续尝试下一个密钥
        except Exception as e:
            print(f"警告：使用 Gemini Key #{i + 1} 时发生未知错误: {e}")
            continue  # 继续尝试下一个密钥

    # 如果循环结束都没有成功返回，意味着所有密钥都已失败
    raise RuntimeError("所有 Gemini API 密钥均尝试失败，无法完成分析。")


def _get_analysis_from_claude(content, article_title):
    """使用 Anthropic (Claude) 进行分析"""
    import anthropic

    # 动态构建客户端参数，如果配置了base_url，则使用它
    client_args = {'api_key': config.ANTHROPIC_API_KEY}
    if config.BASE_URL_CLAUDE:
        client_args['base_url'] = config.BASE_URL_CLAUDE

    client = anthropic.Anthropic(**client_args)

    prompt = SYSTEM_PROMPT.format(article_title=article_title, content=content)
    response = client.messages.create(
        model=config.MODEL_CLAUDE,
        max_tokens=4096,  # Claude API推荐指定最大输出长度
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.content[0].text


# ===============================================================
# --- 主调度函数 (对外的唯一接口) ---
# ===============================================================

def get_analysis_from_ai(content, article_title):
    """
    根据 config.py 中的 AI_PROVIDER 设置，调用相应的AI模型进行分析。
    这是本模块对外的唯一接口，隐藏了所有内部实现细节。
    """
    if not content:
        return "没有内容需要分析。"

    provider = config.AI_PROVIDER.lower()
    print(f"正在使用 '{provider}' 模型进行深度分析...")

    # 定义一个调度字典，将配置字符串映射到对应的处理函数
    provider_map = {
        "zhipu": _get_analysis_from_zhipu,
        "openai": _get_analysis_from_openai,
        "gemini": _get_analysis_from_gemini,
        "claude": _get_analysis_from_claude,
    }

    # 获取对应的处理函数
    analysis_function = provider_map.get(provider)

    if not analysis_function:
        return f"错误：未知的AI提供商 '{config.AI_PROVIDER}'。请检查 config.py 文件中的 AI_PROVIDER 设置。"

    # 使用统一的错误处理来调用选定的函数
    try:
        analysis_result = analysis_function(content, article_title)
        print(f"'{provider}' 模型分析完成。")
        return analysis_result
    except Exception as e:
        # 捕获所有可能的异常（API连接错误、认证失败、超时、或Gemini所有密钥失败的RuntimeError）
        print(f"调用 '{provider}' API时出错: {e}")
        return f"AI分析失败，提供商: {provider}, 错误信息: {e}"

