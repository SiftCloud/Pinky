from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# 🔐 Bot-Token (von @BotFather)
BOT_TOKEN = 7559409764:AAFvTN63N4XxMqbVnty2LAzZ8uFY3U_GHOo
# 🧑 Admin-ID (Telegram-ID, wohin Bestellung gesendet wird)
ADMIN_CHAT_ID = 7286023802

# 🧾 Startbefehl
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🧪 Paste", callback_data='order_paste')],
        [InlineKeyboardButton("💨 Vape", callback_data='order_vape')],
        [InlineKeyboardButton("🧱 Hash", callback_data='order_hash')],
        [InlineKeyboardButton("📦 Bestellung", callback_data='order_start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Willkommen bei PinkyBot! Was brauchst du?", reply_markup=reply_markup)

# 📦 Auswahl Verarbeitung
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith('order_'):
        produkt = data.split('_')[1]
        if produkt in ['paste', 'vape', 'hash']:
            context.user_data['produkt'] = produkt
            keyboard = [
                [InlineKeyboardButton("1g", callback_data='menge_1g')],
                [InlineKeyboardButton("3g", callback_data='menge_3g')],
                [InlineKeyboardButton("5g", callback_data='menge_5g')],
            ]
            query.edit_message_text(text=f"{produkt.title()} ausgewählt. Wähle Menge:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
        elif produkt == 'start':
            query.edit_message_text("Wähle zuerst ein Produkt, bevor du bestellst.")

    elif data.startswith('menge_'):
        menge = data.split('_')[1]
        context.user_data['menge'] = menge
        keyboard = [
            [InlineKeyboardButton("📬 Post", callback_data='versand_post')],
            [InlineKeyboardButton("🏪 Abholung", callback_data='versand_abholung')],
        ]
        query.edit_message_text(text=f"{context.user_data['produkt'].title()} – {menge} ausgewählt. Versandart?",
                                reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith('versand_'):
        versand = data.split('_')[1]
        context.user_data['versand'] = versand

        zusammenfassung = f"""✅ Zusammenfassung:
Produkt: {context.user_data['produkt'].title()}
Menge: {context.user_data['menge']}
Versand: {versand.title()}"""

        query.edit_message_text(text=zusammenfassung + "\n\nWird jetzt an den Admin gesendet ...")

        # Nachricht an Admin
        admin_message = f"""📬 Neue Bestellung:
👤 Von: @{query.from_user.username} ({query.from_user.id})
🧪 Produkt: {context.user_data['produkt'].title()}
⚖️ Menge: {context.user_data['menge']}
📦 Versand: {versand.title()}"""
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

# ❌ /cancel
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Abgebrochen.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
