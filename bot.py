import os
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8214295509:AAFvMKakkVFyP_F3CFKPeU-kY8y5bngWBpw")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ============ ДАННЫЕ ============

TOPICS_MODES = [
    "Шд", "Нокаунт", "Броулбол", "Дуэль", "Бой с боссом",
    "Награда за поимку", "Захват кристаллов", "Ранговый бой"
]

TOPICS_CHARACTERS = [
    "Наджия", "Мортис", "Кланси", "Хэнк", "Биби", "Даг", "Сириус", "Булл",
    "Драко", "Чак", "Мико", "Джанет", "Алли", "Бо", "Анджело", "Р-Т",
    "Джей-Янг", "Бастер", "Корделиус", "Мэг", "Зигги", "Ворон", "Эмз",
    "Леон", "Кит", "Люми", "Раффс", "Глоуу", "Мэнди", "Честер", "Мина",
    "Отис", "Пайпер", "Биа", "Финкс", "Чарли", "Мипл", "Сэм", "Мо",
    "Нани", "Пирс", "Шелли", "Мелоди", "Шейд", "Джуджу", "Перл", "Эмбер",
    "Лола", "Кадзэ", "Рико", "Карл", "Грей", "Фэнг", "Эдгар", "Гейл",
    "Тара", "Транк", "Лили", "Стью", "Грифф", "Мэйзи", "Гас", "Кольт",
    "Спайк", "Олли", "Ева", "Бонни", "Фрэнк", "Байрон", "Брок", "Уиллоу",
    "Кэндзи", "Белль", "Мистер Пи", "Тик", "Пэм", "Сэнди", "Нита",
    "Колетт", "Поко", "Базз", "Гром", "Даррил", "Джесси", "Макс", "Джин",
    "Джеки", "Лу", "Роза", "Скрик", "Сёрдж", "Пенни", "Спраут", "Гиги",
    "Эль Примо", "Эш", "Динамайк", "8-БИТ", "Ларри и Лоури", "Берри", "Барли"
]

ALL_TOPICS = TOPICS_MODES + TOPICS_CHARACTERS

RULES_TEXT = (
    "🕵️ <b>Правила игры «Угадай кто шпион»</b>\n\n"
    "1️⃣ Всем игрокам раздаётся одна и та же тема (слово), кроме шпиона — он не знает тему.\n"
    "2️⃣ Игроки по очереди пишут по <b>одному</b> сообщению (подсказку/вопрос), "
    "чтобы понять, кто шпион, но при этом не раскрыть тему шпиону.\n"
    "3️⃣ Проходит 3 круга обсуждения.\n"
    "4️⃣ После 3 кругов начинается голосование — каждый голосует за того, кого считает шпионом "
    "(за себя голосовать нельзя!).\n"
    "5️⃣ Побеждает тот, кто угадает шпиона. Шпион побеждает, если его не раскроют!\n\n"
    "🎮 Темы: режимы и персонажи Brawl Stars."
)

# ============ ХРАНИЛИЩА ============

# Настройки пользователей: {user_id: {"nick": str, "spy_count": int}}
user_settings = {}

# Комнаты онлайн: {room_id: {...}}
rooms = {}
room_id_counter = 1

# Маппинг user -> room
user_room = {}


# ============ СОСТОЯНИЯ FSM ============

class SettingsStates(StatesGroup):
    waiting_nick = State()
    waiting_spy_count = State()


class LocalGameStates(StatesGroup):
    choosing_players = State()
    choosing_topic_type = State()
    waiting_manual_topic = State()
    showing_roles = State()


class OnlineStates(StatesGroup):
    waiting_room_code = State()
    in_room = State()
    game_message = State()
    voting = State()


# ============ КЛАВИАТУРЫ ============

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Онлайн"), KeyboardButton(text="📱 Один телефон")],
            [KeyboardButton(text="📞 Поддержка/Предложка"), KeyboardButton(text="⚙️ Настройки")]
        ],
        resize_keyboard=True
    )


