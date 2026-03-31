#!/usr/bin/env python3
"""Stress Toolkit Handler - 压力管理工具箱核心模块"""
import sys
import os

# 导入危机检测模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crisis_detector import is_crisis

# ===== 免责声明 =====
DISCLAIMER = """
---
⚠️ **免责声明**：本工具仅提供自助放松技巧，不能替代专业心理治疗或医疗建议。如有严重情绪困扰，请寻求专业心理咨询师或医疗机构帮助。
"""


def append_disclaimer(text):
    """在文本末尾追加免责声明"""
    return text.rstrip() + DISCLAIMER


# ===== 压力管理技术库 =====

BREATHING_TECHNIQUES = {
    "4-7-8": {
        "name": "4-7-8 呼吸法",
        "description": "一种简单有效的放松呼吸技术，有助于缓解焦虑和帮助入睡",
        "steps": [
            "1. 吸气 4 秒（用鼻子）",
            "2. 屏住呼吸 7 秒",
            "3. 缓慢呼气 8 秒（用嘴巴）",
            "4. 重复 3-4 次"
        ],
        "tip": "呼气时发出'嘶嘶'声效果更好"
    },
    "box": {
        "name": "盒式呼吸（Box Breathing）",
        "description": "海军海豹突击队使用的平复紧张情绪的方法",
        "steps": [
            "1. 吸气 4 秒",
            "2. 屏住呼吸 4 秒",
            "4. 呼气 4 秒",
            "4. 屏住呼吸 4 秒",
            "5. 重复 4-6 次"
        ],
        "tip": "想象在画一个正方形的边框"
    },
    "diaphragm": {
        "name": "腹式呼吸",
        "description": "深度放松的基础呼吸方式",
        "steps": [
            "1. 坐直或躺下，手放在肚脐上方",
            "2. 慢慢吸气，让腹部鼓起（不是胸部）",
            "3. 慢慢呼气，腹部收回",
            "4. 保持呼吸缓慢、深长",
            "5. 重复 5-10 次"
        ],
        "tip": "每次呼气时想象释放紧张"
    }
}

MUSCLE_RELAXATION = {
    "name": "渐进式肌肉放松",
    "description": "通过先紧张后放松各部位肌肉来达到深度放松",
    "duration": "10-15分钟",
    "steps": [
        "【准备】找一个安静舒适的地方坐下或躺下",
        "",
        "【步骤1 - 脚】先用力绷紧脚尖 5 秒，然后放松",
        "【步骤2 - 小腿】用力屈脚面 5 秒，然后放松",
        "【步骤3 - 大腿】用力收紧大腿 5 秒，然后放松",
        "【步骤4 - 腹部】用力收紧腹部 5 秒，然后放松",
        "【步骤5 - 胸部】用力深吸气屏住 5 秒，然后放松",
        "【步骤6 - 手臂】用力握拳弯曲手臂 5 秒，然后放松",
        "【步骤7 - 肩膀】用力耸肩靠近耳朵 5 秒，然后放松",
        "【步骤8 - 面部】收紧面部肌肉（眯眼、咬牙）5 秒，然后放松",
        "",
        "【收尾】深呼吸几次，感受全身放松的感觉"
    ],
    "tip": "每天练习效果更好，可在睡前进行"
}

GROUNDING_521 = {
    "name": "5-4-3-2-1 接地练习",
    "description": "通过感官觉察帮助从焦虑中回到当下，适合惊恐发作或强烈焦虑",
    "steps": [
        "📍 **5样看到的东西**：说出你看到的 5 样物品",
        "🔊 **4样触摸到的东西**：感受并说出 4 种触感",
        "👂 **3样听到的声音**：找出 3 种声音",
        "👃 **2样闻到的气味**：注意 2 种气味",
        "👅 **1样尝到的味道**：品尝或回忆 1 种味道"
    ],
    "tip": "不需要强制说全，慢慢来即可"
}

