"""
儲存登入 Cookie 腳本
執行此腳本後，手動完成登入（包括驗證碼），
登入成功後 Cookie 會自動儲存供後續使用。
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path(__file__).parent / "cookies.json"
MEMBER_URL = "https://yesally.com.tw/member.php"


def save_cookies():
    with sync_playwright() as p:
        # 使用有頭瀏覽器，方便手動操作
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 前往首頁
        print("正在開啟 yesally.com.tw...")
        page.goto("https://yesally.com.tw/")

        print("\n" + "=" * 50)
        print("請手動完成以下步驟：")
        print("1. 點擊登入按鈕")
        print("2. 輸入帳號密碼")
        print("3. 完成 reCAPTCHA 驗證")
        print("4. 登入成功後，頁面會自動偵測")
        print("=" * 50 + "\n")

        # 等待用戶登入成功，最多等待 5 分鐘
        # 登入成功後會跳轉到會員頁面或首頁會顯示會員狀態
        try:
            # 等待會員頁面載入或登入狀態改變
            page.wait_for_url("**/member.php**", timeout=300000)
            print("偵測到已登入會員頁面！")
        except:
            # 如果沒有自動跳轉，嘗試手動前往會員頁
            print("嘗試前往會員頁面確認登入狀態...")
            page.goto(MEMBER_URL)
            page.wait_for_load_state("networkidle")

        # 確認是否在會員頁面
        if "member.php" in page.url:
            # 儲存 cookies
            cookies = context.cookies()
            with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)

            print(f"\nCookie 已儲存至: {COOKIES_FILE}")
            print(f"共儲存 {len(cookies)} 個 Cookie")

            # 產生 Base64 編碼版本（用於 Railway 環境變數）
            import base64
            cookies_json = json.dumps(cookies, ensure_ascii=False)
            cookies_base64 = base64.b64encode(cookies_json.encode("utf-8")).decode("utf-8")

            env_file = COOKIES_FILE.parent / "cookies_env.txt"
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(cookies_base64)

            print(f"\n[Railway 部署用] Base64 Cookie 已儲存至: {env_file}")
            print("請將該檔案內容設定為 Railway 的環境變數 YESALLY_COOKIES")
            print("\n現在可以關閉瀏覽器，之後執行 auto_click.py 進行自動化操作。")
        else:
            print("\n登入失敗或未偵測到會員頁面，請重新執行此腳本。")

        # 等待用戶確認後關閉
        input("\n按 Enter 鍵關閉瀏覽器...")
        browser.close()


if __name__ == "__main__":
    save_cookies()
