"""
Spy Game Telegram Bot — single-file version for Python 3.11
Установка: pip install pyTelegramBotAPI python-dotenv
Запуск:    python bot.py
"""

from __future__ import annotations

import os
import random
import string
import sys
import threading
import time
from pathlib import Path
from typing import Any

import telebot
from telebot import types
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

load_dotenv(Path(__file__).parent / ".env")
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN не задан. Создайте .env файл или задайте переменную окружения.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ══════════════════════════════════════════════════════════════════════════════
# THEMES
# ══════════════════════════════════════════════════════════════════════════════

THEMES_RU: dict[str, list[str]] = {
    "Места": [
        "Пляж", "Аэропорт", "Больница", "Школа", "Супермаркет",
        "Ресторан", "Кинотеатр", "Библиотека", "Спортзал", "Зоопарк",
        "Цирк", "Банк", "Полицейский участок", "Отель", "Музей",
        "Парк аттракционов", "Космический корабль", "Подводная лодка",
        "Замок", "Пиратский корабль", "Арктическая станция",
        "Джунгли", "Пустыня", "Горнолыжный курорт", "Стадион",
        "Театр", "Тюрьма", "Яхта", "Фабрика", "Ферма",
        "Вулкан", "Нефтяная платформа", "Военная база", "Казино",
        "Аквапарк", "Боулинг", "Автосервис", "Автовокзал",
        "Железнодорожный вокзал", "Метро", "Маяк", "Шахта",
        "Атомная станция", "Телестудия", "Пожарная часть",
        "Кондитерская", "Пекарня", "Рыбный рынок", "Барбершоп",
        "Спа-салон", "Ветеринарная клиника",
    ],
    "Еда": [
        "Пицца", "Суши", "Бургер", "Борщ", "Паста",
        "Шашлык", "Блины", "Роллы", "Стейк", "Рамен",
        "Хот-дог", "Шаурма", "Мороженое", "Торт", "Шоколад",
        "Кофе", "Чай", "Лимонад", "Смузи", "Энергетик",
        "Вино", "Пиво", "Квас", "Компот", "Молочный коктейль",
        "Омлет", "Яичница", "Каша", "Пельмени", "Вареники",
        "Оливье", "Холодец", "Жульен", "Крем-суп",
        "Тирамису", "Чизкейк", "Круассан", "Маффин",
    ],
    "Электроника": [
        "Смартфон", "Ноутбук", "Планшет", "Умные часы", "Наушники",
        "Телевизор", "Игровая консоль", "Электронная книга", "Дрон",
        "Видеокарта", "Процессор", "Клавиатура", "Мышь", "Монитор",
        "Маршрутизатор", "Флешка", "Внешний жёсткий диск",
        "Фотоаппарат", "Видеокамера", "Проектор", "Акустика",
        "Электросамокат", "Робот-пылесос", "Умная колонка",
        "VR-шлем", "Фитнес-браслет", "Принтер", "Сканер",
        "Веб-камера", "Микрофон", "PowerBank",
    ],
    "Бытовая техника": [
        "Холодильник", "Стиральная машина", "Посудомоечная машина",
        "Микроволновка", "Пылесос", "Утюг", "Фен", "Блендер",
        "Мультиварка", "Кофемашина", "Тостер", "Электрочайник",
        "Духовка", "Кондиционер", "Обогреватель", "Вентилятор",
        "Хлебопечка", "Соковыжималка", "Морозильник", "Сушилка",
        "Пароварка", "Аэрогриль", "Вафельница", "Мясорубка",
        "Миксер", "Кухонный комбайн", "Электрогриль",
    ],
    "Актёры": [
        "Леонардо ДиКаприо", "Том Хэнкс", "Скарлетт Йоханссон",
        "Роберт Дауни мл.", "Мерил Стрип", "Брэд Питт",
        "Анджелина Джоли", "Джонни Депп", "Натали Портман",
        "Киану Ривз", "Уилл Смит", "Дензел Вашингтон",
        "Кейт Бланшетт", "Хоакин Феникс", "Марго Робби",
        "Тимоти Шаламе", "Зендея", "Том Холланд",
        "Крис Эванс", "Крис Хемсворт", "Галь Гадот",
        "Джейсон Стэтхэм", "Дуэйн Джонсон", "Вин Дизель",
        "Кевин Харт", "Эдди Мёрфи", "Джим Керри",
        "Адам Сэндлер", "Сандра Буллок", "Данила Козловский",
    ],
    "Музыканты": [
        "Майкл Джексон", "Мадонна", "Элтон Джон", "Адель",
        "Эд Ширан", "Тейлор Свифт", "Бейонсе", "Рианна",
        "Леди Гага", "Эминем", "Дрейк", "Кендрик Ламар",
        "The Beatles", "Queen", "Metallica", "AC/DC",
        "Нирвана", "Linkin Park", "Coldplay", "Radiohead",
        "Моргенштерн", "Тимати", "Баста", "Земфира",
        "Imagine Dragons", "Billie Eilish", "Post Malone",
    ],
    "Спорт": [
        "Футбол", "Баскетбол", "Теннис", "Волейбол", "Хоккей",
        "Бокс", "ММА", "Гимнастика", "Лёгкая атлетика", "Плавание",
        "Велоспорт", "Лыжи", "Биатлон", "Фигурное катание",
        "Шахматы", "Покер", "Дартс", "Боулинг", "Гольф",
        "Регби", "Американский футбол", "Бейсбол",
        "Сёрфинг", "Скейтбординг", "Паркур",
        "Борьба", "Дзюдо", "Карате", "Тхэквондо",
    ],
    "Транспорт": [
        "Спортивный автомобиль", "Грузовик", "Мотоцикл", "Велосипед",
        "Самолёт", "Вертолёт", "Поезд", "Метро", "Трамвай",
        "Троллейбус", "Автобус", "Такси", "Яхта", "Катер",
        "Паром", "Круизный лайнер", "Подводная лодка",
        "Ракета", "Дирижабль", "Воздушный шар",
        "Квадроцикл", "Снегоход", "Трактор", "Экскаватор",
        "Танк", "Скорая помощь", "Пожарная машина",
    ],
    "Животные": [
        "Лев", "Тигр", "Слон", "Жираф", "Зебра",
        "Горилла", "Дельфин", "Кит", "Акула",
        "Крокодил", "Питон", "Орёл", "Пингвин", "Фламинго",
        "Панда", "Коала", "Кенгуру", "Ленивец",
        "Волк", "Медведь", "Лиса", "Заяц", "Олень",
        "Лошадь", "Корова", "Свинья", "Овца",
        "Кот", "Собака", "Попугай", "Хомяк", "Черепаха",
    ],
    "Видеоигры": [
        "Minecraft", "GTA V", "Fortnite", "Among Us", "Roblox",
        "FIFA", "Counter-Strike", "Dota 2", "League of Legends",
        "World of Warcraft", "The Witcher", "Cyberpunk 2077",
        "Red Dead Redemption", "Assassins Creed", "Call of Duty",
        "Battlefield", "Overwatch", "Valorant", "Apex Legends",
        "PUBG", "Hollow Knight", "Undertale", "Portal",
        "Half-Life", "Doom", "Super Mario", "Zelda", "Pokemon",
    ],
    "Страны и города": [
        "Россия", "США", "Китай", "Япония", "Германия",
        "Франция", "Италия", "Испания", "Бразилия", "Индия",
        "Австралия", "Канада", "Мексика", "Аргентина",
        "Москва", "Нью-Йорк", "Лондон", "Париж", "Токио",
        "Дубай", "Рим", "Барселона", "Берлин", "Пекин",
        "Сидней", "Торонто", "Рио-де-Жанейро", "Каир",
    ],
    "Профессии": [
        "Врач", "Учитель", "Программист", "Дизайнер", "Юрист",
        "Полицейский", "Пожарный", "Военный", "Пилот", "Моряк",
        "Повар", "Официант", "Бармен", "Парикмахер", "Фотограф",
        "Журналист", "Актёр", "Певец", "Танцор",
        "Архитектор", "Инженер", "Строитель", "Электрик",
        "Водитель", "Механик", "Фермер", "Рыбак",
        "Астронавт", "Учёный", "Психолог", "Стоматолог", "Хирург",
    ],
}