def online_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Вступить в свободную комнату", callback_data="join_open")],
        [InlineKeyboardButton(text="🔑 Вступить в комнату по коду", callback_data="join_code")],
        [InlineKeyboardButton(text="➕ Создать свободную комнату", callback_data="create_open")],
        [InlineKeyboardButton(text="🔒 Создать закрытую комнату", callback_data="create_closed")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])


def settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ник", callback_data="set_nick")],
        [InlineKeyboardButton(text="🕵️ Кол-во шпионов (1 телефон)", callback_data="set_spy_count")],
        [InlineKeyboardButton(text="📖 Правила игры", callback_data="show_rules")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])


def support_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Написать", url="https://t.me/Suprisemotherrfucker")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])


def players_count_keyboard():
    buttons = []
    row = []
    for i in range(3, 9):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"local_players_{i}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def topic_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Рандом", callback_data="topic_random")],
        [InlineKeyboardButton(text="✏️ Вручную", callback_data="topic_manual")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])


def spy_count_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="spycount_1"),
            InlineKeyboardButton(text="2", callback_data="spycount_2"),
            InlineKeyboardButton(text="3", callback_data="spycount_3")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_settings")]
    ])


# ============ УТИЛИТЫ ============

def get_user_nick(user_id):
    s = user_settings.get(user_id, {})
    return s.get("nick", None)


def get_user_spy_count(user_id):
    s = user_settings.get(user_id, {})
    return s.get("spy_count", 1)


def get_random_topic():
    return random.choice(ALL_TOPICS)


def generate_room_code():
    return random.randint(100, 999)


def find_open_room():
    for rid, room in rooms.items():
        if (room["type"] == "open"
                and not room["started"]
                and len(room["players"]) < 8):
            return rid
    return None


def get_room_info_text(room):
    players_text = "\n".join(
        [f"  {'👑' if p == room['leader'] else '👤'} {get_user_nick(p) or p}"
         for p in room["players"]]
    )
    status = "⏳ Ожидание" if not room["started"] else "🎮 Игра идёт"
    rtype = "🔓 Открытая" if room["type"] == "open" else f"🔒 Закрытая (код: {room.get('code', '?')})"
    return (
        f"🏠 <b>Комната #{room['id']}</b>\n"
        f"Тип: {rtype}\n"
        f"Статус: {status}\n"
        f"Игроки ({len(room['players'])}/8):\n{players_text}"
    )


