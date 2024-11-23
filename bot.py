import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# Bot tokeningizni kiriting
TOKEN = "8154422973:AAHwER2hRlKoJl2XsWd7HAPX2s5k9XQ8V-o"
CHANNEL = "@+sYDzraTgdGw1ZThi"  # Kanal username'ini kiriting
bot_username = "test_123_ball_bot"



bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Admin foydalanuvchi IDlarini belgilash
ADMINS = [6864190303, 7892858628, 1606551]  # Admin foydalanuvchi ID'larni kiriting

# SQLite bilan ishlash uchun bazani ulash
db = sqlite3.connect("users.db")
cursor = db.cursor()

# Ma'lumotlar bazasi jadvalini yaratish
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        points INTEGER DEFAULT 0
    )
""")
db.commit()

# Inline va Reply tugmalar
inline_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL[1:]}")],
        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")],
    ]
)




# Holatlar uchun FSM
class UserForm(StatesGroup):
    waiting_for_name = State()

# Obuna tekshiruvchi funksiya 
async def check_subscription(user_id: int):
    try:
        chat_member = await bot.get_chat_member(chat_id="-1001963360862", user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# /start komandasi
@router.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext):
    # Komandadan kelgan argumentlarni ajratib olish
    args = message.text.split(maxsplit=1)
    inviter_id = None
    if len(args) > 1:
        inviter_id = args[1]
    
    
 # Kanalga obuna bo'lish haqidagi xabar
    await message.answer(
        '''
        Assalomu alaykum va rohmatullohi va barokatuh!

   Professional Psixolog E'zozaxon Sobirovaning  3 kunlik bepul onlayn marafonini o'tazishda yordam beradigan yordamchi botiga xush kelibsiz.

🎁 Ushbu botda  do'stlaringizni botga taklif qilish orqali bir nechta kurslarimga, bundan tashqari mendan konsultatsiya va bir nechta sovg'alarga ega bo'lasiz 🚀

 👉 Hoziroq marafon bo‘ladigan kanalga qo‘shiling, buning uchun
 «KANALGA OBUNA BOʻLISH» tugmasini bosing 
👇🏻👇🏻👇🏻
        ''',
        reply_markup=inline_buttons
    )   
    # Taklif qilgan foydalanuvchi ID'sini saqlash
    if inviter_id:
        await state.update_data(inviter_id=inviter_id)


# Obunani tekshirish callback tugmasi
@router.callback_query(lambda c: c.data == "check_subscription")
async def handle_check_subscription(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        # Foydalanuvchi holatidagi inviter_id qiymatini olish
        data = await state.get_data()
        inviter_id = data.get("inviter_id")

        if inviter_id:
            cursor.execute("SELECT id FROM users WHERE id = ?", (inviter_id,))
            if cursor.fetchone():  # Taklif qilgan foydalanuvchi mavjudligini tekshirish
                cursor.execute("UPDATE users SET points = points + 1 WHERE id = ?", (inviter_id,))
                db.commit()

        # Foydalanuvchini xabardor qilish
        await callback.message.answer("Iltimos, ismingizni yozing:")
        await state.set_state(UserForm.waiting_for_name)

    else:
        await callback.message.answer(
            "Siz hali kanalga obuna bo‘lmadingiz. Iltimos, kanalga obuna bo‘ling!",
            reply_markup=inline_buttons
        )




# Foydalanuvchi ismini olish
# Foydalanuvchi ismini olish
@router.message(UserForm.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.text

    # Ismni ma'lumotlar bazasiga saqlash
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, full_name, username) 
        VALUES (?, ?, ?)
    """, (user_id, full_name, message.from_user.username))
    db.commit()

    # Foydalanuvchi admin ekanligini tekshirish
    is_admin = user_id in ADMINS

    # Foydalanuvchini xabardor qilish va tugmalarni chiqarish
    await message.answer('''🎉 Assalomu alaykum xush kelibsiz!

😊 Sizga ajoyib imkoniyatlarni taqdim etmoqchiman: 
🎁 bepul kurslar, 
🎁 qimmatbaho podkastlar
🎁 shaxsiy konsultatsiyalarga ega bo'lishingiz mumkin! 🎁

🎯 Sovg'ani olish shartlari juda oddiy:

Do‘stlaringiz va yaqinlaringizni ushbu bot va kanalimizga qo‘shing.

Kim ko‘p do‘stlarini qo‘shsa, eng zo‘r sovg‘alarni qo‘lga kiritadi!

📚 Bonus: Kanalimizda BEPUL DARSLIKLAR mavjud! O'zingizni rivojlantirishga shoshiling va yaqinlaringizga ham tavsiya qiling! 🌟

🎁 Sovg'alar olish uchun:

Botimizga va "MEHRLI TARBIYA" bepul onlayn marafoniga dugonangiz yoki tanishlaringizni qo‘shing va maxsus sovg‘alar yutib oling!''', reply_markup=get_main_buttons(is_admin))

    # Taklif postini yuborish {invite_link}
    invite_link = f"https://t.me/{bot_username}?start={user_id}"
    invite_link_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Maxsus linkni olish", callback_data=f"get_invite_link:{user_id}")]
    ]
    )
    await message.answer(
        f'''
        Sizga tayyorlab qoʻygan sovgʻalarim bilan tanishing:

🎁 10 ta ayol tanishingizni qoʻshing va maxsus Zavjingizga atalgan  "SMS TOʻPLAM" ni BEPULga qoʻlga kiriting

🎁 20 ta odam qoʻshsangiz 100% ishlaydigan  "SHUKRONA YOZISH SIRLARI"  darsimni BEPULga olasiz.

🎁 30 ta odam qoʻshsangiz  Konsultatsiyamda beriladigan eng qimmatbaxo texnikalarimdan biri "HALOL SEXR" texnikasini BEPULga olasiz.

🎁  35  ta odam qoʻshsangiz, 250.000 soʻmlik  "MA'SHUQANING 7 KECHASI"  kursini BEPULga olasiz.

🎁  40 ta odam qoʻshsangiz, 250.000 soʻmlil  "ICHKI JOZIBA"  kursini BEPULga olasiz.

🎁  45 ta odam qoʻshsangiz 600.000 soʻmlik "BARAKALI AYOL"  kursini BEPULga olasiz

🎁  50 ta  odam qoʻshsangiz  E'zozaxon Sobirova bilan 500.000 mingli konsultatsiyani qoʻlga kiritasiz.

        🧮 Yaqinlaringizni taklif qilganingizni mana shu bot hisoblab boradi.
Har bir qo‘shgan insoningiz sizga 1 ball olib keladi!

🎁 Ballaringiz ko‘paygani sari sovg‘alar egasi bo‘lish imkoningiz ham oshadi. 
Qancha koʻp ball boʻlsa shuncha koʻp sovgʻa boʻladi

(Diqqat ushbu o’yin faqat ayol va qizlar uchun. Erkaklar qatnasha olishmaydi ❌)

        ''',
        reply_markup=invite_link_button
    )
    

    # Holatni tozalash
    await state.clear()

