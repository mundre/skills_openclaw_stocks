#!/usr/bin/env python3
"""
create-word-doc.py - 企业级 Word 文档生成器 v5.0（多规范支持版）

支持多文档规范自动识别：
- 公文格式（GB/T 9704-2012）- 默认
- 合同格式
- 会议纪要格式
- 技术方案格式
- 需求文档格式
- 工作报告格式

用法：
    python create-word-doc.py <输出路径> [标题] [正文] [编号] [版本] [密级] [格式]
"""

import sys
import os
import re
import ssl
import json
import datetime
import urllib.request
import xmlrpc.client
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ============== 文档格式预设 ==============
class FormatPreset:
    """文档格式预设"""
    def __init__(self, name, margin_top=3.7, margin_bottom=3.5,
                 margin_left=2.8, margin_right=2.6,
                 font_body='仿宋', font_title='黑体', font_heading='黑体',
                 size_title=22, size_chapter=16, size_section=14, size_body=12,
                 heading_patterns=None, line_spacing=1.5,
                 has_version_history=True, has_approval=True,
                 header_style='company', footer_style='page'):
        self.name = name
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.font_body = font_body
        self.font_title = font_title
        self.font_heading = font_heading
        self.size_title = size_title
        self.size_chapter = size_chapter
        self.size_section = size_section
        self.size_body = size_body
        self.line_spacing = line_spacing
        self.has_version_history = has_version_history
        self.has_approval = has_approval
        self.header_style = header_style
        self.footer_style = footer_style
        # 标题识别模式：[正则, 层级]
        self.heading_patterns = heading_patterns or []

# 预定义格式
PRESET_GONGWEN = FormatPreset(
    name='公文',
    heading_patterns=[
        (r'^第[一二三四五六七八九十百千]+[章节篇款]', 'chapter'),
        (r'^[一二三四五六七八九十百千]+[、．,，]', 'section'),
        (r'^[（\(][一二三四五六七八九十百千]+[）\)]', 'article'),
    ]
)

PRESET_HETONG = FormatPreset(
    name='合同',
    margin_top=2.54, margin_bottom=2.54, margin_left=3.17, margin_right=3.17,
    font_body='宋体', font_title='宋体', font_heading='宋体',
    size_title=22, size_chapter=15, size_section=12, size_body=12,
    line_spacing=1.5,
    heading_patterns=[
        (r'^第[一二三四五六七八九十百千]+[章节条款]', 'chapter'),
        (r'^[一二三四五六七八九十百千]+[、]', 'section'),
    ],
    has_version_history=False,
    has_approval=True,
    header_style='simple',
    footer_style='page'
)

PRESET_HUIYI = FormatPreset(
    name='会议纪要',
    font_body='仿宋', font_title='方正小标宋简体', font_heading='黑体',
    size_title=22, size_chapter=14, size_section=12, size_body=12,
    line_spacing=1.5,
    heading_patterns=[
        (r'^【[^】]+】', 'chapter'),
        (r'^[一二三四五六七八九十]+[、]', 'section'),
    ],
    has_version_history=False,
    has_approval=False,
    header_style='title_only',
    footer_style='page'
)

PRESET_FANGAN = FormatPreset(
    name='技术方案',
    font_body='宋体', font_title='黑体', font_heading='黑体',
    size_title=22, size_chapter=16, size_section=14, size_body=12,
    line_spacing=1.5,
    heading_patterns=[
        (r'^[一二三四五六七八九十百]+[．、]', 'chapter'),
        (r'^[0-9]+[．、]', 'section'),
        (r'^[0-9]+\.[0-9]+', 'article'),
    ],
    has_version_history=True,
    has_approval=True,
    header_style='company',
    footer_style='page'
)

PRESET_XUQIU = FormatPreset(
    name='需求文档',
    font_body='宋体', font_title='黑体', font_heading='黑体',
    size_title=22, size_chapter=16, size_section=14, size_body=12,
    line_spacing=1.5,
    heading_patterns=[
        (r'^[一二三四五六七八九十百]+[．、]', 'chapter'),
        (r'^[0-9]+[．、]', 'section'),
        (r'^[0-9]+\.[0-9]+', 'article'),
    ],
    has_version_history=True,
    has_approval=True,
    header_style='company',
    footer_style='page'
)

