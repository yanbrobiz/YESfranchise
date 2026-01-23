"""
Yes!加盟 自動化排程主程式
用於 Railway 雲端部署，每天凌晨 00:01 (台北時間) 自動執行。
"""

import os
import signal
import sys
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from auto_click import run_automation, log_message
from notify import notify_success, notify_failure

# 台北時區 (UTC+8)
TZ_TAIPEI = timezone(timedelta(hours=8))


def scheduled_job():
    """排程任務：執行自動點擊"""
    log_message("排程任務觸發")
    try:
        success = run_automation(headless=True)
        if success:
            log_message("排程任務成功完成")
            notify_success()
        else:
            log_message("排程任務執行失敗")
            notify_failure("自動化執行失敗，請查看日誌了解詳情")
    except Exception as e:
        log_message(f"排程任務發生錯誤: {e}")
        notify_failure(str(e))


def run_once():
    """立即執行一次（用於測試）"""
    log_message("手動觸發執行")
    success = run_automation(headless=True)
    return success


def main():
    log_message("=" * 50)
    log_message("Yes!加盟 自動化排程服務啟動")
    log_message(f"目前時間 (台北): {datetime.now(TZ_TAIPEI).strftime('%Y-%m-%d %H:%M:%S')}")

    # 檢查是否有設定 Cookie
    if not os.environ.get("YESALLY_COOKIES"):
        log_message("警告: 未設定 YESALLY_COOKIES 環境變數")
        log_message("請先在本地執行 save_cookies.py 並設定環境變數")

    # 檢查是否要立即執行一次
    if os.environ.get("RUN_NOW") == "true" or "--now" in sys.argv:
        log_message("偵測到 RUN_NOW 參數，立即執行一次")
        run_once()

    # 建立排程器 (使用 UTC)
    scheduler = BlockingScheduler(timezone="UTC")

    # 台北 00:01 = UTC 16:01 (前一天)
    # 所以設定 UTC 16:01
    trigger = CronTrigger(hour=16, minute=1, timezone="UTC")
    scheduler.add_job(scheduled_job, trigger, id="daily_click", name="每日分館搶先排序")

    log_message("排程已設定: 每天 00:01 (台北時間) / 16:01 (UTC) 執行")
    log_message("服務運行中，等待排程觸發...")
    log_message("=" * 50)

    # 處理關閉信號
    def shutdown(signum, frame):
        log_message("收到關閉信號，正在停止排程器...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log_message("排程器已停止")


if __name__ == "__main__":
    main()
