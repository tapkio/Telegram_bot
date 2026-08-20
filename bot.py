import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ===== ТВОЙ ТОКЕН =====
BOT_TOKEN = "8882978541:AAGy6mD9eog1lPL8MI5iRxbdv71x3AoADlg"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаём бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ===== ВСЕ ТВОИ NFT (СПИСОК) =====
NFT_LIST = [
    {"name": "🍀 JellyBunny", "link": "https://t.me/nft/JellyBunny-107325"},
    {"name": "⭐ IonGem", "link": "https://t.me/nft/IonGem-2953"},
    {"name": "🍦 IceCream", "link": "https://t.me/nft/ViceCream-189539"},
    {"name": "💎 SnoopDogg", "link": "https://t.me/nft/SnoopDogg-345937"},
    {"name": "🧸 ToyBear", "link": "https://t.me/nft/ToyBear-18504"},
    {"name": "🚬 VintageCigar", "link": "https://t.me/nft/SnoopCigar-25711"},
    {"name": "⌚ SwissWatch", "link": "https://t.me/nft/SwissWatch-20201"},
    {"name": "💀 ElectricSkull", "link": "https://t.me/nft/ElectricSkull-1727"},
    {"name": "💩 HappyBrownie", "link": "https://t.me/nft/HappyBrownie-225808"},
    {"name": "🐱 ScaredCat", "link": "https://t.me/nft/ScaredCat-18626"},
    {"name": "🖊️ FinePen", "link": "https://t.me/nft/FinePen-16472"},
    {"name": "🍑 PreciousPeach", "link": "https://t.me/nft/PreciousPeach-2730"},
    {"name": "🏺 RestlessJar", "link": "https://t.me/nft/RestlessJar-22982"},
    {"name": "🎒 MoodPack", "link": "https://t.me/nft/MoodPack-157479"},
    {"name": "🗽 LibertyFigure", "link": "https://t.me/nft/LibertyFigure-144982"},
]

# ===== КНОПКИ =====
dice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Бросить кубик", callback_data="roll_dice")]
    ]
)

# ===== ВРЕМЕННОЕ ХРАНИЛИЩЕ =====
user_data = {}

# ===== КОМАНДА /start =====
@dp.message(Command("start"))
async def start_command(message: types.Message):
    try:
        photo = FSInputFile("gifft.jpg")
        caption = "Брось кубик и получи подарок👇🎁"
        await message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=dice_keyboard
        )
    except Exception as e:
        print(f"Ошибка при отправке картинки: {e}")
        await message.answer(
            "Брось кубик и получи подарок👇🎁",
            reply_markup=dice_keyboard
        )

# ===== ОБРАБОТЧИК КНОПКИ "Бросить кубик" =====
@dp.callback_query(F.data == "roll_dice")
async def roll_dice(callback: types.CallbackQuery):
    await bot.send_dice(
        chat_id=callback.message.chat.id,
        emoji="🎲"
    )
    
    await asyncio.sleep(4)
    
    selected_nft = random.choice(NFT_LIST)
    gift_name = selected_nft["name"]
    nft_link = selected_nft["link"]
    
    claim_button = InlineKeyboardButton(
        text="🎁 Забрать подарок",
        callback_data=f"claim_{NFT_LIST.index(selected_nft)}"
    )
    claim_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[claim_button]]
    )
    
    response_text = (
        f"🎉 Вам выпал подарок: <b>{gift_name}</b>\n"
        f"🔗 <a href='{nft_link}'>Ссылка на NFT</a>"
    )
    
    await callback.message.answer(
        text=response_text,
        reply_markup=claim_keyboard
    )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

# ===== ОБРАБОТЧИК КНОПКИ "Забрать подарок" =====
@dp.callback_query(F.data.startswith("claim_"))
async def claim_gift(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[1])
    gift_name = NFT_LIST[index]["name"]
    nft_link = NFT_LIST[index]["link"]
    
    user_id = callback.from_user.id
    user_data[user_id] = {
        "step": "waiting_screenshot",
        "screenshots": [],
        "gift_name": gift_name,
        "nft_link": nft_link
    }
    
    instruction_text = (
        f"👮‍♀️ <b>Для получения {gift_name} необходимо:</b>\n\n"
        f"1️⃣ Написать <b>\"работает ура\"</b> под комментарием, с которого узнали о нас, и лайкнуть его\n\n"
        f"📤 <b>Отправьте боту скриншот выполнения</b>"
    )
    
    await callback.message.answer(
        text=instruction_text,
        parse_mode=ParseMode.HTML
    )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("✅ Инструкция отправлена!")