PRESET_GONGZUO = FormatPreset(
    name='工作报告',
    font_body='仿宋', font_title='方正小标宋简体', font_heading='楷体',
    size_title=22, size_chapter=16, size_section=14, size_body=12,
    line_spacing=1.5,
    heading_patterns=[
        (r'^[一二三四五六七八九十百]+[、．]', 'chapter'),
        (r'^[（\(][一二三四五六七八九十]+[）\)]', 'section'),
    ],
    has_version_history=False,
    has_approval=True,
    header_style='company',
    footer_style='page'
)

# 格式注册表
FORMAT_PRESETS = {
    '公文': PRESET_GONGWEN,
    '合同': PRESET_HETONG,
    '会议纪要': PRESET_HUIYI,
    '技术方案': PRESET_FANGAN,
    '需求文档': PRESET_XUQIU,
    '工作报告': PRESET_GONGZUO,
}

# 识别关键词
FORMAT_KEYWORDS = {
    '合同': ['合同', '协议', '协议书'],
    '会议纪要': ['会议纪要', '纪要'],
    '技术方案': ['技术方案', '实施方案', '解决方案', '设计文档'],
    '需求文档': ['需求', '需求规格', '需求说明', 'SRS'],
    '工作报告': ['工作报告', '周报', '月报', '季报', '年报', '述职报告'],
}

# ============== 公司信息 ==============
USER_HOME = os.path.expanduser("~")
LOGO_DIR = os.path.join(USER_HOME, ".huo15", "assets")
DEFAULT_LOGO_PATH = os.path.join(LOGO_DIR, "logo.png")
FALLBACK_LOGO_URL = 'https://tools.huo15.com/uploads/images/system/logo-colours.png'
DEFAULT_COMPANY_NAME = '青岛火一五信息科技有限公司'

# 首行缩进
FIRST_LINE_INDENT = Cm(0.74)


def get_company_info():
    """从公司系统获取公司信息和 LOGO"""
    info = {'company_name': DEFAULT_COMPANY_NAME, 'logo_path': None}

    if os.path.exists(DEFAULT_LOGO_PATH) and os.path.getsize(DEFAULT_LOGO_PATH) > 1000:
        info['logo_path'] = DEFAULT_LOGO_PATH
        return info

    try:
        creds_file = os.path.join(
            os.path.expanduser('~/.openclaw/agents'),
            os.environ.get('OC_AGENT_ID', 'main'),
            'odoo_creds.json'
        )
        if os.path.exists(creds_file):
            with open(creds_file) as f:
                creds = json.load(f)

            cfg_file = os.path.expanduser('~/.openclaw/openclaw.json')
            if os.path.exists(cfg_file):
                with open(cfg_file) as f:
                    cfg = json.load(f)
                    odoo_env = cfg.get('skills', {}).get('entries', {}).get('huo15-odoo', {}).get('env', {})
                    url = odoo_env.get('ODOO_URL', 'https://huihuoyun.huo15.com')
                    db = odoo_env.get('ODOO_DB', 'huo15_prod')

                user = creds.get('user', '')
                password = creds.get('password', '')
                if user and password:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=ctx)
                    uid = common.authenticate(db, user, password, {})
                    if uid:
                        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=ctx)
                        data = models.execute_kw(db, uid, password, 'res.company',
                            'search_read', [[('id', '=', 1)]], {'fields': ['name', 'logo'], 'limit': 1})
                        if data:
                            info['company_name'] = data[0].get('name', DEFAULT_COMPANY_NAME)
                            logo_id = data[0].get('logo')
                            if logo_id:
                                _download(f'{url}/web/image/res.company/{logo_id}/logo', DEFAULT_LOGO_PATH)
                                if os.path.exists(DEFAULT_LOGO_PATH):
                                    info['logo_path'] = DEFAULT_LOGO_PATH
    except Exception as e:
        print(f"获取公司信息失败: {e}")

    if not info['logo_path']:
        _download(FALLBACK_LOGO_URL, DEFAULT_LOGO_PATH)
        if os.path.exists(DEFAULT_LOGO_PATH):
            info['logo_path'] = DEFAULT_LOGO_PATH

    return info


def _download(url, dest_path):
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"✓ LOGO 已下载: {dest_path}")
    except Exception as e:
        print(f"⚠ LOGO 下载失败: {e}")


def detect_format(title='', content=''):
    """根据标题和内容自动检测文档格式"""
    text = (title + ' ' + (content or '')[:500]).lower()

    for fmt, keywords in FORMAT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                return fmt

    # 默认公文格式
    return '公文'


def get_preset(format_name):
    """获取格式预设"""
    return FORMAT_PRESETS.get(format_name, PRESET_GONGWEN)


