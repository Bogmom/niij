import time
import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import asyncio


cred = credentials.Certificate("مسار")
firebase_admin.initialize_app(cred, {'databaseURL': 'رابط'})

SELECT_LOCATION, SEARCH_PERSON, VIEW_FAMILY, VIEW_RELATIVES, RESTARTING, SELECT_MESSAGE, ENTER_ID = map(lambda x: x, range(7))
message_ids = []
database_connections = {
    "اربيل": "erbil.sqlite", 
    "الانبار": "anbar.sqlite",
    "بابل": "babl.sqlite",
    "بلد": "balad.sqlite",
    "البصرة": "basra.sqlite",
    "بغداد": "bg.sqlite",
    "دهوك" : "duhok.sqlite",
    "الديوانية-القادسية": "qadisiya.sqlite",
    "كربلاء":"krbl.sqlite",
    "بابل":"babl.sqlite",
    "ديالى":"deala.sqlite",
    "ذي قار":"zy.sqlite",
    "السليمانية":"sulaymaniyah.sqlite",
    "صلاح الدين":"salah-aldeen.sqlite",
    "كركوك":"kirkuk.sqlite",
    "المثنى":"muthana.sqlite",
    "ميسان":"mesan.sqlite",
    "النجف":"najaf.sqlite",
    "نينوى":"nineveh.sqlite",
    "واسط":"wasit.sqlite",
}
user_messages = {}
bot_messages = {}
file_path = ('login.txt')
allowed_users = [ايدي, ]  
def start_send_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        update.message.reply_text("ليس لديك إذن لاستخدام هذا الأمر.")
        return ConversationHandler.END
    update.message.reply_text("مرحبًا! يرجى إدخال الرسالة التي تريد إرسالها إلى جميع المستخدمين.")
    return SELECT_MESSAGE
def select_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    users_ref = db.reference('users')
    snapshot = users_ref.get()
    if snapshot:
        all_user_ids = [int(user_id) for user_id in snapshot.keys()]
        for user_id in all_user_ids:
            try:
                context.bot.send_message(chat_id=user_id, text=message_text)
            except Exception as e:
                print(f"فشل إرسال الرسالة إلى المستخدم ذو المعرف: {user_id}, الخطأ: {e}")
        update.message.reply_text("تم إرسال الرسالة إلى جميع المستخدمين.")
    else:
        update.message.reply_text("لا يوجد مستخدمين في قاعدة البيانات حتى الآن.")
    return ConversationHandler.END
