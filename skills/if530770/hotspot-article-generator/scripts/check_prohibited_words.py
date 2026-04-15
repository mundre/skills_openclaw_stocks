#!/usr/bin/env python3
"""
文章违禁词检测脚本
检测文章内容是否包含敏感词、违禁词
"""

import re
import json


def check_prohibited_words(text):
    """
    检测文章中的违禁词
    
    Args:
        text: 待检测的文章内容
    
    Returns:
        dict: 检测结果，包含是否通过、违禁词列表、风险等级
    """
    
    # 违禁词库（分类）
    prohibited_words = {
        # 政治敏感
        "political": [
            "反党", "反政府", "颠覆", "分裂国家", "台独", "藏独", "疆独",
            "法轮功", "邪教", "六四", "天安门事件"
        ],
        
        # 暴力恐怖
        "violence": [
            "恐怖袭击", "爆炸", "杀人", "砍人", "枪击", "暴恐",
            "人体炸弹", "自杀式袭击"
        ],
        
        # 色情低俗
        "pornography": [
            "色情", "淫秽", "裸体", "性交", "强奸", "乱伦"
        ],
        
        # 违法犯罪
        "crime": [
            "贩毒", "吸毒", "走私", "洗钱", "诈骗", "传销",
            "非法集资", "非法经营"
        ],
        
        # 社会敏感
        "social_sensitive": [
            "群体性事件", "暴力执法", "黑警", "城管打人",
            "强拆", "暴力拆迁"
        ],
        
        # 平台违禁（知乎等平台特有）
        "platform_sensitive": [
            "微信号", "加微信", "扫码领红包", "点击领取",
            "免费领取", "限时优惠", "回复领取"
        ]
    }
    
    # 广告营销词
    marketing_words = [
        "加我微信", "私聊我", "扫码添加", "限时特价",
        "仅限今日", "错过后悔", "必须转发"
    ]
    
    # 风险词汇（需要人工审核）
    risk_words = [
        "封锁", "制裁", "打压", "抵制", "抗议",
        "腐败", "贪污", "渎职", "权色交易"
    ]
    
    results = {
        "passed": True,
        "prohibited_found": [],
        "risk_found": [],
        "marketing_found": [],
        "risk_level": "low",
        "suggestions": []
    }
    
    # 检测违禁词
    for category, words in prohibited_words.items():
        for word in words:
            if word in text:
                results["prohibited_found"].append({
                    "word": word,
                    "category": category,
                    "level": "high"
                })
                results["passed"] = False
    
    # 检测风险词
    for word in risk_words:
        if word in text:
            # 获取上下文
            pattern = re.compile(r'.{0,20}' + re.escape(word) + r'.{0,20}')
            matches = pattern.findall(text)
            results["risk_found"].append({
                "word": word,
                "level": "medium",
                "context": matches[:2] if matches else []
            })
    
    # 检测营销词
    for word in marketing_words:
        if word in text:
            results["marketing_found"].append({
                "word": word,
                "level": "low"
            })
    
    # 确定风险等级
    if results["prohibited_found"]:
        results["risk_level"] = "high"
    elif results["risk_found"]:
        results["risk_level"] = "medium"
    elif results["marketing_found"]:
        results["risk_level"] = "low"
    else:
        results["risk_level"] = "safe"
    
    # 生成建议
    if results["prohibited_found"]:
        results["suggestions"].append("❌ 发现违禁词，必须修改后发布")
    if results["risk_found"]:
        results["suggestions"].append("⚠️ 发现风险词，建议人工审核上下文")
    if results["marketing_found"]:
        results["suggestions"].append("💡 发现营销词，可能影响推荐")
    if results["risk_level"] == "safe":
        results["suggestions"].append("✅ 未发现违禁词，可以发布")
    
    return results


def analyze_text_content(text):
    """分析文本内容的其他指标"""
    
    analysis = {
        "word_count": len(text),
        "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
        "has_sensitive_numbers": False,
        "has_external_links": False,
        "suggestions": []
    }
    
    # 检测敏感数字（可能涉及隐私或违规）
    phone_pattern = re.compile(r'1[3-9]\d{9}')
    id_pattern = re.compile(r'\d{17}[\dXx]')
    
    if phone_pattern.search(text):
        analysis["has_sensitive_numbers"] = True
        analysis["suggestions"].append("⚠️ 文章包含手机号，建议删除")
    
    if id_pattern.search(text):
        analysis["has_sensitive_numbers"] = True
        analysis["suggestions"].append("⚠️ 文章包含身份证号，建议删除")
    
    # 检测外链
    url_pattern = re.compile(r'https?://[^\s]+')
    external_links = url_pattern.findall(text)
    if external_links:
        analysis["has_external_links"] = True
        analysis["external_links"] = external_links
        analysis["suggestions"].append("💡 文章包含外链，部分平台可能限制")
    
    return analysis