# Reply tugmalar (asosiy tugmalar)
def get_main_buttons(is_admin=False):
    buttons = [
        [KeyboardButton(text="🎗 Ballarim")],
        [KeyboardButton(text="📃 Taklif Linki")]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="📋 Foydalanuvchilar ro'yxati")])  # Faqat adminlar uchun
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)



# Ballarni ko‘rsatish
@router.message(lambda message: message.text == "🎗 Ballarim")
async def show_points(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT points FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    # Agar foydalanuvchi bazada mavjud bo'lmasa, ball 0 deb hisoblanadi
    points = result[0] if result else 0
    await message.answer(f"Sizda {points} ball mavjud.")


# Taklif qilish havolasi
# Taklif qilish havolasi
@router.message(lambda message: message.text == "📃 Taklif Linki")
async def send_invitation(message: types.Message):
    user_id = message.from_user.id
    invite_link = f"https://t.me/{bot_username}?start={user_id}"
    await message.answer(
        f'''
"Farzandingizni urmasdan, baqirmasdan buyuk shaxs qilib tarbiyalashni xohlaysizmi?"

Unda bu marafon aynan siz uchun! 🫵

📅 26, 27, 28-noyabr kunlari bo‘lib o‘tadigan Professional Psixolog E'zozaxon Sobirovaning 
"MEHRLI TARBIYA" bepul online marafoniga taklif qilamiz!

Farzandingizning kelajagini baxtli va muvaffaqiyatli qilish uchun kerakli bilim va ko‘nikmalarni o‘rganing.
📌 Joylar cheklangan – bugunoq ro‘yxatdan o‘ting!

Sizning maxsus linkingiz 👇👇👇

{invite_link}
        ''',)

# Inline tugmadagi "Havolamni ko'rish" callback funksiyasi
@router.callback_query(lambda c: c.data.startswith("get_invite_link"))
async def handle_invite_link(callback: types.CallbackQuery):
    user_id = callback.data.split(":")[1]
    invite_link = f"https://t.me/{bot_username}?start={user_id}"
    await callback.message.answer(f'''🤔Farzandingiz bilan munosabatlaringiz yomonmi?

😱Jahlingiz chiqqanda uni urib, baqirib yoki kimlarnidir alamini farzandingizdan olasizmi?

🔥Katta boʻlganida sizdan 1 umr yoshlikdagi travmalar sababli ich ichidan norozi boʻlishini, va u ham ota ona boʻlganida xuddi sizdek farzandlariga jazo bilan tarbiyalashini bilasizmi?

💯Bunga hoziroq chek qoʻying va avlodlaringiz sizdan boshlab oʻzgarsin!

🙋🏻‍♀️Qanday qilib deysizmi?

Hoziroq 26,27,28- noyabr kunlari boʻlib oʻtadigan mutlaqo bepul "MEHRLI TARBIYA" marafoniga qoʻshiling!
                                 
    Sizning maxsus linkingiz 👇👇👇                              
    \n{invite_link}'''
    )
    await callback.answer()

# Foydalanuvchi ro‘yxatini ko‘rish (faqat adminlar uchun)
@router.message(lambda message: message.text == "📋 Foydalanuvchilar ro'yxati")
async def list_users(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.answer("Ushbu buyruq faqat adminlar uchun.")
        return

    # Foydalanuvchi ma'lumotlarini bazadan olish
    cursor.execute("SELECT full_name, username, points FROM users")
    users = cursor.fetchall()
    if not users:
        await message.answer("Hali hech kim ro'yhatdan o'tmagan!")
        return

    # Foydalanuvchi ro'yxatini shakllantirish
    response = "📋 Foydalanuvchilar ro'yxati:\n\n"
    for user in users:
        full_name, username, points = user
        username = f"@{username}" if username else "Noma'lum"
        response += f"👤 {full_name} ({username}) - {points} ball\n"

    await message.answer(response)

# Botni ishga tushirish
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