# ============== 字体工具 ==============

def _set_font(run, font_name, size, bold=False, color=None):
    """设置中文字体（WPS/Word 双兼容）"""
    run.font.name = font_name
    rPr = run._element.find(qn('w:rPr'))
    if rPr is None:
        rPr = OxmlElement('w:rPr')
        run._element.insert(0, rPr)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), font_name)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = color


def _add_border_bottom(paragraph):
    """给段落下方加细线"""
    pPr = paragraph._element.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        paragraph._element.insert(0, pPr)
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)


def _set_cell_shading(cell, fill_color):
    """设置单元格背景色"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)


# ============== 页眉页脚 ==============

def add_header(doc, preset, logo_path, company_name, doc_number=None, classification=None, title=''):
    """添加页眉"""
    section = doc.sections[0]
    header = section.header
    header.is_linked_to_previous = False

    for p in header.paragraphs:
        for r in p.runs:
            r.text = ''
    para = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT

    style = preset.header_style
    size = preset.size_body - 2

    if style == 'company':
        # 公文式：LOGO + 公司名 + 文档编号 + 密级
        if logo_path and os.path.exists(logo_path):
            try:
                run = para.add_run()
                run.add_picture(logo_path, height=Cm(1.0))
            except Exception as e:
                print(f"⚠ LOGO 添加失败: {e}")
        run = para.add_run(f' {company_name}')
        _set_font(run, '黑体', size)
        if doc_number:
            run = para.add_run(f'  {doc_number}')
            _set_font(run, '黑体', size)
        if classification:
            run = para.add_run(f'  【{classification}】')
            _set_font(run, '黑体', size, bold=True)
        _add_border_bottom(para)

    elif style == 'simple':
        # 合同式：仅公司名，居中
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(company_name)
        _set_font(run, '宋体', size)
        _add_border_bottom(para)

    elif style == 'title_only':
        # 纪要式：仅标题
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if title:
            run = para.add_run(title)
            _set_font(run, '黑体', size)


def add_footer(doc, preset):
    """添加页脚"""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False

    para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for r in para.runs:
        r.text = ''

    def add_text(text):
        r = para.add_run(text)
        _set_font(r, preset.font_body, preset.size_body - 2)
        return r

    def add_field(name):
        r = para.add_run()
        fc1 = OxmlElement('w:fldChar')
        fc1.set(qn('w:fldCharType'), 'begin')
        it = OxmlElement('w:instrText')
        it.set(qn('xml:space'), 'preserve')
        it.text = f' {name} '
        fc2 = OxmlElement('w:fldChar')
        fc2.set(qn('w:fldCharType'), 'end')
        r._element.clear()
        r._element.append(fc1)
        r._element.append(it)
        r._element.append(fc2)
        _set_font(r, preset.font_body, preset.size_body - 2)

    if preset.footer_style == 'page':
        add_text('第 ')
        add_field('PAGE')
        add_text(' 页 / 共 ')
        add_field('NUMPAGES')
        add_text(' 页')


# ============== 段落样式 ==============

class ParagraphStyle:
    def __init__(self, font, size, bold=False, indent=True,
                 alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                 space_before=0, space_after=6, line_spacing=1.5):
        self.font = font
        self.size = size
        self.bold = bold
        self.indent = indent
        self.alignment = alignment
        self.space_before = space_before
        self.space_after = space_after
        self.line_spacing = line_spacing

    def apply(self, p):
        p.alignment = self.alignment
        p.paragraph_format.line_spacing = self.line_spacing
        p.paragraph_format.space_before = Pt(self.space_before)
        p.paragraph_format.space_after = Pt(self.space_after)
        if self.indent:
            p.paragraph_format.first_line_indent = FIRST_LINE_INDENT
        else:
            p.paragraph_format.first_line_indent = Cm(0)


def get_styles(preset):
    """获取格式对应的段落样式"""
    return {
        'chapter': ParagraphStyle(
            preset.font_heading, preset.size_chapter, bold=True,
            indent=False, alignment=WD_ALIGN_PARAGRAPH.LEFT,
            space_before=18, space_after=6, line_spacing=preset.line_spacing
        ),
        'section': ParagraphStyle(
            preset.font_heading, preset.size_section, bold=True,
            indent=False, alignment=WD_ALIGN_PARAGRAPH.LEFT,
            space_before=12, space_after=4, line_spacing=preset.line_spacing
        ),
        'article': ParagraphStyle(
            preset.font_heading, preset.size_body, bold=True,
            indent=False, alignment=WD_ALIGN_PARAGRAPH.LEFT,
            space_before=6, space_after=3, line_spacing=preset.line_spacing
        ),
        'body': ParagraphStyle(
            preset.font_body, preset.size_body, bold=False,
            indent=True, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
            space_before=0, space_after=6, line_spacing=preset.line_spacing
        ),
        'empty': ParagraphStyle(
            preset.font_body, preset.size_body, bold=False,
            indent=False, alignment=WD_ALIGN_PARAGRAPH.LEFT,
            space_before=0, space_after=0, line_spacing=preset.line_spacing
        ),
    }


def add_paragraph(doc, text, style):
    """添加段落并应用样式"""
    p = doc.add_paragraph()
    style.apply(p)
    if text:
        run = p.add_run(text)
        _set_font(run, style.font, style.size, style.bold)
    return p


def add_empty_line(doc):
    """添加空行"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0


