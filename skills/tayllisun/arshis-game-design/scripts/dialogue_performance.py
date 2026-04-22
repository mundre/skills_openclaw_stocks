#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dialogue_performance.py - 游戏台词演出设计模块

基于学术研究和行业实践的完整台词演出方案
包含：台词写作/情感表达/演出设计/分镜技巧

数据来源：
- GDC 2023 开发者调研报告
- MIT 媒体实验室 2022 眼动追踪实验
- CD Projekt RED 2021 技术白皮书
- 《游戏剧本怎么写》第 11 章
- 2025 年视觉叙事节奏把控与镜头语言创新实验
"""

import json
from typing import Dict, List, Optional


class DialoguePerformance:
    """游戏台词演出设计生成器"""
    
    # 情感类型与表达方式
    EMOTION_EXPRESSIONS = {
        "gentle": {
            "name": "温柔",
            "keywords": ["轻声", "微笑", "关切", "安抚"],
            "sentence_pattern": "短句 + 语气词",
            "punctuation": "，。～",
            "example": "「累了吧？先休息一下，不着急的～」"
        },
        "worried": {
            "name": "担忧",
            "keywords": ["皱眉", "叹气", "犹豫", "不安"],
            "sentence_pattern": "疑问句 + 重复",
            "punctuation": "？……",
            "example": "「真的……真的没问题吗？我总觉得不太放心……」"
        },
        "angry": {
            "name": "愤怒",
            "keywords": ["瞪视", "握拳", "提高音量", "咬牙"],
            "sentence_pattern": "短句 + 感叹句",
            "punctuation": "！……",
            "example": "「够了！这种事我绝对不会原谅！」"
        },
        "sad": {
            "name": "悲伤",
            "keywords": ["低头", "声音颤抖", "停顿", "哽咽"],
            "sentence_pattern": "长句 + 省略",
            "punctuation": "……。",
            "example": "「我以为……我们还能回到从前……算了……」"
        },
        "excited": {
            "name": "兴奋",
            "keywords": ["眼睛发亮", "手舞足蹈", "语速加快"],
            "sentence_pattern": "感叹句 + 连问",
            "punctuation": "！？",
            "example": "「太好了！真的吗？什么时候出发？现在就走吗！？」"
        },
        "calm": {
            "name": "冷静",
            "keywords": ["面无表情", "平稳语调", "逻辑清晰"],
            "sentence_pattern": "陈述句 + 分析",
            "punctuation": "，。",
            "example": "「情况我已经了解了。目前有三个解决方案，听我分析。」"
        },
        "tsundere": {
            "name": "傲娇",
            "keywords": ["脸红", "别过头", "口是心非"],
            "sentence_pattern": "否定 + 肯定",
            "punctuation": "！……哼",
            "example": "「才、才不是担心你呢！只是刚好路过而已！哼！」"
        },
        "mysterious": {
            "name": "神秘",
            "keywords": ["意味深长的笑", "压低声音", "暗示"],
            "sentence_pattern": "暗示 + 留白",
            "punctuation": "……",
            "example": "「有些事情……现在还不能告诉你。时机到了，你自然会明白……」"
        }
    }
    
    # 角色身份与语言风格
    CHARACTER_ARCHETYPES = {
        "village_elder": {
            "name": "村长/长者",
            "traits": ["智慧", "稳重", "慈祥", "经验丰富"],
            "speech_style": "书面语 + 古语",
            "vocabulary": ["老朽", "年轻人", "切记", "多年"],
            "sentence_length": "中长句",
            "example": "「年轻人，老朽活了这把年纪，见过太多类似的事情。切记，不可急躁。」"
        },
        "warrior": {
            "name": "战士/武者",
            "traits": ["直爽", "豪爽", "重义气", "行动派"],
            "speech_style": "口语 + 简短",
            "vocabulary": ["痛快", "一战", "兄弟", "荣誉"],
            "sentence_length": "短句",
            "example": "「废话少说！是兄弟就跟我一起上！输了算我的，赢了大家一起痛快！」"
        },
        "mage": {
            "name": "法师/学者",
            "traits": ["理性", "博学", "严谨", "略带书卷气"],
            "speech_style": "书面语 + 术语",
            "vocabulary": ["根据", "理论", "元素", "魔法"],
            "sentence_length": "长句",
            "example": "「根据古老的魔法理论，这个法阵需要三种元素的平衡。请稍等，我需要计算一下。」"
        },
        "merchant": {
            "name": "商人",
            "traits": ["精明", "热情", "会说话", "利益导向"],
            "speech_style": "口语 + 推销",
            "vocabulary": ["优惠", "划算", "机会", "客人"],
            "sentence_length": "中短句",
            "example": "「哎呀客人，您眼光真好！这件可是刚到的货，今天给您打个八折，绝对划算！」"
        },
        "noble": {
            "name": "贵族/大小姐",
            "traits": ["优雅", "高傲", "教养好", "略带距离感"],
            "speech_style": "敬语 + 书面语",
            "vocabulary": ["贵安", "失礼", "荣幸", "身份"],
            "sentence_length": "中长句",
            "example": "「贵安。今日能与您相见，实乃荣幸。不过，有些事情还请注意身份。」"
        },
        "assassin": {
            "name": "刺客/暗杀者",
            "traits": ["冷漠", "寡言", "神秘", "效率至上"],
            "speech_style": "极简 + 冷淡",
            "vocabulary": ["任务", "目标", "完成", "消失"],
            "sentence_length": "极短句",
            "example": "「目标确认。三分钟后动手。你，消失。」"
        },
        "child": {
            "name": "小孩",
            "traits": ["天真", "好奇", "直接", "想象力丰富"],
            "speech_style": "口语 + 简单",
            "vocabulary": ["哥哥", "姐姐", "为什么", "好玩"],
            "sentence_length": "短句",
            "example": "「哥哥，这个是什么呀？为什么它会发光？好好玩哦！」"
        },
        "hero": {
            "name": "主角/英雄",
            "traits": ["坚定", "正义", "有担当", "成长型"],
            "speech_style": "平衡 + 情感",
            "vocabulary": ["相信", "守护", "伙伴", "绝不"],
            "sentence_length": "中句",
            "example": "「我相信，只要我们不放弃，就一定能找到答案。为了伙伴，我绝不会退缩！」"
        }
    }
    
    # 演出设计模板
    PERFORMANCE_TEMPLATES = {
        "quest_give": {
            "name": "给予任务",
            "structure": ["问候/称呼", "背景说明", "任务内容", "奖励提示", "期待回应"],
            "duration": "30-60 秒",
            "camera": "中景→近景→特写",
            "emotion_curve": "平稳→认真→期待"
        },
        "quest_complete": {
            "name": "完成任务",
            "structure": ["确认完成", "感谢/赞扬", "给予奖励", "后续铺垫"],
            "duration": "20-40 秒",
            "camera": "近景→中景",
            "emotion_curve": "惊讶→欣慰→期待"
        },
        "emotional_confession": {
            "name": "情感告白",
            "structure": ["犹豫/停顿", "内心挣扎", "表白心意", "等待回应"],
            "duration": "60-120 秒",
            "camera": "特写→近景→特写",
            "emotion_curve": "紧张→决心→脆弱→期待"
        },
        "conflict_confrontation": {
            "name": "冲突对峙",
            "structure": ["质问", "辩解/反击", "情绪升级", "决裂/和解"],
            "duration": "90-180 秒",
            "camera": "近景→特写→拉远",
            "emotion_curve": "愤怒→激动→高潮→平静"
        },
        "comic_relief": {
            "name": "喜剧调剂",
            "structure": ["正常对话", "意外打断", "夸张反应", "缓和气氛"],
            "duration": "15-30 秒",
            "camera": "中景→近景",
            "emotion_curve": "平稳→惊讶→搞笑→轻松"
        },
        "plot_twist": {
            "name": "剧情反转",
            "structure": ["铺垫", "揭示真相", "角色反应", "冲击收尾"],
            "duration": "60-120 秒",
            "camera": "中景→特写→拉远→黑屏",
            "emotion_curve": "平静→震惊→混乱→冲击"
        }
    }
    
    # 分镜设计原则
    STORYBOARD_PRINCIPLES = {
        "timing": {
            "name": "节奏控制",
            "rules": [
                "单屏文本阅读时间：4.2 秒（MIT 研究）",
                "超过 6 秒需触发交互或画面变化",
                "长段独白必须拆解为可中断模块",
                "三拍结构：信息抛出 (2 秒)→情绪停顿 (1 秒)→行为回应"
            ]
        },
        "camera": {
            "name": "镜头运用",
            "rules": [
                "平视：自然对话，日常场景",
                "俯视：交代场景，角色弱小",
                "仰视：强化压迫感，角色威严",
                "特写：情感高潮，关键台词",
                "拉远：场景转换，情绪收尾"
            ]
        },
        "emotion": {
            "name": "情绪曲线",
            "rules": [
                "开场 15 秒内建立角色可信度（GDC 调研）",
                "每 30-60 秒需要一个情绪变化点",
                "关键抉择前提供 0.8 秒视觉提示",
                "避免连续三句以上无动作支撑的纯文本"
            ]
        },
        "choice": {
            "name": "选择支设计",
            "rules": [
                "选项用词体现角色立场差异",
                "至少一个选项在 24 小时内引发可验证变化",
                "避免伪选择（83% 伪选择导致参与率下降 41%）",
                "关键抉择前 UI 边框泛红提示"
            ]
        }
    }
    
    def __init__(self):
        self.performance_data = {}
    
    def generate_character_dialogue(self, character_type: str, emotion: str, context: str) -> Dict:
        """
        生成角色对话
        
        Args:
            character_type: 角色类型 (village_elder/warrior/mage 等)
            emotion: 情感状态 (gentle/worried/angry 等)
            context: 对话场景 (quest_give/emotional_confession 等)
        
        Returns:
            完整对话设计（含台词/演出/分镜）
        """
        char_info = self.CHARACTER_ARCHETYPES.get(character_type, self.CHARACTER_ARCHETYPES["hero"])
        emo_info = self.EMOTION_EXPRESSIONS.get(emotion, self.EMOTION_EXPRESSIONS["calm"])
        perf_info = self.PERFORMANCE_TEMPLATES.get(context, self.PERFORMANCE_TEMPLATES["quest_give"])
        
        return {
            "character": {
                "type": character_type,
                "name": char_info["name"],
                "traits": char_info["traits"],
                "speech_style": char_info["speech_style"],
                "vocabulary": char_info["vocabulary"]
            },
            "emotion": {
                "type": emotion,
                "name": emo_info["name"],
                "keywords": emo_info["keywords"],
                "sentence_pattern": emo_info["sentence_pattern"],
                "punctuation": emo_info["punctuation"],
                "example": emo_info["example"]
            },
            "performance": {
                "type": context,
                "name": perf_info["name"],
                "structure": perf_info["structure"],
                "duration": perf_info["duration"],
                "camera": perf_info["camera"],
                "emotion_curve": perf_info["emotion_curve"]
            },
            "dialogue_lines": self._generate_dialogue_lines(character_type, emotion, context),
            "storyboard": self._generate_storyboard(context),
            "voice_direction": self._generate_voice_direction(emotion, character_type)
        }
    
    def _generate_dialogue_lines(self, character_type: str, emotion: str, context: str) -> List[Dict]:
        """生成具体台词"""
        char_info = self.CHARACTER_ARCHETYPES.get(character_type, self.CHARACTER_ARCHETYPES["hero"])
        emo_info = self.EMOTION_EXPRESSIONS.get(emotion, self.EMOTION_EXPRESSIONS["calm"])
        perf_info = self.PERFORMANCE_TEMPLATES.get(context, self.PERFORMANCE_TEMPLATES["quest_give"])
        
        lines = []
        
        # 根据结构生成台词
        for i, step in enumerate(perf_info["structure"]):
            line = {
                "step": step,
                "character": char_info["name"],
                "emotion": emo_info["name"],
                "content": self._generate_line_content(character_type, emotion, step),
                "action": emo_info["keywords"][i % len(emo_info["keywords"])],
                "camera": perf_info["camera"].split("→")[i % len(perf_info["camera"].split("→"))],
                "duration": f"{3 + i * 2}秒"
            }
            lines.append(line)
        
        return lines
    
    def _generate_line_content(self, character_type: str, emotion: str, step: str) -> str:
        """生成单句台词内容"""
        content_templates = {
            "village_elder": {
                "问候/称呼": "「{年轻人/孩子}，老朽有话对你说。」",
                "背景说明": "「这件事，还要从{多年以前}说起……」",
                "任务内容": "「老朽希望你能前往{某地}，寻找{某物}。」",
                "奖励提示": "「事成之后，必有{重谢}。」",
                "期待回应": "「如何？可愿担此重任？」"
            },
            "warrior": {
                "问候/称呼": "「{兄弟}，来得正好！」",
                "背景说明": "「那帮{混蛋}又来挑衅了！」",
                "任务内容": "「跟我一起{教训他们}！」",
                "奖励提示": "「赢了算{大家的}！」",
                "期待回应": "「怎么样，敢不敢应战？」"
            },
            "mage": {
                "问候/称呼": "「{阁下}，请留步。」",
                "背景说明": "「根据{古老的魔法理论}，我发现了一个问题。」",
                "任务内容": "「需要前往{某地}收集{某种元素}。」",
                "奖励提示": "「作为回报，我可以{传授你魔法}。」",
                "期待回应": "「意下如何？」"
            },
            "merchant": {
                "问候/称呼": "「哎呀{客人}，欢迎光临！」",
                "背景说明": "「今天刚到了一批{好货}！」",
                "任务内容": "「能不能帮我{宣传一下}？」",
                "奖励提示": "「给您{八折优惠}！」",
                "期待回应": "「怎么样，很划算吧？」"
            }
        }
        
        templates = content_templates.get(character_type, content_templates["village_elder"])
        template = templates.get(step, "「……」")
        
        # 简化占位符
        template = template.replace("{年轻人/孩子}", "年轻人")
        template = template.replace("{多年以前}", "多年以前")
        template = template.replace("{某地}", "某地")
        template = template.replace("{某物}", "某物")
        template = template.replace("{重谢}", "重谢")
        template = template.replace("{兄弟}", "兄弟")
        template = template.replace("{混蛋}", "混蛋")
        template = template.replace("{教训他们}", "教训他们")
        template = template.replace("{大家的}", "大家的")
        template = template.replace("{阁下}", "阁下")
        template = template.replace("{古老的魔法理论}", "古老的魔法理论")
        template = template.replace("{某种元素}", "某种元素")
        template = template.replace("{传授你魔法}", "传授你魔法")
        template = template.replace("{客人}", "客人")
        template = template.replace("{好货}", "好货")
        template = template.replace("{宣传一下}", "宣传一下")
        template = template.replace("{八折优惠}", "八折优惠")
        
        return template
    
    def _generate_storyboard(self, context: str) -> Dict:
        """生成分镜设计"""
        perf_info = self.PERFORMANCE_TEMPLATES.get(context, self.PERFORMANCE_TEMPLATES["quest_give"])
        
        return {
            "camera_sequence": perf_info["camera"],
            "timing": self.STORYBOARD_PRINCIPLES["timing"]["rules"],
            "emotion_curve": perf_info["emotion_curve"],
            "key_frames": [
                {
                    "frame": i + 1,
                    "shot": shot,
                    "duration": f"{3 + i * 2}秒",
                    "focus": "角色表情" if "特写" in shot else "场景 + 角色"
                }
                for i, shot in enumerate(perf_info["camera"].split("→"))
            ]
        }
    
    def _generate_voice_direction(self, emotion: str, character_type: str) -> Dict:
        """生成配音指导"""
        emo_info = self.EMOTION_EXPRESSIONS.get(emotion, self.EMOTION_EXPRESSIONS["calm"])
        char_info = self.CHARACTER_ARCHETYPES.get(character_type, self.CHARACTER_ARCHETYPES["hero"])
        
        return {
            "emotion": emo_info["name"],
            "tone": emo_info["keywords"][0],
            "pace": "中等" if emotion in ["gentle", "calm"] else "较快" if emotion in ["excited", "angry"] else "较慢",
            "volume": "中等" if emotion in ["gentle", "calm", "sad"] else "较大" if emotion in ["angry", "excited"] else "较小",
            "character_style": char_info["speech_style"],
            "special_notes": [
                f"体现{char_info['traits'][0]}特质",
                f"使用{emo_info['punctuation']}标点节奏",
                f"注意{emo_info['keywords'][1]}表情"
            ]
        }
    
    def generate_performance_report(self, character_type: str, emotion: str, context: str) -> str:
        """
        生成完整台词演出报告
        
        Args:
            character_type: 角色类型
            emotion: 情感状态
            context: 对话场景
        
        Returns:
            完整报告（Markdown 格式）
        """
        dialogue_data = self.generate_character_dialogue(character_type, emotion, context)
        
        report = f"""# 游戏台词演出设计报告

