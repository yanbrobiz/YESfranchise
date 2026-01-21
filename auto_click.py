"""
Yes!加盟 自動點擊「分館搶先排序」腳本
每天凌晨 00:01 執行，自動完成分館排序操作。
支援本地執行和雲端部署（Railway）。
"""

import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 設定檔案路徑
SCRIPT_DIR = Path(__file__).parent
COOKIES_FILE = SCRIPT_DIR / "cookies.json"
LOG_FILE = SCRIPT_DIR / "execution_log.txt"

# 網站 URL
MEMBER_URL = "https://yesally.com.tw/member.php"


def log_message(message: str):
    """記錄訊息到檔案和終端"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except:
        pass  # 雲端環境可能無法寫入檔案


def load_cookies() -> list:
    """載入儲存的 Cookie（支援環境變數或檔案）"""
    # 優先從環境變數讀取（用於雲端部署）
    cookies_env = os.environ.get("YESALLY_COOKIES")
    if cookies_env:
        try:
            # 環境變數中的 Cookie 是 base64 編碼的 JSON
            decoded = base64.b64decode(cookies_env).decode("utf-8")
            return json.loads(decoded)
        except Exception as e:
            raise ValueError(f"環境變數 YESALLY_COOKIES 格式錯誤: {e}")

    # 從檔案讀取（本地執行）
    if not COOKIES_FILE.exists():
        raise FileNotFoundError(
            f"Cookie 檔案不存在: {COOKIES_FILE}\n"
            "請先執行 save_cookies.py 儲存登入資訊。"
        )

    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_automation(headless: bool = True):
    """執行自動化點擊"""
    log_message("=" * 50)
    log_message("開始執行 Yes!加盟 分館搶先排序自動化")

    try:
        cookies = load_cookies()
        log_message(f"已載入 {len(cookies)} 個 Cookie")
    except FileNotFoundError as e:
        log_message(f"錯誤: {e}")
        return False

    with sync_playwright() as p:
        # 啟動瀏覽器
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        # 載入 Cookie
        context.add_cookies(cookies)
        log_message("Cookie 已載入瀏覽器")

        page = context.new_page()

        try:
            # 前往會員頁面
            log_message(f"正在前往會員頁面: {MEMBER_URL}")
            page.goto(MEMBER_URL, wait_until="networkidle")

            # 確認是否成功進入會員頁面（檢查是否有登出按鈕或會員內容）
            # 如果 Cookie 過期，可能會被重導向到登入頁面
            if "member.php" not in page.url:
                log_message("錯誤: Cookie 可能已過期，請重新執行 save_cookies.py")
                browser.close()
                return False

            log_message("成功進入會員頁面")

            # 等待頁面完全載入
            page.wait_for_load_state("networkidle")

            # 尋找並點擊「分館搶先排序」按鈕
            # 根據截圖，按鈕文字為「分館搶先排序」
            log_message("尋找「分館搶先排序」按鈕...")

            # 嘗試多種選擇器
            selectors = [
                "text=分館搶先排序",
                "a:has-text('分館搶先排序')",
                "button:has-text('分館搶先排序')",
                "[onclick*='分館']",
                "text=搶先排序",
            ]

            button_found = False
            for selector in selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=3000):
                        log_message(f"找到按鈕，使用選擇器: {selector}")
                        button.click()
                        button_found = True
                        break
                except:
                    continue

            if not button_found:
                log_message("錯誤: 找不到「分館搶先排序」按鈕")
                log_message("可能原因：今日已點擊過、頁面結構改變、或 Cookie 過期")

                # 截圖供除錯
                screenshot_path = SCRIPT_DIR / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=str(screenshot_path))
                log_message(f"已儲存除錯截圖: {screenshot_path}")

                browser.close()
                return False

            # 等待操作完成
            page.wait_for_load_state("networkidle")
            log_message("成功點擊「分館搶先排序」按鈕！")

            # 截圖保存結果
            screenshot_path = SCRIPT_DIR / f"success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=str(screenshot_path))
            log_message(f"已儲存成功截圖: {screenshot_path}")

        except PlaywrightTimeout as e:
            log_message(f"操作逾時: {e}")
            browser.close()
            return False
        except Exception as e:
            log_message(f"執行錯誤: {e}")
            browser.close()
            return False

        browser.close()
        log_message("自動化執行完成")
        log_message("=" * 50)
        return True


if __name__ == "__main__":
    # 檢查是否要以有頭模式執行（用於測試）
    headless = "--visible" not in sys.argv

    if "--visible" in sys.argv:
        print("以可見模式執行（用於測試）")

    success = run_automation(headless=headless)
    sys.exit(0 if success else 1)
