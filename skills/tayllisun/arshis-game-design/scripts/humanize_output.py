#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 人性化输出模块
让输出更有温度、更像人写的东西
"""

import random
from typing import Dict, Any, List


class HumanizeOutput:
    """人性化输出转换器"""
    
    def __init__(self):
        # 情感化词汇库
        self.emotion_words = {
            'excitement': ['太棒了', '令人兴奋', '惊喜', '精彩', '绝佳'],
            'warmth': ['温柔', '贴心', '温暖', '关怀', '用心'],
            'encouragement': ['加油', '相信', '可以', '没问题', '一定行'],
            'empathy': ['想象一下', '试想', '还记得', '有没有', '是不是'],
            'storytelling': ['从前', '有一天', '记得', '曾经', '故事']
        }
        
        # 过渡句库
        self.transitions = [
            '说到这里，',
            '你可能会想，',
            '有趣的是，',
            '别忘了，',
            '最重要的是，',
            '想象一下，',
            '还记得吗，',
            '其实，',
            '说实话，',
            '悄悄告诉你，'
        ]
        
        # 反问句库
        self.rhetorical_questions = [
            '是不是很心动？',
            '有没有get 到？',
            '怎么样，是不是这个理？',
            '你品，你细品，',
            '是不是瞬间明白了？',
            '有没有戳中你？',
            '是不是很熟悉？',
            '有没有画面感了？'
        ]
        
        # 比喻库
        self.metaphors = {
            'difficulty': ['像爬楼梯一样，每一步都不太高', '像打游戏通关，一关比一关有趣'],
            'progress': ['像种花一样，每天浇水，终会绽放', '像酿酒一样，时间越久越香醇'],
            'challenge': ['像爬山，累但值得', '像解谜，难但有趣'],
            'reward': ['像拆礼物，充满惊喜', '像收获，满满的成就感'],
            'growth': ['像小树长大，每天都在变化', '像升级打怪，越来越强']
        }
    
    def humanize_text(self, text: str, style: str = 'warm') -> str:
        """
        人性化文本转换
        
        Args:
            text: 原始文本
            style: 风格（warm/professional/friendly）
        
        Returns:
            人性化文本
        """
        if style == 'warm':
            return self._warm_style(text)
        elif style == 'professional':
            return self._professional_style(text)
        elif style == 'friendly':
            return self._friendly_style(text)
        else:
            return self._warm_style(text)
    
    def _warm_style(self, text: str) -> str:
        """温暖风格"""
        # 添加开场白
        opening = random.choice([
            '来，我们一起看看~\n\n',
            '别急，慢慢来~\n\n',
            '听我说~\n\n',
            '来聊聊这个~\n\n'
        ])
        
        # 添加情感词
        enhanced = self._add_emotion_words(text, 'warmth')
        
        # 添加过渡句
        enhanced = self._add_transitions(enhanced)
        
        # 添加反问句
        enhanced = self._add_rhetorical_questions(enhanced)
        
        # 添加比喻
        enhanced = self._add_metaphors(enhanced)
        
        # 添加结尾
        ending = random.choice([
            '\n\n怎么样，是不是清晰多了？',
            '\n\n希望能帮到你~',
            '\n\n有问题随时问我哦~',
            '\n\n一起加油！'
        ])
        
        return opening + enhanced + ending
    
    def _professional_style(self, text: str) -> str:
        """专业但有人情味的风格"""
        # 保持专业性，但添加一些人情味
        enhanced = text.replace('确保', '我们要确保')
        enhanced = enhanced.replace('考虑', '需要充分考虑')
        enhanced = enhanced.replace('设计', '精心设计')
        
        # 添加专业建议
        advice = random.choice([
            '\n\n💡 小建议：这个部分可以多花点心思，效果会更好~',
            '\n\n💡 经验之谈：这样做可以避免很多坑~',
            '\n\n💡 提醒一下：记得多测试几次~'
        ])
        
        return enhanced + advice
    
    def _friendly_style(self, text: str) -> str:
        """朋友聊天风格"""
        # 添加朋友间的语气词
        enhanced = text.replace('应该', '我觉得可以')
        enhanced = enhanced.replace('需要', '最好是')
        enhanced = enhanced.replace('建议', '我个人推荐')
        
        # 添加语气词
        particles = ['呢', '哦', '啦', '哈', '嘛']
        enhanced += random.choice(particles)
        
        return enhanced
    
    def _add_emotion_words(self, text: str, emotion: str) -> str:
        """添加情感词汇"""
        words = self.emotion_words.get(emotion, self.emotion_words['warmth'])
        
        # 在关键位置添加情感词
        sentences = text.split('。')
        enhanced = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                if i > 0 and random.random() > 0.7:
                    word = random.choice(words)
                    sentence = f'{word}的是，{sentence}'
                enhanced.append(sentence)
        
        return '。'.join(enhanced)
    
    def _add_transitions(self, text: str) -> str:
        """添加过渡句"""
        paragraphs = text.split('\n\n')
        enhanced = []
        
        for i, para in enumerate(paragraphs):
            if para.strip() and i > 0 and random.random() > 0.6:
                transition = random.choice(self.transitions)
                para = transition + para
            enhanced.append(para)
        
        return '\n\n'.join(enhanced)
    
    def _add_rhetorical_questions(self, text: str) -> str:
        """添加反问句"""
        # 在段落末尾添加反问
        paragraphs = text.split('\n\n')
        enhanced = []
        
        for para in paragraphs:
            if para.strip() and len(para) > 50 and random.random() > 0.7:
                question = random.choice(self.rhetorical_questions)
                para = para + '\n\n' + question
            enhanced.append(para)
        
        return '\n\n'.join(enhanced)
    
    def _add_metaphors(self, text: str) -> str:
        """添加比喻"""
        # 根据内容添加比喻
        if '难度' in text or '挑战' in text:
            metaphor = random.choice(self.metaphors['challenge'])
            text += f'\n\n就像{metaphor}~'
        
        if '成长' in text or '进步' in text:
            metaphor = random.choice(self.metaphors['growth'])
            text += f'\n\n就像{metaphor}~'
        
        if '奖励' in text or '收获' in text:
            metaphor = random.choice(self.metaphors['reward'])
            text += f'\n\n就像{metaphor}~'
        
        return text
    
    def convert_list_to_narrative(self, items: List[str]) -> str:
        """将列表转换为叙述性文本"""
        if not items:
            return ''
        
        if len(items) == 1:
            return items[0]
        
        if len(items) == 2:
            return f'{items[0]}，还有{items[1]}'
        
        # 3 个及以上
        narrative = ''
        for i, item in enumerate(items):
            if i == 0:
                narrative = f'首先，{item}'
            elif i == len(items) - 1:
                narrative += f'，最后{item}'
            else:
                narrative += f'，然后{item}'
        
        return narrative + '。'
    
    def add_personal_touch(self, text: str) -> str:
        """添加个人色彩"""
        personal_phrases = [
            '我个人觉得，',
            '根据我的经验，',
            '说真的，',
            '老实说，',
            '不瞒你说，',
            '跟你分享一个小秘诀，'
        ]
        
        if random.random() > 0.5:
            phrase = random.choice(personal_phrases)
            text = phrase + text
        
        return text


def humanize_design_output(design_text: str, style: str = 'warm') -> str:
    """
    人性化设计文档输出
    
    Args:
        design_text: 设计文档文本
        style: 风格
    
    Returns:
        人性化文本
    """
    humanizer = HumanizeOutput()
    return humanizer.humanize_text(design_text, style)


def main():
    """测试"""
    # 测试文本
    test_text = """
    心流设计：确保挑战与玩家技能匹配
    玩家动机：考虑四类玩家需求
    奖励设计：混合使用固定和变动奖励
    进度反馈：清晰展示进度
    """
    
    humanizer = HumanizeOutput()
    
    print("原始文本:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    print("温暖风格:")
    print(humanizer.humanize_text(test_text, 'warm'))
    print("\n" + "="*50 + "\n")
    
    print("专业风格:")
    print(humanizer.humanize_text(test_text, 'professional'))
    print("\n" + "="*50 + "\n")
    
    print("朋友风格:")
    print(humanizer.humanize_text(test_text, 'friendly'))


if __name__ == '__main__':
    main()