def room_lobby_keyboard(room, user_id):
    buttons = []
    if user_id == room["leader"] and len(room["players"]) >= 3 and not room["started"]:
        buttons.append([InlineKeyboardButton(text="🚀 Начать игру", callback_data=f"start_game_{room['id']}")])
    buttons.append([InlineKeyboardButton(text="🚪 Покинуть комнату", callback_data=f"leave_room_{room['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def notify_room(room, text, keyboard_func=None, exclude=None):
    for p in room["players"]:
        if exclude and p in exclude:
            continue
        try:
            kb = keyboard_func(room, p) if keyboard_func else None
            await bot.send_message(p, text, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            logging.error(f"Ошибка отправки {p}: {e}")


async def send_room_update(room):
    text = get_room_info_text(room)
    for p in room["players"]:
        try:
            kb = room_lobby_keyboard(room, p)
            await bot.send_message(p, text, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            logging.error(f"Ошибка отправки {p}: {e}")


# ============ СТАРТ ============

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if user_id not in user_settings:
        user_settings[user_id] = {"nick": None, "spy_count": 1}
    await message.answer(
        "🕵️ <b>Добро пожаловать в игру «Угадай кто шпион»!</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# ============ ГЛАВНОЕ МЕНЮ (Reply кнопки) ============

@dp.message(F.text == "🌐 Онлайн")
async def menu_online(message: types.Message, state: FSMContext):
    await state.clear()
    nick = get_user_nick(message.from_user.id)
    if not nick:
        await message.answer(
            "⚠️ Сначала установите ник в настройках!",
            reply_markup=main_keyboard()
        )
        return
    await message.answer("🌐 <b>Онлайн режим</b>\nВыберите действие:",
                         parse_mode="HTML", reply_markup=online_keyboard())


@dp.message(F.text == "📱 Один телефон")
async def menu_local(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("📱 <b>Игра с одного телефона</b>\nВыберите количество игроков:",
                         parse_mode="HTML", reply_markup=players_count_keyboard())


@dp.message(F.text == "📞 Поддержка/Предложка")
async def menu_support(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("📞 <b>Поддержка / Предложка</b>\nНажмите кнопку ниже, чтобы написать оператору:",
                         parse_mode="HTML", reply_markup=support_keyboard())


@dp.message(F.text == "⚙️ Настройки")
async def menu_settings(message: types.Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    s = user_settings.get(uid, {"nick": None, "spy_count": 1})
    nick = s.get("nick", "Не установлен")
    sc = s.get("spy_count", 1)
    await message.answer(
        f"⚙️ <b>Настройки</b>\n\n"
        f"Ник: <b>{nick or 'Не установлен'}</b>\n"
        f"Кол-во шпионов (1 телефон): <b>{sc}</b>",
        parse_mode="HTML",
        reply_markup=settings_keyboard()
    )


# ============ CALLBACK: Назад ============

@dp.callback_query(F.data == "back_main")
async def cb_back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🕵️ Главное меню. Используйте кнопки ниже.")
    await callback.answer()


@dp.callback_query(F.data == "back_settings")
async def cb_back_settings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    uid = callback.from_user.id
    s = user_settings.get(uid, {"nick": None, "spy_count": 1})
    nick = s.get("nick", "Не установлен")
    sc = s.get("spy_count", 1)
    await callback.message.edit_text(
        f"⚙️ <b>Настройки</b>\n\n"
        f"Ник: <b>{nick or 'Не установлен'}</b>\n"
        f"Кол-во шпионов (1 телефон): <b>{sc}</b>",
        parse_mode="HTML",
        reply_markup=settings_keyboard()
    )
    await callback.answer()


# ============ НАСТРОЙКИ ============

@dp.callback_query(F.data == "set_nick")
async def cb_set_nick(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите ваш ник (до 20 символов):")
    await state.set_state(SettingsStates.waiting_nick)
    await callback.answer()


@dp.message(SettingsStates.waiting_nick)
async def process_nick(message: types.Message, state: FSMContext):
    nick = message.text.strip()[:20]
    if not nick:
        await message.answer("❌ Ник не может быть пустым. Попробуйте ещё раз:")
        return
    uid = message.from_user.id
    if uid not in user_settings:
        user_settings[uid] = {"nick": None, "spy_count": 1}
    user_settings[uid]["nick"] = nick
    await state.clear()
    await message.answer(
        f"✅ Ник установлен: <b>{nick}</b>",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data == "set_spy_count")
async def cb_set_spy_count(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🕵️ Выберите количество шпионов для игры с одного телефона (1-3):\n\n"
        "⚠️ Если игроков мало, бот автоматически снизит до 1.",
        reply_markup=spy_count_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("spycount_"))
async def cb_spycount(callback: CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[1])
    uid = callback.from_user.id
    if uid not in user_settings:
        user_settings[uid] = {"nick": None, "spy_count": 1}
    user_settings[uid]["spy_count"] = count
    await callback.message.edit_text(f"✅ Количество шпионов установлено: <b>{count}</b>", parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "show_rules")
async def cb_show_rules(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        RULES_TEXT,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_settings")]
        ])
    )
    await callback.answer()


# ============ ИГРА С ОДНОГО ТЕЛЕФОНА ============

@dp.callback_query(F.data.startswith("local_players_"))
async def cb_local_players(callback: CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[2])
    await state.update_data(local_players=count, local_current=0)
    await callback.message.edit_text(
        f"👥 Игроков: <b>{count}</b>\nВыберите тему:",
        parse_mode="HTML",
        reply_markup=topic_type_keyboard()
    )
    await state.set_state(LocalGameStates.choosing_topic_type)
    await callback.answer()


@dp.callback_query(F.data == "topic_random", LocalGameStates.choosing_topic_type)
async def cb_topic_random(callback: CallbackQuery, state: FSMContext):
    topic = get_random_topic()
    data = await state.get_data()
    players_count = data["local_players"]
    uid = callback.from_user.id
    spy_count_setting = get_user_spy_count(uid)

    # Автоматическая корректировка
    if spy_count_setting >= players_count:
        spy_count_setting = 1
    if players_count <= 3 and spy_count_setting > 1:
        spy_count_setting = 1

    spies = random.sample(range(1, players_count + 1), spy_count_setting)

    await state.update_data(
        local_topic=topic,
        local_spies=spies,
        local_current=1,
        local_spy_count=spy_count_setting
    )
    await state.set_state(LocalGameStates.showing_roles)

    spy_warn = ""
    if spy_count_setting != get_user_spy_count(uid):
        spy_warn = f"\n⚠️ Кол-во шпионов снижено до {spy_count_setting} (мало игроков)."

    await callback.message.edit_text(
        f"🎲 Тема выбрана!{spy_warn}\n\n📱 Передайте телефон <b>Игроку 1</b>.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👀 Посмотреть тему", callback_data="local_show_role")]
        ])
    )
    await callback.answer()


@dp.callback_query(F.data == "topic_manual", LocalGameStates.choosing_topic_type)
async def cb_topic_manual(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✏️ Пусть человек, который <b>НЕ играет</b>, введёт тему:",
        parse_mode="HTML"
    )
    await state.set_state(LocalGameStates.waiting_manual_topic)
    await callback.answer()


@dp.message(LocalGameStates.waiting_manual_topic)
async def process_manual_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    if not topic:
        await message.answer("❌ Тема не может быть пустой!")
        return

    data = await state.get_data()
    players_count = data["local_players"]
    uid = message.from_user.id
    spy_count_setting = get_user_spy_count(uid)

    if spy_count_setting >= players_count:
        spy_count_setting = 1
    if players_count <= 3 and spy_count_setting > 1:
        spy_count_setting = 1

    spies = random.sample(range(1, players_count + 1), spy_count_setting)

    await state.update_data(
        local_topic=topic,
        local_spies=spies,
        local_current=1,
        local_spy_count=spy_count_setting
    )
    await state.set_state(LocalGameStates.showing_roles)

    spy_warn = ""
    if spy_count_setting != get_user_spy_count(uid):
        spy_warn = f"\n⚠️ Кол-во шпионов снижено до {spy_count_setting} (мало игроков)."

    await message.answer(
        f"✅ Тема принята!{spy_warn}\n\n📱 Передайте телефон <b>Игроку 1</b>.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👀 Посмотреть тему", callback_data="local_show_role")]
        ])
    )


