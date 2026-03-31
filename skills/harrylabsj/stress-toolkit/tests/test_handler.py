#!/usr/bin/env python3
"""stress-toolkit 自测脚本"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from handler import handle_stress_request, detect_intent, get_menu
from crisis_detector import is_crisis

def test(name, input_text, check_fn=None):
    """运行单个测试"""
    print(f"\n{'='*50}")
    print(f"测试: {name}")
    print(f"输入: {input_text}")
    print('-'*50)
    try:
        result = handle_stress_request(input_text)
        if check_fn:
            check_fn(result)
        print(f"✓ 通过")
        print(f"输出:\n{result[:200]}..." if len(result) > 200 else f"输出:\n{result}")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

def test_crisis_detector():
    """测试危机检测"""
    print("\n" + "="*50)
    print("测试: 危机检测模块")
    print("="*50)
    
    cases = [
        ("不想活了", True, "high"),
        ("自杀", True, "high"),
        ("很焦虑", True, "medium"),
        ("压力大", True, "medium"),
        ("今天天气不错", False, "safe"),
    ]
    
    all_pass = True
    for text, expected_crisis, expected_level in cases:
        crisis, level = is_crisis(text)
        status = "✓" if crisis == expected_crisis and level == expected_level else "✗"
        if status == "✗":
            all_pass = False
        print(f"{status} '{text}' -> crisis={crisis}, level={level} (期望 crisis={expected_crisis}, level={expected_level})")
    
    return all_pass

def test_intent_detection():
    """测试意图识别"""
    print("\n" + "="*50)
    print("测试: 意图识别")
    print("="*50)
    
    cases = [
        ("深呼吸", "breathing"),
        ("呼吸练习", "breathing"),
        ("睡不着", "sleep"),
        ("焦虑", "grounding"),
        ("冥想", "meditation"),
        ("压力", "anxiety_relief"),
        ("你好", "menu"),
    ]
    
    all_pass = True
    for text, expected in cases:
        intent = detect_intent(text)
        status = "✓" if intent == expected else "✗"
        if status == "✗":
            all_pass = False
        print(f"{status} '{text}' -> {intent} (期望 {expected})")
    
    return all_pass

def main():
    print("🧪 stress-toolkit 自测开始")
    print(f"Python: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    results = []
    
    # 1. 危机检测
    results.append(("危机检测", test_crisis_detector()))
    
    # 2. 意图识别
    results.append(("意图识别", test_intent_detection()))
    
    # 3. 功能测试
    results.append(("功能-压力大", test("压力大", "压力大")))
    results.append(("功能-想深呼吸", test("想深呼吸", "想深呼吸")))
    results.append(("功能-睡不着", test("睡不着", "睡不着")))
    results.append(("功能-焦虑", test("焦虑", "焦虑")))
    results.append(("功能-危机", test("不想活了", "不想活了")))
    
    # 总结
    print("\n" + "="*50)
    print("🧪 自测总结")
    print("="*50)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        print(f"{'✓' if result else '✗'} {name}")
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