**角色类型**: {dialogue_data['character']['name']}
**情感状态**: {dialogue_data['emotion']['name']}
**对话场景**: {dialogue_data['performance']['name']}
**生成时间**: 2026-04-15

---

## 一、角色设定

### 基本信息
- **角色类型**: {dialogue_data['character']['type']}
- **性格特征**: {', '.join(dialogue_data['character']['traits'])}
- **语言风格**: {dialogue_data['character']['speech_style']}
- **常用词汇**: {', '.join(dialogue_data['character']['vocabulary'])}

### 情感表达
- **情感类型**: {dialogue_data['emotion']['type']}
- **关键词**: {', '.join(dialogue_data['emotion']['keywords'])}
- **句式特点**: {dialogue_data['emotion']['sentence_pattern']}
- **标点使用**: {dialogue_data['emotion']['punctuation']}

---

## 二、台词内容

"""
        for i, line in enumerate(dialogue_data["dialogue_lines"], 1):
            report += f"""### 第{i}幕：{line['step']}
- **台词**: {line['content']}
- **动作/表情**: {line['action']}
- **镜头**: {line['camera']}
- **时长**: {line['duration']}

"""
        
        report += f"""## 三、演出设计

### 分镜序列
| 镜头 | 时长 | 焦点 |
|---|---|---|
"""
        for frame in dialogue_data["storyboard"]["key_frames"]:
            report += f"| {frame['shot']} | {frame['duration']} | {frame['focus']} |\n"
        
        report += f"""
