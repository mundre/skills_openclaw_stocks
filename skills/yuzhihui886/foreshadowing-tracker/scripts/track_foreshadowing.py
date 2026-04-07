#!/usr/bin/env python3
"""伏笔追踪器 - Foreshadowing Tracker

用于识别、追踪和报告小说中的伏笔。
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress


console = Console()


class Foreshadowing:
    """伏笔类"""
    
    def __init__(
        self,
        text: str,
        chapter: int,
        location: int,
        hint_type: str,
        is_recycled: bool = False,
        recycled_chapter: int | None = None,
        recycled_location: int | None = None,
        explanation: str = ""
    ):
        self.text = text
        self.chapter = chapter
        self.location = location
        self.hint_type = hint_type
        self.is_recycled = is_recycled
        self.recycled_chapter = recycled_chapter
        self.recycled_location = recycled_location
        self.explanation = explanation
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "chapter": self.chapter,
            "location": self.location,
            "hint_type": self.hint_type,
            "is_recycled": self.is_recycled,
            "recycled_chapter": self.recycled_chapter,
            "recycled_location": self.recycled_location,
            "explanation": self.explanation
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Foreshadowing":
        return cls(
            text=data["text"],
            chapter=data["chapter"],
            location=data["location"],
            hint_type=data["hint_type"],
            is_recycled=data.get("is_recycled", False),
            recycled_chapter=data.get("recycled_chapter"),
            recycled_location=data.get("recycled_location"),
            explanation=data.get("explanation", "")
        )


class ForeshadowingTracker:
    """伏笔追踪器"""
    
    HINT_PATTERNS = {
        "suspense": [
            r"似乎[只]?有[我他她它].*知道",
            r"不知道[为什什么].*",
            r"总觉得.*要发生",
            r"隐约.*不祥",
            r"似乎.*着什么",
            r"这.*绝不简单",
            r"背后.*有.*原因",
            r"[可是然而但是]，谁.*知道呢",
        ],
        "foreshadowing": [
            r"此时.*还不.*知道",
            r"多年.*后才明白",
            r"那时.*还年轻",
            r"说.*时，.*不.*懂",
            r"这.*后来.*关键",
        ],
        "callback": [
            r"后来.*证实.*这.*原因",
            r"之前.*说过.*这",
            r"终于明白.*当时.*为什么",
            r"这一切.*是因为.*之前",
        ]
    }
    
    def __init__(self):
        self.foreshadowings: list[Foreshadowing] = []
        self._seen_texts: dict[tuple[str, int], bool] = {}  # 用于去重
    
    def load_existing(self, file_path: Path) -> None:
        """加载已记录的伏笔"""
        if not file_path.exists():
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("foreshadowings", []):
                    fs = Foreshadowing.from_dict(item)
                    self.foreshadowings.append(fs)
                    self._seen_texts[(fs.text, fs.chapter)] = True
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[yellow]警告: 读取伏笔记录失败 {file_path}: {e}[/yellow]")
    
    def extract_hints(self, text: str, chapter: int) -> list[Foreshadowing]:
        """从文本中提取伏笔线索"""
        foreshadowings = []
        
        lines = text.split("\n")
        for line_num, line in enumerate(lines):
            for hint_type, patterns in self.HINT_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        confidence = self.CONFIDENCE_WEIGHTS.get(hint_type, 0.5)
                        foreshadowings.append(
                            Foreshadowing(
                                text=match.group(0),
                                chapter=chapter,
                                location=line_num,
                                hint_type=hint_type,
                                is_recycled=False,
                                explanation=f"置信度：{confidence:.0%}"
                            )
                        )
        
        foreshadowings.sort(key=lambda x: self.CONFIDENCE_WEIGHTS.get(x.hint_type, 0.5), reverse=True)
        return foreshadowings

    def detect_recycling(self, text: str, chapter: int) -> dict[int, bool]:
        """检测已存在的伏笔是否被回收"""
        recycling_map = {}
        
        for idx, fs in enumerate(self.foreshadowings):
            if fs.is_recycled:
                continue
            
            if re.search(re.escape(fs.text), text):
                recycling_map[idx] = True
            elif self._match_context(fs.text, text):
                recycling_map[idx] = True
        
        return recycling_map
    
    def _match_context(self, hint_text: str, chapter_text: str) -> bool:
        """通过上下文匹配检测伏笔回收"""
        hint_lower = hint_text.lower()
        
        recycling_keywords = [
            "证实", "证明", "原来", "竟然是", "终于明白",
            "正是此时", "一切揭晓", "真相大白", "恍然大悟",
            "当年那个", "此刻", "多年后", "回忆起"
        ]
        
        for keyword in recycling_keywords:
            if keyword in chapter_text and hint_lower in chapter_text.lower():
                return True
        
        return False
    
    def process_chapter(self, chapter_path: Path, chapter_num: int) -> list[Foreshadowing]:
        """处理单个章节"""
        console.print(f"[bold blue]处理章节: {chapter_path.name}[/bold blue]")
        
        foreshadowings = []
        
        try:
            with open(chapter_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            console.print(f"[red]错误: 无法读取章节 {chapter_path}: {e}[/red]")
            return foreshadowings
        
        new_hints = self.extract_hints(text, chapter_num)
        foreshadowings.extend(new_hints)
        
        recycling_map = self.detect_recycling(text, chapter_num)
        
        for idx, is_recycled in recycling_map.items():
            if is_recycled and idx < len(self.foreshadowings):
                self.foreshadowings[idx].is_recycled = True
                self.foreshadowings[idx].recycled_chapter = chapter_num
                self.foreshadowings[idx].recycled_location = 0  # 需要进一步分析确定具体位置
        
        return foreshadowings
    
    def process_book(self, book_dir: Path, chapter_file: str | None = None) -> list[Foreshadowing]:
        """处理整本书"""
        all_new_foreshadowings: list[Foreshadowing] = []
        
        if chapter_file:
            chapter_path = book_dir / chapter_file
            if chapter_path.exists():
                new_foreshadowings = self.process_chapter(chapter_path, 1)
                all_new_foreshadowings.extend(new_foreshadowings)
            else:
                console.print(f"[yellow]警告: 指定章节文件不存在: {chapter_path}[/yellow]")
        else:
            chapters = sorted(book_dir.glob("chapter_*.txt"))
            
            with Progress() as progress:
                task = progress.add_task(
                    f"[cyan]处理书籍 {book_dir.name}...", 
                    total=len(chapters)
                )
                
                for i, chapter_path in enumerate(chapters, 1):
                    new_foreshadowings = self.process_chapter(chapter_path, i)
                    all_new_foreshadowings.extend(new_foreshadowings)
                    progress.update(task, advance=1)
        
        return all_new_foreshadowings
    
    def generate_report(self, output_path: Path) -> None:
        """生成伏笔追踪报告"""
        console.print("\n[bold underline]生成伏笔追踪报告[/bold underline]")
        
        new_foreshadowings = [
            fs for fs in self.foreshadowings
            if not fs.is_recycled and (fs.text, fs.chapter) not in self._seen_texts
        ]
        
        pending_foreshadowings = [
            fs for fs in self.foreshadowings 
            if not fs.is_recycled
        ]
        
        recycled_foreshadowings = [
            fs for fs in self.foreshadowings 
            if fs.is_recycled
        ]
        
        report_data = {
            "summary": {
                "total_foreshadowings": len(self.foreshadowings),
                "new_count": len(new_foreshadowings),
                "pending_count": len(pending_foreshadowings),
                "recycled_count": len(recycled_foreshadowings)
            },
            "new": [fs.to_dict() for fs in new_foreshadowings],
            "pending": [fs.to_dict() for fs in pending_foreshadowings],
            "recycled": [fs.to_dict() for fs in recycled_foreshadowings]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self._print_report_dashboard(report_data)
    
    def _print_report_dashboard(self, report_data: dict[str, Any]) -> None:
        """打印报告仪表盘"""
        summary = report_data["summary"]
        
        console.print("\n" + "=" * 60)
        console.print(
            Panel.fit(
                Text.from_markup(
                    "[bold green]伏笔追踪报告[/bold green]\n"
                    f"新增: [cyan]{summary['new_count']}[/cyan] | "
                    f"待回收: [yellow]{summary['pending_count']}[/yellow] | "
                    f"已回收: [green]{summary['recycled_count']}[/green] | "
                    f"总计: [blue]{summary['total_foreshadowings']}[/blue]"
                ),
                title="📊 统计概览"
            )
        )
        console.print("=" * 60)
        
        if report_data["new"]:
            table = Table(
                title="[bold cyan]✨ 新增伏笔[/bold cyan]",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("章节", style="cyan")
            table.add_column("位置", style="cyan")
            table.add_column("类型", style="yellow")
            table.add_column("伏笔内容", style="white")
            
            for fs in report_data["new"]:
                table.add_row(
                    str(fs["chapter"]),
                    str(fs["location"]),
                    fs["hint_type"],
                    fs["text"][:50] + "..." if len(fs["text"]) > 50 else fs["text"]
                )
            
            console.print("\n")
            console.print(table)
        
        if report_data["pending"]:
            table = Table(
                title="[bold yellow]⏳ 待回收伏笔[/bold yellow]",
                show_header=True,
                header_style="bold yellow"
            )
            table.add_column("章节", style="cyan")
            table.add_column("类型", style="yellow")
            table.add_column("伏笔内容", style="white")
            
            for fs in report_data["pending"]:
                table.add_row(
                    str(fs["chapter"]),
                    fs["hint_type"],
                    fs["text"][:50] + "..." if len(fs["text"]) > 50 else fs["text"]
                )
            
            console.print("\n")
            console.print(table)
        
        if report_data["recycled"]:
            table = Table(
                title="[bold green]✅ 已回收伏笔[/bold green]",
                show_header=True,
                header_style="bold green"
            )
            table.add_column("原章节", style="cyan")
            table.add_column("回收章节", style="green")
            table.add_column("类型", style="yellow")
            table.add_column("伏笔内容", style="white")
            
            for fs in report_data["recycled"]:
                table.add_row(
                    str(fs["chapter"]),
                    str(fs.get("recycled_chapter", "N/A")),
                    fs["hint_type"],
                    fs["text"][:50] + "..." if len(fs["text"]) > 50 else fs["text"]
                )
            
            console.print("\n")
            console.print(table)


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="伏笔追踪器 - 识别、追踪和报告小说中的伏笔"
    )
    parser.add_argument(
        "--book-dir",
        type=str,
        required=True,
        help="书籍目录路径"
    )
    parser.add_argument(
        "--chapter",
        type=str,
        default=None,
        help="指定章节文件名（可选）"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="输出报告文件路径"
    )
    parser.add_argument(
        "--record",
        type=str,
        default="foreshadowings.json",
        help="伏笔记录文件路径"
    )
    
    args = parser.parse_args()
    
    book_dir = Path(args.book_dir)
    output_path = Path(args.output)
    record_path = Path(args.record)
    
    if not book_dir.exists():
        console.print(f"[red]错误: 书籍目录不存在: {book_dir}[/red]")
        return 1
    
    tracker = ForeshadowingTracker()
    tracker.load_existing(record_path)
    
    new_foreshadowings = tracker.process_book(book_dir, args.chapter)
    
    tracker.foreshadowings.extend(new_foreshadowings)
    
    tracker.generate_report(output_path)
    
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(
            {"foreshadowings": [fs.to_dict() for fs in tracker.foreshadowings]},
            f,
            ensure_ascii=False,
            indent=2
        )
    
    console.print(f"\n[green]✓ 报告已保存: {output_path}[/green]")
    console.print(f"[green]✓ 伏笔记录已更新: {record_path}[/green]")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
