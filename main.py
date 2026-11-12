
import os
import requests
from flask import Flask, request, jsonify

TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
K_PAY = os.environ.get("K_PAY", "09422190218")
WAVE_PAY = os.environ.get("WAVE_PAY", "09893463559")
BOT = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

PRODUCTS = {
    "Weekly Pass": 6900,
    "Twilight Pass": 34500,
    "86 Dia": 5800,
    "172 Dia": 11000,
    "257 Dia": 16300,
    "343 Dia": 21800,
    "429 Dia": 27000,
    "514 Dia": 32500,
    "600 Dia": 37600,
    "706 Dia": 42900,
    "878 Dia": 53600,
    "964 Dia": 58900,
    "1049 Dia": 64100,
    "2195 Dia": 127500,
    "2x50 Double": 4100,
    "2x150 Double": 11500,
    "2x250 Double": 17200,
    "2x500 Double": 33700
}

users = {}
orders = {}
order_number = 1000


def api(method, data=None):
    try:
        return requests.post(
            f"{BOT}/{method}",
            json=data or {},
            timeout=30
        ).json()
    except Exception as e:
        print("Telegram API Error:", e)
        return {}


def send(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = keyboard
    return api("sendMessage", data)


def main_menu():
    return {
        "keyboard": [
            [{"text": "🛒 Buy Diamond"},
             {"text": "💎 Diamond List"}],
            [{"text": "📦 My Orders"},
             {"text": "💳 Payment"}],
            [{"text": "📞 Contact Admin"},
             {"text": "❓ Help"}]
        ],
        "resize_keyboard": True
    }


def products_menu():
    rows = []
    items = list(PRODUCTS.items())
    for i in range(0, len(items), 2):
        row = []
        for name, price in items[i:i+2]:
            row.append({
                "text": f"{name} - {price:,} Ks",
                "callback_data": f"buy|{name}"
            })
        rows.append(row)
    return {"inline_keyboard": rows}


def start_order(chat_id, name):
    users[chat_id] = {"product": name, "step": "userid"}
    send(chat_id, f"💎 <b>{name}</b>\n"
         f"💰 ဈေးနှုန်း - {PRODUCTS[name]:,} Ks\n\n"
         "MLBB User ID ကို ပို့ပေးပါ။")


def handle_message(msg):
    global order_number

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    user = msg.get("from", {})
    name = user.get("first_name", "Customer")
    username = user.get("username", "မရှိပါ")

    state = users.get(chat_id, {})

    if text == "/start":
        users[chat_id] = {"step": "menu"}
        send(chat_id,
             "💜 <b>League 2 Diamond Shop မှ ကြိုဆိုပါတယ်။</b>\n\n"
             "MLBB Diamond နှင့် Pass များကို ဝယ်ယူနိုင်ပါပြီ။\n"
             "အောက်ပါ Menu ကို ရွေးချယ်ပါ။",
             main_menu())
        return

    if text == "💎 Diamond List":
        lines = ["💎 <b>Diamond Package List</b>\n"]
        for product, price in PRODUCTS.items():
            lines.append(f"• {product} — {price:,} Ks")
        send(chat_id, "\n".join(lines), main_menu())
        return

    if text == "🛒 Buy Diamond":
        send(chat_id, "ဝယ်ယူလိုသော Package ကို ရွေးချယ်ပါ။",
             products_menu())
        return

    if text == "💳 Payment":
        send(chat_id,
             "💳 <b>Payment Methods</b>\n\n"
             f"KBZPay: <code>{K_PAY}</code>\n"
             f"WavePay: <code>{WAVE_PAY}</code>\n\n"
             "ဝယ်ယူမှုအတွက် Order တစ်ခုစတင်ပြီး ငွေလွှဲပါ။",
             main_menu())
        return

    if text == "📞 Contact Admin":
        send(chat_id, "Admin ကို ဆက်သွယ်ရန် Telegram မှာ "
             "Admin ကိုရှာပြီး ဆက်သွယ်ပေးပါ။",
             main_menu())
        return

    if text == "❓ Help":
        send(chat_id,
             "📌 <b>အသုံးပြုနည်း</b>\n\n"
             "1. Buy Diamond နှိပ်ပါ။\n"
             "2. Package ရွေးပါ။\n"
             "3. User ID / Server ID ဖြည့်ပါ။\n"
             "4. ငွေလွှဲပြီး Screenshot ပို့ပါ။\n"
             "5. Admin အတည်ပြုသည်အထိ စောင့်ပါ။",
             main_menu())
        return

    if text == "📦 My Orders":
        my_orders = [
            f"#{oid} - {o['product']} - {o['status']}"
            for oid, o in orders.items()
            if o["chat_id"] == chat_id
        ]
        send(chat_id,
             "📦 <b>My Orders</b>\n\n" +
             ("\n".join(my_orders) if my_orders else
              "Order မရှိသေးပါ။"),
             main_menu())
        return

    if not state:
        send(chat_id, "Menu မှ စတင်ရွေးချယ်ပေးပါ။", main_menu())
        return

    if state.get("step") == "userid":
        if not text.isdigit():
            send(chat_id, "User ID ကို နံပါတ်ဖြင့် ထည့်ပေးပါ။")
            return
        state["userid"] = text
        state["step"] = "serverid"
        send(chat_id, "MLBB Server ID ကို ပို့ပေးပါ။")
        return

    if state.get("step") == "serverid":
        if not text.isdigit():
            send(chat_id, "Server ID ကို နံပါတ်ဖြင့် ထည့်ပေးပါ။")
            return
        state["serverid"] = text
        state["step"] = "receipt"
        send(chat_id,
             "💳 <b>ငွေပေးချေရန်</b>\n\n"
             f"Product: {state['product']}\n"
             f"Price: {PRODUCTS[state['product']]:,} Ks\n\n"
             f"KBZPay: <code>{K_PAY}</code>\n"
             f"WavePay: <code>{WAVE_PAY}</code>\n\n"
             "ငွေလွှဲပြီး ပြေစာ Screenshot ပို့ပေးပါ။")
        return

    if state.get("step") == "receipt":
        photo = msg.get("photo")
        if not photo:
            send(chat_id, "ပြေစာကို Screenshot ပုံအဖြစ် ပို့ပေးပါ။")
            return

        order_number += 1
        oid = str(order_number)

        orders[oid] = {
            "chat_id": chat_id,
            "product": state["product"],
            "price": PRODUCTS[state["product"]],
            "userid": state["userid"],
            "serverid": state["serverid"],
            "status": "Pending"
        }

        users[chat_id] = {"step": "menu"}

        caption = (
            f"🛒 <b>New Order #{oid}</b>\n\n"
            f"👤 Name: {name}\n"
            f"Username: @{username}\n"
            f"Product: {state['product']}\n"
            f"Price: {PRODUCTS[state['product']]:,} Ks\n"
            f"User ID: <code>{state['userid']}</code>\n"
            f"Server ID: <code>{state['serverid']}</code>\n"
            f"Customer ID: <code>{chat_id}</code>\n"
            "Status: Pending"
        )

        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ Approve", "callback_data": f"approve|{oid}"},
                {"text": "❌ Reject", "callback_data": f"reject|{oid}"}
            ]]
        }

        result = api("sendPhoto", {
            "chat_id": ADMIN_ID,
            "photo": photo[-1]["file_id"],
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        })

        if result.get("ok"):
            send(chat_id,
                 f"✅ Order #{oid} Admin ဆီ ပို့ပြီးပါပြီ။\n"
                 "ငွေပေးချေမှုကို စစ်ဆေးနေပါတယ်။",
                 main_menu())
        else:
            send(chat_id,
                 "Order ပို့ရာမှာ အမှားဖြစ်နေပါတယ်။ Admin ကို ဆက်သွယ်ပါ။",
                 main_menu())
        return

    send(chat_id, "Menu မှ ပြန်စတင်ရွေးချယ်ပါ။", main_menu())