# ============== 内容解析 ==============

def detect_paragraph_type(text, preset):
    """检测段落类型"""
    if not text or not text.strip():
        return 'blank', ''

    t = text.strip()

    for pattern, ptype in preset.heading_patterns:
        if re.match(pattern, t):
            # 去掉标题前缀
            cleaned = re.sub(pattern, '', t).strip()
            return ptype, cleaned

    return 'body', t


def parse_table_lines(lines, start_idx):
    """解析连续表格行"""
    table_lines = []
    i = start_idx
    while i < len(lines):
        t = lines[i].strip()
        if t.startswith('|'):
            if re.match(r'^[\|\-\s]+$', t):
                i += 1
                continue
            table_lines.append(t)
            i += 1
        else:
            break
    return table_lines, i


def build_table(doc, table_lines):
    """将表格行数据写入 Word 表格"""
    rows_data = []
    for line in table_lines:
        # 过滤分隔行
        if re.match(r'^[\|\-\s]+$', line.strip()):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows_data.append(cells)

    if len(rows_data) < 2:
        return

    cols = len(rows_data[0])
    table = doc.add_table(rows=len(rows_data), cols=cols)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for r, row in enumerate(rows_data):
        is_header = (r == 0)
        for c, text in enumerate(row):
            cell = table.rows[r].cells[c]
            cell.text = text
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                font_name = '宋体' if is_header else '仿宋'
                for run in para.runs:
                    _set_font(run, font_name, 10.5, bold=is_header)
            if is_header:
                _set_cell_shading(cell, 'D9D9D9')

    return table


def parse_content(doc, content, preset):
    """将纯文本内容解析并写入 Word"""
    if not content:
        return

    styles = get_styles(preset)
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        t = line.strip()

        if not t:
            add_empty_line(doc)
            i += 1
            continue

        if t.startswith('|'):
            table_lines, i = parse_table_lines(lines, i)
            build_table(doc, table_lines)
            continue

        ptype, clean_text = detect_paragraph_type(t, preset)

        if ptype == 'blank':
            add_empty_line(doc)
        elif ptype in styles:
            add_paragraph(doc, t, styles[ptype])
        else:
            add_paragraph(doc, clean_text, styles['body'])

        i += 1


# ============== 版本历史 & 审批区 ==============

def add_version_history(doc, preset, version='V1.0', date=None, author=None):
    """添加版本历史表"""
    if not preset.has_version_history:
        return

    if not date:
        date = datetime.date.today().strftime('%Y-%m-%d')

    add_empty_line(doc)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run('【版本历史】')
    _set_font(run, preset.font_heading, preset.size_section, bold=True)
    p.paragraph_format.space_after = Pt(6)

    table_data = [
        '| 版本 | 日期 | 作者 | 修改内容 |',
        f'| {version} | {date} | {author or "未知"} | 首次创建 |',
    ]
    build_table(doc, table_data)


def add_approval_block(doc, preset, approval_list=None):
    """添加审批签字区"""
    if not preset.has_approval:
        return

    if approval_list is None:
        approval_list = [
            {'role': '编制', 'name': ''},
            {'role': '审核', 'name': ''},
            {'role': '批准', 'name': ''},
        ]

    add_empty_line(doc)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run('【审批记录】')
    _set_font(run, preset.font_heading, preset.size_section, bold=True)
    p.paragraph_format.space_after = Pt(6)

    today = datetime.date.today().strftime('%Y-%m-%d')

    header = '| 角色 | 姓名 | 日期 | 签字 |'
    rows = [header]
    for item in approval_list:
        role = item.get('role', '')
        name = item.get('name', '__________')
        date_str = item.get('date', today if role == '编制' else '')
        rows.append(f'| {role} | {name or "__________"} | {date_str} | __________ |')

    build_table(doc, rows)


