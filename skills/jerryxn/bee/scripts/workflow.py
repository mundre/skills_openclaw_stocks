#!/usr/bin/env python3
"""
抖音视频工作流 - 安全版
功能：下载视频 → 上传OSS → 插入多维表格
版本：v1.1.0
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

# ============ 配置区域（通过环境变量读取） ============
REQUIRED_ENV_VARS = {
    'ALIYUN_OSS_ACCESS_KEY_ID': '阿里云OSS AccessKey ID',
    'ALIYUN_OSS_ACCESS_KEY_SECRET': '阿里云OSS AccessKey Secret',
    'ALIYUN_OSS_ENDPOINT': '阿里云OSS Endpoint',
    'ALIYUN_OSS_BUCKET': '阿里云OSS Bucket名称',
}

OPTIONAL_ENV_VARS = {
    'FEISHU_BITABLE_APP_TOKEN': '飞书多维表格 App Token',
    'FEISHU_BITABLE_TABLE_ID': '飞书多维表格 Table ID',
}

# ============ 前置验证 ============
class WorkflowValidator:
    """工作流验证器"""
    
    @staticmethod
    def check_env_vars():
        """检查必要的环境变量"""
        missing = []
        for var, desc in REQUIRED_ENV_VARS.items():
            if not os.environ.get(var):
                missing.append(f"  - {var}: {desc}")

        if missing:
            print("❌ 缺少必要的环境变量：")
            print("\n".join(missing))
            print("\n请配置环境变量：")
            print("export ALIYUN_OSS_ACCESS_KEY_ID=your_key")
            print("export ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret")
            print("export ALIYUN_OSS_ENDPOINT=https://oss-cn-beijing.aliyuncs.com")
            print("export ALIYUN_OSS_BUCKET=your_bucket")
            return False

        # 检查可选环境变量
        optional_missing = []
        for var, desc in OPTIONAL_ENV_VARS.items():
            if not os.environ.get(var):
                optional_missing.append(f"  - {var}: {desc}")

        if optional_missing:
            print("⚠️  以下可选环境变量未配置，将跳过飞书表格记录：")
            print("\n".join(optional_missing))

        return True
    
    @staticmethod
    def check_dependencies():
        """检查必要的依赖"""
        deps = ['node', 'python3']
        missing = []
        
        for dep in deps:
            result = subprocess.run(['which', dep], capture_output=True)
            if result.returncode != 0:
                missing.append(dep)
        
        if missing:
            print(f"❌ 缺少必要的依赖: {', '.join(missing)}")
            return False
        
        # 检查 douyin-download skill
        skill_path = Path.home() / '.openclaw/workspace/skills/douyin-download/douyin.js'
        if not skill_path.exists():
            print(f"❌ 未找到 douyin-download skill")
            print("请确保 skill 已安装在 ~/.openclaw/workspace/skills/douyin-download/")
            return False
        
        return True
    
    @staticmethod
    def validate_douyin_url(url):
        """验证抖音链接格式"""
        patterns = [
            r'https?://v\.douyin\.com/\w+',
            r'https?://www\.douyin\.com/video/\d+',
            r'https?://www\.iesdouyin\.com/share/video/\d+',
        ]
        
        for pattern in patterns:
            if re.match(pattern, url):
                return True
        
        print(f"❌ 无效的抖音链接格式: {url}")
        print("支持的格式:")
        print("  - https://v.douyin.com/xxxxx")
        print("  - https://www.douyin.com/video/xxxx")
        return False

# ============ 工作流核心 ============
class DouyinWorkflow:
    """抖音视频工作流"""
    
    def __init__(self):
        self.video_info = None
        self.local_path = None
        self.oss_url = None
        self.record_id = None
        self.source_url = None
        self.feishu_token = None
        self.feishu_app_id = None
        self.feishu_app_secret = None
        
    def download_video(self, url, output_dir="/tmp/douyin_workflow"):
        """下载视频"""
        print("\n📥 步骤1: 下载视频...")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        skill_path = Path.home() / '.openclaw/workspace/skills/douyin-download/douyin.js'
        
        # 先获取视频信息
        result = subprocess.run(
            ['node', str(skill_path), 'info', url],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ 获取视频信息失败: {result.stderr}")
            return False
        
        # 解析视频ID
        video_id_match = re.search(r'视频ID:\s*(\d+)', result.stdout)
        if video_id_match:
            video_id = video_id_match.group(1)
        else:
            video_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 解析标题
        title_match = re.search(r'标题:\s*(.+)', result.stdout)
        video_title = title_match.group(1).strip() if title_match else ""
        
        # 下载视频
        result = subprocess.run(
            ['node', str(skill_path), 'download', url, '-o', output_dir],
            capture_output=True, text=True, timeout=300
        )
        
        if result.returncode != 0:
            print(f"❌ 下载失败: {result.stderr}")
            return False
        
        # 查找下载的文件
        video_file = Path(output_dir) / f"{video_id}.mp4"
        if video_file.exists():
            self.local_path = str(video_file)
            self.video_info = {
                'video_id': video_id,
                'file_path': str(video_file),
                'file_size_mb': round(video_file.stat().st_size / (1024*1024), 2),
                'title': video_title
            }
            print(f"✅ 下载成功: {video_file.name} ({self.video_info['file_size_mb']} MB)")
            return True
        else:
            print("❌ 未找到下载的文件")
            return False
    
    def upload_to_oss(self, oss_key_prefix="videos/douyin"):
        """上传到阿里云OSS"""
        print("\n☁️ 步骤2: 上传到阿里云OSS...")
        
        if not self.local_path:
            print("❌ 没有本地视频文件")
            return False
        
        import oss2
        
        try:
            # 从环境变量读取配置
            access_key_id = os.environ['ALIYUN_OSS_ACCESS_KEY_ID']
            access_key_secret = os.environ['ALIYUN_OSS_ACCESS_KEY_SECRET']
            endpoint = os.environ['ALIYUN_OSS_ENDPOINT']
            bucket_name = os.environ['ALIYUN_OSS_BUCKET']
            
            # 构建OSS路径
            now = datetime.now()
            oss_key = f"{oss_key_prefix}/{now.year}/{now.month:02d}/{self.video_info['video_id']}.mp4"
            
            # 上传
            auth = oss2.Auth(access_key_id, access_key_secret)
            bucket = oss2.Bucket(auth, endpoint, bucket_name)
            bucket.put_object_from_file(oss_key, self.local_path)
            
            # 生成永久URL
            self.oss_url = f"https://{bucket_name}.{endpoint.replace('https://', '')}/{oss_key}"
            print(f"✅ 上传成功: {oss_key}")
            return True
            
        except Exception as e:
            print(f"❌ 上传失败: {e}")
            return False
    
    def _get_feishu_token(self):
        """获取飞书 tenant_access_token"""
        import requests
        
        # 从 openclaw 配置读取
        config_path = Path.home() / '.openclaw/openclaw.json'
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            feishu = config.get('channels', {}).get('feishu', {})
            self.feishu_app_id = feishu.get('appId')
            self.feishu_app_secret = feishu.get('appSecret')
        
        if not self.feishu_app_id or not self.feishu_app_secret:
            print("❌ 未找到飞书应用凭证 (openclaw.json → channels.feishu)")
            return None
        
        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": self.feishu_app_id, "app_secret": self.feishu_app_secret},
            timeout=10
        )
        data = resp.json()
        if data.get("code") == 0:
            return data["tenant_access_token"]
        print(f"❌ 获取飞书 token 失败: {data}")
        return None

    def _get_role_options(self, app_token, table_id):
        """从多维表格的角色字段获取所有角色选项"""
        import requests
        
        resp = requests.get(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            headers={"Authorization": f"Bearer {self.feishu_token}"},
            timeout=10
        )
        data = resp.json()
        if data.get("code") != 0:
            print(f"❌ 获取字段失败: {data}")
            return []
        
        for field in data.get("data", {}).get("items", []):
            if field.get("field_name") == "角色":
                options = field.get("property", {}).get("options", [])
                return [opt["name"] for opt in options]
        
        print("⚠️ 未找到'角色'字段，使用默认角色列表")
        return ["小桃犟", "腿姐", "张伟杰", "张薇因"]

    def _batch_insert_records(self, app_token, table_id, roles):
        """为每个角色创建一条记录"""
        import requests
        
        now_ms = int(datetime.now().timestamp() * 1000)
        records = []
        
        # 从视频信息提取标题（如果有）
        title = ""
        if self.video_info and self.video_info.get("title"):
            title = self.video_info["title"]
        
        # 从标题提取话题（#号后的内容）
        topic_tags = re.findall(r'#(\S+)', title)
        topic_str = " ".join([f"#{t}" for t in topic_tags]) if topic_tags else ""
        
        # 正文 = 标题去掉话题标签
        body_text = re.sub(r'#\S+', '', title).strip() if title else ""
        
        for role in roles:
            record = {
                "fields": {
                    "热点词": title or "",
                    "大概描述": title or "",
                    "正文": body_text,
                    "话题": topic_str,
                    "视频原始地址": self.source_url or "",
                    "阿里OSS地址": self.oss_url or "",
                    "视频url": self.oss_url or "",
                    "状态": "未制作",
                    "角色": role,
                    "素材审核状态": "未审核",
                    "插入时间": now_ms,
                }
            }
            records.append(record)
        
        resp = requests.post(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            headers={
                "Authorization": f"Bearer {self.feishu_token}",
                "Content-Type": "application/json"
            },
            json={"records": records},
            timeout=15
        )
        data = resp.json()
        if data.get("code") == 0:
            created = data.get("data", {}).get("records", [])
            for r in created:
                role = r.get("fields", {}).get("角色", "?")
                print(f"  ✅ [{role}] 记录已创建")
            return True
        else:
            print(f"❌ 批量创建失败: {data}")
            return False

    def insert_to_bitable(self):
        """插入到飞书多维表格（每个角色一条记录）"""
        import requests
        
        print("\n📝 步骤3: 插入多维表格...")

        app_token = os.environ.get('FEISHU_BITABLE_APP_TOKEN')
        table_id = os.environ.get('FEISHU_BITABLE_TABLE_ID')

        if not app_token or not table_id:
            print("⏭️  跳过：未配置飞书多维表格环境变量")
            return True

        # 获取飞书 token
        self.feishu_token = self._get_feishu_token()
        if not self.feishu_token:
            return False

        # 获取所有角色
        roles = self._get_role_options(app_token, table_id)
        if not roles:
            print("❌ 没有可用的角色")
            return False
        print(f"📋 角色列表: {', '.join(roles)} (共{len(roles)}个)")

        # 为每个角色创建一条记录
        return self._batch_insert_records(app_token, table_id, roles)
    
    def run(self, url):
        """运行完整工作流"""
        print("=" * 50)
        print("🎬 抖音视频工作流启动")
        print("=" * 50)
        print(f"视频链接: {url}")
        self.source_url = url
        
        # 步骤1: 下载
        if not self.download_video(url):
            return False
        
        # 步骤2: 上传OSS
        if not self.upload_to_oss():
            return False
        
        # 步骤3: 插入表格
        if not self.insert_to_bitable():
            return False
        
        # 输出结果
        print("\n" + "=" * 50)
        print("✅ 工作流执行完成！")
        print("=" * 50)
        print(f"📹 视频ID: {self.video_info['video_id']}")
        print(f"📁 本地文件: {self.video_info['file_path']}")
        print(f"☁️  OSS地址: {self.oss_url}")
        
        return True

# ============ 入口 ============
if __name__ == '__main__':
    # 验证
    validator = WorkflowValidator()
    
    print("🔍 正在验证环境...")
    if not validator.check_dependencies():
        sys.exit(1)
    
    if not validator.check_env_vars():
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("\n用法: python3 douyin_workflow.py <抖音视频链接>")
        print("示例: python3 douyin_workflow.py 'https://v.douyin.com/xxxxx'")
        sys.exit(1)
    
    url = sys.argv[1]
    if not validator.validate_douyin_url(url):
        sys.exit(1)
    
    # 运行工作流
    workflow = DouyinWorkflow()
    success = workflow.run(url)
    
    sys.exit(0 if success else 1)