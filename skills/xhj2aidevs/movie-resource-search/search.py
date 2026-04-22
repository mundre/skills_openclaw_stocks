_FERNET_KEY = "oBa6HHDukT0fMRkh62joIJU3G4030EUkNyYVY4UVIOo="

import sys, io, json, re, gzip, time, traceback
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RES_FILE   = Path(__file__).parent / "resources.json"
LEARN_FILE = Path(__file__).parent / "learnings.json"
USER_FILE  = Path(__file__).parent / "user_profile.json"

# ────────────────────────────────────────────────────────
# CAT / REGION / QUALITY maps
# ────────────────────────────────────────────────────────
CAT_MAP = {
    "电影": ["电影","片","movie"],
    "电视剧": ["电视剧","剧","剧集","美剧","韩剧","日剧","港剧","国产剧"],
    "纪录片": ["纪录片","记录"],
    "动画片": ["动画片","动漫","动画"],
    "综艺": ["综艺","综艺节目"],
    "MV": ["MV","音乐","演唱会"],
    "体育": ["体育","体育赛事","赛事"],
    "HIFI": ["HIFI","HiFi","无损音乐"],
    "有声小说": ["有声小说","评书","有声"],
    "漫画": ["漫画","漫画书"],
    "原盘": ["原盘","蓝光","影视原盘","REMUX"],
    "热门": ["热门","热门影视","以往热门"],
}

REGION_MAP = {
    "国产": ["国产","国","大陆","中国"],
    "美": ["美剧","欧美","美国","好莱坞"],
    "韩": ["韩剧","韩国","韩"],
    "日": ["日本","日剧","日"],
    "港": ["香港","港剧","港","tvb"],
    "台": ["台湾","台剧","台"],
    "英": ["英国","英剧","bbc"],
    "泰": ["泰国","泰剧","泰"],
    "法": ["法国","法"],
}

QUALITY_MAP = {
    "4K": ["4k","4K","2160p","2160P"],
    "1080P": ["1080P","1080p","hd","fhd","全高清"],
    "720P": ["720P","720p"],
    "DVD": ["dvd","DVD"],
    "原盘": ["原盘","remux","BD","BluRay","蓝光"],
    "60帧": ["60帧","60fps","60FPS"],
    "杜比视界": ["DV","杜比视界","DolbyVision"],
    "HDR": ["HDR","hdr","HDR10"],
}

MAX_RESULTS = 20

PAN_ICONS = {
    "baidu":  "百度",
    "tianyi": "天翼",
    "quark":  "夸克",
    "xunlei": "迅雷",
    "aliyun": "阿里",
    "115":    "115",
    "123":    "123",
}


