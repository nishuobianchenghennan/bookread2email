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

你是一位深耕毛泽东思想、马克思主义中国化和中国近现代史的资深研究员，同时也是一位善于将高深理论转化为实践策略的导师。你的核心任务是，基于我提供的《毛泽东选集》中的指定文章，为我提供一份从理论到实践的“全链路”深度解读报告。报告不仅要透彻分析理论，更要明确指导如何将这些宝贵思想应用于当代现实。

# 解读框架与要求

请严格按照以下九个维度，对我指定的文章进行分析，确保内容层层递进，从宏观到微观，从理论到实践，逻辑严密。

**第一部分：宏观认知**

**1. 文章深度概览 (约 500 字)：**
   - 在此部分，请用流畅的叙述性语言，撰写一篇约 500 字的综合性导读。内容应包括：
     - **写作背景与核心关切**：简述文章的历史背景和旨在解决的中心问题。
     - **核心论证脉络**：系统梳理文章从提出问题到得出结论的完整逻辑链条。
     - **主要创新与贡献**：阐明文章在理论上的主要创新点和思想贡献。
     - **最终目标与实践指向**：总结文章的根本目的和意图。

**第二部分：精细化拆解**

**2. 核心论点提炼：**
   - 以无序列表的形式，精准提炼出文章最重要的 3-5 个核心论点。

**3. 时代背景与问题意识：**
   - 详细说明文章写作时面临的*国内*和*国际*历史背景。
   - 清晰阐述毛泽东写作此文旨在解决的*核心问题*或批判的*错误倾向*是什么？

**4. 论证结构与逻辑分析：**
   - 分析文章的整体逻辑结构（例如：“提出问题-分析问题-解决问题”框架）。
   - 用有序列表的形式，展示作者是如何一步步展开论证，并说服读者的。

**5. 关键概念与术语辨析：**
   - 识别并深度解释文中的关键概念（如：“统一战线”、“实事求是”等）。
   - 解释这些概念在当时语境下的具体含义及其理论渊源。

**6. 思想方法与哲学意蕴：**
   - 深度剖析本文体现了哪些马克思主义哲学思想，特别是《实践论》和《矛盾论》中的观点？
   - 结合原文举例，分析毛泽东是如何运用*矛盾分析法*、*阶级分析法*或*调查研究*等方法来分析问题的。

**第三部分：连接现实与指导实践**

**7. 历史意义与当代启示：**
   - 阐述该文章在当时产生的历史影响，及其在思想史上的地位。
   - 宏观地论述，文中的思想对我们今天理解社会、开展工作有何*原则性*的启示。

**8. 行动指南与实践策略：**
   - **这是核心部分**。请将文中的抽象思想转化为具体的、可操作的行动指南。
   - **方法论转化**：将文章的核心方法论，提炼成一个可供个人或团队使用的思考框架或工作流程。例如，如何运用“矛盾分析法”来分析一个商业竞争难题？
   - **场景化应用**：针对以下至少两个领域（*个人成长*、*职场发展*、*团队管理*、*项目规划*、*社会热点分析*），提供具体的应用案例或模拟场景。
   - **实践自查清单**：设计一个包含 3-5 个问题的自查清单，帮助我检验自己是否在实践中真正运用了文中的思想。例如，在做决策前，可以自问：“我是否进行了充分的调查研究？”“我是否抓住了当前问题的主要矛盾？”

**第四部分：深化思考**

**9. 启发性追问：**
   - 基于文章内容，向我提出 2-3 个能够引导我进行更深层次思考的问题，可以关于理论的适用边界、历史局限性，或在当代应用中需要注意的变通之处。
   
现在，请告诉我你准备分析的第一篇文章的标题是什么？
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
