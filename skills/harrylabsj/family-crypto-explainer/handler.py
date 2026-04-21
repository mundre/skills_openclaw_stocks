import json
import re

def _load_skill_meta(skill_name):
    skill_dir = f"/Users/jianghaidong/.openclaw/skills/{skill_name}"
    with open(f"{skill_dir}/SKILL.md", "r") as f:
        content = f.read()
    return {"name": skill_name, "description": "loaded"}

def _load_prompt_template(skill_name):
    return "placeholder template"

def handle(args):
    skill_name = args.get("skill_name", "")
    user_input = args.get("input", "")
    mode = args.get("mode", "guide")
    meta = _load_skill_meta(skill_name)
    template = _load_prompt_template(skill_name)
    return {"result": "done"}