THEMES_EN: dict[str, list[str]] = {
    "Places": [
        "Beach", "Airport", "Hospital", "School", "Supermarket",
        "Restaurant", "Cinema", "Library", "Gym", "Zoo",
        "Circus", "Bank", "Police Station", "Hotel", "Museum",
        "Amusement Park", "Spaceship", "Submarine",
        "Castle", "Pirate Ship", "Arctic Station",
        "Jungle", "Desert", "Ski Resort", "Stadium",
        "Theatre", "Prison", "Yacht", "Factory", "Farm",
        "Volcano", "Oil Platform", "Military Base", "Casino",
        "Water Park", "Bowling Alley", "Car Service", "Bus Station",
        "Railway Station", "Subway", "Lighthouse", "Mine",
        "Nuclear Plant", "TV Studio", "Fire Station",
        "Candy Shop", "Bakery", "Fish Market", "Barbershop",
        "Spa Salon", "Vet Clinic",
    ],
    "Food": [
        "Pizza", "Sushi", "Burger", "Borscht", "Pasta",
        "BBQ", "Pancakes", "Rolls", "Steak", "Ramen",
        "Hot Dog", "Shawarma", "Ice Cream", "Cake", "Chocolate",
        "Coffee", "Tea", "Lemonade", "Smoothie", "Energy Drink",
        "Wine", "Beer", "Milkshake", "Omelette", "Porridge",
        "Dumplings", "Tiramisu", "Cheesecake", "Croissant", "Muffin",
    ],
    "Electronics": [
        "Smartphone", "Laptop", "Tablet", "Smartwatch", "Headphones",
        "TV", "Gaming Console", "E-Reader", "Drone",
        "GPU", "CPU", "Keyboard", "Mouse", "Monitor",
        "Router", "USB Drive", "External HDD",
        "Camera", "Camcorder", "Projector", "Speaker",
        "Electric Scooter", "Robot Vacuum", "Smart Speaker",
        "VR Headset", "Fitness Tracker", "Printer",
        "Webcam", "Microphone", "PowerBank",
    ],
    "Home Appliances": [
        "Fridge", "Washing Machine", "Dishwasher",
        "Microwave", "Vacuum Cleaner", "Iron", "Hair Dryer", "Blender",
        "Slow Cooker", "Coffee Machine", "Toaster", "Electric Kettle",
        "Oven", "Air Conditioner", "Heater", "Fan",
        "Bread Maker", "Juicer", "Freezer", "Dryer",
        "Steamer", "Air Fryer", "Waffle Maker",
        "Mixer", "Food Processor", "Electric Grill",
    ],
    "Actors": [
        "Leonardo DiCaprio", "Tom Hanks", "Scarlett Johansson",
        "Robert Downey Jr", "Meryl Streep", "Brad Pitt",
        "Angelina Jolie", "Johnny Depp", "Natalie Portman",
        "Keanu Reeves", "Will Smith", "Denzel Washington",
        "Cate Blanchett", "Joaquin Phoenix", "Margot Robbie",
        "Timothee Chalamet", "Zendaya", "Tom Holland",
        "Chris Evans", "Chris Hemsworth", "Gal Gadot",
        "Jason Statham", "Dwayne Johnson", "Vin Diesel",
        "Kevin Hart", "Eddie Murphy", "Jim Carrey",
        "Adam Sandler", "Sandra Bullock",
    ],
    "Musicians": [
        "Michael Jackson", "Madonna", "Elton John", "Adele",
        "Ed Sheeran", "Taylor Swift", "Beyonce", "Rihanna",
        "Lady Gaga", "Eminem", "Drake", "Kendrick Lamar",
        "The Beatles", "Queen", "Metallica", "AC/DC",
        "Nirvana", "Linkin Park", "Coldplay", "Radiohead",
        "Imagine Dragons", "Billie Eilish", "Post Malone",
    ],
    "Sports": [
        "Football", "Basketball", "Tennis", "Volleyball", "Hockey",
        "Boxing", "MMA", "Gymnastics", "Athletics", "Swimming",
        "Cycling", "Skiing", "Biathlon", "Figure Skating",
        "Chess", "Poker", "Darts", "Bowling", "Golf",
        "Rugby", "American Football", "Baseball",
        "Surfing", "Skateboarding", "Parkour",
        "Wrestling", "Judo", "Karate", "Taekwondo",
    ],
    "Transport": [
        "Sports Car", "Truck", "Motorcycle", "Bicycle",
        "Airplane", "Helicopter", "Train", "Subway", "Tram",
        "Bus", "Taxi", "Yacht", "Boat", "Ferry",
        "Cruise Ship", "Submarine", "Rocket",
        "Airship", "Hot Air Balloon", "ATV",
        "Snowmobile", "Tractor", "Tank",
        "Ambulance", "Fire Truck",
    ],
    "Animals": [
        "Lion", "Tiger", "Elephant", "Giraffe", "Zebra",
        "Gorilla", "Dolphin", "Whale", "Shark",
        "Crocodile", "Python", "Eagle", "Penguin", "Flamingo",
        "Panda", "Koala", "Kangaroo", "Sloth",
        "Wolf", "Bear", "Fox", "Rabbit", "Deer",
        "Horse", "Cow", "Pig", "Sheep",
        "Cat", "Dog", "Parrot", "Hamster", "Turtle",
    ],
    "Video Games": [
        "Minecraft", "GTA V", "Fortnite", "Among Us", "Roblox",
        "FIFA", "Counter-Strike", "Dota 2", "League of Legends",
        "World of Warcraft", "The Witcher", "Cyberpunk 2077",
        "Red Dead Redemption", "Assassins Creed", "Call of Duty",
        "Battlefield", "Overwatch", "Valorant", "Apex Legends",
        "PUBG", "Hollow Knight", "Undertale", "Portal",
        "Half-Life", "Doom", "Super Mario", "Zelda", "Pokemon",
    ],
    "Countries and Cities": [
        "Russia", "USA", "China", "Japan", "Germany",
        "France", "Italy", "Spain", "Brazil", "India",
        "Australia", "Canada", "Mexico", "Argentina",
        "Moscow", "New York", "London", "Paris", "Tokyo",
        "Dubai", "Rome", "Barcelona", "Berlin", "Beijing",
        "Sydney", "Toronto", "Rio de Janeiro", "Cairo",
    ],
    "Professions": [
        "Doctor", "Teacher", "Programmer", "Designer", "Lawyer",
        "Police Officer", "Firefighter", "Soldier", "Pilot", "Sailor",
        "Cook", "Waiter", "Bartender", "Hairdresser", "Photographer",
        "Journalist", "Actor", "Singer", "Dancer",
        "Architect", "Engineer", "Builder", "Electrician",
        "Driver", "Mechanic", "Farmer", "Fisherman",
        "Astronaut", "Scientist", "Psychologist", "Dentist", "Surgeon",
    ],
}


def get_random_theme(lang: str = "ru") -> str:
    themes_dict = THEMES_EN if lang == "en" else THEMES_RU
    all_items: list[str] = []
    for lst in themes_dict.values():
        all_items.extend(lst)
    return random.choice(all_items)


def get_room_lang(room: dict[str, Any]) -> str:
    owner_id = room.get("owner")
    if owner_id is not None:
        return get_settings(owner_id).get("lang", "ru")
    return "ru"


# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "welcome": "Добро пожаловать в Угадай кто шпион!\n\nВыберите режим:",
        "main_menu_title": "Главное меню\n\nВыберите режим:",
        "btn_online": "Играть онлайн",
        "btn_solo": "Один телефон",
        "btn_support": "Поддержка",
        "btn_settings": "Настройки",
        "btn_back": "Назад",
        "btn_main_menu": "Главное меню",
        "support_text": "Поддержка\n\nПо вопросам: @SupAssasin",
        "settings_title": "Настройки",
        "btn_spy_count": "Шпионов: {n}  (изменить)",
        "btn_theme_mode": "Тема: {m}  (изменить)",
        "btn_lang": "Язык: Русский  (переключить на English)",
        "btn_nick_set": "Ник: {nick}  (изменить)",
        "btn_nick_none": "Установить ник",
        "theme_auto_label": "Авто",
        "theme_manual_label": "Ручной",
        "spy_count_title": "Выберите количество шпионов:",
        "btn_spy_1": "1 шпион",
        "btn_spy_2": "2 шпиона",
        "btn_spy_3": "3 шпиона",
        "spy_saved": "Шпионов: {n}",
        "enter_theme": "Введите тему для игры:",
        "theme_saved": "Тема сохранена: {t}",
        "theme_too_short": "Тема слишком короткая. Введите ещё раз:",
        "enter_nick_prompt": "Введите ваш ник (от 3 до 15 символов):",
        "nick_bad": "Ник должен быть от 3 до 15 символов. Попробуйте ещё раз:",
        "nick_saved": "Ник сохранён: {nick}",
        "nick_required": "Сначала установите ник в Настройках.\n/start -> Настройки -> Установить ник",
        "solo_title": "Игра на одном телефоне\n\nСколько игроков?",
        "solo_theme_q": "Игроков: {n}\n\nКак задать тему?",
        "btn_theme_auto": "Авто-тема",
        "btn_theme_manual": "Ввести тему",
        "enter_manual_theme": "Ведущий, введите тему. Шпион её не увидит:",
        "solo_started": "Игра началась!\n\nИгроков: {p}\nШпионов: {s}\n\nПередайте телефон Игроку 1 и нажмите кнопку.",
        "btn_show_role": "Показать роль  Игрок {n}",
        "spy_role": "Ты ШПИОН!\n\nПостарайся не раскрыться!",
        "citizen_role": "Ты обычный игрок\n\nТема: {t}",
        "role_note": "\n\nЗапомни роль и передай телефон.",
        "btn_pass": "Передать Игроку {n}",
        "btn_start_discuss": "Начать обсуждение!",
        "pass_phone": "Передайте телефон Игроку {n}\n\nИгрок {n}, нажми кнопку ниже.",
        "discuss_title": "Обсуждение!\n\nЗадавайте вопросы и ищите шпиона.\nШпионов в игре: {s}",
        "btn_reveal": "Раскрыть шпионов",
        "btn_new_game": "Новая игра",
        "btn_end_game": "Завершить игру",
        "end_game_q": "Завершить игру?\n\nШпионы будут раскрыты.",
        "btn_yes_end": "Да, завершить",
        "btn_no_back": "Нет, продолжить",
        "reveal_text": "Результат!\n\nТема была: {t}\n\nШпион(ы): {spies}",
        "online_title": "Онлайн режим\n\nВыберите действие:",
        "btn_create_private": "Создать приватную комнату",
        "btn_join_private": "Войти по коду",
        "btn_create_public": "Создать открытую комнату",
        "btn_free_game": "Свободная игра",
        "enter_code": "Введите код комнаты (6 символов):",
        "room_created_private": "Приватная комната создана!\n\nКод: {code}\n\nПоделитесь кодом с друзьями.\n\nИгроков: 1 из 8\n\n{lst}",
        "room_created_public": "Открытая комната создана!\n\nЛюбой может присоединиться без кода.\n\nИгроков: 1 из 8\n\n{lst}",
        "btn_start_game": "Начать игру",
        "btn_close_room": "Закрыть комнату",
        "btn_leave_room": "Покинуть комнату",
        "joined_room": "Вы вошли в комнату!\n\nИгроков: {n} из 8\nОжидайте начала...\n\n{lst}",
        "player_joined": "{nick} присоединился!\n\nИгроков: {n} из 8\n\n{lst}",
        "player_left": "{nick} покинул комнату.\n\nИгроков: {n} из 8\n\n{lst}",
        "you_left": "Вы покинули комнату.",
        "room_closed": "Комната закрыта владельцем.",
        "room_not_found": "Комната не найдена. Проверьте код.",
        "room_started": "Игра уже началась. Дождитесь следующего раунда.",
        "room_full": "Комната заполнена. Максимум 8 игроков.",
        "already_in_room": "Вы уже в этой комнате.",
        "no_open_rooms": "Нет доступных открытых комнат.\nСоздайте свою или подождите.",
        "free_joined": "Вас добавили в комнату!\n\nИгроков: {n} из 8\nОжидайте начала...\n\n{lst}",
        "need_more": "Нужно минимум 3 игрока! Сейчас: {n}",
        "only_owner": "Только владелец может это сделать.",
        "already_in_other": "Вы уже в другой комнате. Сначала покиньте её.",
        "game_starting": "Игра начинается!",
        "online_spy_role": "Ты ШПИОН!\n\nТы не знаешь тему. Слушай других и не раскрывайся!",
        "online_citizen_role": "Ты обычный игрок\n\nТема: {t}\n\nНайди шпиона среди игроков!",
        "btn_role_ok": "Роль получена",
        "round_start": "Круг {r} из 3\n\nОчерёдность ответов:\n{order}\n\nСейчас отвечает: {nick}",
        "your_turn": "Ваш ход!  Круг {r} из 3\n\nНапишите одно предложение.\nОпишите место или тему своими словами.\nДругие игроки увидят ваш ответ.",
        "wait_turn": "Сейчас отвечает: {nick}\nПодождите своей очереди...",
        "answer_sent": "Ответ отправлен! Ждите следующего хода.",
        "player_answered": "{nick} написал:\n{text}",
        "one_sentence_only": "Только одно предложение и без переносов строк.\nПопробуйте ещё раз:",
        "too_long": "Слишком длинно! Максимум 200 символов.",
        "round_done": "Круг {r} завершён!\n\nВсе ответили.",
        "all_rounds_done": "Все 3 круга завершены!\n\nПереходим к голосованию...",
        "vote_title": "Голосование!\n\nКто по-вашему шпион?\nВыберите игрока из списка:",
        "you_voted": "Вы проголосовали за {nick}",
        "already_voted": "Вы уже проголосовали.",
        "vote_progress": "Проголосовали: {done} из {total}",
        "vote_result": "Итоги голосования:\n\n{results}\n\nШпион(ы): {spies}\nТема: {theme}\n\n{verdict}",
        "spy_caught": "Шпион пойман! Мирные победили!",
        "spy_escaped": "Шпион не пойман! Шпионы победили!",
        "cant_vote_self": "Нельзя голосовать за себя!",
        "use_start": "Используйте /start для вызова меню.",
        "new_owner": "Вы стали новым владельцем комнаты!",
        # ── /leave ──────────────────────────────────────────────────────────
        "not_in_room": "Вы не находитесь ни в какой комнате.",
        "you_left_game": "Вы покинули игру.",
        "player_left_game": "{nick} покинул игру во время партии.",
        "game_dissolved_owner": "Владелец покинул игру. Комната расформирована.",
        "game_dissolved_few": "Игроков стало меньше минимума. Игра расформирована.",
        "game_continues": "Игра продолжается. Игроков: {n}",
        "leave_hint": "Чтобы покинуть комнату или игру напишите /leave",
    },
    "en": {
        "welcome": "Welcome to Guess Who is the Spy!\n\nChoose mode:",
        "main_menu_title": "Main Menu\n\nChoose mode:",
        "btn_online": "Play Online",
        "btn_solo": "One Phone",
        "btn_support": "Support",
        "btn_settings": "Settings",
        "btn_back": "Back",
        "btn_main_menu": "Main Menu",
        "support_text": "Support\n\nContact: @SupAssasin",
        "settings_title": "Settings",
        "btn_spy_count": "Spies: {n}  (change)",
        "btn_theme_mode": "Theme: {m}  (change)",
        "btn_lang": "Language: English  (switch to Russian)",
        "btn_nick_set": "Nick: {nick}  (change)",
        "btn_nick_none": "Set nickname",
        "theme_auto_label": "Auto",
        "theme_manual_label": "Manual",
        "spy_count_title": "Choose number of spies:",
        "btn_spy_1": "1 spy",
        "btn_spy_2": "2 spies",
        "btn_spy_3": "3 spies",
        "spy_saved": "Spies: {n}",
        "enter_theme": "Enter game theme:",
        "theme_saved": "Theme saved: {t}",
        "theme_too_short": "Theme too short. Try again:",
        "enter_nick_prompt": "Enter your nickname (3 to 15 characters):",
        "nick_bad": "Nickname must be 3 to 15 characters. Try again:",
        "nick_saved": "Nickname saved: {nick}",
        "nick_required": "Please set a nickname in Settings first.\n/start -> Settings -> Set nickname",
        "solo_title": "One Phone Game\n\nHow many players?",
        "solo_theme_q": "Players: {n}\n\nHow to set the theme?",
        "btn_theme_auto": "Auto theme",
        "btn_theme_manual": "Enter theme",
        "enter_manual_theme": "Host, enter the theme. Spy will not see it:",
        "solo_started": "Game started!\n\nPlayers: {p}\nSpies: {s}\n\nPass the phone to Player 1 and press the button.",
        "btn_show_role": "Show role  Player {n}",
        "spy_role": "You are a SPY!\n\nDo not get caught!",
        "citizen_role": "You are a citizen\n\nTheme: {t}",
        "role_note": "\n\nRemember your role and pass the phone.",
        "btn_pass": "Pass to Player {n}",
        "btn_start_discuss": "Start discussion!",
        "pass_phone": "Pass the phone to Player {n}\n\nPlayer {n}, press the button below.",
        "discuss_title": "Discussion!\n\nAsk questions and find the spy.\nSpies in game: {s}",
        "btn_reveal": "Reveal spies",
        "btn_new_game": "New game",
        "btn_end_game": "End game",
        "end_game_q": "End the game?\n\nSpies will be revealed.",
        "btn_yes_end": "Yes, end",
        "btn_no_back": "No, continue",
        "reveal_text": "Result!\n\nTheme was: {t}\n\nSpy or spies: {spies}",
        "online_title": "Online Mode\n\nChoose action:",
        "btn_create_private": "Create Private Room",
        "btn_join_private": "Join by Code",
        "btn_create_public": "Create Public Room",
        "btn_free_game": "Quick Game",
        "enter_code": "Enter room code (6 characters):",
        "room_created_private": "Private room created!\n\nCode: {code}\n\nShare with friends.\n\nPlayers: 1 of 8\n\n{lst}",
        "room_created_public": "Public room created!\n\nAnyone can join without a code.\n\nPlayers: 1 of 8\n\n{lst}",
        "btn_start_game": "Start game",
        "btn_close_room": "Close room",
        "btn_leave_room": "Leave room",
        "joined_room": "You joined the room!\n\nPlayers: {n} of 8\nWaiting for start...\n\n{lst}",
        "player_joined": "{nick} joined!\n\nPlayers: {n} of 8\n\n{lst}",
        "player_left": "{nick} left.\n\nPlayers: {n} of 8\n\n{lst}",
        "you_left": "You left the room.",
        "room_closed": "Room closed by owner.",
        "room_not_found": "Room not found. Check the code.",
        "room_started": "Game already started. Wait for next round.",
        "room_full": "Room is full. Maximum 8 players.",
        "already_in_room": "You are already in this room.",
        "no_open_rooms": "No open rooms available.\nCreate your own or wait.",
        "free_joined": "You joined a room!\n\nPlayers: {n} of 8\nWaiting for start...\n\n{lst}",
        "need_more": "Need at least 3 players! Now: {n}",
        "only_owner": "Only the owner can do this.",
        "already_in_other": "You are already in another room. Leave it first.",
        "game_starting": "Game is starting!",
        "online_spy_role": "You are a SPY!\n\nYou do not know the theme. Listen carefully and do not reveal yourself!",
        "online_citizen_role": "You are a citizen\n\nTheme: {t}\n\nFind the spy!",
        "btn_role_ok": "Role received",
        "round_start": "Round {r} of 3\n\nAnswer order:\n{order}\n\nNow answering: {nick}",
        "your_turn": "Your turn!  Round {r} of 3\n\nWrite one sentence.\nDescribe the place or theme in your own words.\nOther players will see your answer.",
        "wait_turn": "Now answering: {nick}\nPlease wait for your turn...",
        "answer_sent": "Answer sent! Wait for your next turn.",
        "player_answered": "{nick} wrote:\n{text}",
        "one_sentence_only": "One sentence only and no line breaks.\nTry again:",
        "too_long": "Too long! Maximum 200 characters.",
        "round_done": "Round {r} complete!\n\nEveryone answered.",
        "all_rounds_done": "All 3 rounds complete!\n\nTime to vote...",
        "vote_title": "Voting!\n\nWho do you think is the spy?\nChoose a player from the list:",
        "you_voted": "You voted for {nick}",
        "already_voted": "You already voted.",
        "vote_progress": "Voted: {done} of {total}",
        "vote_result": "Voting results:\n\n{results}\n\nSpy or spies: {spies}\nTheme: {theme}\n\n{verdict}",
        "spy_caught": "Spy caught! Citizens win!",
        "spy_escaped": "Spy escaped! Spies win!",
        "cant_vote_self": "You cannot vote for yourself!",
        "use_start": "Use /start to open the menu.",
        "new_owner": "You are now the room owner!",
        # ── /leave ──────────────────────────────────────────────────────────
        "not_in_room": "You are not in any room.",
        "you_left_game": "You have left the game.",
        "player_left_game": "{nick} left during the game.",
        "game_dissolved_owner": "The owner left. Room has been disbanded.",
        "game_dissolved_few": "Not enough players remaining. Game disbanded.",
        "game_continues": "Game continues. Players: {n}",
        "leave_hint": "Type /leave to leave the room or game at any time.",
    },
}