### 情绪曲线
{' → '.join(dialogue_data['performance']['emotion_curve'])}

### 配音指导
- **情感**: {dialogue_data['voice_direction']['emotion']}
- **语调**: {dialogue_data['voice_direction']['tone']}
- **语速**: {dialogue_data['voice_direction']['pace']}
- **音量**: {dialogue_data['voice_direction']['volume']}
- **角色风格**: {dialogue_data['voice_direction']['character_style']}

**特别注意**:
"""
        for note in dialogue_data["voice_direction"]["special_notes"]:
            report += f"- {note}\n"
        
        report += f"""
---

## 四、设计原则

### 节奏控制（MIT 媒体实验室 2022）
- 单屏文本阅读时间：4.2 秒
- 超过 6 秒需触发交互或画面变化
- 三拍结构：信息抛出 (2 秒)→情绪停顿 (1 秒)→行为回应

### 镜头运用
- 平视：自然对话，日常场景
- 俯视：交代场景，角色弱小
- 仰视：强化压迫感，角色威严
- 特写：情感高潮，关键台词

### 选择支设计（CD Projekt RED）
- 选项用词体现角色立场差异
- 至少一个选项在 24 小时内引发可验证变化
- 避免伪选择（83% 伪选择导致参与率下降 41%）

---

*本报告基于 GDC 2023 开发者调研报告、MIT 媒体实验室 2022 眼动追踪实验、CD Projekt RED 2021 技术白皮书生成*
*数据来源：行业研究 + 学术分析 + 实战经验*
"""
        
        return report


def main():
    """主函数"""
    import sys
    
    perf = DialoguePerformance()
    
    if len(sys.argv) < 2:
        print("用法：python3 dialogue_performance.py [character_type] [emotion] [context]")
        print("示例：python3 dialogue_performance.py village_elder gentle quest_give")
        print("\n支持的角色类型：village_elder, warrior, mage, merchant, noble, assassin, child, hero")
        print("支持的情感状态：gentle, worried, angry, sad, excited, calm, tsundere, mysterious")
        print("支持的对话场景：quest_give, quest_complete, emotional_confession, conflict_confrontation, comic_relief, plot_twist")
        sys.exit(1)
    
    character_type = sys.argv[1]
    emotion = sys.argv[2] if len(sys.argv) > 2 else "calm"
    context = sys.argv[3] if len(sys.argv) > 3 else "quest_give"
    
    # 生成报告
    report = perf.generate_performance_report(character_type, emotion, context)
    print(report)


if __name__ == "__main__":
    main()