def handle_callback(query):
    data = query.get("data", "")
    callback_id = query["id"]
    chat_id = query["message"]["chat"]["id"]

    if data.startswith("buy|"):
        product = data.split("|", 1)[1]
        if product in PRODUCTS:
            start_order(chat_id, product)
        api("answerCallbackQuery", {"callback_query_id": callback_id})
        return

    if data.startswith(("approve|", "reject|")):
        if str(chat_id) != str(ADMIN_ID):
            api("answerCallbackQuery", {
                "callback_query_id": callback_id,
                "text": "Admin only!",
                "show_alert": True
            })
            return

        action, oid = data.split("|", 1)
        order = orders.get(oid)

        if not order or order["status"] != "Pending":
            api("answerCallbackQuery", {
                "callback_query_id": callback_id,
                "text": "Order မရှိတော့ပါ။",
                "show_alert": True
            })
            return

        if action == "approve":
            order["status"] = "Approved"
            send(order["chat_id"], "ထည့်လိုက်ပါပြီ✅", main_menu())
            message = f"✅ Order #{oid} Approved"
        else:
            order["status"] = "Rejected"
            send(order["chat_id"],
                 "❌ သင့် Order ကို ပယ်ဖျက်လိုက်ပါတယ်။ Admin ကို ဆက်သွယ်ပါ။",
                 main_menu())
            message = f"❌ Order #{oid} Rejected"

        api("editMessageCaption", {
            "chat_id": chat_id,
            "message_id": query["message"]["message_id"],
            "caption": message
        })
        api("answerCallbackQuery", {
            "callback_query_id": callback_id,
            "text": message
        })


@app.route("/", methods=["GET"])
def home():
    return "League 2 Diamond Shop is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    if "message" in update:
        handle_message(update["message"])
    elif "callback_query" in update:
        handle_callback(update["callback_query"])
    return jsonify({"ok": True})


if not TOKEN or not ADMIN_ID:
    print("BOT_TOKEN or ADMIN_ID is missing!")

if TOKEN:
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if base_url:
        api("setWebhook", {"url": base_url.rstrip("/") + "/webhook"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
