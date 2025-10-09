# book_parser.py (健壮性升级版)

import fitz
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import json
import os
import config

# --- 路径构建 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_PATH = os.path.join(BASE_DIR, config.BOOK_FILENAME)
CACHE_PATH = os.path.join(BASE_DIR, config.TOC_CACHE_FILE)


def _flatten_epub_toc(toc_list):
    # ... (此函数无需修改) ...
    flat_list = []
    for item in toc_list:
        if isinstance(item, ebooklib.epub.Link):
            flat_list.append(item)
        elif isinstance(item, tuple) and len(item) > 0:
            link, children = item
            if isinstance(link, ebooklib.epub.Link): flat_list.append(link)
            if children: flat_list.extend(_flatten_epub_toc(children))
    return flat_list


def _get_pdf_toc():
    # ... (此函数无需修改) ...
    print("解析PDF目录...")
    doc = fitz.open(BOOK_PATH)
    raw_toc = doc.get_toc()
    doc.close()
    articles = [item for item in raw_toc if
                item[0] >= config.MIN_PDF_TOC_LEVEL and not any(kw in item[1] for kw in config.EXCLUDED_KEYWORDS)]
    toc_data = []
    for i, article in enumerate(articles):
        _level, title, start_page = article
        end_page = articles[i + 1][2] if i + 1 < len(articles) else fitz.open(BOOK_PATH).page_count
        toc_data.append({'title': title, 'start_page': start_page, 'end_page': end_page})
    return toc_data


def _get_epub_toc():
    # ... (此函数无需修改) ...
    print("解析EPUB目录...")
    book = epub.read_epub(BOOK_PATH)
    raw_toc = book.toc
    flat_toc = _flatten_epub_toc(raw_toc)
    articles_toc = [item for item in flat_toc if not any(kw in item.title for kw in config.EXCLUDED_KEYWORDS)]
    toc_data = []
    for i, item in enumerate(articles_toc):
        start_href = item.href.split('#')[0]
        end_href = articles_toc[i + 1].href.split('#')[0] if i + 1 < len(articles_toc) else None
        toc_data.append({'title': item.title, 'start_href': start_href, 'end_href': end_href})
    return toc_data


def get_book_toc():
    """获取书籍目录的主函数，增强了缓存校验功能。"""
    if os.path.exists(CACHE_PATH):
        # 【新增校验】检查缓存文件是否为空
        if os.path.getsize(CACHE_PATH) > 0:
            try:
                print(f"从缓存文件 '{config.TOC_CACHE_FILE}' 读取目录...")
                with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"警告：缓存文件 '{config.TOC_CACHE_FILE}' 格式损坏，将重新解析。")
                # 如果文件存在但格式错误，将继续执行下面的解析逻辑
        else:
            print(f"警告：缓存文件 '{config.TOC_CACHE_FILE}' 为空，将重新解析。")

    # --- 如果缓存不存在、为空或损坏，则执行以下解析逻辑 ---
    print("缓存无效或未找到，开始解析书籍目录...")
    _, file_extension = os.path.splitext(BOOK_PATH)
    toc_data = []
    if file_extension.lower() == '.pdf':
        toc_data = _get_pdf_toc()
    elif file_extension.lower() == '.epub':
        toc_data = _get_epub_toc()
    else:
        print(f"不支持的文件格式: {file_extension}")
        return []

    # 写入新的、正确的缓存
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(toc_data, f, ensure_ascii=False, indent=4)
    print(f"目录已解析并缓存到 '{config.TOC_CACHE_FILE}'")
    return toc_data


def read_unit_content(toc, unit_index):
    # ... (此函数无需修改) ...
    if unit_index >= len(toc): return None, "全书文章已读完", True
    unit_info = toc[unit_index]
    title = unit_info['title']
    content = ""
    _, file_extension = os.path.splitext(BOOK_PATH)
    if file_extension.lower() == '.pdf':
        print(f"读取PDF文章: '{title}'")
        doc = fitz.open(BOOK_PATH)
        for page_num in range(unit_info['start_page'] - 1, unit_info['end_page'] - 1):
            if page_num < doc.page_count: content += doc.load_page(page_num).get_text()
        doc.close()
    elif file_extension.lower() == '.epub':
        print(f"读取EPUB文章: '{title}'")
        book = epub.read_epub(BOOK_PATH)
        reading = False
        start_href, end_href = unit_info['start_href'], unit_info['end_href']
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if item.get_name() == start_href: reading = True
            if reading and item.get_name() == end_href and start_href != end_href: reading = False
            if reading:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                content += soup.get_text() + "\n\n"
    return content, title, False