# ===== ОБРАБОТЧИК СКРИНШОТОВ =====
@dp.message(F.photo)
async def handle_screenshot(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.answer(
            "❌ Сначала нажмите 'Забрать подарок'!",
            parse_mode=ParseMode.HTML
        )
        return
    
    if user_data[user_id]["step"] == "waiting_screenshot":
        user_data[user_id]["step"] = "waiting_comments"
        
        next_step_text = (
            f"🎯 <b>Осталось совсем чуть-чуть:</b>\n\n"
            f"2️⃣ Написать под 10 любыми видео:\n"
            f"<b>«HokageGiftBot лучший просто»</b>\n\n"
            f"📤 <b>После этого отправьте 10 скриншотов</b>"
        )
        
        await message.answer(
            text=next_step_text,
            parse_mode=ParseMode.HTML
        )
        
    elif user_data[user_id]["step"] == "waiting_comments":
        user_data[user_id]["step"] = "waiting_bots"
        
        third_step_text = (
            f"🎯 <b>3️⃣ и последнее:</b>\n\n"
            f"Перейди в ботов и выполни <b>5 заданий</b> в каждом, "
            f"они финансируют часть подарков взамен на пользователей\n\n"
            f"👮‍♀️ <b>Добавь их в архив и выключи звук, чтобы не мешали!</b>"
        )
        
        await message.answer(
            text=third_step_text,
            parse_mode=ParseMode.HTML
        )
        
        # ===== СПОНСОРЫ =====
        sponsors = [
            "https://clck.ru/3VHuJT",
            "https://clck.ru/3VHuJw",
            "https://clck.ru/3VHuKV",
            "https://clck.ru/3VHuKf",
            "https://clck.ru/3VHuKx",
            "https://clck.ru/3VHuLB",
            "https://clck.ru/3VHuLT",
            "https://clck.ru/3VHuLm",
            "https://clck.ru/3VHuM2",
            "https://clck.ru/3VHuMA",
            "https://clck.ru/3VHuME",
            "https://clck.ru/3VHuMU",
            "https://clck.ru/3VHuMf",
            "https://clck.ru/3VHuMp"
        ]
        
        selected_sponsors = random.sample(sponsors, 5)
        
        sponsors_text = "👩‍🌾 <b>Держи спонсоров</b> 👇\n\n"
        for i, link in enumerate(selected_sponsors, 1):
            sponsors_text += f"{i}. <a href='{link}'>Спонсор {i}</a>\n"
        
        # ===== КНОПКА "ВЫПОЛНЕНО" =====
        done_button = InlineKeyboardButton(
            text="✅ Выполнено",
            callback_data="done_sponsors"
        )
        done_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[done_button]]
        )
        
        await message.answer(
            text=sponsors_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=done_keyboard
        )

# ===== ОБРАБОТЧИК КНОПКИ "ВЫПОЛНЕНО" =====
@dp.callback_query(F.data == "done_sponsors")
async def done_sponsors(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_data:
        await callback.answer("❌ Ошибка!", show_alert=True)
        return
    
    gift_name = user_data[user_id]["gift_name"]
    nft_link = user_data[user_id]["nft_link"]
    
    final_text = (
        f"🎉 <b>Поздравляем! Вы выполнили все условия!</b>\n\n"
        f"🎁 Ваш подарок: <b>{gift_name}</b>\n"
        f"🔗 <a href='{nft_link}'>Ссылка на NFT</a>\n\n"
        f"⏳ <b>NFT скоро вам отправят!</b>\n"
        f"✅ Ожидайте, администратор проверит выполнение."
    )
    
    await callback.message.answer(
        text=final_text,
        parse_mode=ParseMode.HTML
    )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    
    del user_data[user_id]
    
    await callback.answer("✅ Готово!")

# ===== ОБРАБОТЧИК ТЕКСТА =====
@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.answer(
        "🤖 Используйте кнопки или отправьте скриншот.",
        parse_mode=ParseMode.HTML
    )

# ===== ЗАПУСК =====
async def main():
    print("✅ Бот запущен!")
    print(f"📦 Всего NFT: {len(NFT_LIST)}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
