#!/usr/bin/env python3
# 测试SSML拆分功能

import sys
sys.path.insert(0, 'scripts')

from dialogue_formatter import DialogueFormatter

formatter = DialogueFormatter()

# 创建一个长SSML
ssml = '''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="度小美">
    小明：这是一段很长的文本，用于测试SSML拆分功能。当SSML超过1024字节时，需要拆分成多个片段。每个片段都应该是完整的XML结构，以speak标签开始和结束。
  </voice>
  <break time="300ms"/>
  <voice name="度小宇">
    小红：这是另一个角色的对话，同样很长。我们需要确保拆分后的每个片段都是有效的SSML，并且保持语音的连贯性。拆分算法应该智能地处理长文本。
  </voice>
  <break time="500ms"/>
  <voice name="度博文">
    老师：这是第三个角色的对话，内容也很长。如果单个voice标签内的文本超过1024字节，我们需要在文本内部进行拆分，同时保持voice标签的完整性。这是一个复杂但必要的功能。
  </voice>
</speak>'''

print(f"原始SSML字节数: {len(ssml.encode('utf-8'))}")

# 验证
is_valid, msg = formatter.validate_ssml(ssml)
print(f"验证结果: {msg}")

# 拆分
segments = formatter.split_long_ssml(ssml, max_bytes=500)  # 使用较小的max_bytes以便触发拆分
print(f"\n拆分成 {len(segments)} 个片段:")

for i, seg in enumerate(segments):
    print(f"\n=== 片段 {i+1} ===")
    print(f"字节数: {len(seg.encode('utf-8'))}")
    print(f"内容预览: {seg[:100]}...")
    
    # 验证每个片段
    is_valid, msg = formatter.validate_ssml(seg)
    print(f"验证: {msg}")