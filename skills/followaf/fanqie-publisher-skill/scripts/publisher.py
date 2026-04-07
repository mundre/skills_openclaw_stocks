# -*- coding: utf-8 -*-
"""
番茄小说自动发布 - 章节发布模块（修复版 v2）

完整发布流程：
1. 进入创建章节页面
2. 填写章节号
3. 填写标题
4. 填写正文内容（使用剪贴板粘贴）
5. 点击"下一步"
6. 处理错别字检测弹窗 - 点击"提交"
7. 处理内容风险检测弹窗 - 点击"确定"
8. 处理发布设置弹窗 - 选择"否"（不使用AI）- 点击"确认发布"
9. 等待成功提示
"""

import time
import subprocess
import re
import platform
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from browser import get_browser
from works import FanqieWorks, Work
from login import check_login_detail


@dataclass
class Chapter:
    """章节信息"""
    title: str
    content: str
    chapter_number: str = ""
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "chapter_number": self.chapter_number
        }


class FanqiePublisher:
    """章节发布类"""
    
    def __init__(self):
        self.browser = get_browser()
        self.works_manager = FanqieWorks()
    
    def publish_chapter(self, work_title: str, chapter: Chapter) -> dict:
        """发布单个章节"""
        result = {
            "success": False,
            "message": "",
            "chapter_title": chapter.title
        }
        
        # 检查登录状态
        login_status = check_login_detail()
        if not login_status.get("logged_in"):
            result["message"] = "请先登录"
            return result
        
        try:
            print(f"[发布] 准备发布章节: {chapter.title}")
            
            # 获取作品
            work = self.works_manager.get_work_by_title(work_title)
            if not work:
                result["message"] = f"未找到作品: {work_title}"
                return result
            
            print(f"[发布] 作品: {work.title} ({work.chapters}章)")
            
            # 进入创建章节页面
            if not self.works_manager.go_to_create_chapter(work):
                result["message"] = "进入创建章节页面失败"
                return result
            
            time.sleep(3)
            
            # 处理初始弹窗
            self._handle_initial_popups()
            
            # 填写章节内容
            if not self._fill_chapter(chapter):
                result["message"] = "填写章节内容失败"
                return result
            
            # 点击下一步
            if not self._click_next():
                result["message"] = "点击下一步失败"
                return result
            
            # 处理确认流程
            if not self._handle_confirm_flow():
                result["message"] = "确认发布失败"
                return result
            
            result["success"] = True
            result["message"] = f"章节 '{chapter.title}' 发布成功，等待审核"
            print(f"[发布] [OK] {result['message']}")
            
        except Exception as e:
            result["message"] = f"发布出错: {str(e)}"
            print(f"[发布] ✗ 错误: {e}")
            self.browser.page.screenshot(path="publish_error.png")
        
        return result
    
    def _handle_initial_popups(self):
        """处理初始弹窗"""
        print("[发布] 棄查初始弹窗...")
        time.sleep(2)
        
        # 关闭作者有话说引导
        try:
            close_btn = self.browser.page.query_selector(".author-speak-guide-close")
            if close_btn and close_btn.is_visible():
                close_btn.click()
                print("[发布] 关闭作者有话说引导")
                time.sleep(0.5)
        except:
            pass
        
        # 关闭编辑器分区引导弹窗（___reactour div）
        try:
            # 直接查找 ___reactour 容器中的关闭按钮
            reactour_close = self.browser.page.query_selector("#___reactour button, #___reactour .close, #___reactour [class*='close']")
            if reactour_close:
                reactour_close.click()
                print("[发布] 关闭 reactour 引导弹窗")
                time.sleep(0.5)
            else:
                # 尝试隐藏整个 reactour 容器
                self.browser.page.evaluate("document.getElementById('___reactour')?.style?.display = 'none'")
                print("[发布] 隐藏 reactour 弹窗容器")
                time.sleep(0.3)
        except:
            pass
        
        # ESC 键关闭通用弹窗
        try:
            self.browser.page.keyboard.press("Escape")
            time.sleep(0.3)
        except:
            pass
        
        # 再次检查其他可能的弹窗
        try:
            generic_close = self.browser.page.query_selector(".modal-close, .popup-close, .dialog-close, [aria-label='关闭']")
            if generic_close and generic_close.is_visible():
                generic_close.click()
                print("[发布] 关闭通用弹窗")
                time.sleep(0.5)
        except:
            pass
    
    def _fill_chapter(self, chapter: Chapter) -> bool:
        """填写章节内容"""
        print("[发布] 填写章节内容...")
        
        try:
            # 1. 填写章节号
            chapter_input = self.browser.page.query_selector(
                ".serial-input.byte-input.byte-input-size-default:not(.serial-editor-input-hint-area)"
            )
            if chapter_input:
                chapter_input.click()
                time.sleep(0.3)
                chapter_input.fill("")
                time.sleep(0.3)
                
                # 提取章节号
                chapter_num = chapter.chapter_number
                if not chapter_num:
                    match = re.search(r'第\s*(\d+)\s*章', chapter.title)
                    chapter_num = match.group(1) if match else ""
                
                if chapter_num:
                    chapter_input.fill(str(int(chapter_num)))
                    print(f"[发布] 章节号: {chapter_num}")
                    time.sleep(0.5)
            
            # 2. 填写标题
            title_input = self.browser.page.query_selector(".serial-editor-input-hint-area")
            if title_input:
                title_input.click()
                time.sleep(0.3)
                title_input.fill("")
                time.sleep(0.3)
                
                pure_title = re.sub(r'第\s*\d+\s*章\s*', '', chapter.title).strip()
                title_input.fill(pure_title)
                print(f"[发布] 标题: {pure_title}")
                time.sleep(0.5)
            
            # 3. 填写正文（使用剪贴板粘贴）
            editor = self.browser.page.query_selector(".ProseMirror")
            if editor:
                editor.click()
                time.sleep(0.5)
                
                # 复制内容到剪贴板
                if not self._copy_to_clipboard(chapter.content):
                    print("[发布] 警告: 剪贴板复制失败，尝试直接输入")
                    editor.fill(chapter.content)
                else:
                    time.sleep(0.3)
                    # 跨平台粘贴快捷键
                    paste_key = "Meta+v" if platform.system() == "Darwin" else "Control+v"
                    self.browser.page.keyboard.press(paste_key)
                print(f"[发布] 正文: 已粘贴 {len(chapter.content)} 字")
                time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"[发布] 填写失败: {e}")
            return False
    
    def _copy_to_clipboard(self, text: str) -> bool:
        """
        复制文本到系统剪贴板（跨平台支持）
        
        支持平台:
        - macOS: 使用 pbcopy
        - Linux: 优先使用 xclip，其次 xsel
        - Windows: 使用 clip 命令
        
        Args:
            text: 要复制的文本内容
        
        Returns:
            bool: 是否复制成功
        """
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                proc = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                proc.communicate(text.encode('utf-8'))
                return True
            
            elif system == "Windows":
                # Windows 使用 clip 命令，需要 utf-16le 编码
                proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                proc.communicate(text.encode('utf-16le'))
                return True
            
            elif system == "Linux":
                # Linux 优先尝试 xclip，其次 xsel
                try:
                    proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                          stdin=subprocess.PIPE)
                    proc.communicate(text.encode('utf-8'))
                    return True
                except FileNotFoundError:
                    # xclip 不可用，尝试 xsel
                    try:
                        proc = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                              stdin=subprocess.PIPE)
                        proc.communicate(text.encode('utf-8'))
                        return True
                    except FileNotFoundError:
                        print("[剪贴板] 错误: 请安装 xclip 或 xsel")
                        print("  Ubuntu/Debian: sudo apt install xclip")
                        print("  Arch Linux: sudo pacman -S xclip")
                        print("  Fedora: sudo dnf install xclip")
                        return False
            
            else:
                print(f"[剪贴板] 不支持的系统: {system}")
                return False
                
        except Exception as e:
            print(f"[剪贴板] 复制失败: {e}")
            return False
    
    def _click_next(self) -> bool:
        """点击下一步"""
        print("[发布] 点击下一步...")
        
        try:
            next_btn = self.browser.page.query_selector("button:has-text('下一步')")
            if next_btn and not next_btn.is_disabled():
                next_btn.click()
                print("[发布] [OK] 点击下一步")
                time.sleep(3)
                return True
            return False
        except Exception as e:
            print(f"[发布] 点击下一步失败: {e}")
            return False
    
    def _handle_confirm_flow(self) -> bool:
        """处理确认发布流程"""
        print("[发布] 处理确认流程...")
        
        try:
            # 1. 处理错别字检测弹窗
            time.sleep(2)
            submit_btn = self.browser.page.query_selector("button:has-text('提交')")
            if submit_btn and submit_btn.is_visible():
                submit_btn.click()
                print("[发布] [OK] 错别字弹窗: 点击提交")
                time.sleep(3)
            
            # 2. 处理内容风险检测弹窗
            confirm_btn = self.browser.page.query_selector("button:has-text('确定')")
            if confirm_btn and confirm_btn.is_visible():
                confirm_btn.click()
                print("[发布] [OK] 风险检测弹窗: 点击确定")
                time.sleep(5)
            
            # 3. 处理发布设置弹窗 - 选择"否"不使用AI
            no_label = self.browser.page.query_selector("label:has-text('否')")
            if no_label and no_label.is_visible():
                no_label.click()
                print("[发布] [OK] AI选项: 选择否")
                time.sleep(0.5)
            
            # 4. 点击确认发布
            publish_btn = self.browser.page.query_selector("button:has-text('确认发布')")
            if publish_btn and publish_btn.is_visible():
                publish_btn.click()
                print("[发布] [OK] 点击确认发布")
                time.sleep(3)
            
            # 5. 检查是否成功
            time.sleep(2)
            current_url = self.browser.page.url
            
            if "chapter-manage" in current_url:
                print("[发布] [OK] 已跳转到章节管理页面")
                
                # 检查成功提示
                page_text = self.browser.page.content()
                if "已提交" in page_text or "审核中" in page_text:
                    print("[发布] [OK] 检测到成功提交提示")
                    return True
            
            # 截图当前状态
            self.browser.page.screenshot(path="confirm_final.png")
            return True
            
        except Exception as e:
            print(f"[发布] 确认流程失败: {e}")
            self.browser.page.screenshot(path="confirm_error.png")
            return False
    
    def publish_batch(self, work_title: str, chapters: List[Chapter], interval: int = 5) -> List[dict]:
        """批量发布"""
        results = []
        
        for i, chapter in enumerate(chapters):
            print(f"\n[批量] 进度: {i+1}/{len(chapters)}")
            result = self.publish_chapter(work_title, chapter)
            results.append(result)
            
            if i < len(chapters) - 1:
                print(f"[批量] 等待 {interval} 秒...")
                time.sleep(interval)
        
        return results


