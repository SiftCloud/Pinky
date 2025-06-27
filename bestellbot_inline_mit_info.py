from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# 🔐 Bot-Token (von @BotFather)
BOT_TOKEN =  7559409764:AAFvTN63N4XxMqbVnty2LAzZ8uFY3U_GHOo
# 🧑 Admin-ID (Telegram-ID, wohin Bestellung gesendet wird)
ADMIN_CHAT_ID = 7286023802

# Konversationsstatus
INFO_EINGABE = range(1)

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🧪 Paste", callback_data='order_paste')],
        [InlineKeyboardButton("💨 Vape", callback_data='order_vape')],
        [InlineKeyboardButton("🧱 Hash", callback_data='order_hash')],
        [InlineKeyboardButton("📦 Bestellung", callback_data='order_start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Willkommen bei PinkysBrainBot! Was brauchst du?", reply_markup=reply_markup)

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
        query.edit_message_text("Bitte gib jetzt Adresse und Benutzernamen ein:")
        return INFO_EINGABE

def info_eingabe(update: Update, context: CallbackContext):
    info = update.message.text
    context.user_data['info'] = info
    produkt = context.user_data.get('produkt', 'Unbekannt')
    menge = context.user_data.get('menge', 'Unbekannt')
    versand = context.user_data.get('versand', 'Unbekannt')

    zusammenfassung = f"""✅ Zusammenfassung:
Produkt: {produkt.title()}
Menge: {menge}
Versand: {versand.title()}
Info: {info}

✅ Wird an Admin gesendet ..."""
    update.message.reply_text(zusammenfassung, reply_markup=ReplyKeyboardRemove())

    # Nachricht an Admin senden
    user = update.effective_user
    admin_message = f"""📬 Neue Bestellung:
👤 Von: @{user.username} ({user.id})
🧪 Produkt: {produkt.title()}
⚖️ Menge: {menge}
📦 Versand: {versand.title()}
📍 Info: {info}"""
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Abgebrochen.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Conversation Handler für Infoeingabe
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            INFO_EINGABE: [MessageHandler(Filters.text & ~Filters.command, info_eingabe)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END,
        }
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
