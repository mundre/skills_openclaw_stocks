"""
2号人事部 餐补申请 - 整月模式
用法: python meal_month.py 2026 3
"""
import sys, os, csv, re, time, calendar
from pathlib import Path
from datetime import datetime, timedelta

# 直接复用 meal_subsidy.py 的所有函数和配置
sys.path.insert(0, str(Path(__file__).parent))
exec(open(Path(__file__).parent / "meal_subsidy.py", encoding='utf-8').read().split('if __name__')[0])

def main():
    if len(sys.argv) >= 3:
        year, month = int(sys.argv[1]), int(sys.argv[2])
    else:
        today = datetime.now()
        year, month = today.year, today.month - 1
        if month == 0: year, month = year - 1, 12

    log(f"=== {year}年{month}月 整月模式 ===")
    driver = None
    try:
        driver = init_driver()
        time.sleep(2)
        safe_get(driver, TARGET_URL)
        if not wait_login(driver):
            sys.exit(1)

        go_attendance(driver)

        _, last_day = calendar.monthrange(year, month)
        today = datetime.now()
        overtime_records = []

        for day in range(1, last_day + 1):
            d = datetime(year, month, day)
            if d.date() > today.date():
                break
            rec = read_record(driver, year, month, day)
            if rec and (ge(rec[1], LATE) or iscross(rec[1])):
                overtime_records.append(rec)
                tag = "[OK/X]" if iscross(rec[1]) else "[OK/]"
                log(f"  {tag} {rec[0]} off={rec[1]}")
            else:
                reason = "no_rec" if not rec else f"off={rec[1]}"
                log(f"  [SKIP] {year}-{month:02d}-{day:02d} {reason}")

        log(f"=== Found {len(overtime_records)} overtime days ===")
        if not overtime_records:
            log(f"[no apply] {year}年{month}月整月无加班记录，无需申请餐补"); sys.exit(0)

        csv_p = savecsv(overtime_records)

        for i, (ds, off) in enumerate(overtime_records):
            att_shot = str(SHOT_DIR / f"attendance_{ds.replace('-','')}.png")
            log(f"--- [{i+1}/{len(overtime_records)}] {ds} ---")
            go_meal_form(driver)
            fill(driver, [(ds, off)], att_shot)
            time.sleep(2)

        log("=" * 55)
        log(f"Done! {len(overtime_records)} meal subsidies")
        if csv_p: log(f"CSV: {csv_p}")
        log("=" * 55)

    except KeyboardInterrupt:
        log("\nUser break")
    except Exception as e:
        log(f"ERR: {e}")
        import traceback; traceback.print_exc()
        if driver: take(driver, "error.png")
    finally:
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    main()
