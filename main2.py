import time
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(dotenv_path="/app/.env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_URL = os.getenv("TARGET_URL")
TARGET_MONTH = os.getenv("TARGET_MONTH")
TARGET_DAY = os.getenv("TARGET_DAY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "20"))

def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def check_seats():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="ko-KR"
        )
        page = context.new_page()
        page.goto(TARGET_URL)

        # 날짜 클릭 (월/일 기준으로 찾기)
        #page.click(f"li[data-date*='{TARGET_MONTH}-{TARGET_DAY}']")
        page.wait_for_load_state("networkidle")  # 네트워크 요청 다 끝날 때까지 대기

        # 팝업 닫기
        try:
            page.wait_for_selector(".popupWrap", timeout=5000)
            page.evaluate("document.querySelector('.popupWrap').remove()")
            page.wait_for_timeout(500)
        except:
            pass  # 팝업 없으면 그냥 넘어감
        page.screenshot(path="/app/debug.png")  # 추가
        page.locator("ul[data-view='days'] li").filter(has_text=f"{int(TARGET_DAY)}").first.click()
        page.wait_for_timeout(2000)

        # 오토캠핑존 잔여석 읽기
        items = page.query_selector_all(".seatTableItem")
        for item in items:
            name = item.query_selector(".seatTableName")
            status = item.query_selector(".seatTableStatus")
            if name and "오토캠핑존" in name.inner_text():
                seat_text = status.inner_text()  # ex) "0석"
                count = int(seat_text.replace("석", "").strip())
                browser.close()
                return count

        browser.close()
        return 0

def main():
    print("bookSentinel 시작!", flush=True)
    previous = 0

    while True:
        try:
            count = check_seats()
            print(f"오토캠핑존 잔여석: {count}")

            if previous == 0 and count > 0:
                send_telegram(f"🏕️ 오토캠핑존 자리 생겼어요! 잔여석: {count}석\n{TARGET_URL}")

            previous = count

        except Exception as e:
            print(f"에러 발생: {e}")

        print(f"[대기] {CHECK_INTERVAL}초 후 다시 체크...", flush=True)
        time.sleep(CHECK_INTERVAL)  # 1분마다 체크

if __name__ == "__main__":
    main()