def get_user_count(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        update.message.reply_text("ليس لديك إذن لاستخدام هذا الأمر.")
        return
    users_ref = db.reference('users')
    snapshot = users_ref.get()
    if snapshot:
        user_count = len(snapshot)
        update.message.reply_text(f"عدد المستخدمين في قاعدة البيانات: {user_count}")
    else:
        update.message.reply_text("لا يوجد مستخدمين في قاعدة البيانات حتى الآن.")

def xnxx(update: Update, context: CallbackContext) -> int:
    user_id = str(update.message.from_user.id)
    file_path1 = "login.txt"
    with open(file_path1, "r") as file:
        user_ids_list = file.read().splitlines()
    if user_id in user_ids_list:
        return start 
    else:
        update.message.reply_text("ليس لديك إذن لاستخدام هذا الأمر راسل المطور يا اخ الكحبة.")
def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    name = update.message.from_user.first_name
    user_ref = db.reference(f'users/{user_id}')
    user_ref.set({
        'user_id': user_id,
        'user_name': user_name,
        'name': name
    })
  #  user_id = update.effective_user.id
  #  context.user_data.clear() 
   # context.user_data.clear()
    context.user_data['user_state'] = SELECT_LOCATION
    context.user_data['selected_db'] = None
  #  context.user_data['user_id'] = user_id

   # context.user_data['user_id'] = user_id
    keyboard = []
    for governorate_title in database_connections:
        keyboard.append(InlineKeyboardButton(governorate_title, callback_data=f"select_db_{governorate_title}"))
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
    update.message.reply_text("الرجاء اختيار المحافضة المطلوبة:", reply_markup=reply_markup)
    return SELECT_LOCATION
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
def select_location(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = update.effective_user.id
   # context.user_data['user_id'] = user_id

  #  context.user_data['user_id'] = user_id
    selected_db = query.data.replace("select_db_", "")
    context.user_data['selected_db'] = database_connections.get(selected_db)
    query.answer()
    query.message.reply_text(f"تم اختيار محافضة: {selected_db}\n\nالرجاء إرسال الاسم الثلاثي للبحث فيه:")
    return SEARCH_PERSON
def search_person(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    first_name = update.message.from_user.first_name
    username = update.message.from_user.username
    name = update.message.text
    p_first1, p_father1, p_grand1 = name.split()
    selected_db = context.user_data.get('selected_db')
    print(p_first1, p_father1,p_grand1)
    governorate_titles = {
        "erbil.sqlite": "اربيل",
        "anbar.sqlite": "الانبار",
        "babl.sqlite": "بابل",
        "bg.sqlite":"بغداد",
        "bg.sqlite": "بغداد",
        "balad.sqlite": "بلد",
        "basra.sqlite": "البصرة",
        "duhok.sqlite": "دهوك",
        "qadisiya.sqlite": "الديوانية-القادسية",
        "krbl.sqlite": "كربلاء",
        "bba.sqlite": "بابل",
        "deala.sqlite": "ديالى",
        "zy.sqlite": "ذي قار",
        "sulaymaniyah.sqlite": "السليمانية",
        "salah-aldeen.sqlite": "صلاح الدين",
        "kirkuk.sqlite": "كركوك",
        "muthana.sqlite": "المثنى",
        "mesan.sqlite": "ميسان",
        "najaf.sqlite": "النجف",
        "nineveh.sqlite": "نينوى",
        "wasit.sqlite": "واسط"
    }
    governorate_title = governorate_titles.get(selected_db, "محافظة غير معروفة")
    connection = sqlite3.connect(selected_db)
    cursor = connection.cursor()
    cursor.execute("SELECT p_first, p_father, p_grand, fam_no, seq_no, SUBSTR(p_birth, 1, 4) FROM person WHERE p_first LIKE ? AND p_father LIKE ? AND p_grand LIKE ?",
                   ('%' + p_first1 + '%', '%' + p_father1 + '%', '%' + p_grand1 + '%',))
    rows = cursor.fetchall()
    if rows:
        results_count = 0
        for idx, row in enumerate(rows, start=1):
            result = f"الاسم الثلاثي: {row[0]} {row[1]} {row[2]}\n"
            result += f"رقم العائلة: {row[3]}\n"
            result += f"المحافظة: {governorate_title}\n"
            result += f"المواليد: {row[5]}\n"
            birth_year = int(row[5])
            current_year = datetime.now().year
            age = current_year - birth_year
            result += f"العمر: {age} سنة\n"
            result += f"تسلسل الفرد: {str(row[4]).lstrip('0')}\n"           
            unique_identifier = f"view_family{row[3]}"
            context.user_data[unique_identifier] = row[3]
            keyboard = [[InlineKeyboardButton("جلب العائلة", callback_data=unique_identifier)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=user_id, text=result, reply_markup=reply_markup)
            results_count += 1
            if results_count % 30 == 0:
                time.sleep(10)  
        context.bot.send_message(chat_id=user_id, text="تم الانتهاء من البحث.")
    else:
        context.bot.send_message(chat_id=user_id, text="لم يتم العثور على نتائج ارسل /start للبحث من جديد.")
    return VIEW_FAMILY
def get_family_details(update: Update, context: CallbackContext):
  #  user_id = context.user_data['user_id']
    query = update.callback_query
    query.answer()
    user_id = update.effective_user.id
    unique_identifier = query.data
    fam_no = context.user_data.get(unique_identifier)
    selected_db = context.user_data.get('selected_db')
    governorate_titles = {
        "erbil.sqlite": "اربيل",
        "anbar.sqlite": "الانبار",
        "babl.sqlite": "بابل",
        "bg.sqlite": "بغداد",
        "balad.sqlite": "بلد",
        "basra.sqlite": "البصرة",
        "bg.sqlite" : "بغداد",
        "duhok.sqlite": "دهوك",
        "qadisiya.sqlite": "الديوانية-القادسية",
        "krbl.sqlite": "كربلاء",
        "bba.sqlite": "بابل",
        "deala.sqlite": "ديالى",
        "zy.sqlite": "ذي قار",
        "sulaymaniyah.sqlite": "السليمانية",
        "salah-aldeen.sqlite": "صلاح الدين",
        "kirkuk.sqlite": "كركوك",
        "muthana.sqlite": "المثنى",
        "mesan.sqlite": "ميسان",
        "najaf.sqlite": "النجف",
        "nineveh.sqlite": "نينوى",
        "wasit.sqlite": "واسط"
    }
    governorate_title = governorate_titles.get(selected_db, "محافظة غير معروفة")
    if fam_no:
        connection = sqlite3.connect(context.user_data.get('selected_db'))
        cursor = connection.cursor()
        cursor.execute("SELECT p_first, p_father, p_grand, seq_no, p_birth FROM person WHERE fam_no = ?", (fam_no,))
        rows = cursor.fetchall()
        if rows:
            family_details = []
            family_size = len(rows)
            for row in sorted(rows, key=lambda x: x[4]):
                p_first = row[0]
                p_father = row[1]
                p_grand = row[2]
                seq_no = str(row[3]).lstrip('0')
                p_birth = int(row[4])
                current_year = datetime.now().year
                age = current_year - int(str(p_birth)[:4])
                family_member_info = (
                    f"الاسم الثلاثي: {p_first} {p_father} {p_grand}\n"
                    f"العمر: {age} سنة\n"
                    f"المواليد: {str(p_birth)[:4]}\n"
                    f"تسلسل الفرد: {seq_no}\n"
                    f"رقم العائلة: {fam_no}\n"
                    f"المحافظة: {governorate_title}\n"
                )
                family_details.append(family_member_info)
            family_info_text = "\n\n".join(family_details)
            final_message = (
                f"عدد أفراد العائلة: {family_size}\n\n"
                f"تفاصيل الأفراد:\n\n"
                f"{family_info_text}"
            )
            context.bot.send_message(chat_id=user_id, text=final_message)
            connection.close()
    else:
        context.bot.send_message(chat_id=user_id, text="لم يتم العثور على نتائج")
    return RESTARTING
def restart(update: Update, context: CallbackContext):
    return start(update, context)
def add(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        update.message.reply_text("ليس لديك إذن لاستخدام هذا الأمر.")
        return ConversationHandler.END
    update.message.reply_text("قم بإرسال الايدي الخاص بالمستخدم الجديد:")
    return ENTER_ID
def save_id(update: Update, context: CallbackContext) -> int:
    user_id = update.message.text
    with open("login.txt", "a") as file:
        file.write(user_id + "\n")
    update.message.reply_text(f"تمت إضافة المستخدم بنجاح. الايدي: {user_id}")
    return ConversationHandler.END
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("تم إلغاء الأمر.")
    return ConversationHandler.END

def main():
    updater = Updater("توكن البوت", use_context=True)

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', xnxx)],
        states={
            SELECT_LOCATION: [CallbackQueryHandler(select_location, pattern='^select_db')],
            SEARCH_PERSON: [MessageHandler(Filters.text & ~Filters.command, search_person)],
            VIEW_FAMILY: [CallbackQueryHandler(get_family_details, pattern='^view_family')],
            RESTARTING: [CommandHandler('start', restart)]
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('count', get_user_count))
    send_message_conversation = ConversationHandler(
        entry_points=[CommandHandler('send', start_send_message)],
        states={
            SELECT_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, select_message)],
    },
    fallbacks=[]
)
    dp.add_handler(send_message_conversation)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add)],
        states={
            ENTER_ID: [MessageHandler(Filters.text & ~Filters.command, save_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # إضافة المحادثة إلى المعالج
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
