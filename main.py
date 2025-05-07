import os
from flask import Flask, request
from pyrogram import Client, filters
from pyrogram.types import Message
from checker import start_checker

API_ID = 28748671   # your api_id
API_HASH = "f53ec7c41ce34e6d585674ed9ce6167c"
BOT_TOKEN = "7793230457:AAGSNLF1YzjSPFnuKPKZJhEjYN-NPsSs2p8"

app = Flask(__name__)
bot = Client("checker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply("Welcome to Netflix Checker Bot!\nPlease send accounts.txt and proxies.txt.")

@bot.on_message(filters.document)
async def save_file(client, message: Message):
    file_name = message.document.file_name
    if not file_name.endswith(".txt"):
        return await message.reply("Only .txt files allowed.")

    path = f"{message.from_user.id}_{file_name}"
    await message.download(file_name=path)

    if message.from_user.id not in user_data:
        user_data[message.from_user.id] = {}

    if "accounts" in file_name:
        user_data[message.from_user.id]["accounts"] = path
        await message.reply("Accounts file received.")
    elif "proxies" in file_name:
        user_data[message.from_user.id]["proxies"] = path
        await message.reply("Proxies file received.")

@bot.on_message(filters.command("startcheck"))
async def start_check(client, message: Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    if not data.get("accounts") or not data.get("proxies"):
        return await message.reply("Please upload both accounts.txt and proxies.txt before starting check.")

    await message.reply("Starting check. Please wait...")

    success_file, failed_file = start_checker(data["accounts"], data["proxies"])

    await message.reply_document(success_file, caption="Success Results")
    await message.reply_document(failed_file, caption="Failed Results")

@app.route("/")
def home():
    return "<h3>Netflix Checker Bot is running.</h3>"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if update:
        bot.process_update(update)
    return "OK"

if __name__ == "__main__":
    bot.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