def add_classification_mark(doc, classification):
    """添加密级标识"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(f'【{classification}】')
    _set_font(run, '仿宋', 12, bold=True)
    p.paragraph_format.space_after = Pt(0)


# ============== 主函数 ==============

def create_word_doc(output_path, title='', content='', doc_number=None, version='V1.0',
                   classification='内部', author=None, company_name=None,
                   logo_path=None, approval=None, footer_page=True, header_doc_number=True,
                   doc_format=None):
    """
    生成企业标准 Word 文档 v5.0（多规范支持）

    参数:
        output_path: 输出文件路径（必需）
        title: 文档标题（可选）
        content: 正文内容（可选）
        doc_number: 文档编号（可选）
        version: 版本号（默认 V1.0）
        classification: 密级（默认内部）
        author: 作者（可选）
        company_name: 公司名称（可选）
        logo_path: LOGO路径（可选）
        approval: 审批人列表（可选）
        footer_page: 页脚显示页码（默认 True）
        header_doc_number: 页眉显示文档编号（默认 True）
        doc_format: 文档格式（自动检测：公文/合同/会议纪要/技术方案/需求文档/工作报告）
    """
    doc = Document()

    # 检测格式
    if not doc_format or doc_format == 'auto':
        doc_format = detect_format(title, content)

    preset = get_preset(doc_format)
    print(f"📄 使用文档格式: {preset.name} ({doc_format})")

    # 页面设置
    for sec in doc.sections:
        sec.top_margin = Cm(preset.margin_top)
        sec.bottom_margin = Cm(preset.margin_bottom)
        sec.left_margin = Cm(preset.margin_left)
        sec.right_margin = Cm(preset.margin_right)
        sec.header_distance = Cm(1.5)
        sec.footer_distance = Cm(1.5)

    # 公司信息
    info = get_company_info()
    logo = logo_path or info.get('logo_path')
    company = company_name or info.get('company_name', DEFAULT_COMPANY_NAME)

    # 页眉
    header_doc_num = doc_number if header_doc_number else None
    add_header(doc, preset, logo, company, header_doc_num, classification, title)

    # 页脚
    if footer_page:
        add_footer(doc, preset)

    # 默认样式
    style = doc.styles['Normal']
    style.font.name = preset.font_body
    style.font.size = Pt(preset.size_body)

    # 密级标识
    if classification and classification != '公开':
        add_classification_mark(doc, classification)

    # 文档标题
    if title:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title)
        _set_font(run, preset.font_title, preset.size_title, bold=True)
        p.paragraph_format.line_spacing = preset.line_spacing
        p.paragraph_format.space_after = Pt(18)

    # 元数据
    meta_items = []
    if doc_number:
        meta_items.append(f'文档编号：{doc_number}')
    meta_items.append(f'版本：{version}')
    meta_items.append(f'密级：{classification}')
    today = datetime.date.today().strftime('%Y-%m-%d')
    meta_items.append(f'日期：{today}')
    if author:
        meta_items.append(f'作者：{author}')

    if meta_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(6)
        meta_text = '  |  '.join(meta_items)
        run = p.add_run(meta_text)
        _set_font(run, preset.font_body, preset.size_body - 1)

    # 版本历史
    add_version_history(doc, preset, version, today, author or '未知')

    # 正文
    parse_content(doc, content, preset)

    # 审批签字区
    if approval is not None:
        add_approval_block(doc, preset, approval)

    doc.save(output_path)
    print(f'✅ 文档已生成: {output_path}')
    return output_path


if __name__ == '__main__':
    args = sys.argv
    output = args[1] if len(args) > 1 else 'output.docx'
    title = args[2] if len(args) > 2 else ''
    content = args[3] if len(args) > 3 else ''
    doc_number = args[4] if len(args) > 4 else None
    version = args[5] if len(args) > 5 else 'V1.0'
    classification = args[6] if len(args) > 6 else '内部'
    doc_format = args[7] if len(args) > 7 else 'auto'

    create_word_doc(
        output_path=output,
        title=title,
        content=content,
        doc_number=doc_number,
        version=version,
        classification=classification,
        doc_format=doc_format
    )
