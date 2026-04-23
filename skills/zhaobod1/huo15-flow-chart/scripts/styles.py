"""火一五流程图 — 4 种风格的主题变量。

供 Mermaid `--themeVariables`、PlantUML skinparam、Graphviz attr 共用。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Style:
    key: str
    name: str
    # Mermaid theme：default / neutral / forest / dark / base
    mermaid_theme: str = "base"
    # 核心色板
    primary_color: str = "#2C3E50"         # 主节点背景
    primary_text_color: str = "#FFFFFF"    # 主节点文字
    primary_border_color: str = "#1A252F"  # 主节点描边
    secondary_color: str = "#ECF0F1"       # 次级节点
    tertiary_color: str = "#BDC3C7"        # 三级节点
    line_color: str = "#34495E"            # 连线
    background: str = "#FFFFFF"            # 整体背景
    font_family: str = '"PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Hiragino Sans GB", sans-serif'
    font_size: str = "14px"
    # 流程中的 decision (diamond) 用强调色
    accent_color: str = "#E67E22"
    note_color: str = "#FDF6E3"
    note_border: str = "#E8D7A0"


MODERN = Style(
    key="modern",
    name="现代商务",
    mermaid_theme="base",
    primary_color="#2C3E50",
    primary_text_color="#FFFFFF",
    primary_border_color="#1A252F",
    secondary_color="#ECF0F1",
    tertiary_color="#BDC3C7",
    line_color="#34495E",
    background="#FFFFFF",
    accent_color="#E67E22",
)

CLASSIC = Style(
    key="classic",
    name="经典稳重",
    mermaid_theme="neutral",
    primary_color="#374785",
    primary_text_color="#FFFFFF",
    primary_border_color="#24305E",
    secondary_color="#A8D0E6",
    tertiary_color="#F8E9A1",
    line_color="#24305E",
    background="#FAFAFA",
    accent_color="#F76C6C",
)

DARK = Style(
    key="dark",
    name="暗色霓虹",
    mermaid_theme="dark",
    primary_color="#38BDF8",
    primary_text_color="#0F172A",
    primary_border_color="#7DD3FC",
    secondary_color="#1E293B",
    tertiary_color="#334155",
    line_color="#38BDF8",
    background="#0F172A",
    accent_color="#F472B6",
    note_color="#1E293B",
    note_border="#38BDF8",
)

XIAOHONGSHU = Style(
    key="xiaohongshu",
    name="小红书暖奶油",
    mermaid_theme="base",
    primary_color="#FF2442",
    primary_text_color="#FFFFFF",
    primary_border_color="#D91E33",
    secondary_color="#FFE5EC",
    tertiary_color="#FFB5C2",
    line_color="#FF2442",
    background="#FFF8F3",
    accent_color="#FF8A65",
    note_color="#FFF1E6",
    note_border="#FFB38A",
)

OCEAN = Style(
    key="ocean",
    name="海洋蓝",
    mermaid_theme="base",
    primary_color="#0077B6",
    primary_text_color="#FFFFFF",
    primary_border_color="#023E8A",
    secondary_color="#CAF0F8",
    tertiary_color="#90E0EF",
    line_color="#0077B6",
    background="#F8FBFE",
    accent_color="#FB8500",
    note_color="#E7F5FA",
    note_border="#90CAF9",
)

FOREST = Style(
    key="forest",
    name="森林绿",
    mermaid_theme="base",
    primary_color="#2D6A4F",
    primary_text_color="#FFFFFF",
    primary_border_color="#1B4332",
    secondary_color="#D8F3DC",
    tertiary_color="#95D5B2",
    line_color="#40916C",
    background="#F7FAF8",
    accent_color="#D68C45",
    note_color="#F1F8E9",
    note_border="#AED581",
)

SUNSET = Style(
    key="sunset",
    name="夕阳暖橙",
    mermaid_theme="base",
    primary_color="#E76F51",
    primary_text_color="#FFFFFF",
    primary_border_color="#9D3B1E",
    secondary_color="#FFEBD6",
    tertiary_color="#F4A261",
    line_color="#E76F51",
    background="#FFFBF5",
    accent_color="#2A9D8F",
    note_color="#FFF6E9",
    note_border="#F4A261",
)

MINIMAL = Style(
    key="minimal",
    name="极简素雅",
    mermaid_theme="neutral",
    primary_color="#2E2E2E",
    primary_text_color="#FFFFFF",
    primary_border_color="#000000",
    secondary_color="#F5F5F5",
    tertiary_color="#D4D4D4",
    line_color="#595959",
    background="#FFFFFF",
    accent_color="#0A4D8E",
    note_color="#FAFAFA",
    note_border="#D4D4D4",
)

PASTEL = Style(
    key="pastel",
    name="马卡龙粉嫩",
    mermaid_theme="base",
    primary_color="#B5D8FA",
    primary_text_color="#2D3748",
    primary_border_color="#7FA7CC",
    secondary_color="#FFE5EC",
    tertiary_color="#F7D8D8",
    line_color="#C4A4E1",
    background="#FFFBFC",
    accent_color="#FFB5A7",
    note_color="#FFF5F7",
    note_border="#FFB5A7",
)

GITHUB = Style(
    key="github",
    name="极客 GitHub",
    mermaid_theme="base",
    primary_color="#24292E",
    primary_text_color="#FFFFFF",
    primary_border_color="#0366D6",
    secondary_color="#F6F8FA",
    tertiary_color="#E1E4E8",
    line_color="#0366D6",
    background="#FFFFFF",
    accent_color="#28A745",
    note_color="#FFF8C5",
    note_border="#D9C873",
)


_ALL = {
    s.key: s
    for s in (
        MODERN,
        CLASSIC,
        DARK,
        XIAOHONGSHU,
        OCEAN,
        FOREST,
        SUNSET,
        MINIMAL,
        PASTEL,
        GITHUB,
    )
}
_ALIAS = {
    "现代": MODERN.key,
    "商务": MODERN.key,
    "经典": CLASSIC.key,
    "稳重": CLASSIC.key,
    "暗色": DARK.key,
    "黑色": DARK.key,
    "霓虹": DARK.key,
    "dark-neon": DARK.key,
    "小红书": XIAOHONGSHU.key,
    "xhs": XIAOHONGSHU.key,
    "奶油": XIAOHONGSHU.key,
    "海洋": OCEAN.key,
    "蓝": OCEAN.key,
    "蓝色": OCEAN.key,
    "森林": FOREST.key,
    "绿": FOREST.key,
    "绿色": FOREST.key,
    "自然": FOREST.key,
    "夕阳": SUNSET.key,
    "暖橙": SUNSET.key,
    "橙": SUNSET.key,
    "橙色": SUNSET.key,
    "极简": MINIMAL.key,
    "素雅": MINIMAL.key,
    "黑白": MINIMAL.key,
    "学术": MINIMAL.key,
    "论文": MINIMAL.key,
    "马卡龙": PASTEL.key,
    "粉嫩": PASTEL.key,
    "粉": PASTEL.key,
    "粉色": PASTEL.key,
    "儿童": PASTEL.key,
    "极客": GITHUB.key,
    "程序员": GITHUB.key,
    "gh": GITHUB.key,
}


def get_style(key: str) -> Style:
    k = (key or "modern").strip().lower()
    if k in _ALL:
        return _ALL[k]
    if k in _ALIAS:
        return _ALL[_ALIAS[k]]
    raise ValueError(f"未知风格：{key}；可选 {list(_ALL)}")


def list_styles() -> Dict[str, Style]:
    return dict(_ALL)


def to_mermaid_theme_variables(style: Style) -> Dict[str, str]:
    """Mermaid initialize 支持的 themeVariables。"""
    return {
        "primaryColor": style.primary_color,
        "primaryTextColor": style.primary_text_color,
        "primaryBorderColor": style.primary_border_color,
        "lineColor": style.line_color,
        "secondaryColor": style.secondary_color,
        "tertiaryColor": style.tertiary_color,
        "background": style.background,
        "mainBkg": style.primary_color,
        "secondBkg": style.secondary_color,
        "fontFamily": style.font_family,
        "fontSize": style.font_size,
        "noteBkgColor": style.note_color,
        "noteBorderColor": style.note_border,
        "actorBkg": style.primary_color,
        "actorBorder": style.primary_border_color,
        "actorTextColor": style.primary_text_color,
        "activationBkgColor": style.secondary_color,
        "sequenceNumberColor": style.primary_text_color,
    }


def to_mermaid_init_directive(style: Style) -> str:
    """返回 `%%{init: {...}}%%` 这一行，放在 Mermaid 代码最前。"""
    import json
    cfg = {
        "theme": style.mermaid_theme,
        "themeVariables": to_mermaid_theme_variables(style),
        "flowchart": {"curve": "basis", "htmlLabels": True},
        "sequence": {"mirrorActors": False, "showSequenceNumbers": False},
    }
    return "%%{init: " + json.dumps(cfg, ensure_ascii=False) + "}%%"


def to_plantuml_skinparam(style: Style) -> str:
    """PlantUML skinparam 片段（泳道图 / 活动图用）。"""
    return f"""skinparam backgroundColor {style.background}
skinparam defaultFontName {style.font_family.split(',')[0].strip('"')}
skinparam defaultFontSize 14
skinparam roundCorner 8
skinparam shadowing false
skinparam activity {{
    BackgroundColor {style.primary_color}
    BorderColor {style.primary_border_color}
    FontColor {style.primary_text_color}
    DiamondBackgroundColor {style.accent_color}
    DiamondBorderColor {style.primary_border_color}
    DiamondFontColor #FFFFFF
}}
skinparam swimlane {{
    BorderColor {style.primary_border_color}
    BorderThickness 1.5
    TitleBackgroundColor {style.secondary_color}
    TitleFontColor {style.primary_border_color}
}}
skinparam note {{
    BackgroundColor {style.note_color}
    BorderColor {style.note_border}
}}
skinparam arrow {{
    Color {style.line_color}
    Thickness 1.5
}}
"""