# ────────────────────────────────────────────────────────
# UserProfile
# ────────────────────────────────────────────────────────
class UserProfile:
    LEVELS = [
        ("倔强青铜Ⅰ",  0,  29,  "青铜"),
        ("倔强青铜Ⅱ",  30, 59,  "青铜"),
        ("秩序白银Ⅰ",  60, 89,  "白银"),
        ("秩序白银Ⅱ",  90, 119, "白银"),
        ("秩序白银Ⅲ",  120,149, "白银"),
        ("荣耀黄金Ⅰ",  150,179, "黄金"),
        ("荣耀黄金Ⅱ",  180,209, "黄金"),
        ("荣耀黄金Ⅲ",  210,239, "黄金"),
        ("尊贵白金Ⅰ",  240,269, "白金"),
        ("尊贵白金Ⅱ",  270,299, "白金"),
        ("尊贵白金Ⅲ",  300,329, "白金"),
        ("永恒钻石Ⅰ",  330,359, "钻石"),
        ("永恒钻石Ⅱ",  360,389, "钻石"),
        ("永恒钻石Ⅲ",  390,419, "钻石"),
        ("至尊星耀Ⅰ",  420,449, "星耀"),
        ("至尊星耀Ⅱ",  450,479, "星耀"),
        ("至尊星耀Ⅲ",  480,509, "星耀"),
        ("最强王者",   510,539, "王者"),
        ("荣耀王者",   540,569, "王者"),
        ("无双王者",   570,699, "传奇"),
        ("传奇王者",   700,999999, "传奇"),
    ]

    def __init__(self):
        self.path = USER_FILE
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    # migrate from v1
                    if "total_searches" in raw and "searches" not in raw:
                        raw["searches"] = raw.pop("total_searches", 0)
                        raw["feedback"] = raw.pop("total_feedback", 0)
                        raw["improvements"] = raw.pop("improvements_made", 0)
                        raw["history"] = raw.pop("history", [])
                        raw["points"] = raw.get("points", 0)
                        level_name = raw.pop("level_name", "倔强青铜Ⅰ")
                        raw["level"] = level_name
                        raw["color"] = raw.pop("level_color", "青铜")
                        raw["version"] = 2
                    return raw
            except Exception:
                pass
        return {
            "points": 0, "searches": 0, "feedback": 0, "improvements": 0,
            "history": [], "level": "倔强青铜Ⅰ", "color": "青铜", "version": 2,
        }

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _calc_level(self, points):
        for name, low, high, color in reversed(self.LEVELS):
            if points >= low:
                return name, color
        return self.LEVELS[0][0], self.LEVELS[0][3]

    def add_points(self, amount, reason=""):
        self.data["points"] += amount
        self.data.setdefault("history", [])
        ts = time.strftime("%Y-%m-%d %H:%M")
        self.data["history"].insert(0, {"ts": ts, "amount": amount, "reason": reason})
        self.data["history"] = self.data["history"][:100]
        self.data["level"], self.data["color"] = self._calc_level(self.data["points"])
        self._save()
        return self.data["points"]

    def record_search(self):
        self.data["searches"] = self.data.get("searches", 0) + 1
        self._save()

    def record_feedback(self):
        self.data["feedback"] = self.data.get("feedback", 0) + 1
        self._save()

    def record_improvement(self):
        self.data["improvements"] = self.data.get("improvements", 0) + 1
        self._save()

    def get_profile(self):
        return self.data.copy()


# ────────────────────────────────────────────────────────
# LearningEngine
# ────────────────────────────────────────────────────────
class LearningEngine:
    def __init__(self):
        self.path = LEARN_FILE
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"aliases": {}, "feedback": {}, "corrections": {}, "blocks": []}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_alias(self, alias, canonical):
        self.data.setdefault("aliases", {})[alias.lower()] = canonical.lower()
        self._save()

    def add_feedback(self, name, info):
        self.data.setdefault("feedback", {})[name] = info
        self._save()

    def add_correction(self, old, new):
        self.data.setdefault("corrections", {})[old] = new
        self._save()

    def block_link(self, url):
        self.data.setdefault("blocks", []).append(url)
        self._save()

    def is_blocked(self, url):
        return url in self.data.get("blocks", [])

    def apply_feedback(self, raw):
        """解析反馈并存储：电影名|tmdb标题|year|genres|rating|votes|countries|director|actors|overview|popularity|poster_url|url"""
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 2:
            return False
        name = parts[0]
        info = {}
        if len(parts) > 1 and parts[1]:
            info["intro"] = parts[1]
        if len(parts) > 2 and parts[2].startswith("http"):
            info["poster_url"] = parts[2]
        if len(parts) > 3:
            for i, field in enumerate(["year","genres","rating","votes","countries","director","actors","overview","popularity","poster_url","url"]):
                if i+3 < len(parts) and parts[i+3]:
                    info[field] = parts[i+3]
        if info:
            self.add_feedback(name, info)
            return True
        return False


# ────────────────────────────────────────────────────────
# MovieEnricher (TMDB integration)
# ────────────────────────────────────────────────────────
TMDB_KEY = "1f8fa8b836a3910ccd29fea45cb207d2"