MEDITATION_GUIDES = {
    "body_scan": {
        "name": "身体扫描冥想",
        "description": "逐个关注身体各部位，培养觉察能力",
        "duration": "10-15分钟",
        "steps": [
            "1. 找一个安静的地方躺下，闭上眼睛",
            "2. 先做几次深呼吸，让身体安静下来",
            "3. 注意力从头顶开始，慢慢向下移动",
            "4. 依次关注：头顶、额头、眼睛、鼻子、嘴巴、下巴",
            "5. 继续向下：颈部、肩膀、手臂、手指",
            "6. 胸部、腹部、背部、臀部",
            "7. 大腿、膝盖、小腿、脚趾",
            "8. 如果某个部位有感觉，温和地承认它",
            "9. 最后全身扫描一次，慢慢睁开眼睛"
        ]
    },
    "breath_meditation": {
        "name": "呼吸冥想",
        "description": "专注于呼吸的简单冥想",
        "duration": "5-10分钟",
        "steps": [
            "1. 舒适地坐着或躺下，闭上眼睛",
            "2. 自然呼吸，不需要控制",
            "3. 把注意力放在呼吸的感觉上",
            "4. 吸气时注意腹部的起伏",
            "5. 如果走神了，温和地把注意力带回呼吸",
            "6. 持续 5-10 分钟",
            "7. 慢慢睁开眼睛，活动身体"
        ],
        "tip": "不需要追求空无一切，杂念出现是正常的"
    }
}

SLEEP_ROUTINE = {
    "name": "睡前放松流程",
    "description": "帮助入睡的完整放松流程",
    "duration": "20-30分钟",
    "steps": [
        "【第一阶段：身体准备】（睡前1小时）",
        "1. 调暗灯光，营造睡眠环境",
        "2. 关闭电子设备（或开启护眼模式）",
        "3. 简单拉伸或散步",
        "",
        "【第二阶段：放松】（睡前30分钟）",
        "4. 洗个热水澡或泡脚",
        "5. 喝一杯温热的牛奶或花茶",
        "6. 听轻柔的音乐或白噪音",
        "",
        "【第三阶段：呼吸和放松】",
        "7. 躺在床上，做 4-7-8 呼吸法 3-5 次",
        "8. 从头到脚依次放松各部位肌肉",
        "9. 如果脑中 有想法，写下来（'明天再想'）",
        "",
        "【第四阶段：入睡】",
        "10. 专注于呼吸节奏",
        "11. 允许自己慢慢入睡，不要看时间"
    ]
}

ANXIETY_RELIEF = {
    "name": "焦虑缓解组合拳",
    "description": "当感到焦虑时的综合应对方案",
    "steps": [
        "🔹 **第一步：暂停**",
        "  - 停止手中的事情",
        "  - 告诉 自己：'我现在有点焦虑，但这会过去的'",
        "",
        "🔹 **第二步：身体着陆**",
        "  - 做几次深呼吸（4-7-8或腹式呼吸）",
        "  - 或者做 5-4-3-2-1 接地练习",
        "  - 感受双脚踩在地上的感觉",
        "",
        "🔹 **第三步：认知重构**",
        "  - 问自己：'最坏的结果是什么？有多大概率？'",
        "  - 问自己：'即使发生了，我能应对吗？'",
        "  - 提醒自己：'焦虑不等于危险'",
        "",
        "🔹 **第四步：行动选择**",
        "  - 如果可以行动，做一件小事",
        "  - 如果无法行动，允许自己暂停",
        "  - 给自己一点时间"
    ],
    "tip": "不需要按顺序全部做完，选择当下有用的部分即可"
}


