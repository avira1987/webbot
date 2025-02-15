import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# تنظیمات
BOT_TOKEN = '7852224234:AAGSzAiyW-6KyrDkPraLuTulM9qe-NKZbFU'
DJANGO_API_URL = 'http://e1bd-141-95-54-124.ngrok-free.app/api/'

# لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# وضعیت‌ها
SELECTING_PRODUCT, SELECTING_QUANTITY = range(2)

# دیکشنری برای ذخیره اطلاعات موقت کاربر
user_data = {}

def get_orders():
    response = requests.get(f'{DJANGO_API_URL}orders/')
    if response.status_code == 200:
        return response.json()
    return []

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = get_orders()
    if orders:
        message = "لیست سفارش‌ها:\n"
        for order in orders:
            message += (
                f"سفارش #{order['id']}: "
                f"{order['quantity']} عدد از محصول شماره {order['product']} - "
                f"قیمت کل: {order['total_price']} تومان - "
                f"تاریخ: {order['created_at']}\n"
            )
    else:
        message = "سفارشی موجود نیست."
    await update.message.reply_text(message)

# تابع محاسبه قیمت کل
def calculate_total_price(product_id, quantity):
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return float(product['price']) * quantity
    return 0

# دریافت لیست محصولات از جنگو
def get_products():
    try:
        response = requests.get(f'{DJANGO_API_URL}products/')
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching products: {e}")
    return []

# ثبت سفارش در جنگو
def create_order_backend(product_id, quantity):
    total_price = calculate_total_price(product_id, quantity)
    data = {
        'product': product_id,
        'quantity': quantity,
        'total_price': total_price
    }
    response = requests.post(f'{DJANGO_API_URL}orders/', json=data)
    if response.status_code == 201:
        return True
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return False

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['نمایش محصولات']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('به فروشگاه ما خوش آمدید!', reply_markup=reply_markup)

# انتخاب محصول
async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_products()
    if not products:
        await update.message.reply_text("محصولی موجود نیست.")
        return ConversationHandler.END

    keyboard = [[product['name']] for product in products]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("لطفاً یک محصول انتخاب کنید:", reply_markup=reply_markup)
    return SELECTING_PRODUCT

# انتخاب تعداد
async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text
    products = get_products()

    selected_product = next((p for p in products if p['name'] == product_name), None)
    if not selected_product:
        await update.message.reply_text("محصول انتخاب‌شده معتبر نیست.")
        return ConversationHandler.END

    user_data[update.effective_user.id] = {'product_id': selected_product['id'], 'product_name': product_name}
    await update.message.reply_text(f"چه تعداد از محصول '{product_name}' می‌خواهید؟")
    return SELECTING_QUANTITY

# ثبت سفارش
async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    quantity = update.message.text

    if not quantity.isdigit() or int(quantity) <= 0:
        await update.message.reply_text("لطفاً یک عدد معتبر وارد کنید.")
        return SELECTING_QUANTITY

    product_id = user_data[user_id]['product_id']
    product_name = user_data[user_id]['product_name']

    success = create_order_backend(product_id, int(quantity))
    if success:
        await update.message.reply_text(f"سفارش شما برای {quantity} عدد از محصول '{product_name}' با موفقیت ثبت شد.")
    else:
        await update.message.reply_text("خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.")

    del user_data[user_id]
    return ConversationHandler.END

# لغو فرآیند
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند ثبت سفارش لغو شد.")
    return ConversationHandler.END

# اجرای بات
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^نمایش محصولات$'), select_product)],
        states={
            SELECTING_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_quantity)],
            SELECTING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(CommandHandler("orders", show_orders))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()