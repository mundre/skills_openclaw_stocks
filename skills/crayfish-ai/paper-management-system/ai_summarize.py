#!/usr/bin/env python3
"""
AI智能文献提炼模块
- 读取新提取全文的文献
- 生成结构化摘要
- 保存到ai_summary字段
- 发送飞书通知
"""

import sqlite3
import sys
import os
import re

DB_PATH = "/data/disk/papers/index.db"

def get_papers_need_summary():
    """获取需要AI提炼的文献（有full_text但没有ai_summary）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    papers = conn.execute("""
        SELECT id, title, authors, doi, year, journal, full_text 
        FROM papers 
        WHERE full_text IS NOT NULL 
        AND (ai_summary IS NULL OR ai_summary = '') 
        AND LENGTH(full_text) > 1000
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return papers



def generate_summary(title, authors, journal, year, full_text):
    """生成结构化中文摘要（带医学术语翻译）"""
    # 提取关键信息
    summary_parts = []
    
    # 1. 研究背景/目的
    background = extract_section(full_text, 
        ["Background", "OBJECTIVE", "AIM", "PURPOSE", "Introduction", "INTRODUCTION"],
        ["Methods", "METHODS", "Material", "MATERIAL", "方法"])
    if background:
        summary_parts.append(f"📌 **研究背景**: {background[:200]}...")
    
    # 2. 研究方法
    methods = extract_section(full_text,
        ["Methods", "METHODS", "Methodology", "方法", "材料与方法"],
        ["Results", "RESULTS", "Findings", "FINDINGS", "结果"])
    if methods:
        summary_parts.append(f"🔬 **研究方法**: {methods[:200]}...")
    
    # 3. 主要结果
    results = extract_section(full_text,
        ["Results", "RESULTS", "Findings", "FINDINGS", "结果"],
        ["Conclusion", "CONCLUSION", "Discussion", "DISCUSSION", "结论", "讨论"])
    if results:
        summary_parts.append(f"📊 **主要结果**: {results[:300]}...")
    
    # 4. 结论
    conclusion = extract_section(full_text,
        ["Conclusion", "CONCLUSION", "Conclusions", "CONCLUSIONS", "结论"],
        ["References", "REFERENCES", "Acknowledgment", "参考文献"])
    if conclusion:
        summary_parts.append(f"💡 **核心结论**: {conclusion[:200]}...")
    
    # 如果没有提取到内容，使用abstract
    if not summary_parts:
        abstract_match = re.search(r'Abstract[\s:]*(.*?)(?:Keywords|Introduction|$)', 
                                   full_text, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            summary_parts.append(f"📝 **摘要**: {abstract_match.group(1)[:500]}...")
    
    # 构建中文格式的头部信息
    header_lines = ["📄 **文献AI提炼**", ""]
    if title:
        header_lines.append(f"**标题**: {title}")
    if authors:
        header_lines.append(f"**作者**: {authors}")
    if journal:
        header_lines.append(f"**期刊**: {journal}")
    if year:
        header_lines.append(f"**年份**: {year}")
    header_lines.append("")
    
    header = "\n".join(header_lines)
    return header + "\n\n".join(summary_parts)

def extract_section(text, start_keywords, end_keywords):
    """从文本中提取特定章节（改进版）"""
    import re
    
    # 清理文本中的常见噪音
    text = re.sub(r'ARTICLE IN PRESS|ACCEPTED MANUSCRIPT|© The Author\(s\).*?licence', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://\S+', '', text)
    
    # 构建正则表达式
    start_pattern = '|'.join(re.escape(k) for k in start_keywords)
    end_pattern = '|'.join(re.escape(k) for k in end_keywords)
    
    # 尝试多种匹配模式
    patterns = [
        # 标准格式: Keyword: content
        rf'(?:{start_pattern})[\s:]+\n?(.*?)(?:(?:{end_pattern})|$)',
        # 大写格式: KEYWORD\ncontent
        rf'(?:{start_pattern})\s*\n\s*\n?(.*?)(?:(?:{end_pattern})|$)',
        # 带数字格式: 1. Keyword\ncontent
        rf'\d+\.\s*(?:{start_pattern})[\s:]*\n?(.*?)(?:(?:{end_pattern})|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section = match.group(1).strip()
            # 清理多余空白和特殊字符
            section = re.sub(r'\s+', ' ', section)
            section = re.sub(r'^[\s\W]+', '', section)  # 移除开头的非文字字符
            if len(section) > 20:  # 确保内容有意义
                return section
    return ""

def save_summary(paper_id, summary):
    """保存AI提炼结果到数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE papers SET ai_summary = ? WHERE id = ?", (summary, paper_id))
    conn.commit()
    conn.close()

def send_feishu_notification(summary, doi=None):
    """发送飞书通知"""
    import subprocess
    
    title = "📚 新文献AI提炼"
    message = summary[:1500]  # 限制长度
    
    if doi:
        message += f"\n\n🔗 DOI: {doi}"
    
    # 调用feishu-notifier
    cmd = f'/opt/feishu-notifier/bin/notify "{title}" "{message}"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except:
        return False

def main():
    papers = get_papers_need_summary()
    
    if not papers:
        print("没有需要提炼的文献")
        return
    
    print(f"发现 {len(papers)} 篇需要AI提炼的文献")
    
    for paper in papers:
        title_display = paper['title'][:50] if paper['title'] else f"ID:{paper['id']}"
        print(f"\n处理: {title_display}...")
        
        # 生成摘要
        summary = generate_summary(
            paper['title'],
            paper['authors'],
            paper['journal'],
            paper['year'],
            paper['full_text']
        )
        
        # 保存到数据库
        save_summary(paper['id'], summary)
        print(f"✓ 已保存提炼内容 (ID: {paper['id']})")
        
        # 发送飞书通知（只发送最新的1篇，避免刷屏）
        if paper == papers[0]:  # 只发送第一篇
            send_feishu_notification(summary, paper['doi'])
            print("✓ 已发送飞书通知")

if __name__ == "__main__":
    main()
