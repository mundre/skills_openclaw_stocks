"""
2号人事部 餐补申请自动化
"""
import os, sys, csv, re, time, argparse
from pathlib import Path
from datetime import datetime, timedelta

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # fix PowerShell GBK encoding issue for Chinese args
    for i, arg in enumerate(sys.argv):
        if isinstance(arg, str):
            # try to fix GBK double-decode issue
            try:
                arg.encode('utf-8').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                try:
                    sys.argv[i] = arg.encode('gbk', errors='replace').decode('utf-8', errors='replace')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 日期解析
def parse_natural_date(date_str):
    today = datetime.now()
    date_str = date_str.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    m = re.match(r'^(\d{4})年(\d+)月(\d+)日$', date_str)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r'^(\d+)月(\d+)日$', date_str)
    if m:
        return f"{today.year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.match(r'^(\d+)日?$', date_str)
    if m:
        return f"{today.year}-{today.month:02d}-{int(m.group(1)):02d}"
    raise ValueError(f"cannot parse: {date_str}")

# 配置
SKILL_DIR = Path(__file__).parent.parent
SHOT_DIR = SKILL_DIR / "screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)
TARGET_URL = 'https://i-wework.2haohr.com/desk/home'
LATE = "20:30"; MEAL_N = 20; MEAL_C = 40; PAGE_TMO = 60
WDMPATH = Path(os.environ.get('USERPROFILE', '')) / '.wdm'
_cands = sorted(WDMPATH.glob('drivers/chromedriver/win64/*/chromedriver-win32/chromedriver.exe')) if WDMPATH.exists() else []
CHROMEDRIVER = str(_cands[-1]) if _cands else ''

def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)