@dp.callback_query(F.data == "local_show_role", LocalGameStates.showing_roles)
async def cb_local_show_role(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data["local_current"]
    spies = data["local_spies"]
    topic = data["local_topic"]

    if current in spies:
        text = f"🕵️ <b>Игрок {current}</b>\n\n❗ Вы — <b>ШПИОН</b>!\nВы не знаете тему."
    else:
        text = f"👤 <b>Игрок {current}</b>\n\nТема: <b>{topic}</b>"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Посмотрел", callback_data="local_seen_role")]
        ])
    )
    await callback.answer()


@dp.callback_query(F.data == "local_seen_role", LocalGameStates.showing_roles)
async def cb_local_seen_role(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data["local_current"]
    players_count = data["local_players"]

    if current >= players_count:
        # Все посмотрели
        await callback.message.edit_text(
            "✅ Все игроки посмотрели свои роли!\n\n"
            "Начинайте обсуждение! Когда закончите — нажмите кнопку.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Новая игра", callback_data="local_new_game")],
                [InlineKeyboardButton(text="❌ Закрыть", callback_data="local_close")]
            ])
        )
    else:
        next_p = current + 1
        await state.update_data(local_current=next_p)
        await callback.message.edit_text(
            f"📱 Передайте телефон <b>Игроку {next_p}</b>.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👀 Посмотреть тему", callback_data="local_show_role")]
            ])
        )
    await callback.answer()


