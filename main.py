import time
import os
import datetime
import requests
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
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # 팝업 제거
        page.evaluate("""
            const popup = document.querySelector('#popup-prdGuide');
            if (popup) popup.remove();
            document.documentElement.style.overflow = 'auto';
            document.body.style.overflow = 'auto';
            document.documentElement.style.pointerEvents = 'auto';
            document.body.style.pointerEvents = 'auto';
        """)
        page.wait_for_timeout(500)

        # 현재 달과 목표 달 비교해서 다음 달 버튼 클릭
        current_month = datetime.datetime.now().month
        target_month = int(TARGET_MONTH)
        month_diff = target_month - current_month

        for _ in range(month_diff):
            page.locator("li[data-view='month next']").click()
            page.wait_for_timeout(1000)

        # 날짜 클릭
        page.evaluate(f"""
            const days = document.querySelectorAll("ul[data-view='days'] li");
            for (const day of days) {{
                if (day.textContent.trim() === '{int(TARGET_DAY)}') {{
                    day.dispatchEvent(new MouseEvent('mousedown', {{bubbles: true}}));
                    day.dispatchEvent(new MouseEvent('mouseup', {{bubbles: true}}));
                    day.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                    break;
                }}
            }}
        """)
        page.wait_for_timeout(2000)

        # 1박2일 클릭
        page.locator("a[data-text='1박2일']").first.click()
        page.wait_for_timeout(2000)

        page.screenshot(path="/app/debug2.png")

        # 오토캠핑존 잔여석 읽기
        items = page.query_selector_all(".seatTableItem")
        for item in items:
            name = item.query_selector(".seatTableName")
            status = item.query_selector(".seatTableStatus")
            if name and "오토캠핑존" in name.inner_text():
                seat_text = status.inner_text().replace("석", "").strip()
                count = int(seat_text) if seat_text else 0
                browser.close()
                return count

        browser.close()
        return 0

def main():
    print("bookSentinel 시작!", flush=True)
    previous = 0

    while True:
        try:
            print(f"[체크 중] {TARGET_MONTH}월 {TARGET_DAY}일 오토캠핑존 확인...", flush=True)
            count = check_seats()
            print(f"[결과] 오토캠핑존 잔여석: {count}석", flush=True)

            if previous == 0 and count > 0:
                send_telegram(f"🏕️ 오토캠핑존 자리 생겼어요! 잔여석: {count}석\n{TARGET_URL}")
                print("[알람] 텔레그램 전송 완료!", flush=True)

            previous = count

        except Exception as e:
            print(f"[에러] {e}", flush=True)

        print(f"[대기] {CHECK_INTERVAL}초 후 다시 체크...", flush=True)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