def tx(uid: int, key: str, **kwargs: Any) -> str:
    lang = get_settings(uid).get("lang", "ru")
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS["ru"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    return text


# ══════════════════════════════════════════════════════════════════════════════
# STORAGE  (in-memory)
# ══════════════════════════════════════════════════════════════════════════════

_user_settings: dict[int, dict[str, Any]] = {}
_user_states:   dict[int, dict[str, Any]] = {}
solo_games:     dict[int, dict[str, Any]] = {}
online_rooms:   dict[str, dict[str, Any]] = {}
user_room:      dict[int, str]            = {}


def get_settings(uid: int) -> dict[str, Any]:
    if uid not in _user_settings:
        _user_settings[uid] = {
            "spy_count": 1,
            "theme_mode": "auto",
            "manual_theme": "",
            "lang": "ru",
            "nick": "",
        }
    return _user_settings[uid]


def get_nick(uid: int) -> str:
    return get_settings(uid).get("nick", "")


def set_state(uid: int, state: str, data: dict[str, Any] | None = None) -> None:
    _user_states[uid] = {"state": state, "data": data or {}}


def get_state(uid: int) -> dict[str, Any]:
    return _user_states.get(uid, {"state": None, "data": {}})


def clear_state(uid: int) -> None:
    _user_states.pop(uid, None)


def gen_code() -> str:
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in online_rooms:
            return code


def players_list_str(room: dict[str, Any]) -> str:
    lines: list[str] = []
    for i, (pid, pd) in enumerate(room["players"].items(), 1):
        crown = " (владелец)" if pid == room["owner"] else ""
        lines.append(f"{i}. {pd['nick']}{crown}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def safe_send(
    chat_id: int,
    text: str,
    reply_markup: types.InlineKeyboardMarkup | None = None,
) -> types.Message | None:
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as exc:
        print(f"send error {chat_id}: {exc}")
    return None


def answer_cb(call: types.CallbackQuery, text: str = "") -> None:
    try:
        bot.answer_callback_query(call.id, text)
    except Exception:
        pass


def edit_call(
    call: types.CallbackQuery,
    text: str,
    kb: types.InlineKeyboardMarkup | None = None,
) -> None:
    try:
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kb,
        )
    except Exception as exc:
        print(f"edit_call error: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════════════════

def kb_main(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_online"),   callback_data="online_menu"),
        types.InlineKeyboardButton(tx(uid, "btn_solo"),     callback_data="solo_menu"),
        types.InlineKeyboardButton(tx(uid, "btn_support"),  callback_data="support"),
        types.InlineKeyboardButton(tx(uid, "btn_settings"), callback_data="settings_menu"),
    )
    return m


def kb_back_main(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(tx(uid, "btn_main_menu"), callback_data="main_menu"))
    return m


def kb_settings(uid: int) -> types.InlineKeyboardMarkup:
    s = get_settings(uid)
    nick = s.get("nick", "")
    mode_label = tx(uid, "theme_auto_label") if s["theme_mode"] == "auto" else tx(uid, "theme_manual_label")
    nick_label = tx(uid, "btn_nick_set", nick=nick) if nick else tx(uid, "btn_nick_none")
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton(nick_label, callback_data="settings_nick"),
        types.InlineKeyboardButton(tx(uid, "btn_spy_count", n=s["spy_count"]), callback_data="settings_spy_menu"),
        types.InlineKeyboardButton(tx(uid, "btn_theme_mode", m=mode_label),    callback_data="settings_theme_toggle"),
        types.InlineKeyboardButton(tx(uid, "btn_lang"),                         callback_data="settings_lang_toggle"),
        types.InlineKeyboardButton(tx(uid, "btn_main_menu"),                    callback_data="main_menu"),
    )
    return m