def print_report(prohibited_result, analysis_result):
    """打印检测报告"""
    
    print("\n" + "="*60)
    print("📋 文章违禁词检测报告")
    print("="*60)
    
    # 基本信息
    print(f"\n📊 基本信息：")
    print(f"  - 字数统计：{analysis_result['word_count']} 字")
    print(f"  - 段落数量：{analysis_result['paragraph_count']} 段")
    
    # 违禁词检测结果
    print(f"\n🔍 违禁词检测：")
    print(f"  - 风险等级：{prohibited_result['risk_level'].upper()}")
    print(f"  - 检测结果：{'✅ 通过' if prohibited_result['passed'] else '❌ 未通过'}")
    
    if prohibited_result["prohibited_found"]:
        print(f"\n  ❌ 发现违禁词：")
        for item in prohibited_result["prohibited_found"]:
            print(f"    - [{item['category']}] {item['word']}")
    
    if prohibited_result["risk_found"]:
        print(f"\n  ⚠️ 发现风险词：")
        for item in prohibited_result["risk_found"]:
            print(f"    - {item['word']}")
            if item['context']:
                print(f"      上下文：...{item['context'][0]}...")
    
    if prohibited_result["marketing_found"]:
        print(f"\n  💡 发现营销词：")
        for item in prohibited_result["marketing_found"]:
            print(f"    - {item['word']}")
    
    # 其他分析
    if analysis_result["suggestions"]:
        print(f"\n📝 其他建议：")
        for suggestion in analysis_result["suggestions"]:
            print(f"  {suggestion}")
    
    # 总体建议
    print(f"\n💡 总体建议：")
    for suggestion in prohibited_result["suggestions"]:
        print(f"  {suggestion}")
    
    print("\n" + "="*60)
    
    return prohibited_result["passed"]


if __name__ == "__main__":
    # 读取文章内容
    article_path = "/workspace/projects/hotspot-article-generator/assets/article2_chip_breakthrough.txt"
    
    # 如果文件不存在，使用内置文章
    article_content = """中国芯片突破：这场"突围战"，我们打了太久

今天，一则消息刷屏：中国发布芯片研发重大突破成果。

看似简单的一句话，背后却是无数科研人员日以继夜的奋斗，是我们在技术封锁下的艰难突围，是一个民族不屈不挠的抗争。

这不是一条普通的新闻，这是一场没有硝烟的战争中的重要转折。

一、从"卡脖子"到"突围"，这条路有多难

过去几年，"芯片"成为中国人心中最痛的字眼。

美国的技术封锁、高端光刻机的禁运、核心技术的缺失……每一个关键词，都像一把刀，刺痛着我们的神经。我们深刻地意识到：在关键核心技术上受制于人，是多么危险的一件事。

于是，无数科研人员开始了艰难的攻关。没有高端设备，就自主研发；没有成熟工艺，就从零探索；没有现成经验，就摸着石头过河。

这就是中国人的韧劲：越是困难，越要迎难而上；越是被封锁，越要突破重围。

今天的突破成果，正是这些努力的结晶。它告诉我们：只要我们想做的事情，没有做不到的。

二、突破的意义，远超技术本身

很多人会问：这次突破到底有多重要？

从技术角度看，它意味着我们在芯片领域又向前迈进了一大步，缩小了与国际先进水平的差距。

从战略角度看，它意味着我们在关键技术上有了更多自主权，不再那么容易被"卡脖子"。

从精神角度看，它意味着我们有信心、有能力突破任何技术封锁，实现科技自立自强。

技术突破只是表象，真正的意义在于：我们证明了自己可以做到。

这种信心，比任何技术成果都更重要。它会激励更多科研人员投身核心技术攻关，会激励更多企业敢于投入研发，会激励整个社会更加重视科技创新。

三、突破是起点，不是终点

当然，我们也要清醒地认识到：一次突破不等于全面领先，我们的芯片产业还有很长的路要走。

在高端光刻机、先进制程、核心设计软件等领域，我们与国际先进水平仍有差距。我们不能因为一次突破就沾沾自喜，更不能因为一点成绩就放松警惕。

突破是起点，不是终点。

我们需要继续加大研发投入，需要培养更多优秀人才，需要建立更完善的产业生态。只有这样，我们才能真正实现芯片产业的自主可控，才能在未来的技术竞争中立于不败之地。

四、给年轻人的话：你们是最好的时代

看到这条新闻，我想对年轻人说几句。

你们是最好的时代。国家正在大力推动科技创新，社会越来越重视技术人才，无数机会正在等待着你们。

如果你对科技感兴趣，如果你有志于投身核心技术攻关，请不要犹豫。这个国家需要你们，这个行业需要你们，未来属于你们。

一个民族的崛起，最终要靠自己的双手。而你们，正是这双手最有力的部分。

结语

中国芯片突破，只是一个开始。

这场"突围战"，我们打了太久。但今天的成果告诉我们：只要坚持不懈，就一定能够突破重围。

未来的路还很长，但我们有理由相信：一个科技自立自强的中国，正在崛起。

致敬每一位默默奉献的科研人员，是你们的坚守，撑起了这个国家的科技脊梁。

你的观点是什么？你认为中国芯片产业还需要多久才能全面领先？欢迎在评论区留言。"""
    
    # 执行检测
    prohibited_result = check_prohibited_words(article_content)
    analysis_result = analyze_text_content(article_content)
    
    # 打印报告
    passed = print_report(prohibited_result, analysis_result)
    
    # 返回状态码
    import sys
    sys.exit(0 if passed else 1)
