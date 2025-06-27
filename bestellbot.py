from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# ⛓️ Schritte im Dialog
PRODUKT, MENGE, VERSAND, INFO, BESTÄTIGUNG = range(5)

# 🔐 Bot-Token (von @BotFather)
BOT_TOKEN = 
# 🧑 Admin-ID (Telegram-ID, wohin Bestellung gesendet wird)
ADMIN_CHAT_ID = 7286023802
# 🧭 Start des Bestellvorgangs
def start_order(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Paste', 'Hash', 'Vape']]
    update.message.reply_text(
        'Was möchtest du bestellen?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return PRODUKT

def produkt(update: Update, context: CallbackContext) -> int:
    context.user_data['produkt'] = update.message.text
    reply_keyboard = [['1g', '3g', '5g']]
    update.message.reply_text(
        'Welche Menge möchtest du?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENGE

def menge(update: Update, context: CallbackContext) -> int:
    context.user_data['menge'] = update.message.text
    reply_keyboard = [['Post', 'Abholung', 'Codename']]
    update.message.reply_text(
        'Wie möchtest du liefern lassen?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return VERSAND

def versand(update: Update, context: CallbackContext) -> int:
    context.user_data['versand'] = update.message.text
    update.message.reply_text('Gib bitte die Lieferinfo oder den Codenamen ein:',
                              reply_markup=ReplyKeyboardRemove())
    return INFO

def info(update: Update, context: CallbackContext) -> int:
    context.user_data['info'] = update.message.text
    data = context.user_data
    zusammenfassung = f"""✅ Bestellübersicht:
🧪 Produkt: {data['produkt']}
⚖️ Menge: {data['menge']}
📦 Versand: {data['versand']}
📍 Info: {data['info']}

✅ Bestätige mit „Ja“ oder breche ab mit „Nein“."""
    update.message.reply_text(zusammenfassung)
    return BESTÄTIGUNG

def bestätigung(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'ja':
        user = update.effective_user
        data = context.user_data
        nachricht = f"""📬 Neue Bestellung:
👤 Von: @{user.username} ({user.id})
🧪 Produkt: {data['produkt']}
⚖️ Menge: {data['menge']}
📦 Versand: {data['versand']}
📍 Info: {data['info']}"""
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=nachricht)
        update.message.reply_text('✅ Deine Bestellung wurde abgeschickt. Danke!')
    else:
        update.message.reply_text('❌ Bestellung abgebrochen.')
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('❌ Bestellung wurde abgebrochen.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('order', start_order)],
        states={
            PRODUKT: [MessageHandler(Filters.text & ~Filters.command, produkt)],
            MENGE: [MessageHandler(Filters.text & ~Filters.command, menge)],
            VERSAND: [MessageHandler(Filters.text & ~Filters.command, versand)],
            INFO: [MessageHandler(Filters.text & ~Filters.command, info)],
            BESTÄTIGUNG: [MessageHandler(Filters.regex('^(Ja|Nein)$'), bestätigung)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
