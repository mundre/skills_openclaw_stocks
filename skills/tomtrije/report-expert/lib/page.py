"""页面 HTML 生成与静态资源部署"""

import re, sys
from pathlib import Path
from datetime import date

from lib.config import BASE_DIR, SITE_NAME, _CFG, load_index, save_index, strip_emoji, add_ids

def generate_page_html(page_info, base_url, no_chrome=False):
    cat = page_info.get("category", "")
    cat_name = cat or ""
    body = add_ids(page_info["body"])
    page_style = page_info.get("style", "")
    style_tag = f"\n  <style>\n    {page_style}\n  </style>" if page_style else ""

    # 按需加载图表 CDN（检测 body 中是否含图表相关标记）
    needs_echarts = 'echarts' in body or 'chart-box' in body
    needs_chartjs = 'Chart(' in body or 'data-chart' in body or 'chart-container' in body
    needs_mermaid = 'mermaid' in body or 'mermaid-wrap' in body
    cdn_tags = ""
    if needs_echarts:
        cdn_tags += '  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>\n'
    if needs_chartjs:
        cdn_tags += '  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>\n'

    # Mermaid 初始化脚本（按需）
    mermaid_script = ""
    if needs_mermaid:
        mermaid_script = f'''  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'base',
      themeMode: 'light',
      themeVariables: {{
        primaryColor: '#ffffff',
        primaryTextColor: '#09090b',
        primaryBorderColor: '#e2e6ec',
        lineColor: '#cbd5e1',
        secondaryColor: '#f8fafc',
        tertiaryColor: '#ffffff',
        noteBkgColor: '#f8fafc',
        noteTextColor: '#52525b',
        noteBorderColor: '#e2e6ec',
        actorBkg: '#ffffff',
        actorTextColor: '#09090b',
        actorBorderColor: '#e2e6ec',
        actorBorder: '#e2e6ec',
        signalColor: '#52525b',
        signalTextColor: '#09090b',
        labelBoxBkgColor: '#f8fafc',
        labelBoxBorderColor: '#e2e6ec',
        labelTextColor: '#09090b',
        loopTextColor: '#52525b',
        activationBorderColor: '#cbd5e1',
        activationBkgColor: '#f8fafc',
        sequenceNumberColor: '#ffffff',
        fontFamily: 'Inter, Noto Sans SC, sans-serif',
        fontSize: '13px'
      }}
    }});
  </script>'''

    # Chrome parts (header + footer)
    if no_chrome:
        css_href = "templates/base.css"
        js_src = "scripts/main.js"
        chrome_header = f'''
    <header class="report-header" style="border-bottom:none;">
      <h1 class="report-header__title">{page_info["title"]}</h1>
      {f'<p class="report-header__desc">{page_info["desc"]}</p>' if page_info.get("desc") else ""}
    </header>'''
        chrome_footer = ""
    else:
        css_href = "../styles/base.css"
        js_src = "../scripts/main.js"
        chrome_header = f'''
    <header class="report-header">
      <div class="report-header__breadcrumb">
        <a href="../" target="_top"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg></a>
        <span>{cat_name}</span>
      </div>
      <div class="report-header__meta">
        <span class="report-header__tag">{cat_name}</span>
        <span class="report-header__date">{page_info["date"]}</span>
      </div>
      <h1 class="report-header__title">{page_info["title"]}</h1>
      {f'<p class="report-header__desc">{page_info["desc"]}</p>' if page_info.get("desc") else ""}
    </header>'''
        chrome_footer = f'''
  <footer class="page-footer">
    <div class="page-footer__logo">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
    </div>
    <a href="../" class="page-footer__link" target="_top">{SITE_NAME}</a>
    <div class="page-footer__sep"></div>
    <span>报告与研究成果</span>
  </footer>'''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_info["title"]}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css_href}">
{cdn_tags}{style_tag}
</head>
<body>
  <div class="scroll-progress"></div>
  <aside class="toc-sidebar">
    <div class="toc-sidebar__header">
      <div class="toc-sidebar__title">目录</div>
      <button class="toc-sidebar__close" aria-label="收起目录">✕</button>
    </div>
    <div class="toc-list"></div>
  </aside>
  <button class="toc-toggle" aria-label="展开目录">☰</button>
  <div class="report-wrap">
{chrome_header}
    <div class="page-body" data-reveal>{body}</div>
  </div>
  <button class="back-to-top" aria-label="回到顶部">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
  </button>
{chrome_footer}
  <script src="{js_src}"></script>
{mermaid_script}
</body>
</html>'''

def copy_assets():
    """同步静态资源到部署目录（实现在 local_deploy.py）"""
    from lib.local_deploy import copy_assets as _sync
    return _sync()