def kb_spy_count(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=3)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_spy_1"), callback_data="set_spy_1"),
        types.InlineKeyboardButton(tx(uid, "btn_spy_2"), callback_data="set_spy_2"),
        types.InlineKeyboardButton(tx(uid, "btn_spy_3"), callback_data="set_spy_3"),
    )
    m.add(types.InlineKeyboardButton(tx(uid, "btn_back"), callback_data="settings_menu"))
    return m


def kb_solo_players(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=3)
    m.add(*[types.InlineKeyboardButton(str(n), callback_data=f"solo_players_{n}") for n in range(3, 9)])
    m.add(types.InlineKeyboardButton(tx(uid, "btn_main_menu"), callback_data="main_menu"))
    return m


def kb_solo_theme(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_theme_auto"),   callback_data="solo_theme_auto"),
        types.InlineKeyboardButton(tx(uid, "btn_theme_manual"), callback_data="solo_theme_manual"),
    )
    m.add(types.InlineKeyboardButton(tx(uid, "btn_back"), callback_data="solo_menu"))
    return m


def kb_show_role(uid: int, idx: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(tx(uid, "btn_show_role", n=idx + 1), callback_data=f"show_role_{idx}"))
    return m


def kb_after_role(uid: int, idx: int, total: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    if idx + 1 < total:
        m.add(types.InlineKeyboardButton(tx(uid, "btn_pass", n=idx + 2), callback_data=f"next_player_{idx + 1}"))
    else:
        m.add(types.InlineKeyboardButton(tx(uid, "btn_start_discuss"), callback_data="solo_start_discuss"))
    return m


def kb_discussion(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_reveal"),   callback_data="solo_reveal"),
        types.InlineKeyboardButton(tx(uid, "btn_end_game"), callback_data="solo_end_confirm"),
    )
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_new_game"),  callback_data="solo_menu"),
        types.InlineKeyboardButton(tx(uid, "btn_main_menu"), callback_data="main_menu"),
    )
    return m


def kb_end_confirm(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_yes_end"), callback_data="solo_reveal"),
        types.InlineKeyboardButton(tx(uid, "btn_no_back"), callback_data="solo_start_discuss"),
    )
    return m


def kb_online_menu(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_create_private"), callback_data="online_create_private"),
        types.InlineKeyboardButton(tx(uid, "btn_join_private"),   callback_data="online_join_private"),
        types.InlineKeyboardButton(tx(uid, "btn_create_public"),  callback_data="online_create_public"),
        types.InlineKeyboardButton(tx(uid, "btn_free_game"),      callback_data="online_free_game"),
        types.InlineKeyboardButton(tx(uid, "btn_main_menu"),      callback_data="main_menu"),
    )
    return m


def kb_owner(uid: int, code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(tx(uid, "btn_start_game"), callback_data=f"online_start_{code}"),
        types.InlineKeyboardButton(tx(uid, "btn_close_room"), callback_data=f"online_close_{code}"),
    )
    return m


def kb_member(uid: int, code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(tx(uid, "btn_leave_room"), callback_data=f"online_leave_{code}"))
    return m


def kb_role_ok(uid: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(tx(uid, "btn_role_ok"), callback_data="online_role_ok"))
    return m


def kb_vote(uid: int, room_code: str) -> types.InlineKeyboardMarkup:
    room = online_rooms.get(room_code)
    m = types.InlineKeyboardMarkup(row_width=1)
    if not room:
        return m
    for pid, pd in room["players"].items():
        if pid != uid:
            m.add(types.InlineKeyboardButton(pd["nick"], callback_data=f"vote_{room_code}_{pid}"))
    return m


# ══════════════════════════════════════════════════════════════════════════════
# GAME LOGIC — SOLO
# ══════════════════════════════════════════════════════════════════════════════

def launch_solo(cid: int, uid: int, gd: dict[str, Any]) -> None:
    pc: int = gd["player_count"]
    sc: int = min(gd["spy_count"], pc - 1)
    roles = ["spy"] * sc + ["citizen"] * (pc - sc)
    random.shuffle(roles)
    solo_games[uid] = {
        "player_count": pc,
        "theme": gd["theme"],
        "spy_count": sc,
        "roles": roles,
    }
    safe_send(cid, tx(uid, "solo_started", p=pc, s=sc), reply_markup=kb_show_role(uid, 0))


# ══════════════════════════════════════════════════════════════════════════════
# GAME LOGIC — ONLINE (комнаты, раунды, голосование)
# ══════════════════════════════════════════════════════════════════════════════

def check_already_in_room(cid: int, uid: int) -> bool:
    if uid in user_room:
        code = user_room[uid]
        if code in online_rooms and uid in online_rooms[code]["players"]:
            safe_send(cid, tx(uid, "already_in_other"))
            return True
        user_room.pop(uid, None)
    return False


def notify_all_in_room(
    room: dict[str, Any],
    code: str,
    key: str,
    skip_uid: int | None = None,
    **kwargs: Any,
) -> None:
    n   = len(room["players"])
    lst = players_list_str(room)
    for pid, pd in room["players"].items():
        if pid == skip_uid:
            continue
        markup = kb_owner(pid, code) if pid == room["owner"] else kb_member(pid, code)
        try:
            bot.send_message(pd["chat_id"], tx(pid, key, n=n, lst=lst, **kwargs), reply_markup=markup)
        except Exception:
            pass


def dissolve_room(code: str, reason_key: str) -> None:
    """Расформировать комнату — уведомить всех и очистить данные."""
    room = online_rooms.get(code)
    if not room:
        return
    for pid, pd in room["players"].items():
        user_room.pop(pid, None)
        clear_state(pid)
        try:
            bot.send_message(pd["chat_id"], tx(pid, reason_key), reply_markup=kb_online_menu(pid))
        except Exception:
            pass
    online_rooms.pop(code, None)


def _min_players_to_continue(total_before: int) -> int:
    """
    Минимальное число игроков для продолжения игры после чьего-то ухода.
    При 3 игроках — нельзя продолжать вообще (нужно >=3, значит уход любого = конец).
    При 4+ — можно продолжать если осталось >= 3.
    """
    return 3