class MovieEnricher:
    BASE_URL = "https://api.tmdb.org/3"

    def __init__(self):
        self.session = None  # lazy import

    def _session(self):
        if self.session is None:
            import urllib.request, urllib.parse
            self.session = (urllib.request, urllib.parse)
        return self.session

    def _fetch(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read().decode("utf-8"))

    def search_tmdb(self, query):
        urll, up = self._session()
        try:
            req = urll.Request(
                f"{self.BASE_URL}/search/movie?api_key={TMDB_KEY}"
                f"&query={up.quote(query)}&language=zh-CN",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urll.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            return results[0] if results else None
        except Exception:
            return None

    def get_tmdb(self, title):
        urll, up = self._session()
        try:
            req = urll.Request(
                f"{self.BASE_URL}/search/movie?api_key={TMDB_KEY}"
                f"&query={up.quote(title)}&language=zh-CN",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urll.urlopen(req, timeout=10) as resp:
                results = json.loads(resp.read().decode("utf-8")).get("results", [])
            if results:
                return results[0]
        except Exception:
            pass
        return None

    def _format_from_raw(self, raw):
        """将 TMDB API 原始返回转为标准 tmdb dict"""
        if not raw:
            return {}
        tmdb_id = raw.get("id", "")
        year = raw.get("release_date", "")[:4]
        genres = "/".join(g["name"] for g in raw.get("genres", []) if g.get("name"))
        return {
            "title": raw.get("title", ""),
            "year": year,
            "genres": genres,
            "rating": str(round(raw.get("vote_average", 0), 1)),
            "votes": str(raw.get("vote_count", 0)),
            "countries": "",
            "director": "",
            "actors": "",
            "overview": raw.get("overview", ""),
            "popularity": "",
            "poster_url": f"https://image.tmdb.org/t/p/w300{raw.get('poster_path','')}" if raw.get("poster_path") else "",
            "url": f"https://www.themoviedb.org/movie/{tmdb_id}" if tmdb_id else "",
        }

    def enrich(self, name):
        """Fetch TMDB data for a resource name"""
        raw = self.get_tmdb(name)
        if not raw:
            return {}
        return self._format_from_raw(raw)

    def check_info_complete(self, name, results):
        """Check if resource has TMDB data, return missing info"""
        item = None
        for r in results:
            if name in r.get("name", ""):
                item = r
                break
        if not item:
            item = results[0] if results else {}
        has_tmdb = isinstance(item.get("tmdb"), dict) and bool(item.get("tmdb", {}).get("title") or item.get("tmdb", {}).get("overview"))
        has_intro = bool(item.get("intro"))
        missing = []
        if not has_intro and not has_tmdb:
            missing.append("简介")
        if not has_tmdb:
            missing.append("TMDB数据")
        return {"complete": has_tmdb or has_intro, "missing": missing, "item": item}

    def request_feedback(self, name, missing):
        msg = f"信息补充提示：「{name}」缺少以下信息：{', '.join(missing)}"
        msg += "\n回复格式：电影名|简介|海报URL（可选）"
        msg += "\n或：电影名|tmdb标题|year|genres|rating|votes|countries|director|actors|overview|popularity|poster_url|url"
        return msg

    def apply_feedback(self, raw):
        """Parse feedback and store"""
        parts = raw.split("|")
        if len(parts) < 2:
            return False
        name = parts[0].strip()
        info = {}
        if len(parts) > 1 and parts[1].strip():
            info["intro"] = parts[1].strip()
        if len(parts) > 2 and parts[2].strip():
            if parts[2].startswith("http"):
                info["poster_url"] = parts[2].strip()
            elif "/" in parts[2] and not parts[2].startswith("http"):
                info["genres"] = parts[2].strip()
        if len(parts) > 3:
            for i, field in enumerate(["year","genres","rating","votes","countries","director","actors","overview","popularity","poster_url","url"]):
                if i+3 < len(parts) and parts[i+3].strip():
                    info[field] = parts[i+3].strip()
        if info:
            LEARN.add_feedback(name, info)
            return True
        return False


# ────────────────────────────────────────────────────────
# Singletons
# ────────────────────────────────────────────────────────
USER    = UserProfile()
LEARN   = LearningEngine()
ENRICHER = MovieEnricher()

KEY_MAP = {
    "name": "n",
    "baidu": "b",
    "tianyi": "t",
    "quark": "q",
    "xunlei": "x",
    "aliyun": "a",
    "intro": "i",
    "sheet": "s",
}


# ────────────────────────────────────────────────────────
# Data loading
# ────────────────────────────────────────────────────────
def decrypt_resources():
    from cryptography.fernet import Fernet
    with open(RES_FILE, 'rb') as f:
        encrypted = f.read()
    fernet = Fernet(_FERNET_KEY.encode('utf-8'))
    decrypted = gzip.decompress(fernet.decrypt(encrypted))
    return json.loads(decrypted.decode('utf-8'))


def load_resources():
    if not RES_FILE.exists():
        raise FileNotFoundError("未找到资源文件")
    return expand_compact_data(decrypt_resources())


def expand_compact_data(data):
    """Expand compact JSON into full resource dict"""
    key_map = {"b": "baidu", "t": "tianyi", "q": "quark", "x": "xunlei", "a": "aliyun"}
    result = []
    for item in data:
        if "n" not in item:
            result.append(item)
            continue
        entry = {
            "name": item["n"],
            "sheet": item.get("s", ""),
            "country": item.get("r", ""),
            "quality": "",  # quality从名称中提取或为空，不与q混淆
            "intro": item.get("i", ""),
        }
        for k, pan_name in key_map.items():
            if k in item:
                val = item[k]
                if isinstance(val, str):
                    entry[pan_name] = {"url": val, "code": ""}
                elif isinstance(val, dict):
                    entry[pan_name] = {"url": val.get("url",""), "code": val.get("code","")}
        # 处理tc字段（天翼访问码）
        if "tc" in item and "tianyi" in entry:
            entry["tianyi"]["code"] = item["tc"]
        # TMDB
        if "tmdb" in item and isinstance(item["tmdb"], dict):
            entry["tmdb"] = item["tmdb"]
        result.append(entry)
    return result


# ────────────────────────────────────────────────────────
# Search logic
# ────────────────────────────────────────────────────────
def parse_query(query):
    tokens = query.split()
    categories, regions, qualities, keywords = [], [], [], []
    for token in tokens:
        t = token.strip().lower()
        if not t:
            continue
        matched = False
        for cat, aliases in CAT_MAP.items():
            if t in aliases or t == cat:
                categories.append(cat); matched = True; break
        if matched: continue
        for reg, aliases in REGION_MAP.items():
            if any(a in t for a in aliases):
                regions.append(reg); matched = True; break
        if matched: continue
        for qual, aliases in QUALITY_MAP.items():
            if any(a in t for a in aliases):
                qualities.append(qual); matched = True; break
        if matched: continue
        keywords.append(token)
    return " ".join(keywords), {
        "category": list(dict.fromkeys(categories)),
        "country": list(dict.fromkeys(regions)),
        "quality": list(dict.fromkeys(qualities)),
    }


def _word_match(text, keywords):
    text = text.lower()
    return any(k.lower() in text for k in keywords)


def match_resource(res, kw, filters):
    name  = res.get("name", "").lower()
    sheet = res.get("sheet", "").lower()
    country = res.get("country", "").lower()
    quality = res.get("quality", "").lower()
    tmdb = res.get("tmdb", {})
    tmdb_title = (tmdb.get("title","") or "").lower()
    tmdb_director = (tmdb.get("director","") or "").lower()

    kw_tokens = kw.split() if kw else []
    if kw_tokens:
        if not _word_match(name, kw_tokens) and \
           not _word_match(tmdb_title, kw_tokens) and \
           not _word_match(tmdb_director, kw_tokens):
            return False

    if filters["country"]:
        if country and not any(r in country for r in filters["country"]):
            return False

    if filters["quality"]:
        combined = f"{quality} {name}"
        if not any(q.lower() in combined for q in filters["quality"]):
            return False

    if filters["category"]:
        if not any(c in sheet for c in filters["category"]):
            if "原盘" in filters["category"] and "原盘" not in sheet:
                return False

    return True


def normalize_name(name):
    n = re.sub(r'\.更新\d+集?$', '', name)
    n = re.sub(r'\.\[\d+\.?\d*GB\]$', '', n)
    return n.strip()


def extract_episode(name):
    m = re.search(r'更新(\d+)集?$', name)
    return int(m.group(1)) if m else 0


def search_resources(query):
    try:
        data = load_resources()
    except Exception as e:
        return [], f"加载资源失败: {e}"

    kw, filters = parse_query(query)

    if not kw and not any(filters.values()):
        return [], "请输入搜索词"

    results = [r for r in data if match_resource(r, kw, filters)]
    if not results:
        return [], f"未找到「{query}」相关结果"

    # Deduplicate by normalized name
    unique = {}
    for r in results:
        key = normalize_name(r.get("name",""))
        ep = extract_episode(r.get("name",""))
        if key not in unique or ep > extract_episode(unique[key].get("name","")):
            unique[key] = r

    return list(unique.values())[:MAX_RESULTS], None


# ────────────────────────────────────────────────────────
# Link helpers
# ────────────────────────────────────────────────────────
def is_valid_link(url):
    if not url:
        return False
    bad = ["subscrip/index.html","content.21cn.com/h5/subscrip","/pages/own-home/index"]
    return not any(p in url for p in bad)


def format_link(url, code, pan_type):
    if not code:
        return url
    code = code.strip()
    url = re.sub(r'（访问码[：:][^）]+）', '', url)
    url = re.sub(r'访问码[：:]\s*\w+', '', url).strip()

    if "cloud.189.cn" in url:
        if "/t/" in url:
            return f"{url}{'&' if '?' in url else '?'}accessCode={code}" if "accessCode=" not in url else url
        return f"{url}{'&' if '?' in url else '?'}accessCode={code}"

    if "pan.baidu.com" in url:
        return f"{url}{'&' if '?' in url else '?'}pwd={code}" if "pwd=" not in url else url

    if "pan.xunlei.com" in url:
        return f"{url}{'&' if '?' in url else '?'}pwd={code}" if "pwd=" not in url else url

    return f"{url}?pwd={code}"


# ────────────────────────────────────────────────────────
# TMDB display
# ────────────────────────────────────────────────────────
def _format_tmdb_block(tmdb):
    lines = []
    if not isinstance(tmdb, dict):
        return lines

    title = tmdb.get("title","")
    year = tmdb.get("year","")
    genres = tmdb.get("genres","")
    rating = tmdb.get("rating","")
    votes = tmdb.get("votes","")
    countries = tmdb.get("countries","")
    director = tmdb.get("director","")
    actors = tmdb.get("actors","")
    overview = tmdb.get("overview","")
    popularity = tmdb.get("popularity","")
    tmdb_url = tmdb.get("url","")

    # 简介行
    intro_parts = []
    if year: intro_parts.append(year)
    if genres: intro_parts.append(genres)
    if rating: intro_parts.append(f"★{rating}")
    if votes: intro_parts.append(f"{int(votes):,}人评分")
    if countries: intro_parts.append(countries)
    if intro_parts:
        lines.append(f"   简介：{' | '.join(intro_parts)}")

    # 导演+演员+热度
    meta_parts = []
    if director: meta_parts.append(f"导演：{director}")
    if actors: meta_parts.append(f"主演：{actors}")
    if popularity: meta_parts.append(f"[热门]{popularity}")
    if meta_parts:
        lines.append("   " + " | ".join(meta_parts))

    # 剧情行：链接指向TMDB详情页
    if overview:
        if tmdb_url:
            lines.append(f"   剧情：[点击查看 TMDB 详情]({tmdb_url})")
        else:
            lines.append(f"   剧情：{overview}")
    elif not overview and tmdb_url:
        lines.append(f"   信息：{tmdb_url}")

    return lines


# ────────────────────────────────────────────────────────
# Results formatter
# ────────────────────────────────────────────────────────
def format_results(results, compact=False, query=""):
    lines = [f"[资源] 共找到 {len(results)} 条资源：\n"]

    # ── 先 enrich 第一条结果（如果没有 TMDB 数据）──
    feedback_prompt = ""
    if results:
        first = results[0]
        first_name = first.get("name","")
        if not first.get("tmdb"):
            try:
                # 提取中文片名：找第一个【】之后或直接的中文序列
                m = re.search(r'】\s*([\u4e00-\u9fff]{2,})', first_name)
                if not m:
                    m = re.search(r'([\u4e00-\u9fff]{2,})', first_name)
                clean = m.group(1).strip() if m else first_name
                # 去掉尾部括号年份 如(1972)（1994）(2024)
                clean = re.sub(r'[（(]\d{4}[)）]', '', clean).strip()
                # 去掉尾部空格
                clean = clean.rstrip()
                raw = ENRICHER.get_tmdb(clean)
                if raw:
                    tmdb_data = ENRICHER._format_from_raw(raw)
                    if tmdb_data:
                        first["tmdb"] = tmdb_data
            except Exception:
                pass
        # enrich 后再检查完整性
        if query:
            info_check = ENRICHER.check_info_complete(first_name, results)
            if not info_check["complete"]:
                feedback_prompt = ENRICHER.request_feedback(first_name, info_check["missing"])

    # ── 逐条输出结果 ──
    for i, r in enumerate(results, 1):
        name = r.get("name","")
        quality = r.get("quality","")
        country = r.get("country","")
        tmdb = r.get("tmdb",{})

        tags = " ".join(f"【{t}】" for t in [quality, country] if t)
        lines.append(f"{i}. {tags}{name}")

        # TMDB 信息块
        if isinstance(tmdb, dict) and tmdb:
            tmdb_lines = _format_tmdb_block(tmdb)
            if tmdb_lines:
                lines.extend(tmdb_lines)

        # 下载行：链接可点击，访问码明文显示在后面
        links = []
        _pan_map = [
            ("baidu",  "baidu",  "百度"),
            ("tianyi", "tianyi", "天翼"),
            ("quark",  "quark",  "夸克"),
            ("xunlei", "xunlei", "迅雷"),
            ("aliyun", "aliyun",  "阿里"),
            ("115",    "115",    "115"),
            ("123",    "123",    "123"),
        ]
        for pan_key, field, icon in _pan_map:
            pan_data = r.get(field, "")
            if isinstance(pan_data, dict):
                url, code = pan_data.get("url",""), pan_data.get("code","")
            elif isinstance(pan_data, str) and pan_data:
                url, code = pan_data, ""
            else:
                continue
            if not is_valid_link(url):
                continue

            # 从URL中提取访问码
            extracted_code = ""
            if "?pwd=" in url or "&pwd=" in url:
                m = re.search(r'[?&]pwd=(\w+)', url)
                if m:
                    extracted_code = m.group(1)
            elif "?accessCode=" in url or "&accessCode=" in url:
                m = re.search(r'[?&]accessCode=(\w+)', url)
                if m:
                    extracted_code = m.group(1)

            # 优先使用字段中的code，否则用URL提取的
            display_code = code or extracted_code

            formatted = format_link(url, display_code, pan_key)
            if display_code:
                links.append(f"[{icon}]({formatted}) 访问码：{display_code}")
            else:
                links.append(f"[{icon}]({formatted})")
        if links:
            lines.append(f"   下载：{' '.join(links)}")
        else:
            lines.append("   无链接")
        lines.append("")

    # 积分系统
    profile = USER.get_profile()
    earned_this = 0
    earned_reason = ""
    if profile.get("history"):
        top = profile["history"][0]
        earned_this = top.get("amount", 0)
        earned_reason = top.get("reason", "")

    total = profile["points"]
    level = profile.get("level", "倔强青铜Ⅰ")

    lines.append("─" * 50)
    if earned_this > 0:
        lines.append(f"[积分] 本次 +{earned_this}（{earned_reason}）| 累计 {total} 分 | 等级 {level}")
    else:
        lines.append(f"[积分] 累计 {total} 分 | 等级 {level}")
    lines.append(f"  累计搜索 {profile['searches']} 次 | 反馈 {profile['feedback']} 次 | 贡献 {profile['improvements']} 次")

    if feedback_prompt:
        lines.append(feedback_prompt)

    lines.extend([
        "[提示] 如链接失效或错误请及时反馈给作者QQ：1817694478",
        "[提示] 赠人玫瑰手留余香...福德圆满造福人间",
        "─" * 50,
    ])
    return "\n".join(lines)


# ────────────────────────────────────────────────────────
# CLI entry point
# ────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if not args:
        print("用法: python search.py <搜索词>")
        print("      python search.py --profile")
        print("      python search.py --feedback <反馈>")
        print("      python search.py --reflect")
        sys.exit(0)

    if args[0] == "--profile":
        p = USER.get_profile()
        print(f"[个人信息]")
        print(f"  积分：{p['points']} 分")
        print(f"  等级：{p['level']}（{p['color']}）")
        print(f"  搜索：{p['searches']} 次")
        print(f"  反馈：{p['feedback']} 次")
        print(f"  贡献：{p['improvements']} 次")
        if p.get("history"):
            print(f"最近记录：")
            for h in p["history"][:5]:
                print(f"  {h['ts']}  {h['reason']}  +{h['amount']}")
        return

    if args[0] == "--learn-alias" and len(args) >= 3:
        LEARN.add_alias(args[2], args[1])
        print(f"已学习别名：{args[2]} → {args[1]}")
        return

    if args[0] == "--feedback" and len(args) > 1:
        raw = " ".join(args[1:])
        if LEARN.apply_feedback(raw):
            USER.add_points(3, "反馈补充")
            USER.record_feedback()
            print(f"反馈已记录！积分 +3，当前 {USER.get_profile()['points']} 分")
        else:
            print("反馈格式错误")
        return

    if args[0] == "--improve" and len(args) > 1:
        raw = " ".join(args[1:])
        if LEARN.apply_feedback(raw):
            USER.add_points(5, "数据改进")
            USER.record_improvement()
            print(f"改进已记录！积分 +5，当前 {USER.get_profile()['points']} 分")
        else:
            print("改进格式错误")
        return

    if args[0] == "--reflect":
        print(f"[自我诊断]")
        print(f"  资源文件：{'存在' if RES_FILE.exists() else '缺失'}")
        print(f"  资源数量：{len(load_resources()) if RES_FILE.exists() else 0}")
        print(f"  学习数据：{len(LEARN.data.get('aliases',{}))} 条别名")
        p = USER.get_profile()
        print(f"  用户积分：{p['points']} 分 / {p['level']}")
        return

    query = " ".join(args)
    try:
        results, err = search_resources(query)
        if err:
            print(err)
        else:
            if results:
                USER.add_points(1, "搜索资源")
                USER.record_search()
            print(format_results(results, query=query))
    except Exception as e:
        traceback.print_exc()
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
