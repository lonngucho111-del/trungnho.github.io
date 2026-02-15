import asyncio
import time
from datetime import datetime
import requests
import matplotlib.pyplot as plt

from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    CommentEvent,
    RoomUserSeqEvent,
    GiftEvent
)

from colorama import Fore, Style, init
init(autoreset=True)

# ================== BANNER ==================
print(Fore.CYAN + Style.BRIGHT + """

▄▄▄█████▓ ██▓ ██ ▄█▀▄▄▄█████▓ ▒█████   ██ ▄█▀    ▄▄▄       ██▓███   ██▓
▓  ██▒ ▓▒▓██▒ ██▄█▒ ▓  ██▒ ▓▒▒██▒  ██▒ ██▄█▒    ▒████▄    ▓██░  ██▒▓██▒
▒ ▓██░ ▒░▒██▒▓███▄░ ▒ ▓██░ ▒░▒██░  ██▒▓███▄░    ▒██  ▀█▄  ▓██░ ██▓▒▒██▒
░ ▓██▓ ░ ░██░▓██ █▄ ░ ▓██▓ ░ ▒██   ██░▓██ █▄    ░██▄▄▄▄██ ▒██▄█▓▒ ▒░██░
  ▒██▒ ░ ░██░▒██▒ █▄  ▒██▒ ░ ░ ████▓▒░▒██▒ █▄    ▓█   ▓██▒▒██▒ ░  ░░██░
  ▒ ░░   ░▓  ▒ ▒▒ ▓▒  ▒ ░░   ░ ▒░▒░▒░ ▒ ▒▒ ▓▒    ▒▒   ▓▒█░▒▓▒░ ░  ░░▓  
    ░     ▒ ░░ ░▒ ▒░    ░      ░ ▒ ▒░ ░ ░▒ ▒░     ▒   ▒▒ ░░▒ ░      ▒ ░
  ░       ▒ ░░ ░░ ░   ░      ░ ░ ░ ▒  ░ ░░ ░      ░   ▒   ░░        ▒ ░
          ░  ░  ░                ░ ░  ░  ░            ░  ░          ░  
                                                                       
                [Telegram: @print_doki]
""")

# ================= TELEGRAM =================
TELE_TOKEN = "8239531574:AAHvGnPKU3umyCVl29Pf0aUZLtfLXpa_bfs"
TELE_CHAT_ID = "7079407562"

def send_telegram(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
            json={"chat_id": TELE_CHAT_ID, "text": text},
            timeout=5
        )
    except:
        pass

def send_telegram_photo(path, caption=""):
    try:
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TELE_TOKEN}/sendPhoto",
                data={"chat_id": TELE_CHAT_ID, "caption": caption},
                files={"photo": f},
                timeout=10
            )
    except:
        pass

# ================= UTILS =================
def get_user_name(user):
    return (
        getattr(user, "display_name", None)
        or getattr(user, "nickname", None)
        or getattr(user, "unique_id", None)
        or f"UID_{getattr(user, 'user_id', 'Unknown')}"
    )

# ================= GLOBAL =================
view_logs = []
last_view = None

gift_rank = {}  # uid: {name, coin}

last_view_chart = 0
last_donate_chart = 0
last_reset_time = time.time()

# ================= CLIENT =================
async def run_client(unique_id):
    global last_view, last_view_chart, last_donate_chart, last_reset_time

    client = TikTokLiveClient(unique_id=unique_id)

    # ---------- CONNECT ----------
    @client.on(ConnectEvent)
    async def on_connect(event):
        msg = f"✅ LIVE CONNECTED @{unique_id}"
        print(Fore.GREEN + msg)
        send_telegram(msg)

    @client.on(DisconnectEvent)
    async def on_disconnect(event):
        print(Fore.RED + "❌ DISCONNECTED – waiting reconnect")

    # ---------- COMMENT ----------
    @client.on(CommentEvent)
    async def on_comment(event):
        try:
            name = get_user_name(event.user_info)
            print(Fore.CYAN + f"[COMENT💬] {name} -> {event.comment}")
        except:
            pass

    # ---------- VIEW ----------
    @client.on(RoomUserSeqEvent)
    async def on_view(event):
        global last_view
        viewers = getattr(event, "m_total", None)
        if viewers is None or viewers == last_view:
            return

        last_view = viewers
        now = datetime.now().strftime("%H:%M:%S")
        view_logs.append({"time": now, "viewers": viewers})

        print(Fore.YELLOW + f"👀 [{now}] Viewers: {viewers}")

    # ---------- GIFT ----------
    @client.on(GiftEvent)
    async def on_gift(event):
        try:
            user = event.user
            uid = getattr(user, "user_id", None)
            if uid is None:
                return

            name = get_user_name(user)
            count = event.repeat_count or 1
            coin = event.gift.diamond_count * count

            if uid not in gift_rank:
                gift_rank[uid] = {"name": name, "coin": 0}

            gift_rank[uid]["coin"] += coin

            print(
                Fore.MAGENTA
                + f"🎁 {name} +{coin}💎 | TOTAL {gift_rank[uid]['coin']}"
            )

        except Exception as e:
            print(Fore.RED + f"[GIFT ERROR] {e}")

    # ================= LOOP =================
    async def loop_task():
        global last_view_chart, last_donate_chart, last_reset_time

        while True:
            await asyncio.sleep(2)

            now_time = time.time()

            # ===== RESET TOP DONATE 2 PHÚT =====
            if now_time - last_reset_time >= 120:
                gift_rank.clear()
                last_reset_time = now_time
                send_telegram("♻️ TOP DONATE RESET (2 phút)")
                print(Fore.BLUE + "♻️ RESET TOP DONATE")

            # ===== VIEW CHART (15s) =====
            if len(view_logs) >= 2 and now_time - last_view_chart >= 15:
                last_view_chart = now_time

                data = view_logs[-30:]
                plt.figure(figsize=(9, 4))
                plt.plot(
                    [x["time"] for x in data],
                    [x["viewers"] for x in data],
                    marker="o",
                    linewidth=2
                )
                plt.xticks(rotation=45, fontsize=8)
                plt.title(f"VIEWERS @{unique_id}")
                plt.tight_layout()
                plt.savefig("view_chart.png", dpi=150)
                plt.close()

                send_telegram_photo(
                    "view_chart.png",
                    f"📈 Viewers now: {data[-1]['viewers']}"
                )

            # ===== DONATE CHART + TOP (20s) =====
            if gift_rank and now_time - last_donate_chart >= 20:
                last_donate_chart = now_time

                top = sorted(
                    gift_rank.values(),
                    key=lambda x: x["coin"],
                    reverse=True
                )[:5]

                names = [u["name"] for u in top]
                coins = [u["coin"] for u in top]

                plt.figure(figsize=(8, 4))
                plt.bar(names, coins)
                plt.title("TOP DONATE")
                plt.ylabel("💎 Diamonds")
                plt.tight_layout()
                plt.savefig("donate_chart.png", dpi=150)
                plt.close()

                send_telegram_photo("donate_chart.png", "📊 TOP DONATE")

                msg = "🏆 TOP DONATE LIVE\n\n"
                for i, u in enumerate(top, 1):
                    msg += f"{i}. {u['name']}: {u['coin']} 💎\n"

                send_telegram(msg)

    asyncio.create_task(loop_task())
    await client.start()

# ================= MAIN (ANTI EXIT) =================
async def main():
    unique_id = input("[+] Enter the username you want to run: ").replace("@", "")
    while True:
        try:
            await run_client(unique_id)
            print("⚠️ Client stopped → reconnect in 5s")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Successful Stop")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