def init_driver():
    import subprocess
    def _make():
        opts = Options(); opts.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
        svc = Service(executable_path=CHROMEDRIVER) if CHROMEDRIVER else None
        return webdriver.Chrome(service=svc, options=opts)
    try:
        d = _make(); d.set_page_load_timeout(PAGE_TMO); d.implicitly_wait(3)
        log("chrome connected"); return d
    except Exception as e:
        log(f"auto-start chrome... ({e})")
        paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                 os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe")]
        for p in paths:
            if os.path.exists(p):
                subprocess.Popen([p, "--remote-debugging-port=9222",
                                  "--user-data-dir=" + os.path.expandvars(r"%TEMP%\chrome-debug-2haohr"),
                                  "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)); break
        time.sleep(5)
        d = _make(); d.set_page_load_timeout(PAGE_TMO); d.implicitly_wait(3)
        log("chrome auto-started"); return d

def safe_get(d, url):
    try: d.get(url)
    except: pass
    time.sleep(3)

def wait_login(d):
    for _ in range(200):
        try:
            if 'desk/home' in d.current_url and 'login' not in d.current_url.lower():
                if len(d.find_element(By.TAG_NAME,'body').text) > 50:
                    log("login ok"); return True
        except: pass
        time.sleep(3)
    log("login timeout"); return False

def take(d, name):
    try:
        d.execute_script("document.body.style.zoom='1';"); time.sleep(0.3)
        p = SHOT_DIR / name; d.get_screenshot_as_file(str(p)); log(f"shot: {p.name}"); return str(p)
    except: return None

def click_text(d, text):
    for xp in [f"//button[contains(text(),'{text}')]", f"//a[contains(text(),'{text}')]",
               f"//span[contains(text(),'{text}')]", f"//*[contains(text(),'{text}')]"]:
        try:
            for e in d.find_elements(By.XPATH, xp):
                if e.is_displayed() and e.is_enabled():
                    d.execute_script("arguments[0].click();", e); time.sleep(1); return True
        except: pass
    return False

def go_attendance(d):
    log("go attendance"); click_text(d, "考勤"); time.sleep(3)
    d.execute_script("window.scrollBy(0,300)"); time.sleep(1)

def get_cal_month(d):
    for el in d.find_elements(By.CSS_SELECTOR, "span[class*='show']"):
        t = el.text.strip()
        if '/' in t and len(t) <= 10: return t
    for el in d.find_elements(By.CSS_SELECTOR, "[class*='dateSwitch']"):
        m = re.search(r'(\d{4}/\d{2})', el.text)
        if m: return m.group(1)
    return ""

def go_month(d, yr, mo):
    tgt = f"{yr}/{int(mo):02d}"
    for _ in range(20):
        if get_cal_month(d) == tgt: return True
        try:
            for sel in ["span[class*='left']","i[class*='arrow-left']","span[class*='prev']"]:
                for btn in d.find_elements(By.CSS_SELECTOR, sel):
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click(); time.sleep(1.5)
                        if get_cal_month(d) == tgt: log(f"cal: {tgt}"); return True; break
        except: pass
        time.sleep(1)
    log(f"cal stuck at {get_cal_month(d)}"); return False

def read_record(d, yr, mo, day):
    go_month(d, yr, mo); time.sleep(2)
    d.switch_to.default_content()
    take(d, f"att_{yr}{int(mo):02d}{int(day):02d}.png")
    cells = d.find_elements(By.CSS_SELECTOR, "[class*='Cell_']")
    log(f"  cells={len(cells)} find={mo}/{day}")
    for cell in cells:
        try:
            txt = cell.text.strip()
            if not txt: continue
            m = re.search(r'(\d+)月(\d+)日', txt)
            cd = int(m.group(2)) if m else int(re.sub(r'\D','', txt.split('\n')[0])) if txt.split('\n') else -1
            if cd != day: continue
            times = re.findall(r'\d{1,2}:\d{2}', txt)
            off = times[-1] if times else None
            if off:
                log(f"  {yr}-{int(mo):02d}-{int(day):02d} off={off}")
                return f"{yr}-{int(mo):02d}-{int(day):02d}", off
        except: pass
    log(f"  not found {mo}/{day}"); return None

def pmin(t): return int(t.split(':')[0])*60 + int(t.split(':')[1])
def iscross(t): return 0 <= pmin(t) < 360
def ge(t1,t2): return pmin(t1) >= pmin(t2)

def go_meal_form(d):
    safe_get(d, TARGET_URL); time.sleep(5)
    log("click approval"); click_text(d, "审批"); time.sleep(3)
    log("click meal"); click_text(d, "餐补"); time.sleep(5)
    try:
        whs = d.window_handles
        if len(whs) > 1:
            d.switch_to.window(whs[-1])
    except: pass
    take(d, "meal_form.png")

def js_picker(d, idx, val):
    js = f"var pks=document.querySelectorAll('.ivu-date-picker');if(pks.length>{idx}){{var inp=pks[{idx}].querySelector('input');if(inp){{var s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;s.call(inp,'{val}');inp.dispatchEvent(new Event('input',{{bubbles:true}}));inp.dispatchEvent(new Event('change',{{bubbles:true}}));return'ok';}}}}return'fail';"
    try:
        r = d.execute_script(js); log(f"  picker[{idx}]={val}: {r}"); return r == 'ok'
    except Exception as e: log(f"  picker err: {e}"); return False

def upload(d, path):
    if not os.path.exists(path): log(f"file not found: {path}"); return False
    for inp in d.find_elements(By.CSS_SELECTOR, "input[type='file']"):
        try:
            d.execute_script("arguments[0].style.display='block';arguments[0].style.visibility='visible';arguments[0].style.opacity='1';arguments[0].style.position='fixed';arguments[0].style.top='0';arguments[0].style.left='0';arguments[0].style.zIndex='99999';", inp)
            time.sleep(0.5); inp.send_keys(path); time.sleep(2); log(f"  upload ok"); return True
        except Exception as e: log(f"  upload fail: {e}")
    return False

def submit(d):
    log("submit"); take(d, "meal_before_submit.png")
    for kw in ["提交"]:
        for xp in [f"//button[contains(text(),'{kw}')]", f"//span[contains(text(),'{kw}')]"]:
            try:
                for e in d.find_elements(By.XPATH, xp):
                    if e.is_displayed() and e.is_enabled():
                        d.execute_script("arguments[0].click();", e); log(f"  submit ok"); time.sleep(2); take(d, "after_submit.png"); return True
            except: pass
    log("submit btn not found"); return False

def fill(d, records, att):
    log(f"fill {len(records)} record(s)"); take(d, "meal_form.png")
    try: d.switch_to.default_content()
    except: pass
    for i, (ds, off) in enumerate(records):
        cross = iscross(off)
        end_d = datetime.strptime(ds, "%Y-%m-%d") + timedelta(days=1) if cross else datetime.strptime(ds, "%Y-%m-%d")
        end_ds = end_d.strftime("%Y-%m-%d")
        tag = "[X]" if cross else "[/]"
        log(f"  {tag} {ds} 18:00->{end_ds} {off} yuan={MEAL_C if cross else MEAL_N}")
        js_picker(d, 0, f"{ds} 18:00"); time.sleep(1)
        js_picker(d, 1, f"{end_ds} {off}"); time.sleep(1)
        if att and os.path.exists(att): upload(d, att)
        time.sleep(1); take(d, f"meal_fill_{i}.png")
    submit(d)

def savecsv(records):
    if not records: return None
    p = SHOT_DIR / f"late_{datetime.now().strftime('%Y%m')}.csv"
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["date","off","cross","yuan"])
        for d,t in records:
            c=iscross(t); w.writerow([d,t,c,MEAL_C if c else MEAL_N])
    log(f"csv: {p}"); return str(p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["weekly","date","month"], default="date")
    ap.add_argument("--date", default=None)
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--month", type=int, default=None)
    args = ap.parse_args()
    driver = None
    try:
        driver = init_driver(); time.sleep(2)
        safe_get(driver, TARGET_URL)
        if not wait_login(driver): sys.exit(1)
        go_attendance(driver)

        if args.mode == "month":
            import calendar as _c
            today = datetime.now()
            yr = args.year or (today.year if today.month > 1 else today.year - 1)
            mo = args.month or (today.month - 1 if today.month > 1 else 12)
            log(f"=== {yr}/{mo} month ===")
            _, ld = _c.monthrange(yr, mo)
            ot = []
            for day in range(1, ld+1):
                dd = datetime(yr, mo, day)
                if dd.date() > today.date(): break
                rec = read_record(driver, yr, mo, day)
                if rec and (ge(rec[1], LATE) or iscross(rec[1])):
                    ot.append(rec); tag="[X]" if iscross(rec[1]) else "[/]"; log(f"  {tag} {rec[0]} off={rec[1]}")
                else: reason="no_rec" if not rec else f"off={rec[1]}"; log(f"  [SKIP] {yr}-{mo:02d}-{day:02d} {reason}")
            log(f"=== found {len(ot)} ===")
            if not ot: log("none, exit"); sys.exit(0)
            csv_p = savecsv(ot)
            for i,(ds,off) in enumerate(ot):
                att = str(SHOT_DIR / f"att_{ds.replace('-','')}.png")
                log(f"--- [{i+1}/{len(ot)}] {ds} ---")
                go_meal_form(driver); fill(driver, [(ds,off)], att); time.sleep(2)
            log(f"=== done {len(ot)} ==="); sys.exit(0)

        elif args.mode == "date":
            if args.date:
                ds = args.date  # YYYY-MM-DD 格式
            else:
                d = datetime.now() - timedelta(days=1); ds = d.strftime("%Y-%m-%d")
            log(f"query: {ds}")
            dt = datetime.strptime(ds, "%Y-%m-%d")
            rec = read_record(driver, dt.year, dt.month, dt.day)
            if rec and (ge(rec[1], LATE) or iscross(rec[1])):
                records = [rec]
            elif rec:
                log(f"[no apply] {ds} off={rec[1]} < {LATE}, skip"); records = []
            else:
                log(f"[no apply] {ds} no record, skip"); records = []
        else:
            records = []
            mon = datetime.now() - timedelta(days=datetime.now().weekday())
            for i in range(7):
                dd = mon + timedelta(days=i)
                if dd.date() > datetime.now().date(): break
                rec = read_record(driver, dd.year, dd.month, dd.day)
                if rec and (ge(rec[1], LATE) or iscross(rec[1])):
                    records.append(rec); log(f"  ok {dd.strftime('%Y-%m-%d')} {rec[1]}")
            log(f"weekly: {len(records)}")

        if not records: log("no records, exit"); sys.exit(0)
        csv_p = savecsv(records)
        att_shot = str(SHOT_DIR / f"att_{records[0][0].replace('-','')}.png")
        go_meal_form(driver); fill(driver, records, att_shot)
        log(f"=== done {len(records)} ===")

    except KeyboardInterrupt: log("break")
    except Exception as e:
        log(f"ERR: {e}"); import traceback; traceback.print_exc()
        if driver: take(driver, "error.png")
    finally:
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    main()