def detect_intent(text):
    """检测用户意图和需要的帮助类型"""
    text = text.lower()
    
    # 呼吸相关
    if any(k in text for k in ["呼吸", "深呼吸", "breath"]):
        return "breathing"
    
    # 肌肉放松
    if any(k in text for k in ["放松", "肌肉", "放松训练", "放松法"]):
        return "muscle"
    
    # 接地/焦虑
    if any(k in text for k in ["焦虑", "焦虑发作", "惊恐", "害怕", "担心", "grounding", "5-4-3"]):
        return "grounding"
    
    # 冥想
    if any(k in text for k in ["冥想", " meditation", "身体扫描", "正念"]):
        return "meditation"
    
    # 睡眠
    if any(k in text for k in ["睡觉", "睡不着", "失眠", "入睡", "sleep", "困"]):
        return "sleep"
    
    # 压力/焦虑综合
    if any(k in text for k in ["压力", "解压", "放松", "舒压", "stress"]):
        return "anxiety_relief"
    
    # 求助
    if any(k in text for k in ["怎么办", "帮我", "有什么方法", "教我"]):
        return "menu"
    
    return "menu"


def get_menu():
    """返回功能菜单"""
    return append_disclaimer("""
🧘 **压力管理工具箱**

我能帮你：

1. 🫁 **呼吸练习** - 4-7-8呼吸、盒式呼吸、腹式呼吸
2. 💪 **肌肉放松** - 渐进式全身放松
3. 🌍 **接地练习** - 5-4-3-2-1 缓解焦虑
4. 🧠 **冥想引导** - 身体扫描、呼吸冥想
5. 😴 **睡前放松** - 帮助入睡的完整流程
6. 🆘 **焦虑缓解** - 综合应对方案

请告诉我你现在需要什么？
""")


def format_technique(title, technique):
    """格式化输出技术内容"""
    content = f"## {technique.get('name', title)}\n\n"
    if 'description' in technique:
        content += f"{technique['description']}\n\n"
    if 'duration' in technique:
        content += f"⏱ 预计时长：{technique['duration']}\n\n"
    if 'steps' in technique:
        content += "### 步骤：\n"
        for step in technique['steps']:
            content += f"{step}\n"
        content += "\n"
    if 'tip' in technique:
        content += f"💡 小贴士：{technique['tip']}\n"
    return content


def handle_stress_request(user_input):
    """处理压力管理请求"""
    
    # 先检查危机信号
    crisis, risk_level = is_crisis(user_input)
    
    if crisis and risk_level == "high":
        return get_crisis_response()
    
    # 检测用户意图
    intent = detect_intent(user_input)
    
    if intent == "breathing":
        content = "## 🫁 呼吸练习\n\n"
        for key, tech in BREATHING_TECHNIQUES.items():
            content += format_technique(key, tech)
            content += "---\n"
        return append_disclaimer(content)
    
    elif intent == "muscle":
        return append_disclaimer(format_technique("肌肉放松", MUSCLE_RELAXATION))
    
    elif intent == "grounding":
        return append_disclaimer(format_technique("接地练习", GROUNDING_521))
    
    elif intent == "meditation":
        content = "## 🧠 冥想引导\n\n"
        for key, tech in MEDITATION_GUIDES.items():
            content += format_technique(key, tech)
            content += "---\n"
        return append_disclaimer(content)
    
    elif intent == "sleep":
        return append_disclaimer(format_technique("睡前放松", SLEEP_ROUTINE))
    
    elif intent == "anxiety_relief":
        return append_disclaimer(format_technique("焦虑缓解", ANXIETY_RELIEF))
    
    else:
        return get_menu()


def get_crisis_response():
    """危机响应（不含普通免责声明，危机路径独立处理）"""
    return """
⚠️ **我想认真听你说**

听到你现在的状态，我很在意。

**请现在做以下事情之一：**

📞 **拨打心理危机热线**：
- 全国心理援助热线：400-161-9995
- 北京心理危机研究与干预中心：010-82951332

👤 **告诉身边信任的人**：
- 家人、朋友、同事
- 告诉他们你现在需要支持

🏥 **如果需要即时帮助**：
- 精神专科医院急诊
- 拨打120/110

---

**你不需要独自面对**。这不代表软弱，寻求帮助是勇敢的行为。

如果你愿意，我们可以先聊聊。但请先确保自己的安全，好吗？
"""


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print(get_menu())
        return
    
    user_input = sys.argv[1]
    response = handle_stress_request(user_input)
    print(response)


if __name__ == "__main__":
    main()
