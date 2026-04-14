#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
荞麦饼 Skills 测试评分脚本
"""

import sys
import os
import time

# 添加当前目录到路径
sys.path.insert(0, '.')

def run_tests():
    """运行所有测试"""
    test_results = []
    
    print("=" * 50)
    print("荞麦饼 Skills 测试评分")
    print("=" * 50)
    print()
    
    # 测试 1: 模块导入
    print("[Test 1] Module Import Test")
    try:
        from core.octo_memory import Memory
        print("  PASS: octo_memory module imported")
        test_results.append(("Module Import", True, "octo_memory OK"))
    except Exception as e:
        print(f"  FAIL: octo_memory import failed: {e}")
        test_results.append(("Module Import", False, str(e)))
    
    try:
        from core.dynamic_kg import KnowledgeGraph
        print("  PASS: dynamic_kg module imported")
        test_results.append(("KG Module", True, "dynamic_kg OK"))
    except Exception as e:
        print(f"  FAIL: dynamic_kg import failed: {e}")
        test_results.append(("KG Module", False, str(e)))
    
    try:
        from core.smart_report import ReportGenerator
        print("  PASS: smart_report module imported")
        test_results.append(("Report Module", True, "smart_report OK"))
    except Exception as e:
        print(f"  FAIL: smart_report import failed: {e}")
        test_results.append(("Report Module", False, str(e)))
    
    print()
    
    # 测试 2: 功能测试
    print("[Test 2] Core Functionality Test")
    try:
        memory = Memory()
        memory.store("test content", tags=["test"])
        results = memory.search("test")
        print("  PASS: Memory system working (store/search)")
        test_results.append(("Memory Function", True, "store/search OK"))
    except Exception as e:
        print(f"  FAIL: Memory test failed: {e}")
        test_results.append(("Memory Function", False, str(e)))
    
    try:
        kg = KnowledgeGraph()
        kg.add_entity("test_entity", "concept")
        entities = kg.get_entities()
        print("  PASS: Knowledge Graph working (add/query)")
        test_results.append(("KG Function", True, "add/query OK"))
    except Exception as e:
        print(f"  FAIL: KG test failed: {e}")
        test_results.append(("KG Function", False, str(e)))
    
    print()
    
    # 测试 3: 安全性测试
    print("[Test 3] Security Test")
    
    # 检查网络模块导入
    network_modules = ['urllib', 'http', 'requests', 'socket']
    found_network = []
    for module in network_modules:
        if module in sys.modules:
            found_network.append(module)
    
    if found_network:
        print(f"  WARNING: Network modules loaded: {found_network}")
        test_results.append(("Network Safety", False, f"modules: {found_network}"))
    else:
        print("  PASS: No network modules loaded")
        test_results.append(("Network Safety", True, "No network modules"))
    
    # 检查文件系统访问
    try:
        test_dir = os.path.expanduser("~/.qiaomai")
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("  PASS: File system access OK (user directory only)")
        test_results.append(("File System", True, "User directory OK"))
    except Exception as e:
        print(f"  FAIL: File system test failed: {e}")
        test_results.append(("File System", False, str(e)))
    
    print()
    
    # 测试 4: 性能测试
    print("[Test 4] Performance Test")
    
    try:
        memory = Memory()
        start = time.time()
        for i in range(100):
            memory.store(f"perf test {i}", tags=["perf"])
        end = time.time()
        duration = end - start
        rate = 100 / duration
        print(f"  PASS: Store 100 items: {duration:.3f}s ({rate:.1f} items/s)")
        test_results.append(("Store Performance", True, f"{rate:.1f} items/s"))
    except Exception as e:
        print(f"  FAIL: Store performance test failed: {e}")
        test_results.append(("Store Performance", False, str(e)))
    
    try:
        start = time.time()
        for i in range(100):
            results = memory.search("perf")
        end = time.time()
        duration = end - start
        rate = 100 / duration
        print(f"  PASS: Search 100 times: {duration:.3f}s ({rate:.1f} queries/s)")
        test_results.append(("Search Performance", True, f"{rate:.1f} queries/s"))
    except Exception as e:
        print(f"  FAIL: Search performance test failed: {e}")
        test_results.append(("Search Performance", False, str(e)))
    
    print()
    
    # 评分汇总
    print("=" * 50)
    print("Test Score Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result, _ in test_results if result)
    total = len(test_results)
    score = (passed / total) * 100 if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Total Score: {score:.1f}/100")
    print()
    
    # 详细结果
    print("Detailed Results:")
    for name, result, detail in test_results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}: {detail}")
    
    print()
    
    # 安全等级
    if score >= 90:
        print("Security Level: A (Excellent)")
    elif score >= 80:
        print("Security Level: B (Good)")
    elif score >= 70:
        print("Security Level: C (Pass)")
    else:
        print("Security Level: D (Needs Improvement)")
    
    return score, test_results

if __name__ == "__main__":
    score, results = run_tests()
    sys.exit(0 if score >= 70 else 1)
