\---

name: Baidu Wenku AIPPT
description: Generate PPT with Baidu Wenku AI. Smart template selection based on content.
metadata: { "openclaw": { "emoji": "📑", "requires": { "bins": \["python3"], "env":\["BAIDU\_API\_KEY"]},"primaryEnv":"BAIDU\_API\_KEY" } }
---

# AI PPT Generator - Staj

Generate PPT using Baidu AI with intelligent template selection.

## Smart Workflow

1. **User provides PPT topic**
2. **Agent asks**: "Want to choose a template style?"
3. **If yes** → Show styles from `ppt\_theme\_list.py` → User picks → Use `generate\_ppt.py` with chosen `tpl\_id` and real `style\_id`
4. **If no** → Use `random\_ppt\_theme.py` (auto-selects appropriate template based on topic content)

## Intelligent Template Selection

`random\_ppt\_theme.py` analyzes the topic and suggests appropriate template:

* **Business topics** → 企业商务 style
* **Technology topics** → 未来科技 style
* **Education topics** → 卡通手绘 style
* **Creative topics** → 创意趣味 style
* **Cultural topics** → 中国风 or 文化艺术 style
* **Year-end reports** → 年终总结 style
* **Minimalist design** → 扁平简约 style
* **Artistic content** → 文艺清新 style

## Scripts

* `scripts/ppt\_theme\_list.py` - List all available templates with style\_id and tpl\_id
* `scripts/random\_ppt\_theme.py` - Smart template selection + generate PPT
* `scripts/generate\_ppt.py` - Generate PPT with specific template (uses real style\_id and tpl\_id from API)

## Key Features

* **Smart categorization**: Analyzes topic content to suggest appropriate style
* **Fallback logic**: If template not found, automatically uses random selection
* **Complete parameters**: Properly passes both style\_id and tpl\_id to API

## Usage Examples

```bash
# List all templates with IDs
python3 scripts/ppt\_theme\_list.py

# Smart automatic selection (recommended for most users)
python3 scripts/random\_ppt\_theme.py --query "人工智能发展趋势报告"

# Specific template with proper style\_id
python3 scripts/generate\_ppt.py --query "儿童英语课件" --tpl\_id 106

# Specific template with auto-suggested category
python3 scripts/random\_ppt\_theme.py --query "企业年度总结" --category "企业商务"
```

## Agent Steps

1. Get PPT topic from user
2. Ask: "Want to choose a template style?"
3. **If user says YES**:

   * Run `ppt\_theme\_list.py` to show available templates
   * User selects a template (note the tpl\_id)
   * Run `generate\_ppt.py --query "TOPIC" --tpl\_id ID`
4. **If user says NO**:

   * Run `random\_ppt\_theme.py --query "TOPIC"`
   * Script will auto-select appropriate template based on topic
5. Set timeout to 300 seconds (PPT generation takes 2-5 minutes)
6. Monitor output, wait for `is\_end: true` to get final PPT URL

## Output Examples

**During generation:**

```json
{"status": "PPT生成中", "run\_time": 45}
```

**Final result:**

```json
{
  "status": "PPT导出结束", 
  "is\_end": true, 
  "data": {"ppt\_url": "https://image0.bj.bcebos.com/...ppt"}
}
```

## Technical Notes

* **API integration**: Fetches real style\_id from Baidu API for each template
* **Error handling**: If template not found, falls back to random selection
* **Timeout**: Generation takes 2-5 minutes, set sufficient timeout
* **Streaming**: Uses streaming API, wait for `is\_end: true` before considering complete