# 便捷函数
def publish_chapter(work_title: str, title: str, content: str) -> dict:
    """发布单个章节"""
    publisher = FanqiePublisher()
    chapter = Chapter(title=title, content=content)
    return publisher.publish_chapter(work_title, chapter)


def publish_batch(work_title: str, chapters: List[dict], interval: int = 5) -> List[dict]:
    """批量发布章节
    
    Args:
        work_title: 作品名称
        chapters: 章节列表，每个元素为 {"title": "标题", "content": "内容"}
        interval: 发布间隔（秒）
    
    Returns:
        发布结果列表
    """
    publisher = FanqiePublisher()
    chapter_list = [Chapter(title=c["title"], content=c["content"]) for c in chapters]
    return publisher.publish_batch(work_title, chapter_list, interval)


def publish_from_file(work_title: str, file_path: str) -> dict:
    """从文件发布章节"""
    from main import extract_content
    
    content = Path(file_path).read_text(encoding='utf-8')
    chapter_data = extract_content(content)
    
    if not chapter_data.get("title") or not chapter_data.get("content"):
        return {"success": False, "message": "无法提取章节内容"}
    
    publisher = FanqiePublisher()
    chapter = Chapter(
        title=chapter_data["title"],
        content=chapter_data["content"]
    )
    return publisher.publish_chapter(work_title, chapter)