def handle_mid_game_leave(code: str, leaving_uid: int) -> None:
    """
    Обработать уход игрока во время активной игры (статус rounds/voting/playing).
    Правила:
      - Вышел владелец → расформировать.
      - Осталось < 3 игроков → расформировать.
      - Иначе → продолжить, убрать из очереди ответов и голосования.
    """
    room = online_rooms.get(code)
    if not room:
        return

    nick = room["players"].get(leaving_uid, {}).get("nick", "?")
    is_owner = room["owner"] == leaving_uid

    # Убираем игрока из комнаты
    room["players"].pop(leaving_uid, None)
    user_room.pop(leaving_uid, None)
    clear_state(leaving_uid)

    # Уведомляем самого игрока
    safe_send(leaving_uid, tx(leaving_uid, "you_left_game"), reply_markup=kb_online_menu(leaving_uid))

    # Владелец вышел — расформировать
    if is_owner:
        dissolve_room(code, "game_dissolved_owner")
        return

    remaining = len(room["players"])

    # Слишком мало игроков — расформировать
    if remaining < _min_players_to_continue(remaining + 1):
        dissolve_room(code, "game_dissolved_few")
        return

    # Уведомляем оставшихся
    for pid, pd in room["players"].items():
        try:
            bot.send_message(
                pd["chat_id"],
                tx(pid, "player_left_game", nick=nick) + "\n" + tx(pid, "game_continues", n=remaining),
            )
        except Exception:
            pass

    # Если уходящий был текущим отвечающим — передаём ход дальше
    status = room.get("status", "")
    if status == "rounds":
        order = room.get("answer_order", [])
        if leaving_uid in order:
            order.remove(leaving_uid)
        cur_idx = room.get("cur_answer_idx", 0)
        # Пересчитываем индекс — если ушедший был до текущего, сдвигаем
        try:
            # Просто проверим — вдруг сейчас его ход
            if cur_idx >= len(order):
                # Все ответили в этом круге
                rnd = room["cur_round"]

                def _next_rnd() -> None:
                    time.sleep(1)
                    start_round(code, rnd + 1)

                threading.Thread(target=_next_rnd, daemon=True).start()
            else:
                # Продолжаем с текущего индекса (следующий в очереди)
                ask_player(code, cur_idx)
        except Exception:
            pass

    elif status == "voting":
        # Убираем голос ушедшего и голос ЗА ушедшего
        room["votes"].pop(leaving_uid, None)
        room["votes"] = {k: v for k, v in room["votes"].items() if v != leaving_uid}
        # Убираем из ролей чтобы не влиял на подсчёт
        room["roles"].pop(leaving_uid, None)

        # Проверяем не пора ли завершить голосование
        total = len(room["players"])
        done  = len(room["votes"])
        if total > 0 and done >= total:
            finish_voting(code)


def create_room(cid: int, uid: int, nick: str, *, public: bool) -> None:
    if check_already_in_room(cid, uid):
        return
    code = gen_code()
    online_rooms[code] = {
        "owner": uid, "public": public,
        "players": {uid: {"nick": nick, "chat_id": cid}},
        "status": "waiting", "cur_round": 0,
        "answer_order": [], "cur_answer_idx": 0,
        "round_answers": {}, "votes": {}, "roles": {}, "theme": "",
    }
    user_room[uid] = code
    lst = players_list_str(online_rooms[code])
    if public:
        safe_send(cid, tx(uid, "room_created_public", lst=lst), reply_markup=kb_owner(uid, code))
    else:
        safe_send(cid, tx(uid, "room_created_private", code=code, lst=lst), reply_markup=kb_owner(uid, code))


def join_room(cid: int, uid: int, code: str) -> None:
    if check_already_in_room(cid, uid):
        return
    nick = get_nick(uid)
    room = online_rooms.get(code)
    if not room:
        safe_send(cid, tx(uid, "room_not_found"), reply_markup=kb_online_menu(uid))
        return
    if room["status"] != "waiting":
        safe_send(cid, tx(uid, "room_started"), reply_markup=kb_online_menu(uid))
        return
    if len(room["players"]) >= 8:
        safe_send(cid, tx(uid, "room_full"), reply_markup=kb_online_menu(uid))
        return
    if uid in room["players"]:
        safe_send(cid, tx(uid, "already_in_room"))
        return
    room["players"][uid] = {"nick": nick, "chat_id": cid}
    user_room[uid] = code
    n   = len(room["players"])
    lst = players_list_str(room)
    safe_send(cid, tx(uid, "joined_room", n=n, lst=lst), reply_markup=kb_member(uid, code))
    notify_all_in_room(room, code, "player_joined", skip_uid=uid, nick=nick)


def free_join(cid: int, uid: int, nick: str) -> None:
    if check_already_in_room(cid, uid):
        return
    candidates = [
        (c, r) for c, r in online_rooms.items()
        if r["public"] and r["status"] == "waiting"
        and len(r["players"]) < 8 and uid not in r["players"]
    ]
    if not candidates:
        safe_send(cid, tx(uid, "no_open_rooms"), reply_markup=kb_online_menu(uid))
        return
    code, room = random.choice(candidates)
    room["players"][uid] = {"nick": nick, "chat_id": cid}
    user_room[uid] = code
    n   = len(room["players"])
    lst = players_list_str(room)
    safe_send(cid, tx(uid, "free_joined", n=n, lst=lst), reply_markup=kb_member(uid, code))
    notify_all_in_room(room, code, "player_joined", skip_uid=uid, nick=nick)


def leave_room(call: types.CallbackQuery, uid: int, code: str) -> None:
    """Покинуть комнату ЧЕРЕЗ КНОПКУ (только в статусе waiting)."""
    room = online_rooms.get(code)
    if not room or uid not in room["players"]:
        answer_cb(call)
        return
    nick = room["players"][uid]["nick"]
    del room["players"][uid]
    user_room.pop(uid, None)
    clear_state(uid)
    answer_cb(call)
    try:
        bot.edit_message_text(
            tx(uid, "you_left"),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kb_online_menu(uid),
        )
    except Exception:
        pass
    if not room["players"]:
        online_rooms.pop(code, None)
        return
    if room["owner"] == uid:
        new_owner = next(iter(room["players"]))
        room["owner"] = new_owner
        try:
            bot.send_message(
                room["players"][new_owner]["chat_id"],
                tx(new_owner, "new_owner"),
                reply_markup=kb_owner(new_owner, code),
            )
        except Exception:
            pass
    notify_all_in_room(room, code, "player_left", nick=nick)


def close_room(call: types.CallbackQuery, uid: int, code: str) -> None:
    room = online_rooms.get(code)
    if not room:
        answer_cb(call)
        return
    if room["owner"] != uid:
        answer_cb(call, tx(uid, "only_owner"))
        return
    answer_cb(call)
    for pid, pd in room["players"].items():
        user_room.pop(pid, None)
        clear_state(pid)
        try:
            bot.send_message(pd["chat_id"], tx(pid, "room_closed"), reply_markup=kb_online_menu(pid))
        except Exception:
            pass
    online_rooms.pop(code, None)


def start_online_game(call: types.CallbackQuery, uid: int, code: str) -> None:
    room = online_rooms.get(code)
    if not room:
        answer_cb(call)
        return
    if room["owner"] != uid:
        answer_cb(call, tx(uid, "only_owner"))
        return
    n = len(room["players"])
    if n < 3:
        answer_cb(call, tx(uid, "need_more", n=n))
        return
    answer_cb(call)
    room["status"] = "playing"
    room["round_answers"] = {}
    room["votes"] = {}

    owner_settings = get_settings(uid)
    room_lang = owner_settings.get("lang", "ru")

    if owner_settings["theme_mode"] == "manual" and owner_settings["manual_theme"]:
        theme = owner_settings["manual_theme"]
    else:
        theme = get_random_theme(room_lang)

    room["theme"] = theme

    sc   = min(owner_settings["spy_count"], n - 1)
    pids = list(room["players"].keys())
    rls  = ["spy"] * sc + ["citizen"] * (n - sc)
    random.shuffle(rls)
    room["roles"] = dict(zip(pids, rls))

    for pid, pd in room["players"].items():
        role = room["roles"][pid]
        txt  = tx(pid, "online_spy_role") if role == "spy" else tx(pid, "online_citizen_role", t=theme)
        try:
            bot.send_message(
                pd["chat_id"],
                f"{tx(pid, 'game_starting')}\n\n{txt}\n\n{tx(pid, 'leave_hint')}",
                reply_markup=kb_role_ok(pid),
            )
        except Exception:
            pass

    def _delayed() -> None:
        time.sleep(4)
        start_round(code, 1)

    threading.Thread(target=_delayed, daemon=True).start()


