#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 剧情对话生成器
创作有情感的 NPC 对话
"""

import os
import json
import sys
import random
from typing import Dict, Any, List
from datetime import datetime


class DialogueGenerator:
    """对话生成器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output', 'dialogue')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # NPC 性格类型
        self.personality_types = {
            'gentle': {
                'name': '温柔',
                'traits': ['体贴', '关怀', '耐心', '善良'],
                'speech_style': '温和，常用语气词',
                'example': '要小心哦'
            },
            'stern': {
                'name': '严厉',
                'traits': ['严肃', '直接', '严格', '正直'],
                'speech_style': '简短，命令式',
                'example': '执行命令'
            },
            'cheerful': {
                'name': '活泼',
                'traits': ['开朗', '乐观', '热情', '友好'],
                'speech_style': '活泼，多感叹号',
                'example': '太棒了！一起加油'
            },
            'mysterious': {
                'name': '神秘',
                'traits': ['深沉', '难以捉摸', '智慧', '冷静'],
                'speech_style': '含蓄，留白',
                'example': '有些事...现在还不是知道的时候'
            },
            'wise': {
                'name': '智慧',
                'traits': ['博学', '慈祥', '睿智', '平和'],
                'speech_style': '引经据典，富有哲理',
                'example': '年轻人，记住...真正的力量来自内心'
            },
            'grounded': {
                'name': '务实',
                'traits': ['实在', '稳重', '踏实', '可靠'],
                'speech_style': '自然，平衡，不过分口语',
                'example': '先把事情做好'
            }
        }
        
        # 情感表达库
        self.emotion_expressions = {
            'happy': ['微笑', '眼中闪着光', '开心地', '兴奋地', '眼中满是喜悦'],
            'sad': ['眼眶泛红', '声音哽咽', '低下头', '眼中含着泪', '声音颤抖'],
            'angry': ['眉头紧锁', '咬牙切齿', '愤怒地', '眼中喷火', '拳头紧握'],
            'worried': ['忧心忡忡', '眉头不展', '叹气', '坐立不安', '眼神忧虑'],
            'grateful': ['眼中泛起泪光', '深深鞠躬', '声音颤抖', '紧紧握住', '感激涕零'],
            'determined': ['目光坚定', '挺直腰板', '握紧拳头', '眼神坚毅', '深吸一口气']
        }
        
        # 语气词库（平衡版，不过分口语）
        self.particles = {
            'gentle': ['呢', '哦', ''],
            'stern': ['', '', ''],
            'cheerful': ['!', '!', ''],
            'mysterious': ['...', '', '...'],
            'wise': ['啊', '呢', '...'],
            'grounded': ['', '', '']  # 务实风格不用语气词
        }
        
        # 对话模板库（平衡版）
        self.dialogue_templates = {
            'greeting': [
                '（{emotion}）"{content}"',
                '"{content}"（{emotion}）',
                '（{emotion}）{name}说道："{content}"'
            ],
            'quest_give': [
                '（{emotion}）"我...我需要你帮忙...{quest}"',
                '"{quest}"（{emotion}）"拜托你了..."',
                '（{emotion}）{name}说："{quest}...这是我能想到的唯一办法了"'
            ],
            'quest_complete': [
                '（{emotion}）"你做到了！{reward}"',
                '"{reward}"（{emotion}）"谢谢你..."',
                '（{emotion}）{name}激动地说："{reward}！你救了大家！"'
            ],
            'farewell': [
                '（{emotion}）"{content}"',
                '"{content}"（{emotion}）',
                '（{emotion}）{name}望着你的背影，轻声说道："{content}"'
            ]
        }
        
        # 语言平衡规则（避免太口语或太书面）
        self.language_balance_rules = [
            # 太口语 → 平衡
            ('收拾收拾', '整理一下'),
            ('搞定', '完成'),
            ('弄好', '处理好'),
            ('自个儿', '自己'),
            ('大家伙儿', '大家'),
            ('顶着', '承担'),
            # 太书面 → 平衡
            ('日头最毒', '正午时分'),
            ('灌溉那头', '灌溉的水渠'),
            ('理了', '疏通'),
        ]
    
    def generate_npc_dialogue(self, npc_name: str, personality: str, 
                               emotion: str, context: str) -> Dict[str, Any]:
        """
        生成 NPC 对话
        
        Args:
            npc_name: NPC 名称
            personality: 性格类型（gentle/stern/cheerful/mysterious/wise）
            emotion: 情感状态（happy/sad/angry/worried/grateful/determined）
            context: 对话情境
        
        Returns:
            生成的对话
        """
        personality_info = self.personality_types.get(personality, self.personality_types['gentle'])
        emotion_expressions = self.emotion_expressions.get(emotion, self.emotion_expressions['happy'])
        particles = self.particles.get(personality, self.particles['gentle'])
        
        # 生成对话内容
        dialogue_content = self._generate_content(context, personality, emotion)
        
        # 添加表情动作
        emotion_action = random.choice(emotion_expressions)
        
        # 添加语气词
        particle = random.choice(particles)
        if particle and not dialogue_content.endswith(('。', '！', '？', '...')):
            dialogue_content += particle
        
        # 选择模板
        template = random.choice(self.dialogue_templates['greeting'])
        
        # 生成完整对话
        full_dialogue = template.format(
            emotion=emotion_action,
            name=npc_name,
            content=dialogue_content
        )
        
        return {
            'npc_name': npc_name,
            'personality': personality_info['name'],
            'emotion': emotion,
            'dialogue': full_dialogue,
            'speech_style': personality_info['speech_style'],
            'traits': personality_info['traits']
        }
    
    def _generate_content(self, context: str, personality: str, emotion: str) -> str:
        """生成对话内容"""
        # 根据情境生成内容
        content_templates = {
            'greeting': {
                'gentle': '欢迎你来~ 这里虽然简陋，但还是很温暖的哦',
                'stern': '站住。报上名来。',
                'cheerful': '哇！有新朋友来啦！欢迎欢迎~',
                'mysterious': '你终于来了...我等你很久了',
                'wise': '年轻人，来到这里，想必是有缘吧'
            },
            'quest_give': {
                'gentle': '那个...我知道这很突然，但是...能帮帮我吗？',
                'stern': '任务交给你了。不要让我失望。',
                'cheerful': '有个超棒的冒险！要不要一起来？',
                'mysterious': '有些事...只有你能做。你愿意听吗？',
                'wise': '孩子，这是你的使命。你准备好了吗？'
            },
            'quest_complete': {
                'gentle': '太感谢你了！多亏有你，大家都安全了~',
                'stern': '干得不错。这是你的报酬。',
                'cheerful': '哇！你太厉害啦！我们赢啦！',
                'mysterious': '正如我所料...你做到了。',
                'wise': '很好。你已经证明了自己。'
            },
            'farewell': {
                'gentle': '要走了吗？一定要小心哦~我会一直为你祈祷的',
                'stern': '去吧。记住你的使命。',
                'cheerful': '下次再来玩哦！一路顺风~',
                'mysterious': '我们...还会再见的。',
                'wise': '前路漫漫，保重。'
            }
        }
        
        # 根据情境选择内容
        for key, templates in content_templates.items():
            if key in context.lower():
                return templates.get(personality, templates['gentle'])
        
        # 默认返回
        return content_templates['greeting'].get(personality, '欢迎~')
    
    def generate_emotional_scene(self, scene_type: str, 
                                  characters: List[Dict]) -> Dict[str, Any]:
        """
        生成情感场景
        
        Args:
            scene_type: 场景类型（crisis/reunion/sacrifice/victory）
            characters: 角色列表
        
        Returns:
            场景对话
        """
        scene_templates = {
            'crisis': self._crisis_scene,
            'reunion': self._reunion_scene,
            'sacrifice': self._sacrifice_scene,
            'victory': self._victory_scene
        }
        
        scene_func = scene_templates.get(scene_type, self._crisis_scene)
        return scene_func(characters)
    
    def _crisis_scene(self, characters: List[Dict]) -> Dict[str, Any]:
        """危机场景"""
        scene = {
            'type': '危机',
            'atmosphere': '紧张，危急',
            'dialogues': []
        }
        
        # 村长发言
        scene['dialogues'].append({
            'character': '村长',
            'emotion': 'worried',
            'dialogue': '（望着远处的火光，声音颤抖）"来不及了...它们已经到村口了..."'
        })
        
        # 主角发言
        scene['dialogues'].append({
            'character': '主角',
            'emotion': 'determined',
            'dialogue': '（握紧武器，目光坚定）"村长，您带大家先撤。我来断后。"'
        })
        
        # 村民发言
        scene['dialogues'].append({
            'character': '村民',
            'emotion': 'grateful',
            'dialogue': '（眼眶泛红）"恩人...一定要活着回来啊..."'
        })
        
        return scene
    
    def _reunion_scene(self, characters: List[Dict]) -> Dict[str, Any]:
        """重逢场景"""
        scene = {
            'type': '重逢',
            'atmosphere': '温馨，感动',
            'dialogues': []
        }
        
        scene['dialogues'].append({
            'character': '失散多年的亲人',
            'emotion': 'grateful',
            'dialogue': '（泪水夺眶而出，声音哽咽）"是你吗...真的是你吗？我找了你好久...好久..."'
        })
        
        scene['dialogues'].append({
            'character': '主角',
            'emotion': 'happy',
            'dialogue': '（快步上前，紧紧拥抱）"我回来了...再也不离开了。"'
        })
        
        return scene
    
    def _sacrifice_scene(self, characters: List[Dict]) -> Dict[str, Any]:
        """牺牲场景"""
        scene = {
            'type': '牺牲',
            'atmosphere': '悲壮，感动',
            'dialogues': []
        }
        
        scene['dialogues'].append({
            'character': '牺牲者',
            'emotion': 'determined',
            'dialogue': '（露出最后的微笑）"别哭...这是我自己选的路。你们要好好活下去..."'
        })
        
        scene['dialogues'].append({
            'character': '主角',
            'emotion': 'sad',
            'dialogue': '（泪水模糊了视线）"为什么...为什么要这么做..."'
        })
        
        return scene
    
    def _victory_scene(self, characters: List[Dict]) -> Dict[str, Any]:
        """胜利场景"""
        scene = {
            'type': '胜利',
            'atmosphere': '欢乐，激动',
            'dialogues': []
        }
        
        scene['dialogues'].append({
            'character': '村民',
            'emotion': 'happy',
            'dialogue': '（欢呼雀跃）"赢了！我们赢了！英雄万岁！"'
        })
        
        scene['dialogues'].append({
            'character': '主角',
            'emotion': 'determined',
            'dialogue': '（望着远方，轻声）"这只是一个开始...还有更多需要守护的东西。"'
        })
        
        return scene
    
    def export_dialogue(self, dialogue_data: Dict[str, Any]) -> Dict[str, Any]:
        """导出对话数据"""
        filename = f"dialogue_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dialogue_data, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'exported',
            'filepath': filepath,
            'filename': filename
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python dialogue_generator.py <command> [args]")
        print("Commands:")
        print("  npc <name> <personality> <emotion> <context>")
        print("  scene <type> <characters_json>")
        sys.exit(1)
    
    import sys as system_module
    command = system_module.argv[1]
    generator = DialogueGenerator()
    
    if command == 'npc':
        if len(system_module.argv) < 6:
            print("Error: 需要提供 NPC 名称/性格/情感/情境")
            system_module.exit(1)
        
        npc_name = system_module.argv[2]
        personality = system_module.argv[3]
        emotion = system_module.argv[4]
        context = system_module.argv[5]
        
        result = generator.generate_npc_dialogue(npc_name, personality, emotion, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 导出
        export_result = generator.export_dialogue(result)
        print(f"\n已导出：{export_result['filepath']}")
    
    elif command == 'scene':
        if len(system_module.argv) < 4:
            print("Error: 需要提供场景类型和角色")
            system_module.exit(1)
        
        scene_type = system_module.argv[2]
        characters_json = system_module.argv[3]
        characters = json.loads(characters_json)
        
        result = generator.generate_emotional_scene(scene_type, characters)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 导出
        export_result = generator.export_dialogue(result)
        print(f"\n已导出：{export_result['filepath']}")
    
    else:
        print(f"未知命令：{command}")
        system_module.exit(1)


if __name__ == '__main__':
    main()
