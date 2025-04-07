import json
import os
import time
from seleniumbase import SB
from bs4 import BeautifulSoup

# Cấu hình
DISCORD_URL = "https://discord.com/channels/1069494820386635796/1342374577967202365"
OROCHI_URL = "https://orochi.network/onactive"
CHECK_URL = "https://orochi.network/onactive/api/auth/session"
PROFILE_PATH = os.path.join(os.getcwd(), "sb_profile")
LAST_CODE = ""

def open_discord_and_listen():
    global LAST_CODE

    with SB(uc=True, headless=False, user_data_dir=PROFILE_PATH) as sb:
        print("[!] Đang check trạng thái đăng nhập của Orochi")
        session_data = check_session_via_browser(sb)
        if session_data == {}:
            sb.open(OROCHI_URL)
            session_data = check_session_via_browser(sb)
            print("Tiến hành login lại Orochi")
            input("==> Sau khi login xong thì lưu thông tin gmail vào profile Chrome luôn nhé, xong hết thì nhấn Enter để kiểm tra lại...")

            if session_data == {}:
                print("[!] Vẫn không có session. Có thể login chưa thành công.")
            else:
                print("[✔] Login thành công. Session hợp lệ:", session_data)
        else:
            print("[✔] Session đã hợp lệ. Không cần login.")

        # Mở Discord
        sb.open(DISCORD_URL)

        # Nếu lần đầu, yêu cầu đăng nhập
        if "login" in sb.get_current_url():
            print("⏳ Đăng nhập Discord rồi nhấn Enter...")
            input("👉 Sau khi đăng nhập xong, nhấn Enter để tiếp tục...")

        print("✅ Set up OK! Bắt đầu chạy...")

    with SB(uc=True, headless=True, user_data_dir=PROFILE_PATH) as sb:
        # Mở Discord
        sb.open(DISCORD_URL)
        print("✅ Đã vào Discord, bắt đầu quét mã mới...")
        while True:
            time.sleep(3)
            html = sb.get_page_source()
            soup = BeautifulSoup(html, "html.parser")

            message_items = soup.select('ol[data-list-id="chat-messages"] > li[class^="messageListItem"]')
            if message_items:
                latest_item = message_items[-1]
                inline_code = latest_item.select_one('.inline')
                if inline_code:
                    latest = inline_code.get_text(strip=True)
                    if latest != LAST_CODE:
                        print(f"📥 Mã mới phát hiện: {latest}")
                        LAST_CODE = latest
                        print(f"🌐 Vào orochi để submit submit mã: {latest}")
                        submit_to_orochi_in_new_tab(sb, latest)
                else:
                    print("⚠️ Không tìm thấy mã trong tin nhắn mới.")
            else:
                print("⏳ Chưa có tin nhắn nào...")           

def submit_to_orochi_in_new_tab(sb, code):
    try:
        sb.open(OROCHI_URL)
        time.sleep(6)

        # Locate the input field and enter the code
        sb.wait_for_element(".size-full.bg-transparent.p-3.outline-none", timeout = 15)
        input_box = sb.find_element("css selector", ".size-full.bg-transparent.p-3.outline-none")
        input_box.send_keys(code)
        print("✍️ Nhập mã vào ô input")

        # Click the "Verify code" button
        button = sb.find_element("xpath", "//button[.//p[text()='Verify code']]")
        sb.execute_script("arguments[0].scrollIntoView(true);", button)
        sb.execute_script("arguments[0].click();", button)
        print("✅ Đã submit mã vào Orochi.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Lỗi khi nhập mã: {e}")

    time.sleep(2)
    print("🔁 Quay lại Discord và tiếp tục lắng nghe mã...")
    sb.open(DISCORD_URL)

def check_session_via_browser(sb):
    sb.open(CHECK_URL)
    time.sleep(2)  # chờ response render ra

    # Lấy JSON text hiển thị trên trang
    raw_json = sb.get_text("body")

    try:
        data = json.loads(raw_json)
        if data == {}:
            print("[✘] Session hết hạn hoặc chưa login.")
            return {}
        else:
            print("[✔] Session hợp lệ:", data)
    except Exception as e:
        print("[!] Không parse được JSON:", e)
        print("Raw response:", raw_json)
        return {}
    
# ────────────────────────────────────────
if __name__ == "__main__":
    open_discord_and_listen()