def start_round(code: str, rnd: int) -> None:
    room = online_rooms.get(code)
    if not room:
        return
    if rnd > 3:
        for pid, pd in room["players"].items():
            try:
                bot.send_message(pd["chat_id"], tx(pid, "all_rounds_done"))
            except Exception:
                pass

        def _go_vote() -> None:
            time.sleep(3)
            start_voting(code)

        threading.Thread(target=_go_vote, daemon=True).start()
        return

    room["status"]    = "rounds"
    room["cur_round"] = rnd
    room["round_answers"].setdefault(rnd, {})

    pids = list(room["players"].keys())
    random.shuffle(pids)
    room["answer_order"]   = pids
    room["cur_answer_idx"] = 0

    order_str  = "\n".join(f"{i}. {room['players'][p]['nick']}" for i, p in enumerate(pids, 1))
    first_nick = room["players"][pids[0]]["nick"]

    for pid, pd in room["players"].items():
        try:
            bot.send_message(pd["chat_id"], tx(pid, "round_start", r=rnd, order=order_str, nick=first_nick))
        except Exception:
            pass
    ask_player(code, 0)


def ask_player(code: str, idx: int) -> None:
    room = online_rooms.get(code)
    if not room:
        return
    order = room.get("answer_order", [])

    # Пропускаем игроков которые уже вышли
    while idx < len(order) and order[idx] not in room["players"]:
        idx += 1
    room["cur_answer_idx"] = idx

    if idx >= len(order):
        rnd = room["cur_round"]
        for pid, pd in room["players"].items():
            try:
                bot.send_message(pd["chat_id"], tx(pid, "round_done", r=rnd))
            except Exception:
                pass

        def _next_rnd() -> None:
            time.sleep(3)
            start_round(code, rnd + 1)

        threading.Thread(target=_next_rnd, daemon=True).start()
        return

    pid = order[idx]
    pd  = room["players"].get(pid)
    if not pd:
        next_answer(code)
        return
    rnd = room["cur_round"]
    set_state(pid, "online_answering", {"room_code": code})
    try:
        bot.send_message(pd["chat_id"], tx(pid, "your_turn", r=rnd))
    except Exception:
        pass
    for other_pid, opd in room["players"].items():
        if other_pid != pid:
            try:
                bot.send_message(opd["chat_id"], tx(other_pid, "wait_turn", nick=pd["nick"]))
            except Exception:
                pass


def next_answer(code: str) -> None:
    room = online_rooms.get(code)
    if not room:
        return
    idx = room.get("cur_answer_idx", 0) + 1
    room["cur_answer_idx"] = idx
    ask_player(code, idx)


def start_voting(code: str) -> None:
    room = online_rooms.get(code)
    if not room:
        return
    room["status"] = "voting"
    room["votes"]  = {}
    for pid, pd in room["players"].items():
        try:
            bot.send_message(pd["chat_id"], tx(pid, "vote_title"), reply_markup=kb_vote(pid, code))
        except Exception:
            pass


def finish_voting(code: str) -> None:
    room = online_rooms.get(code)
    if not room:
        return
    votes   = room["votes"]
    players = room["players"]
    roles   = room["roles"]
    theme   = room["theme"]

    tally: dict[int, int] = {}
    for target in votes.values():
        tally[target] = tally.get(target, 0) + 1

    if tally:
        max_v      = max(tally.values())
        top        = [p for p, v in tally.items() if v == max_v]
        eliminated = top[0] if len(top) == 1 else random.choice(top)
    else:
        eliminated = None

    result_lines = [
        f"{pd['nick']} {'(шпион)' if roles.get(pid) == 'spy' else '(мирный)'}: {tally.get(pid, 0)} гол."
        for pid, pd in players.items()
    ]
    results_str = "\n".join(result_lines)
    spy_nicks   = [pd["nick"] for pid, pd in players.items() if roles.get(pid) == "spy"]
    spies_str   = ", ".join(spy_nicks) if spy_nicks else "—"

    elim_is_spy = roles.get(eliminated) == "spy" if eliminated else False
    spy_pids    = [p for p, r in roles.items() if r == "spy"]
    verdict_key = "spy_caught" if elim_is_spy and len(spy_pids) == 1 else "spy_escaped"

    for pid, pd in players.items():
        try:
            bot.send_message(
                pd["chat_id"],
                tx(pid, "vote_result", results=results_str, spies=spies_str,
                   theme=theme, verdict=tx(pid, verdict_key)),
                reply_markup=kb_online_menu(pid),
            )
        except Exception:
            pass

    for pid in list(players.keys()):
        user_room.pop(pid, None)
        clear_state(pid)
    online_rooms.pop(code, None)


# ══════════════════════════════════════════════════════════════════════════════
# КОМАНДА /leave  — выход в любой момент
# ══════════════════════════════════════════════════════════════════════════════

@bot.message_handler(commands=["leave"])
def cmd_leave(msg: types.Message) -> None:
    uid = msg.from_user.id
    cid = msg.chat.id

    code = user_room.get(uid)
    if not code or code not in online_rooms:
        safe_send(cid, tx(uid, "not_in_room"))
        return

    room   = online_rooms[code]
    status = room.get("status", "waiting")

    if status == "waiting":
        # Комната ещё не началась — обычный выход
        nick = room["players"].get(uid, {}).get("nick", "?")
        room["players"].pop(uid, None)
        user_room.pop(uid, None)
        clear_state(uid)
        safe_send(cid, tx(uid, "you_left"), reply_markup=kb_online_menu(uid))

        if not room["players"]:
            online_rooms.pop(code, None)
            return

        # Смена владельца если нужно
        if room["owner"] == uid:
            new_owner = next(iter(room["players"]))
            room["owner"] = new_owner
            try:
                bot.send_message(
                    room["players"][new_owner]["chat_id"],
                    tx(new_owner, "new_owner"),
                    reply_markup=kb_owner(new_owner, code),
                )
            except Exception:
                pass

        notify_all_in_room(room, code, "player_left", nick=nick)

    else:
        # Игра идёт — особая логика
        handle_mid_game_leave(code, uid)


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGE HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

@bot.message_handler(commands=["start"])
def cmd_start(msg: types.Message) -> None:
    uid = msg.from_user.id
    clear_state(uid)
    bot.send_message(msg.chat.id, tx(uid, "welcome"), reply_markup=kb_main(uid))


@bot.message_handler(func=lambda m: True)
def handle_text(msg: types.Message) -> None:
    uid   = msg.from_user.id
    cid   = msg.chat.id
    text  = (msg.text or "").strip()
    info  = get_state(uid)
    state = info["state"]

    if state == "solo_wait_theme":
        if len(text) < 2:
            safe_send(cid, tx(uid, "theme_too_short"))
            return
        data = info["data"]
        data["theme"]     = text
        data["spy_count"] = get_settings(uid)["spy_count"]
        clear_state(uid)
        launch_solo(cid, uid, data)

    elif state == "settings_wait_theme":
        if len(text) < 2:
            safe_send(cid, tx(uid, "theme_too_short"))
            return
        s = get_settings(uid)
        s["theme_mode"]   = "manual"
        s["manual_theme"] = text
        clear_state(uid)
        safe_send(cid, tx(uid, "theme_saved", t=text), reply_markup=kb_settings(uid))

    elif state == "settings_wait_nick":
        if not 3 <= len(text) <= 15:
            safe_send(cid, tx(uid, "nick_bad"))
            return
        get_settings(uid)["nick"] = text
        clear_state(uid)
        safe_send(cid, tx(uid, "nick_saved", nick=text), reply_markup=kb_settings(uid))

    elif state == "online_wait_code":
        clear_state(uid)
        join_room(cid, uid, text.upper())

    elif state == "online_answering":
        handle_online_answer(uid, cid, text, info)

    else:
        safe_send(cid, tx(uid, "use_start"))


def handle_online_answer(
    uid: int,
    cid: int,
    text: str,
    info: dict[str, Any],
) -> None:
    room_code = info["data"].get("room_code")
    room      = online_rooms.get(room_code)
    if not room or room.get("status") != "rounds":
        clear_state(uid)
        return
    order   = room.get("answer_order", [])
    cur_idx = room.get("cur_answer_idx", 0)
    if not order or cur_idx >= len(order):
        return
    if order[cur_idx] != uid:
        cur_nick = room["players"].get(order[cur_idx], {}).get("nick", "?")
        safe_send(cid, tx(uid, "wait_turn", nick=cur_nick))
        return
    if "\n" in text or len(text) < 2:
        safe_send(cid, tx(uid, "one_sentence_only"))
        return
    if len(text) > 200:
        safe_send(cid, tx(uid, "too_long"))
        return

    cur_round = room.get("cur_round", 1)
    room["round_answers"].setdefault(cur_round, {})[uid] = text
    clear_state(uid)
    safe_send(cid, tx(uid, "answer_sent"))

    nick = room["players"][uid]["nick"]
    for pid, pd in room["players"].items():
        if pid != uid:
            try:
                bot.send_message(pd["chat_id"], tx(pid, "player_answered", nick=nick, text=text))
            except Exception:
                pass
    next_answer(room_code)


