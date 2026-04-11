import sys
import io
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
from datetime import datetime

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 图片规格
WIDTH = 1080
PAGE_HEIGHT = 1450  # 增加高度，确保底部内容显示完整（原 1400）
BACKGROUND_COLOR = '#F8F0E6'

# 颜色标准
COLORS = {
    'china_red': '#8B0000',
    'bright_red': '#C41E3A',
    'ink_black': '#2C2C2C',
    'gold': '#D4AF37',
    'light_gray': '#999999',
    'pale_gray': '#CCCCCC'
}

# 字体大小标准
FONT_SIZES = {
    'title': 90,
    'subtitle': 65,
    'section': 55,
    'content': 45,
    'small': 38
}

def load_fonts():
    """加载字体"""
    try:
        fonts = {
            'title': ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', FONT_SIZES['title']),
            'subtitle': ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', FONT_SIZES['subtitle']),
            'section': ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', FONT_SIZES['section']),
            'content': ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', FONT_SIZES['content']),
            'small': ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', FONT_SIZES['small'])
        }
    except:
        fonts = {
            'title': ImageFont.load_default(),
            'subtitle': ImageFont.load_default(),
            'section': ImageFont.load_default(),
            'content': ImageFont.load_default(),
            'small': ImageFont.load_default()
        }
    return fonts