@dp.callback_query(F.data == "local_new_game")
async def cb_local_new_game(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topic = data.get("local_topic", "?")
    spies = data.get("local_spies", [])
    spies_text = ", ".join([f"Игрок {s}" for s in spies])

    await callback.message.edit_text(
        f"🏁 <b>Итоги раунда:</b>\n\n"
        f"Тема: <b>{topic}</b>\n"
        f"🕵️ Шпион(ы): <b>{spies_text}</b>\n\n"
        f"Выберите тему для новой игры:",
        parse_mode="HTML",
        reply_markup=topic_type_keyboard()
    )
    await state.update_data(local_current=0)
    await state.set_state(LocalGameStates.choosing_topic_type)
    await callback.answer()


@dp.callback_query(F.data == "local_close")
async def cb_local_close(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topic = data.get("local_topic", "?")
    spies = data.get("local_spies", [])
    spies_text = ", ".join([f"Игрок {s}" for s in spies])

    await state.clear()
    await callback.message.edit_text(
        f"🏁 <b>Итоги раунда:</b>\n\n"
        f"Тема: <b>{topic}</b>\n"
        f"🕵️ Шпион(ы): <b>{spies_text}</b>\n\n"
        f"Игра закрыта. Возвращаемся в главное меню.",
        parse_mode="HTML"
    )
    await callback.answer()


# ============ ОНЛАЙН: СОЗДАНИЕ / ВСТУПЛЕНИЕ ============

@dp.callback_query(F.data == "create_open")
async def cb_create_open(callback: CallbackQuery, state: FSMContext):
    global room_id_counter
    uid = callback.from_user.id

    if uid in user_room:
        await callback.answer("Вы уже в комнате!", show_alert=True)
        return

    room = {
        "id": room_id_counter,
        "type": "open",
        "code": None,
        "leader": uid,
        "players": [uid],
        "started": False,
        "topic": None,
        "spies": [],
        "turn_order": [],
        "current_turn": 0,
        "round": 0,
        "messages": {},
        "votes": {},
        "lobby_over": False
    }
    rooms[room_id_counter] = room
    user_room[uid] = room_id_counter
    room_id_counter += 1

    await callback.message.edit_text(
        get_room_info_text(room),
        parse_mode="HTML",
        reply_markup=room_lobby_keyboard(room, uid)
    )
    await state.set_state(OnlineStates.in_room)
    await callback.answer("Комната создана!")


@dp.callback_query(F.data == "create_closed")
async def cb_create_closed(callback: CallbackQuery, state: FSMContext):
    global room_id_counter
    uid = callback.from_user.id

    if uid in user_room:
        await callback.answer("Вы уже в комнате!", show_alert=True)
        return

    code = generate_room_code()
    room = {
        "id": room_id_counter,
        "type": "closed",
        "code": code,
        "leader": uid,
        "players": [uid],
        "started": False,
        "topic": None,
        "spies": [],
        "turn_order": [],
        "current_turn": 0,
        "round": 0,
        "messages": {},
        "votes": {},
        "lobby_over": False
    }
    rooms[room_id_counter] = room
    user_room[uid] = room_id_counter
    room_id_counter += 1

    await callback.message.edit_text(
        f"🔒 Комната создана!\n\n"
        f"<b>Код для входа: {code}</b>\n\n" +
        get_room_info_text(room),
        parse_mode="HTML",
        reply_markup=room_lobby_keyboard(room, uid)
    )
    await state.set_state(OnlineStates.in_room)
    await callback.answer("Закрытая комната создана!")


@dp.callback_query(F.data == "join_open")
async def cb_join_open(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id

    if uid in user_room:
        await callback.answer("Вы уже в комнате!", show_alert=True)
        return

    rid = find_open_room()
    if rid is None:
        await callback.answer("Нет доступных открытых комнат!", show_alert=True)
        return

    room = rooms[rid]
    room["players"].append(uid)
    user_room[uid] = rid

    await callback.message.edit_text("✅ Вы вступили в комнату!")
    await send_room_update(room)
    await state.set_state(OnlineStates.in_room)
    await callback.answer()


@dp.callback_query(F.data == "join_code")
async def cb_join_code(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    if uid in user_room:
        await callback.answer("Вы уже в комнате!", show_alert=True)
        return

    await callback.message.edit_text("🔑 Введите 3-значный код комнаты:")
    await state.set_state(OnlineStates.waiting_room_code)
    await callback.answer()


@dp.message(OnlineStates.waiting_room_code)
async def process_room_code(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    text = message.text.strip()

    if not text.isdigit() or len(text) != 3:
        await message.answer("❌ Введите 3-значный числовой код:")
        return

    code = int(text)
    found_room = None
    for rid, room in rooms.items():
        if room["type"] == "closed" and room["code"] == code and not room["started"] and len(room["players"]) < 8:
            found_room = room
            break

    if not found_room:
        await message.answer("❌ Комната не найдена или уже заполнена. Попробуйте ещё раз:")
        return

    found_room["players"].append(uid)
    user_room[uid] = found_room["id"]
    await state.set_state(OnlineStates.in_room)
    await message.answer("✅ Вы вступили в комнату!")
    await send_room_update(found_room)


# ============ ОНЛАЙН: ЛОББИ ============

@dp.callback_query(F.data.startswith("leave_room_"))
async def cb_leave_room(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    rid_str = callback.data.split("_")[2]
    rid = int(rid_str)

    if rid not in rooms:
        await callback.answer("Комната не найдена!", show_alert=True)
        return

    room = rooms[rid]

    if uid in room["players"]:
        room["players"].remove(uid)
    if uid in user_room:
        del user_room[uid]

    await state.clear()
    await callback.message.edit_text("🚪 Вы покинули комнату.", reply_markup=None)

    if len(room["players"]) == 0:
        del rooms[rid]
        await callback.answer("Комната удалена.")
        return

    # Если лидер ушёл
    if room["leader"] == uid:
        room["leader"] = room["players"][0]

    await send_room_update(room)
    await callback.answer("Вы покинули комнату.")


# ============ ОНЛАЙН: СТАРТ ИГРЫ ============

@dp.callback_query(F.data.startswith("start_game_"))
async def cb_start_game(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    rid = int(callback.data.split("_")[2])

    if rid not in rooms:
        await callback.answer("Комната не найдена!", show_alert=True)
        return

    room = rooms[rid]

    if uid != room["leader"]:
        await callback.answer("Только лидер может начать!", show_alert=True)
        return

    if len(room["players"]) < 3:
        await callback.answer("Нужно минимум 3 игрока!", show_alert=True)
        return

    # Настройка игры
    room["started"] = True
    room["topic"] = get_random_topic()
    room["spies"] = random.sample(room["players"], 1)  # 1 шпион в онлайне
    room["turn_order"] = room["players"].copy()
    random.shuffle(room["turn_order"])
    room["current_turn"] = 0
    room["round"] = 1
    room["messages"] = {}
    room["votes"] = {}
    room["lobby_over"] = False

    # Раздача ролей
    for p in room["players"]:
        if p in room["spies"]:
            try:
                await bot.send_message(
                    p,
                    "🕵️ <b>Вы — ШПИОН!</b>\n"
                    "Вы не знаете тему. Попытайтесь вычислить её из сообщений других игроков.\n"
                    "Не выдайте себя!",
                    parse_mode="HTML"
                )
            except:
                pass
        else:
            try:
                await bot.send_message(
                    p,
                    f"👤 <b>Вы — мирный житель.</b>\n"
                    f"Тема: <b>{room['topic']}</b>\n\n"
                    f"Дайте подсказку, но не раскройте тему шпиону!",
                    parse_mode="HTML"
                )
            except:
                pass

    # Начинаем первый ход
    await announce_turn(room)
    await callback.answer("Игра началась!")


async def announce_turn(room):
    rid = room["id"]
    current_player = room["turn_order"][room["current_turn"]]
    nick = get_user_nick(current_player) or str(current_player)
    round_num = room["round"]

    text = (
        f"🔄 <b>Раунд {round_num}/3</b>\n\n"
        f"Сейчас ход: <b>{nick}</b>\n"
        f"⚠️ Напишите <b>ровно 1 сообщение</b>!"
    )

    for p in room["players"]:
        try:
            if p == current_player:
                await bot.send_message(
                    p,
                    f"📝 <b>Ваш ход!</b> (Раунд {round_num}/3)\n"
                    f"Напишите <b>одно</b> сообщение. Другие игроки увидят его.",
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(p, text, parse_mode="HTML")
        except:
            pass


# ============ ОБРАБОТКА СООБЩЕНИЙ В ИГРЕ ============

@dp.message(OnlineStates.in_room)
async def handle_in_room_message(message: types.Message, state: FSMContext):
    uid = message.from_user.id

    if uid not in user_room:
        return

    rid = user_room[uid]
    if rid not in rooms:
        return

    room = rooms[rid]

    if not room["started"]:
        return

    if room.get("lobby_over"):
        return

    # Проверяем голосование
    if room.get("voting_phase"):
        return

    # Проверяем что сейчас ход этого игрока
    if room["current_turn"] >= len(room["turn_order"]):
        return

    current_player = room["turn_order"][room["current_turn"]]
    if uid != current_player:
        await message.answer("⚠️ Сейчас не ваш ход! Дождитесь своей очереди.")
        return

    # Сохраняем сообщение
    nick = get_user_nick(uid) or str(uid)
    msg_text = message.text or "(пусто)"

    # Рассылаем сообщение всем
    for p in room["players"]:
        try:
            await bot.send_message(
                p,
                f"💬 <b>{nick}</b>: {msg_text}",
                parse_mode="HTML"
            )
        except:
            pass

    # Следующий ход
    room["current_turn"] += 1

    if room["current_turn"] >= len(room["turn_order"]):
        # Конец раунда
        room["current_turn"] = 0

        if room["round"] >= 3:
            # Начинаем голосование
            await start_voting(room)
        else:
            room["round"] += 1
            await announce_turn(room)
    else:
        await announce_turn(room)


async def start_voting(room):
    room["voting_phase"] = True
    room["votes"] = {}

    for p in room["players"]:
        buttons = []
        for other in room["players"]:
            if other != p:
                other_nick = get_user_nick(other) or str(other)
                buttons.append([InlineKeyboardButton(
                    text=f"🗳 {other_nick}",
                    callback_data=f"vote_{room['id']}_{other}"
                )])

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        try:
            await bot.send_message(
                p,
                "🗳 <b>ГОЛОСОВАНИЕ!</b>\n\n"
                "3 раунда прошли. Выберите, кого вы считаете шпионом.\n"
                "⚠️ За себя голосовать нельзя!",
                parse_mode="HTML",
                reply_markup=kb
            )
        except:
            pass


@dp.callback_query(F.data.startswith("vote_"))
async def cb_vote(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    rid = int(parts[1])
    target = int(parts[2])
    uid = callback.from_user.id

    if rid not in rooms:
        await callback.answer("Комната не найдена!", show_alert=True)
        return

    room = rooms[rid]

    if uid not in room["players"]:
        await callback.answer("Вы не в этой комнате!", show_alert=True)
        return

    if uid == target:
        await callback.answer("Нельзя голосовать за себя!", show_alert=True)
        return

    if uid in room["votes"]:
        await callback.answer("Вы уже проголосовали!", show_alert=True)
        return

    room["votes"][uid] = target
    target_nick = get_user_nick(target) or str(target)
    await callback.message.edit_text(f"✅ Вы проголосовали за <b>{target_nick}</b>", parse_mode="HTML")
    await callback.answer()

    # Проверяем все ли проголосовали
    if len(room["votes"]) >= len(room["players"]):
        await finish_game(room)


async def finish_game(room):
    # Подсчёт голосов
    vote_count = {}
    for voter, target in room["votes"].items():
        vote_count[target] = vote_count.get(target, 0) + 1

    # Определяем кто набрал больше голосов
    max_votes = max(vote_count.values()) if vote_count else 0
    most_voted = [p for p, v in vote_count.items() if v == max_votes]

    spies = room["spies"]
    spy_nicks = ", ".join([get_user_nick(s) or str(s) for s in spies])
    topic = room["topic"]

    votes_text = ""
    for target, count in vote_count.items():
        tn = get_user_nick(target) or str(target)
        votes_text += f"  {tn}: {count} голос(ов)\n"

    result_text = (
        f"🏁 <b>РЕЗУЛЬТАТЫ</b>\n\n"
        f"📊 Голоса:\n{votes_text}\n"
        f"🕵️ Шпион(ы): <b>{spy_nicks}</b>\n"
        f"📋 Тема: <b>{topic}</b>\n\n"
    )

    # Проверяем угадали ли
    spy_caught = any(s in most_voted for s in spies)
    if spy_caught:
        result_text += "🎉 <b>Шпион раскрыт! Мирные победили!</b>"
    else:
        result_text += "😈 <b>Шпион не раскрыт! Шпион победил!</b>"

    room["started"] = False
    room["voting_phase"] = False
    room["lobby_over"] = True

    for p in room["players"]:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Начать заново", callback_data=f"restart_room_{room['id']}")],
                [InlineKeyboardButton(text="🚪 Покинуть комнату", callback_data=f"leave_room_{room['id']}")]
            ])
            await bot.send_message(p, result_text, parse_mode="HTML", reply_markup=kb)
        except:
            pass


@dp.callback_query(F.data.startswith("restart_room_"))
async def cb_restart_room(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    rid = int(callback.data.split("_")[2])

    if rid not in rooms:
        await callback.answer("Комната не найдена!", show_alert=True)
        return

    room = rooms[rid]

    if uid != room["leader"]:
        await callback.answer("Только лидер может перезапустить!", show_alert=True)
        return

    # Сбрасываем комнату
    room["started"] = False
    room["topic"] = None
    room["spies"] = []
    room["turn_order"] = []
    room["current_turn"] = 0
    room["round"] = 0
    room["messages"] = {}
    room["votes"] = {}
    room["voting_phase"] = False
    room["lobby_over"] = False

    if len(room["players"]) < 3:
        text = (
            "🔄 Комната перезапущена.\n\n"
            f"⏳ Ожидание игроков ({len(room['players'])}/3 мин.)...\n\n" +
            get_room_info_text(room)
        )
        for p in room["players"]:
            try:
                kb = room_lobby_keyboard(room, p)
                await bot.send_message(p, text, parse_mode="HTML", reply_markup=kb)
            except:
                pass
    else:
        await send_room_update(room)

    await callback.answer("Комната перезапущена!")


# ============ ОБРАБОТКА ВСЕХ НЕИЗВЕСТНЫХ СООБЩЕНИЙ ============

@dp.message()
async def fallback(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # Если в комнате онлайн и игра идёт — обработано выше через OnlineStates.in_room
    # Здесь ловим всё остальное
    uid = message.from_user.id
    if uid in user_room:
        rid = user_room[uid]
        if rid in rooms:
            room = rooms[rid]
            if room["started"] and not room.get("lobby_over"):
                if room.get("voting_phase"):
                    await message.answer("⚠️ Сейчас голосование! Используйте кнопки.")
                    return
                current_player = room["turn_order"][room["current_turn"]] if room["current_turn"] < len(room["turn_order"]) else None
                if uid != current_player:
                    await message.answer("⚠️ Сейчас не ваш ход!")
                    return

    await message.answer(
        "Используйте кнопки меню или /start",
        reply_markup=main_keyboard()
    )


# ============ ЗАПУСК ============

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())