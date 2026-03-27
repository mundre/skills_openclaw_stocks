#!/usr/bin/env python3
# 测试单个voice元素超过字节限制的拆分

import sys
sys.path.insert(0, 'scripts')

from dialogue_formatter import DialogueFormatter

formatter = DialogueFormatter()

# 创建一个非常长的文本，确保单个voice元素超过500字节
long_text = "这是一段非常长的文本，" * 50  # 大约 10*50 = 500字节，加上中文字符更多

ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="度小美">
    {long_text}
  </voice>
</speak>'''

print(f"原始SSML字节数: {len(ssml.encode('utf-8'))}")

# 验证
is_valid, msg = formatter.validate_ssml(ssml)
print(f"验证结果: {msg}")

# 拆分，使用较小的max_bytes
segments = formatter.split_long_ssml(ssml, max_bytes=300)
print(f"\n拆分成 {len(segments)} 个片段:")

for i, seg in enumerate(segments):
    print(f"\n=== 片段 {i+1} ===")
    print(f"字节数: {len(seg.encode('utf-8'))}")
    # 只打印前150个字符
    preview = seg[:150].replace('\n', ' ')
    print(f"内容预览: {preview}...")
    
    # 验证每个片段
    is_valid, msg = formatter.validate_ssml(seg)
    print(f"验证: {msg}")