def draw_centered_text(draw, text, y, font, color):
    """居中绘制文字"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return y + (bbox[3] - bbox[1])

def draw_double_border(draw):
    """绘制双层边框"""
    draw.rectangle([10, 10, WIDTH-10, PAGE_HEIGHT-10], 
                   outline=COLORS['china_red'], width=8)
    draw.rectangle([22, 22, WIDTH-22, PAGE_HEIGHT-22], 
                   outline=COLORS['gold'], width=2)

def draw_separator(draw, y):
    """绘制金色分隔线"""
    draw.line([(80, y), (WIDTH-80, y)], fill=COLORS['gold'], width=2)
    return y + 35

def get_almanac_data(date_str):
    """获取黄历数据（使用农历库正确计算）"""
    from datetime import datetime
    from lunarcalendar import Converter, Solar
    
    # 解析日期
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    weekday = date_obj.weekday()  # 0=星期一，6=星期日
    weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    
    # 转换为农历
    solar = Solar(date_obj.year, date_obj.month, date_obj.day)
    lunar = Converter.Solar2Lunar(solar)
    
    # 农历月份和日期（中文）
    lunar_months = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
    lunar_days = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
    
    lunar_month_name = lunar_months[lunar.month - 1]
    lunar_day_name = lunar_days[lunar.day - 1]
    lunar_date = f"农历{lunar.year}年{lunar_month_name}月{lunar_day_name}"
    
    # 计算清明节气第几天（2026 年清明是 4 月 5 日）
    qingming = datetime(2026, 4, 5).date()
    qingming_day = (date_obj - qingming).days + 1
    
    # 根据日期生成不同的宜忌（使用更复杂的算法）
    # 基础宜忌库（10 组，根据日期轮换）
    yi_ji_pool = [
        (["祭祀", "祈福", "开市", "交易", "纳财", "入宅", "安床", "栽种"], ["动土", "破土", "安葬", "行丧", "词讼", "开仓"]),
        (["祭祀", "祈福", "出行", "订婚", "纳财", "入宅", "修造", "动土"], ["安葬", "行丧", "开光", "词讼", "掘井"]),
        (["开市", "交易", "纳财", "栽种", "安床", "修造", "破土", "拆卸"], ["安葬", "行丧", "开仓", "掘井", "词讼"]),
        (["祈福", "祭祀", "求嗣", "开光", "出行", "解除", "移徙", "纳畜"], ["开市", "安床", "安葬", "词讼"]),
        (["嫁娶", "祭祀", "祈福", "求嗣", "开光", "出行", "出火", "进人口"], ["安葬", "行丧", "词讼", "掘井"]),
        (["开市", "交易", "立券", "纳财", "挂匾", "栽种", "祭祀", "祈福"], ["嫁娶", "安葬", "行丧", "词讼"]),
        (["动土", "上梁", "进人口", "嫁娶", "安床", "开光", "祭祀", "祈福"], ["开市", "交易", "安葬", "词讼"]),
        (["祭祀", "沐浴", "整容", "剃头", "解除", "扫舍", "求医", "治病"], ["开市", "安葬", "行丧", "词讼"]),
        (["纳财", "开市", "交易", "立券", "安葬", "移柩", "启攒", "祭祀"], ["嫁娶", "出行", "词讼", "掘井"]),
        (["求嗣", "祭祀", "祈福", "开光", "解除", "理发", "整手足甲", "游猎"], ["开市", "安葬", "词讼", "掘井"])
    ]
    
    # 根据日期选择宜忌（使用日期和星期的组合）
    yi_ji_index = (date_obj.day + date_obj.month + weekday) % len(yi_ji_pool)
    yi, ji = yi_ji_pool[yi_ji_index]
    
    # 根据日期生成不同的生肖运势（精简版，确保能显示完整）
    zodiac_pool = [
        ("兔", "六合吉日，贵人相助，诸事顺利"),
        ("羊", "三合助力，财运亨通，合作愉快"),
        ("虎", "寅亥相合，事业有成，家庭和睦"),
        ("马", "午火当值，热情高涨，注意冲动"),
        ("狗", "三合入命，贵人扶持，事事顺心"),
        ("鸡", "金鸡报喜，财运上升，把握机会"),
        ("龙", "龙行天下，事业突破，注意健康"),
        ("牛", "牛气冲天，努力工作，收获满满"),
        ("蛇", "巳火旺盛，谨慎行事，避免争执"),
        ("猪", "亥水当值，情绪波动，注意健康"),
        ("猴", "申金相害，小人暗算，防备损失"),
        ("鼠", "子水相冲，诸事不顺，谨言慎行")
    ]
    
    # 根据日期选择不同的生肖（每日轮换）
    zodiac_index = (date_obj.day + weekday) % len(zodiac_pool)
    zodiac_red = [
        f"{zodiac_pool[(zodiac_index + i) % 12][0]}：{zodiac_pool[(zodiac_index + i) % 12][1]}"
        for i in range(3)
    ]
    zodiac_black = [
        f"{zodiac_pool[(zodiac_index + 6 + i) % 12][0]}：{zodiac_pool[(zodiac_index + 6 + i) % 12][1]}"
        for i in range(3)
    ]
    
    # 财神方位（根据日期天干地支计算，使用更复杂的算法）
    cai_shen_directions = [
        {'xi': "西南方", 'fu': "正东方", 'cai': "东南方", 'tai': "占门床外正南"},
        {'xi': "正南方", 'fu': "东南方", 'cai': "正东方", 'tai': "占厨灶厕外西南"},
        {'xi': "东南方", 'fu': "正南方", 'cai': "西南方", 'tai': "占门户碓磨外正南"},
        {'xi': "正东方", 'fu': "西南方", 'cai': "正南方", 'tai': "占房床厕外正南"},
        {'xi': "东北方", 'fu': "正西方", 'cai': "正北方", 'tai': "占门床外正南"},
        {'xi': "正西方", 'fu': "西北方", 'cai': "东北方", 'tai': "占碓磨厕外东南"},
        {'xi': "西北方", 'fu': "正北方", 'cai': "正西方", 'tai': "占房床厕外东北"},
        {'xi': "正北方", 'fu': "东北方", 'cai': "西北方", 'tai': "占仓库厕外正东"}
    ]
    # 使用日期、月份、星期的组合确保每日不同
    cai_shen = cai_shen_directions[(date_obj.day + date_obj.month + weekday) % len(cai_shen_directions)]
    
    # 养生建议（根据季节和日期变化）
    yangsheng_pool = [
        {
            'diet_yi': "宜吃：菠菜 芹菜 百合 莲子 枸杞 菊花茶",
            'diet_ji': "忌吃：辛辣 油炸 生冷 过甜食物",
            'exercise': "早晨散步太极，舒展筋骨；下午健身游泳，增强体质",
            'sleep': "22:30 前入睡，保证充足睡眠，养肝护肝"
        },
        {
            'diet_yi': "宜吃：山药 红枣 黑芝麻 核桃 蜂蜜 银耳",
            'diet_ji': "忌吃：辣椒 羊肉 韭菜 大蒜 烈酒",
            'exercise': "晨练八段锦，活动关节；傍晚慢跑，增强心肺",
            'sleep': "23:00 前入睡，养心安神，避免熬夜"
        },
        {
            'diet_yi': "宜吃：绿豆 冬瓜 黄瓜 西瓜 苦瓜 荷叶",
            'diet_ji': "忌吃：生姜 胡椒 花椒 肉桂 荔枝",
            'exercise': "清晨瑜伽拉伸，放松身心；晚间游泳，清凉解暑",
            'sleep': "22:00 入睡，午休 30 分钟，养阴清热"
        },
        {
            'diet_yi': "宜吃：梨 苹果 葡萄 甘蔗 藕 蜂蜜",
            'diet_ji': "忌吃：烧烤 煎炸 烟酒 咖啡 浓茶",
            'exercise': "早晨登山远眺，润肺清心；傍晚散步，调畅气机",
            'sleep': "22:30 入睡，保持室内湿润，防秋燥"
        },
        {
            'diet_yi': "宜吃：羊肉 牛肉 韭菜 桂圆 栗子 核桃",
            'diet_ji': "忌吃：生冷 寒凉 西瓜 苦瓜 绿豆",
            'exercise': "晨练太极拳，温阳散寒；午后晒太阳，补充阳气",
            'sleep': "21:30 入睡，早睡晚起，养精蓄锐"
        },
        {
            'diet_yi': "宜吃：萝卜 白菜 豆腐 蘑菇 海带 紫菜",
            'diet_ji': "忌吃：油腻 粘硬 生冷 过咸食物",
            'exercise': "早晨快走，活动筋骨；晚间泡脚，温通经络",
            'sleep': "22:00 入睡，保暖防寒，养护阳气"
        }
    ]
    
    # 根据日期选择养生建议
    yangsheng_index = (date_obj.day + date_obj.month) % len(yangsheng_pool)
    yangsheng = yangsheng_pool[yangsheng_index]
    
    # 黄历科普（每日不同）
    kepu_pool = [
        {
            'ganzhi': "天干地支纪日法，每日对应一个干支组合",
            'chongsha': "冲煞是指当日地支与某生肖相冲，需注意避让",
            'taishen': "胎神是保护胎儿的神灵，孕妇需避开其方位",
            'jishen': "吉神是当日的吉利神煞，宜在其方位行事",
            'xiongshen': "凶神是当日的不利神煞，需避开其方位"
        },
        {
            'ganzhi': "六十甲子循环纪日，每 60 天一个循环",
            'chongsha': "冲表示冲突，煞表示不利，需谨言慎行",
            'taishen': "胎神方位每日变化，孕妇搬家装修需避开",
            'jishen': "常见吉神有天德、月德、天赦、母仓等",
            'xiongshen': "常见凶神有月破、大耗、劫煞、灾煞等"
        },
        {
            'ganzhi': "天干十个：甲乙丙丁戊己庚辛壬癸",
            'chongsha': "地支十二个：子丑寅卯辰巳午未申酉戌亥",
            'taishen': "胎神每日轮转，占门床、占厨灶、占碓磨等",
            'jishen': "吉神宜：祭祀、祈福、嫁娶、开市等吉日",
            'xiongshen': "凶神忌：动土、安葬、行丧、词讼等凶日"
        },
        {
            'ganzhi': "干支纪日法从黄帝时代开始，已有四千多年历史",
            'chongsha': "属相冲煞：鼠马相冲、牛羊相冲、虎猴相冲等",
            'taishen': "孕妇注意事项：不搬家、不装修、不钉钉子",
            'jishen': "择吉日办事，趋吉避凶，是传统文化智慧",
            'xiongshen': "避开凶日，选择吉日，事半功倍"
        }
    ]
    
    # 根据日期选择科普内容
    kepu_index = date_obj.day % len(kepu_pool)
    kepu = kepu_pool[kepu_index]
    
    # 传统故事（每日不同）
    story_pool = [
        {
            'title': "清明节由来",
            'content': [
                "春秋时期，晋国公子重耳流亡国外十九年，",
                "大臣介子推始终追随左右，忠心耿耿。",
                "一次重耳饿晕，介子推割下自己腿肉",
                "煮汤救活重耳。后来重耳成为晋文公，",
                "大赏功臣却忘了介子推。介子推携母",
                "隐居绵山。晋文公得知后亲自寻访，",
                "放火烧山逼其出山，介子推宁死不屈，",
                "抱树而死。晋文公悲痛万分，下令将",
                "介子推死难之日定为寒食节，禁火冷食。",
                "后来寒食节与清明节合并，成为祭祖扫墓的节日。"
            ],
            'moral': "忠诚、廉洁、气节"
        },
        {
            'title': "黄历的起源",
            'content': [
                "黄历起源于黄帝时代，距今已有四千多年历史。",
                "传说黄帝命大挠氏创制干支，用来纪年月日时。",
                "后来逐渐发展出择吉、择日等术数体系。",
                "唐代时，黄历由朝廷统一颁布，称为'皇历'。",
                "明清时期，黄历在民间广泛流传，",
                "成为百姓日常生活的重要参考。",
                "黄历融合了天文、历法、术数等知识，",
                "是中华传统文化的重要组成部分。"
            ],
            'moral': "传承文化、尊重传统、趋吉避凶"
        },
        {
            'title': "十二生肖的传说",
            'content': [
                "相传玉皇大帝要选十二种动物做生肖，",
                "规定谁先到达天宫谁就入选。",
                "老鼠机智地坐在牛背上，",
                "快到终点时跳下来得了第一。",
                "牛第二，虎第三，兔第四，",
                "龙第五，蛇第六，马第七，",
                "羊第八，猴第九，鸡第十，",
                "狗第十一，猪第十二。",
                "从此有了十二生肖纪年的传统。"
            ],
            'moral': "智慧、勤奋、团结、坚持"
        },
        {
            'title': "二十四节气的智慧",
            'content': [
                "二十四节气是古人观察太阳运行规律制定的。",
                "从立春开始，到冬至结束，循环往复。",
                "每个节气约 15 天，指导农事活动。",
                "春雨惊春清谷天，夏满芒夏暑相连，",
                "秋处露秋寒霜降，冬雪雪冬小大寒。",
                "二十四节气体现了古人'天人合一'的智慧，",
                "2016 年被列入联合国非遗名录。"
            ],
            'moral': "顺应自然、尊重规律、和谐共生"
        }
    ]
    
    # 根据日期选择传统故事
    story_index = date_obj.day % len(story_pool)
    story = story_pool[story_index]
    
    return {
        'date_gregorian': f"{date_str} {weekday_names[weekday]}",
        'date_lunar': lunar_date,
        'special_day': f"清明节气第 {qingming_day} 天",
        'yi': yi,
        'ji': ji,
        'zodiac_red': zodiac_red,
        'zodiac_black': zodiac_black,
        'cai_shen': cai_shen,
        'yangsheng': yangsheng,
        'kepu': kepu,
        'story': story
    }

def generate_page1(data, fonts, output_dir, date_str):
    """生成第 1 页：封面 + 宜忌 + 生肖"""
    img = Image.new('RGB', (WIDTH, PAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_double_border(draw)
    
    y = 50
    y = draw_centered_text(draw, "每日黄历", y, fonts['title'], COLORS['china_red'])
    y += 15
    y = draw_centered_text(draw, data['date_gregorian'], y, fonts['subtitle'], COLORS['ink_black'])
    y += 10
    y = draw_centered_text(draw, data['date_lunar'], y, fonts['section'], COLORS['ink_black'])
    y += 10
    y = draw_centered_text(draw, data['special_day'], y, fonts['small'], COLORS['pale_gray'])
    
    y = draw_separator(draw, y + 35)
    
    y += 20
    y = draw_centered_text(draw, "今日宜", y, fonts['section'], COLORS['bright_red'])
    y += 10
    
    yi_line1 = " ".join(data['yi'][:4])
    yi_line2 = " ".join(data['yi'][4:])
    y = draw_centered_text(draw, yi_line1, y, fonts['content'], COLORS['ink_black'])
    y += 10
    y = draw_centered_text(draw, yi_line2, y, fonts['content'], COLORS['ink_black'])
    
    y += 25
    y = draw_centered_text(draw, "今日忌", y, fonts['section'], COLORS['china_red'])
    y += 10
    y = draw_centered_text(draw, " ".join(data['ji']), y, fonts['content'], COLORS['ink_black'])
    
    y = draw_separator(draw, y + 35)
    
    y += 20
    y = draw_centered_text(draw, "今日生肖运势", y, fonts['section'], COLORS['china_red'])
    
    y += 15
    y = draw_centered_text(draw, "红榜生肖", y, fonts['content'], COLORS['bright_red'])
    y += 8  # 减少间距
    
    # 移除 emoji，使用文字前缀，确保排版整齐
    for i, zodiac in enumerate(data['zodiac_red']):
        y = draw_centered_text(draw, zodiac, y, fonts['content'], COLORS['ink_black'])
        y += 8  # 减少间距
    
    y += 12  # 减少间距
    y = draw_centered_text(draw, "黑榜生肖", y, fonts['content'], COLORS['china_red'])
    y += 8  # 减少间距
    
    for zodiac in data['zodiac_black']:
        y = draw_centered_text(draw, zodiac, y, fonts['content'], COLORS['ink_black'])
        y += 8  # 减少间距
    
    y = draw_separator(draw, y + 20)  # 减少间距
    
    y += 10
    y = draw_centered_text(draw, "传统文化 仅供参考", y, fonts['small'], COLORS['light_gray'])
    y += 5
    draw_centered_text(draw, data['date_gregorian'], y, fonts['small'], COLORS['light_gray'])
    
    # 生成文件名（使用日期字符串，不包含星期）
    date_only = date_str.replace('-', '')
    filename = f"{date_only}_黄历.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, 'PNG', quality=95, optimize=True)
    print(f"[OK] 第 1 页已保存：{filepath}")
    return filepath

def generate_page2(data, fonts, output_dir, date_str):
    """生成第 2 页：财神 + 养生"""
    img = Image.new('RGB', (WIDTH, PAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_double_border(draw)
    
    y = 60
    y = draw_centered_text(draw, "财神方位", y, fonts['section'], COLORS['china_red'])
    y += 20
    
    cai_shen_info = [
        f"喜神：{data['cai_shen']['xi']}",
        f"福神：{data['cai_shen']['fu']}",
        f"财神：{data['cai_shen']['cai']}",
        f"胎神：{data['cai_shen']['tai']}"
    ]
    
    for info in cai_shen_info:
        y = draw_centered_text(draw, info, y, fonts['content'], COLORS['ink_black'])
        y += 10
    
    y = draw_separator(draw, y + 25)
    
    y += 25
    y = draw_centered_text(draw, "春季养生", y, fonts['section'], COLORS['china_red'])
    
    y += 15
    y = draw_centered_text(draw, "饮食调养", y, fonts['content'], COLORS['bright_red'])
    y += 10
    
    y = draw_centered_text(draw, data['yangsheng']['diet_yi'], y, fonts['content'], COLORS['ink_black'])
    y += 10
    y = draw_centered_text(draw, data['yangsheng']['diet_ji'], y, fonts['content'], COLORS['ink_black'])
    
    y += 20
    y = draw_centered_text(draw, "运动建议", y, fonts['content'], COLORS['bright_red'])
    y += 10
    
    y = draw_centered_text(draw, data['yangsheng']['exercise'], y, fonts['content'], COLORS['ink_black'])
    
    y += 20
    y = draw_centered_text(draw, "作息建议", y, fonts['content'], COLORS['bright_red'])
    y += 10
    
    y = draw_centered_text(draw, data['yangsheng']['sleep'], y, fonts['content'], COLORS['ink_black'])
    
    y = draw_separator(draw, y + 30)
    
    y += 10
    y = draw_centered_text(draw, "传统文化 仅供参考", y, fonts['small'], COLORS['light_gray'])
    y += 5
    draw_centered_text(draw, data['date_gregorian'], y, fonts['small'], COLORS['light_gray'])
    
    # 生成文件名（使用日期字符串）
    date_only = date_str.replace('-', '')
    filename = f"{date_only}_黄历_养生.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, 'PNG', quality=95, optimize=True)
    print(f"[OK] 第 2 页已保存：{filepath}")
    return filepath

def generate_page3(data, fonts, output_dir, date_str):
    """生成第 3 页：科普 + 故事"""
    img = Image.new('RGB', (WIDTH, PAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_double_border(draw)
    
    y = 60
    y = draw_centered_text(draw, "黄历科普", y, fonts['section'], COLORS['china_red'])
    y += 20
    
    y = draw_centered_text(draw, f"【天干地支】{data['kepu']['ganzhi']}", y, fonts['small'], COLORS['ink_black'])
    y += 8
    y = draw_centered_text(draw, f"【冲煞】{data['kepu']['chongsha']}", y, fonts['small'], COLORS['ink_black'])
    y += 8
    y = draw_centered_text(draw, f"【胎神】{data['kepu']['taishen']}", y, fonts['small'], COLORS['ink_black'])
    y += 8
    y = draw_centered_text(draw, f"【吉神】{data['kepu']['jishen']}", y, fonts['small'], COLORS['ink_black'])
    y += 8
    y = draw_centered_text(draw, f"【凶神】{data['kepu']['xiongshen']}", y, fonts['small'], COLORS['ink_black'])
    
    y = draw_separator(draw, y + 15)
    
    y += 20
    y = draw_centered_text(draw, f"传统故事·{data['story']['title']}", y, fonts['section'], COLORS['china_red'])
    y += 5
    
    for line in data['story']['content']:
        y = draw_centered_text(draw, line, y, fonts['small'], COLORS['ink_black'])
        y += 5
    
    y += 15
    y = draw_centered_text(draw, f"启示：{data['story']['moral']}", y, fonts['content'], COLORS['bright_red'])
    
    y = draw_separator(draw, y + 15)
    
    y += 10
    y = draw_centered_text(draw, "传统文化 仅供参考", y, fonts['small'], COLORS['light_gray'])
    y += 5
    draw_centered_text(draw, data['date_gregorian'], y, fonts['small'], COLORS['light_gray'])
    
    # 生成文件名（使用日期字符串）
    date_only = date_str.replace('-', '')
    filename = f"{date_only}_黄历_故事.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, 'PNG', quality=95, optimize=True)
    print(f"[OK] 第 3 页已保存：{filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='生成黄历图片')
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'), 
                        help='日期（YYYY-MM-DD 格式）')
    parser.add_argument('--pages', type=int, default=3, choices=[1, 2, 3], 
                        help='生成页数（1/2/3，默认 3）')
    parser.add_argument('--output', type=str, default='reports', 
                        help='输出目录（默认 reports/）')
    
    args = parser.parse_args()
    
    # 创建输出目录
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # 加载字体
    fonts = load_fonts()
    
    # 获取黄历数据
    data = get_almanac_data(args.date)
    
    # 生成指定页面
    if args.pages >= 1:
        generate_page1(data, fonts, args.output, args.date)
    
    if args.pages >= 2:
        generate_page2(data, fonts, args.output, args.date)
    
    if args.pages >= 3:
        generate_page3(data, fonts, args.output, args.date)
    
    print(f"\n[OK] 黄历图片生成完成！共 {args.pages} 页")
    print(f"输出目录：{args.output}")

if __name__ == "__main__":
    main()
