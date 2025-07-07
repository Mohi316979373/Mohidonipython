from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# 🔐 توکن ربات و آیدی ادمین
TOKEN = "7889497165:AAHEtpbKrffJBFUnmAJxI6RyUI-18f20t6s"
ADMIN_ID = 1023470785

# 👗 لیست لباس‌ها (می‌تونی چند تا دستی بزاری برای تست اولیه)
clothes = {
    "مانتو تابستانی": {
        "description": "مانتو نخی خنک مناسب تابستان. سایزهای M و L موجود است.",
        "price": "450,000 تومان",
        "image": "https://i.imgur.com/YOUR_IMAGE_ID.jpg"
    },
    "شلوار جین": {
        "description": "شلوار جین کشی فاق بلند. سایز 36 تا 44.",
        "price": "390,000 تومان",
        "image": "https://i.imgur.com/YOUR_OTHER_IMAGE_ID.jpg"
    }
}

# 📍 مراحل اضافه‌کردن لباس
NAME, DESCRIPTION, PRICE, IMAGE = range(4)

# 🎬 شروع ربات برای مشتری
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not clothes:
        await update.message.reply_text("در حال حاضر هیچ لباسی ثبت نشده است.")
        return
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in clothes]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از لباس‌ها رو انتخاب کن:", reply_markup=reply_markup)

# 📸 نمایش لباس انتخاب‌شده
async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = clothes.get(query.data)
    if item:
        await query.message.reply_photo(
            photo=item["image"],
            caption=f"{query.data}\n\n{item['description']}\nقیمت: {item['price']}"
        )

# 🔒 بررسی ادمین بودن
async def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID

# ➕ شروع اضافه‌کردن لباس
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return await update.message.reply_text("❌ شما اجازه این کار را ندارید.")
    await update.message.reply_text("📝 اسم لباس جدید را وارد کن:")
    return NAME

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📝 توضیحات لباس:")
    return DESCRIPTION

async def add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text("💰 قیمت لباس:")
    return PRICE

async def add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    await update.message.reply_text("📸 لینک عکس لباس را وارد کن:")
    return IMAGE

async def add_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    clothes[name] = {
        "description": context.user_data["description"],
        "price": context.user_data["price"],
        "image": update.message.text
    }
    await update.message.reply_text(f"✅ لباس '{name}' با موفقیت اضافه شد!")
    return ConversationHandler.END

# ❌ لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ عملیات لغو شد.")
    return ConversationHandler.END

# 📋 لیست لباس‌ها
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    if not clothes:
        await update.message.reply_text("📭 لیست خالی است.")
    else:
        text = "\n".join([f"👗 {name} - {clothes[name]['price']}" for name in clothes])
        await update.message.reply_text(f"📋 لیست لباس‌ها:\n{text}")

# 🗑️ حذف لباس
async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    if len(context.args) == 0:
        await update.message.reply_text("❗ لطفاً اسم لباس را وارد کن:\nمثلاً:\n/remove مانتو تابستانی")
        return
    name = " ".join(context.args)
    if name in clothes:
        del clothes[name]
        await update.message.reply_text(f"✅ لباس '{name}' حذف شد.")
    else:
        await update.message.reply_text("❌ لباس پیدا نشد.")

# 🚀 اجرای ربات
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_item))

    # گفتگو برای اضافه‌کردن لباس
    conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_description)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_price)],
            IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_image)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)

    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("remove", remove_item))

    app.run_polling()