# ══════════════════════════════════════════════════════════════════════════════
# CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call: types.CallbackQuery) -> None:
    uid  = call.from_user.id
    cid  = call.message.chat.id
    data = call.data

    if data == "main_menu":
        clear_state(uid)
        answer_cb(call)
        edit_call(call, tx(uid, "main_menu_title"), kb_main(uid))

    elif data == "support":
        answer_cb(call)
        edit_call(call, tx(uid, "support_text"), kb_back_main(uid))

    elif data == "settings_menu":
        answer_cb(call)
        edit_call(call, tx(uid, "settings_title"), kb_settings(uid))

    elif data == "settings_nick":
        answer_cb(call)
        set_state(uid, "settings_wait_nick")
        safe_send(cid, tx(uid, "enter_nick_prompt"))

    elif data == "settings_spy_menu":
        answer_cb(call)
        edit_call(call, tx(uid, "spy_count_title"), kb_spy_count(uid))

    elif data in ("set_spy_1", "set_spy_2", "set_spy_3"):
        n = int(data[-1])
        get_settings(uid)["spy_count"] = n
        answer_cb(call, tx(uid, "spy_saved", n=n))
        edit_call(call, tx(uid, "settings_title"), kb_settings(uid))

    elif data == "settings_theme_toggle":
        s = get_settings(uid)
        if s["theme_mode"] == "auto":
            set_state(uid, "settings_wait_theme")
            answer_cb(call)
            safe_send(cid, tx(uid, "enter_theme"))
        else:
            s["theme_mode"]   = "auto"
            s["manual_theme"] = ""
            answer_cb(call)
            edit_call(call, tx(uid, "settings_title"), kb_settings(uid))

    elif data == "settings_lang_toggle":
        s = get_settings(uid)
        s["lang"] = "en" if s.get("lang", "ru") == "ru" else "ru"
        answer_cb(call)
        edit_call(call, tx(uid, "settings_title"), kb_settings(uid))

    elif data == "solo_menu":
        clear_state(uid)
        answer_cb(call)
        edit_call(call, tx(uid, "solo_title"), kb_solo_players(uid))

    elif data.startswith("solo_players_"):
        n = int(data.split("_")[-1])
        set_state(uid, "solo_choose_theme", {"player_count": n})
        answer_cb(call)
        edit_call(call, tx(uid, "solo_theme_q", n=n), kb_solo_theme(uid))

    elif data == "solo_theme_auto":
        info = get_state(uid)
        pc   = info["data"].get("player_count", 4)
        clear_state(uid)
        answer_cb(call)
        lang = get_settings(uid).get("lang", "ru")
        launch_solo(cid, uid, {
            "player_count": pc,
            "theme":        get_random_theme(lang),
            "spy_count":    get_settings(uid)["spy_count"],
        })

    elif data == "solo_theme_manual":
        info = get_state(uid)
        pc   = info["data"].get("player_count", 4)
        set_state(uid, "solo_wait_theme", {"player_count": pc})
        answer_cb(call)
        safe_send(cid, tx(uid, "enter_manual_theme"))

    elif data.startswith("show_role_"):
        idx  = int(data.split("_")[-1])
        game = solo_games.get(uid)
        if not game:
            answer_cb(call)
            return
        answer_cb(call)
        role = game["roles"][idx]
        role_text = tx(uid, "spy_role") if role == "spy" else tx(uid, "citizen_role", t=game["theme"])
        edit_call(
            call,
            f"Игрок {idx + 1}\n\n{role_text}{tx(uid, 'role_note')}",
            kb_after_role(uid, idx, game["player_count"]),
        )

    elif data.startswith("next_player_"):
        idx  = int(data.split("_")[-1])
        game = solo_games.get(uid)
        if not game:
            answer_cb(call)
            return
        answer_cb(call)
        edit_call(call, tx(uid, "pass_phone", n=idx + 1), kb_show_role(uid, idx))

    elif data == "solo_start_discuss":
        game = solo_games.get(uid)
        if not game:
            answer_cb(call)
            return
        answer_cb(call)
        sc = sum(1 for r in game["roles"] if r == "spy")
        edit_call(call, tx(uid, "discuss_title", s=sc), kb_discussion(uid))

    elif data == "solo_end_confirm":
        answer_cb(call)
        edit_call(call, tx(uid, "end_game_q"), kb_end_confirm(uid))

    elif data == "solo_reveal":
        game = solo_games.get(uid)
        answer_cb(call)
        if not game:
            edit_call(call, tx(uid, "main_menu_title"), kb_main(uid))
            return
        spies   = [f"Игрок {i + 1}" for i, r in enumerate(game["roles"]) if r == "spy"]
        spy_str = ", ".join(spies)
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton(tx(uid, "btn_new_game"),  callback_data="solo_menu"),
            types.InlineKeyboardButton(tx(uid, "btn_main_menu"), callback_data="main_menu"),
        )
        edit_call(call, tx(uid, "reveal_text", t=game["theme"], spies=spy_str), kb)
        solo_games.pop(uid, None)

    elif data == "online_menu":
        answer_cb(call)
        edit_call(call, tx(uid, "online_title"), kb_online_menu(uid))

    elif data == "online_create_private":
        nick = get_nick(uid)
        if not nick:
            answer_cb(call)
            safe_send(cid, tx(uid, "nick_required"))
            return
        answer_cb(call)
        create_room(cid, uid, nick, public=False)

    elif data == "online_create_public":
        nick = get_nick(uid)
        if not nick:
            answer_cb(call)
            safe_send(cid, tx(uid, "nick_required"))
            return
        answer_cb(call)
        create_room(cid, uid, nick, public=True)

    elif data == "online_join_private":
        nick = get_nick(uid)
        if not nick:
            answer_cb(call)
            safe_send(cid, tx(uid, "nick_required"))
            return
        answer_cb(call)
        set_state(uid, "online_wait_code")
        safe_send(cid, tx(uid, "enter_code"))

    elif data == "online_free_game":
        nick = get_nick(uid)
        if not nick:
            answer_cb(call)
            safe_send(cid, tx(uid, "nick_required"))
            return
        answer_cb(call)
        free_join(cid, uid, nick)

    elif data.startswith("online_start_"):
        code = data[len("online_start_"):]
        start_online_game(call, uid, code)

    elif data.startswith("online_close_"):
        code = data[len("online_close_"):]
        close_room(call, uid, code)

    elif data.startswith("online_leave_"):
        code = data[len("online_leave_"):]
        leave_room(call, uid, code)

    elif data == "online_role_ok":
        answer_cb(call)
        try:
            bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=None)
        except Exception:
            pass

    elif data.startswith("vote_"):
        parts      = data.split("_", 2)
        room_code  = parts[1]
        target_uid = int(parts[2])
        room       = online_rooms.get(room_code)
        if not room or room.get("status") != "voting":
            answer_cb(call)
            return
        if uid not in room["players"]:
            answer_cb(call)
            return
        if uid == target_uid:
            answer_cb(call, tx(uid, "cant_vote_self"))
            return
        if uid in room["votes"]:
            answer_cb(call, tx(uid, "already_voted"))
            return
        room["votes"][uid] = target_uid
        target_nick = room["players"].get(target_uid, {}).get("nick", "?")
        answer_cb(call, tx(uid, "you_voted", nick=target_nick))
        try:
            bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=None)
        except Exception:
            pass
        total = len(room["players"])
        done  = len(room["votes"])
        for pid, pd in room["players"].items():
            try:
                bot.send_message(pd["chat_id"], tx(pid, "vote_progress", done=done, total=total))
            except Exception:
                pass
        if done >= total:
            finish_voting(room_code)

    else:
        answer_cb(call)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Бот запущен! Для остановки нажмите Ctrl+C")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)