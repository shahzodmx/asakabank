import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 1. BotFather'dan olingan tokenni shu yerga qo'ying:
BOT_TOKEN = "8979749857:AAHqBqGboGFXyxrQeOdg_S2mUJLZfPkEaSo"

# Muallif va mutaxassis ma'lumotlari
AUTHOR_NAME = "Matrasulov Shahzod"
AUTHOR_ROLE = "Kredit inspektori"
AUTHOR_PHONE = "+998 91 431 41 91"
AUTHOR_TG_URL = "https://t.me/Shahzod_Matrasulov"
AUTHOR_TG_USER = "@Shahzod_Matrasulov"

# Har bir hisob-kitob pastida chiqadigan muallif imzosi
AUTHOR_FOOTER = (
    f"\n━━━━━━━━━━━━━━━━━━\n"
    f"👨‍💼 <b>Loyiha muallifi va mas'ul mutaxassis:</b>\n"
    f"<b>{AUTHOR_NAME}</b> ({AUTHOR_ROLE})\n"
    f"📞 Tel: <b>{AUTHOR_PHONE}</b>\n"
    f"📲 Telegram: {AUTHOR_TG_USER}"
)

# =====================================================================
# 2. DAMAS MODELLARI VA NARXLARI (Rasmlarning asl nomlari bilan)
# =====================================================================
MODELS = {
    "d2": {
        "name": "DAMAS D2 STYLE PLUS (DELUX)",
        "desc": "3 qator oynali, yo'lovchi tashishga mo'ljallangan (odam minadigan)",
        "photo": "damas d2 odom.png",
        "rasrochka_price": 96_932_000,
        "kredit_price": 81_932_000,
    },
    "d3": {
        "name": "DAMAS D3 STYLE (COMBI)",
        "desc": "2 qatori oynali, 3-qatori oynasiz (aralash tip)",
        "photo": "damas combi.png",
        "rasrochka_price": 96_449_000,
        "kredit_price": 81_449_000,
    },
    "d11": {
        "name": "DAMAS D11 STYLE (VAN)",
        "desc": "1-qatori oynali, qolgan ikki qatori oynasiz (yuk tashish uchun)",
        "photo": "damas van.png",
        "rasrochka_price": 93_156_000,
        "kredit_price": 78_156_000,
    },
}

# =====================================================================
# 3. AVTOKREDIT 2.6 JADVALI
# Format: Toifa -> { Boshlang'ich to'lov (%): { Muddat (oy): Yillik foiz (%) } }
# =====================================================================
AVTOKREDIT_2_6 = {
    "payroll": {  # Ish haqi loyihasidagi mijozlar
        20: {36: 21.9, 48: 22.9, 60: 23.9},
        30: {12: 18.9, 24: 19.9, 36: 20.9, 48: 21.9, 60: 22.9},
        50: {36: 19.9, 48: 20.9, 60: 21.9},
    },
    "official": {  # Rasmiy daromadli mijozlar
        20: {36: 22.9, 48: 23.9, 60: 24.9},
        30: {12: 19.9, 24: 20.9, 36: 21.9, 48: 22.9, 60: 23.9},
        50: {36: 20.9, 48: 21.9, 60: 22.9},
    },
    "self": {  # O'zini o'zi band qilgan (Rasmiy daromadsiz) mijozlar
        30: {12: 19.9, 24: 20.9, 36: 22.9, 48: 23.9, 60: 24.9},
        50: {36: 21.9, 48: 22.9, 60: 23.9},
    },
}

# =====================================================================
# 4. RASSROCHKA (UzAuto Motors II — 0% foizsiz) JADVALI — DAMAS UCHUN
# Mijoz xohishiga qarab 12 oygacha kamaytirib tanlash imkoniyati bilan
# =====================================================================
RASROCHKA_DAMAS = {
    "official": {  # Rasmiy daromadli mijozlarga (25% dan boshlanadi)
        25: [12, 16],
        30: [12, 16, 18],
        40: [12, 16, 18, 24],
        50: [12, 18, 24, 30],
        60: [12, 18, 24, 30, 36],
    },
    "self": {  # Rasmiy daromadsiz / O'zini o'zi band qilganlarga (30% dan boshlanadi)
        30: [12, 16, 18],
        40: [12, 16, 18, 24],
        50: [12, 18, 24, 30],
        60: [12, 18, 24, 30, 36],
    },
}

# =====================================================================
# 5. SHARTLAR VA TALABLAR MATNLARI (AVTOKREDIT VA RASSROCHKA UCHUN ALOHIDA)
# =====================================================================
SHARTLAR_KREDIT = (
    "📋 <b>AVTOKREDIT 2.6 — SHARTLAR VA TALABLAR:</b>\n\n"
    "Birlamchi bozordan barcha turdagi mamlakatimizda ishlab chiqarilgan va import qilinadigan "
    "avtotransport vositalarini sotib olish uchun ajratiladi:\n\n"
    "🔹 <b>Kredit muddati</b> – uzaytirish huquqisiz 60 oygacha. Imtiyozli davr - ko'zda tutilmagan.\n"
    "🔹 <b>Kredit soni va summasi</b> – avtotransport vositasining 80%dan ko’p bo’lmagan miqdorda:\n"
    "• <i>Rasmiy daromadlari mavjud bo‘lgan qarz oluvchilarga</i> ikkitadan ko‘p bo'lmagan va kredit miqdori "
    "1 (bir) mlrd. so'mdan oshmagan miqdorda;\n"
    "• <i>Rasmiy daromadlari mavjud bo'lmagan qarz oluvchilarga</i> bittadan ko'p bo'lmagan va kredit miqdori "
    "750,0 (yetti yuz ellik) mln. so'mdan oshmagan miqdorda avtokreditlar ajratiladi.\n\n"
    "🔹 <b>Boshlang’ich badal</b> – avtotransport vositasi qiymatining 20 foizdan kam bo’lmagan miqdorda.\n"
    "🔹 <b>Ta'minot</b> – Uchinchi shaxs kafilligi va kredit hisobiga sotib olinayotgan avtotransport vositasi garovi asosida ajratiladi. "
    "Sug’urta mukofoti to’lovi rasmiylashtirilayotgan kredit hisobidan amalga oshirilishi mumkin.\n"
    "🔹 <b>Trade-IN</b> – Trade-IN tizimidan foydalangan holda eski avtomobilni rasmiy dilerga topshirib, eski va yangi avtomobil narxlari "
    "o'rtadagi farq summasiga Asakabank tomonidan avtokredit ajratadi! Topshirilgan avtomobil narxi boshlang’ich badal sifatida qabul qilinadi.\n"
    "🔹 <b>Birgalikda qarz oluvchi</b> – Qarz oluvchining daromadlari kreditning oylik to'lovlarini qoplash uchun yetarli bo’lmagan taqdirda, "
    "birgalikda qarz oluvchi qabul qilish mumkin.\n"
    "🔹 <b>Yosh chegarasi</b> – Kredit 18 yoshga to‘lgan (rasmiy daromadlari mavjud bo‘lmagan qarz oluvchi 21 yoshga to‘lgan) va "
    "65 yoshdan oshmagan, muomalaga layoqatli O‘zbekiston Respublikasi fuqarolariga ajratiladi.\n\n"
    "✅ <b>Daromadni tasdiqlovchi hujjatlarsiz!</b>\n"
    "✅ Ariza berish vaqtida muddati o'tgan qarzning yo'qligi."
)

SHARTLAR_RASROCHKA = (
    "📋 <b>RASSROCHKA (UzAuto Motors II) — SHARTLAR VA TALABLAR:</b>\n\n"
    "Birlamchi bozordan \"UzAuto Motors\" AJ tomonidan ishlab chiqarilgan Damas, Labo, Captiva, Onix va "
    "Tracker, Tahoe avtotransport vositalarini sotib olish uchun ajratiladi:\n\n"
    "🔹 <b>Kredit muddati</b> – uzaytirish huquqisiz 60 oygacha. Imtiyozli davr ko'zda tutilmagan.\n"
    "🔹 <b>Kredit soni va summasi</b> – avtotransport vositasining 80%dan ko’p bo’lmagan miqdorda.\n"
    "<i>*Aksiyada Damas, Labo, Captiva, Onix va Tracker, Tahoe avtomobillarining chegirmasiz narxlardagi "
    "modifikatsiyalari (avtomobillarni yetkazib berish bo'yicha \"SB\" partiyadagi shartnomalar) ishtirok etadi.</i>\n"
    "• Rasmiy daromadlari mavjud bo‘lgan qarz oluvchilarga ikkitadan ko‘p bo'lmagan va kredit miqdori "
    "1 (bir) mlrd. so'mdan oshmagan miqdorda;\n\n"
    "🔹 <b>Boshlang’ich badal</b> – avtotransport vositasi qiymatining 25 foizdan kam bo’lmagan miqdorda.\n"
    "🔹 <b>Ta'minot</b> – Kredit hisobiga sotib olinayotgan avtotransport vositasi garovi asosida ajratiladi.\n"
    "🔹 <b>Trade-IN</b> – Trade-IN tizimidan foydalangan holda eski avtomobilni rasmiy dilerga topshirib, eski va yangi avtomobil narxlari "
    "o'rtadagi farq summasiga Asakabank tomonidan avtokredit ajratadi! Topshirilgan avtomobil narxi boshlang’ich badal sifatida qabul qilinadi.\n"
    "🔹 <b>Birgalikda qarz oluvchi</b> – Qarz oluvchining daromadlari kreditning oylik to'lovlarini qoplash uchun yetarli bo’lmagan taqdirda, "
    "birgalikda qarz oluvchi qabul qilish mumkin.\n"
    "🔹 <b>Yosh chegarasi</b> – Kredit 18 yoshga to‘lgan va 65 yoshdan oshmagan, muomalaga layoqatli "
    "O‘zbekiston Respublikasi fuqarolariga ajratiladi.\n\n"
    "✅ Ariza berish vaqtida muddati o'tgan qarzning yo'qligi."
)


# =====================================================================
# 6. HISOB-KITOB FUNKSIYASI (KALKULYATOR VA SUG'URTA)
# =====================================================================
def fmt(num: float) -> str:
    """Raqamlarni chiroyli formatlash: 81 932 000"""
    return f"{round(num):,}".replace(",", " ")


def calculate_all(price: int, dp_percent: int, months: int, annual_rate: float, schedule: str) -> dict:
    """
    Sug'urta formulasi:
    1 yillik sug'urta = ((Kredit summasi * 125) / 100) * 0.7%
    1 oylik sug'urta = 1 yillik sug'urta / 12
    Jami sug'urta = 1 oylik sug'urta * kredit oylari soni (months)
    """
    dp_amount = price * (dp_percent / 100.0)
    loan_amount = price - dp_amount

    # Sug'urtani hisoblash (aniq siz aytgan usulda)
    yearly_insurance = ((loan_amount * 125.0) / 100.0) * 0.007
    monthly_insurance = yearly_insurance / 12.0
    total_insurance = monthly_insurance * months

    monthly_rate = (annual_rate / 100.0) / 12.0

    if annual_rate == 0:
        first_payment = loan_amount / months
        last_payment = first_payment
        total_loan_payment = loan_amount
    elif schedule == "ann":
        # Annuitet (har oy bir xil to'lov)
        first_payment = loan_amount * (monthly_rate / (1.0 - (1.0 + monthly_rate) ** (-months)))
        last_payment = first_payment
        total_loan_payment = first_payment * months
    else:
        # Differensial (kamayib boruvchi grafik)
        principal_monthly = loan_amount / months
        first_payment = principal_monthly + (loan_amount * monthly_rate)
        last_payment = principal_monthly + (principal_monthly * monthly_rate)
        total_interest = 0.0
        balance = loan_amount
        for _ in range(months):
            total_interest += balance * monthly_rate
            balance -= principal_monthly
        total_loan_payment = loan_amount + total_interest

    return {
        "price": price,
        "dp_percent": dp_percent,
        "dp_amount": dp_amount,
        "loan_amount": loan_amount,
        "months": months,
        "annual_rate": annual_rate,
        "first_payment": first_payment,
        "last_payment": last_payment,
        "total_loan_payment": total_loan_payment,
        "yearly_insurance": yearly_insurance,
        "monthly_insurance": monthly_insurance,
        "total_insurance": total_insurance,
    }


# =====================================================================
# 7. EKRANNI TOZA YANGILASH FUNKSIYASI
# =====================================================================
async def render_screen(update: Update, text: str, keyboard: list, photo_path: str = None):
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.answer()
        chat_id = query.message.chat_id
        try:
            await query.message.delete()
        except Exception:
            pass
    else:
        chat_id = update.effective_chat.id

    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as photo:
            await update.get_bot().send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
    else:
        await update.get_bot().send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )


# =====================================================================
# 8. BOSH SAHIFA VA BARCHA BO'LIMLAR LOGIKASI
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🏦 <b>Asakabank axborot va xizmatlar botiga xush kelibsiz!</b>\n\n"
        "Ushbu bot orqali siz bankning barcha turdagi kreditlari, omonatlari, "
        "plastik kartalari va boshqa moliyaviy xizmatlari haqida sodda hamda "
        "tushunarli tilda to'liq ma'lumot olishingiz mumkin.\n\n"
        f"👨‍💼 <b>Loyiha muallifi:</b>\n"
        f"Asakabank {AUTHOR_ROLE.lower()} <b>{AUTHOR_NAME}</b>\n"
        f"📞 Murojaat uchun: <b>{AUTHOR_PHONE}</b>\n\n"
        "👇 Kerakli bo'limni tanlang:"
    )
    keyboard = [
        [InlineKeyboardButton("🚗 Avtokredit", callback_data="menu_avto")],
        [
            InlineKeyboardButton("🏠 Ipoteka krediti", callback_data="soon:ipoteka"),
            InlineKeyboardButton("💰 Omonatlar", callback_data="soon:omonat"),
        ],
        [
            InlineKeyboardButton("💳 Plastik kartalar", callback_data="soon:karta"),
            InlineKeyboardButton("💵 Mikroqarz", callback_data="soon:mikroqarz"),
        ],
        [InlineKeyboardButton("👨‍💼 Mutaxassis bilan bog'lanish", callback_data="contact_author")],
    ]
    await render_screen(update, text, keyboard)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    parts = data.split(":")

    # Bosh menyuga qaytish
    if data == "main":
        await start(update, context)
        return

    # Keyingi bosqichda qo'shiladigan bo'limlar uchun ma'lumot oynasi
    if parts[0] == "soon":
        text = (
            "⏳ <b>Bu bo'lim hozirda boyitilmoqda!</b>\n\n"
            "Ushbu bank mahsuloti bo'yicha hoziroq to'liq ma'lumot va maslahat olish uchun "
            "mas'ul mutaxassis bilan bog'lanishingiz mumkin:"
            f"{AUTHOR_FOOTER}"
        )
        keyboard = [
            [InlineKeyboardButton("📲 Telegram orqali yozish", url=AUTHOR_TG_URL)],
            [InlineKeyboardButton("⬅️ Bosh sahifaga qaytish", callback_data="main")],
        ]
        await render_screen(update, text, keyboard)
        return

    # Mutaxassis bilan bog'lanish oynasi
    if data == "contact_author":
        text = (
            "👨‍💼 <b>BANK MUTAXASSISI BILAN BOG'LANISH</b>\n\n"
            "Kredit rasmiylashtirish, hujjatlar ro'yxati yoki boshqa bank xizmatlari bo'yicha "
            "savollaringiz bo'lsa, bevosita murojaat qilishingiz mumkin:\n\n"
            f"👤 <b>Mutaxassis:</b> {AUTHOR_NAME}\n"
            f"🏦 <b>Lavozim:</b> Asakabank {AUTHOR_ROLE}\n"
            f"📞 <b>Telefon:</b> <code>{AUTHOR_PHONE}</code>\n"
            f"📲 <b>Telegram:</b> {AUTHOR_TG_USER}"
        )
        keyboard = [
            [InlineKeyboardButton("📲 Telegram orqali yozish", url=AUTHOR_TG_URL)],
            [InlineKeyboardButton("⬅️ Bosh sahifaga qaytish", callback_data="main")],
        ]
        await render_screen(update, text, keyboard)
        return

    # =================================================================
    # AVTOKREDIT BO'LIMI VA MODELLAR
    # =================================================================
    if data == "menu_avto":
        text = (
            "🚗 <b>AVTOKREDIT BO'LIMI</b>\n\n"
            "Avtomobil rusumini tanlang:"
        )
        keyboard = [
            [InlineKeyboardButton("🚐 DAMAS (3 xil model)", callback_data="brand_damas")],
            [InlineKeyboardButton("⬅️ Bosh sahifaga qaytish", callback_data="main")],
        ]
        await render_screen(update, text, keyboard)
        return

    # Damas 3 xil modifikatsiyasi
    if data == "brand_damas":
        text = (
            "🚐 <b>CHEVROLET DAMAS MODELLARI</b>\n\n"
            "Damas avtomobili 3 xil modifikatsiyada taqdim etiladi.\n"
            "Narxlar va shartlarni ko'rish uchun kerakli modelni tanlang:"
        )
        keyboard = [
            [InlineKeyboardButton("1️⃣ D2 STYLE PLUS (DELUX) — Odam minadigan", callback_data="model:d2")],
            [InlineKeyboardButton("2️⃣ D3 STYLE (COMBI) — 2 qator oynali", callback_data="model:d3")],
            [InlineKeyboardButton("3️⃣ D11 STYLE (VAN) — Yuk uchun", callback_data="model:d11")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="menu_avto")],
        ]
        await render_screen(update, text, keyboard)
        return

    # Tanlangan Damas modeli kartasi (Rasm + 2 xil summa + ta'rif)
    if parts[0] == "model":
        m_key = parts[1]
        m = MODELS[m_key]
        text = (
            f"🚐 <b>{m['name']}</b>\n"
            f"ℹ️ <i>{m['desc']}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ <b>RASSROCHKA (Muddatli to'lov) SUMMASI:</b>\n"
            f"💰 <b>{fmt(m['rasrochka_price'])} so'm</b>\n"
            f"• Foiz stavkasi 0% dan\n"
            f"• Kredit muddati 60 oygacha\n"
            f"• Boshlang'ich to'lov 25% dan\n\n"
            f"2️⃣ <b>AVTOKREDIT SUMMASI (Arzon narxda):</b>\n"
            f"💰 <b>{fmt(m['kredit_price'])} so'm</b>\n"
            f"• Foiz stavkasi 18,9% dan\n"
            f"• Kredit muddati 60 oygacha\n"
            f"• Boshlang'ich to'lov 20% dan\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👇 Oylik to'lov va sug'urtani hisoblash uchun variantni tanlang:"
        )
        keyboard = [
            [InlineKeyboardButton("🧮 Avtokredit (Arzon narxda hisoblash)", callback_data=f"kred_inc:{m_key}")],
            [InlineKeyboardButton("🧮 Rassrochka (0% foizsiz hisoblash)", callback_data=f"ras_inc:{m_key}")],
            [InlineKeyboardButton("📋 Shartlar va talablar (Avtokredit)", callback_data=f"terms_kred:{m_key}")],
            [InlineKeyboardButton("📋 Shartlar va talablar (Rassrochka)", callback_data=f"terms_ras:{m_key}")],
            [InlineKeyboardButton("⬅️ Damas modellariga qaytish", callback_data="brand_damas")],
        ]
        await render_screen(update, text, keyboard, photo_path=m["photo"])
        return

    # Shartlar va talablar (Avtokredit)
    if parts[0] == "terms_kred":
        m_key = parts[1]
        keyboard = [
            [InlineKeyboardButton("🧮 Avtokreditni hisoblash", callback_data=f"kred_inc:{m_key}")],
            [InlineKeyboardButton("⬅️ Avtomobilga qaytish", callback_data=f"model:{m_key}")],
        ]
        await render_screen(update, SHARTLAR_KREDIT + AUTHOR_FOOTER, keyboard)
        return

    # Shartlar va talablar (Rassrochka)
    if parts[0] == "terms_ras":
        m_key = parts[1]
        keyboard = [
            [InlineKeyboardButton("🧮 Rassrochkani hisoblash", callback_data=f"ras_inc:{m_key}")],
            [InlineKeyboardButton("⬅️ Avtomobilga qaytish", callback_data=f"model:{m_key}")],
        ]
        await render_screen(update, SHARTLAR_RASROCHKA + AUTHOR_FOOTER, keyboard)
        return

    # =================================================================
    # AVTOKREDIT 2.6 KALKULYATORI BOSQICHLARI
    # =================================================================
    # 1-qadam: Daromad turini tanlash (3 xil variant)
    if parts[0] == "kred_inc":
        m_key = parts[1]
        m = MODELS[m_key]
        text = (
            f"🚐 <b>{m['name']}</b>\n"
            f"💵 Avtokredit narxi: <b>{fmt(m['kredit_price'])} so'm</b>\n\n"
            f"📌 <b>1-qadam: Daromad turini tanlang:</b>"
        )
        keyboard = [
            [InlineKeyboardButton("🏦 Ish haqi loyihasi (18.9% dan)", callback_data=f"kred_dp:{m_key}:payroll")],
            [InlineKeyboardButton("💼 Rasmiy daromadga ega shaxs (19.9% dan)", callback_data=f"kred_dp:{m_key}:official")],
            [InlineKeyboardButton("🛠 O'zini o'zi band qilgan shaxs (19.9% dan)", callback_data=f"kred_dp:{m_key}:self")],
            [InlineKeyboardButton("📋 Shartlar va talablar", callback_data=f"terms_kred:{m_key}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"model:{m_key}")],
        ]
        await render_screen(update, text, keyboard, photo_path=m["photo"])
        return

    # 2-qadam: Boshlang'ich to'lovni tanlash
    if parts[0] == "kred_dp":
        _, m_key, inc_type = parts
        m = MODELS[m_key]
        inc_names = {
            "payroll": "Ish haqi loyihasi",
            "official": "Rasmiy daromadga ega",
            "self": "O'zini o'zi band qilgan shaxs",
        }
        text = (
            f"🚐 <b>{m['name']}</b>\n"
            f"💵 Kredit narxi: <b>{fmt(m['kredit_price'])} so'm</b>\n"
            f"👤 Toifa: <b>{inc_names[inc_type]}</b>\n\n"
            f"📌 <b>2-qadam: Boshlang'ich to'lov miqdorini tanlang:</b>"
        )
        keyboard = []
        for dp in AVTOKREDIT_2_6[inc_type].keys():
            dp_sum = fmt(m["kredit_price"] * dp / 100)
            keyboard.append([
                InlineKeyboardButton(
                    f"💰 {dp}% — {dp_sum} so'm",
                    callback_data=f"kred_m:{m_key}:{inc_type}:{dp}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"kred_inc:{m_key}")])
        await render_screen(update, text, keyboard, photo_path=m["photo"])
        return

    # 3-qadam: Muddatni tanlash
    if parts[0] == "kred_m":
        _, m_key, inc_type, dp_str = parts
        dp = int(dp_str)
        m = MODELS[m_key]
        dp_sum = fmt(m["kredit_price"] * dp / 100)
        text = (
            f"🚐 <b>{m['name']}</b>\n"
            f"💵 Narxi: <b>{fmt(m['kredit_price'])} so'm</b>\n"
            f"💰 Boshlang'ich to'lov ({dp}%): <b>{dp_sum} so'm</b>\n\n"
            f"📌 <b>3-qadam: Kredit muddatini tanlang:</b>\n"
            f"<i>(Yillik foiz stavkasi jadval bo'yicha avtomat belgilanadi)</i>"
        )
        keyboard = []
        for months, rate in AVTOKREDIT_2_6[inc_type][dp].items():
            years = months // 12
            keyboard.append([
                InlineKeyboardButton(
                    f"🗓 {months} oy ({years} yil) — Yillik {rate}%",
                    callback_data=f"kred_sch:{m_key}:{inc_type}:{dp}:{months}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"kred_dp:{m_key}:{inc_type}")])
        await render_screen(update, text, keyboard)
        return

    # 4-qadam: Grafik turini tanlash (Annuitet yoki Differensial izohi bilan)
    if parts[0] == "kred_sch":
        _, m_key, inc_type, dp_str, m_str = parts
        dp, months = int(dp_str), int(m_str)
        rate = AVTOKREDIT_2_6[inc_type][dp][months]
        m = MODELS[m_key]
        text = (
            f"🚐 <b>{m['name']}</b>\n"
            f"• Boshlang'ich to'lov: <b>{dp}% ({fmt(m['kredit_price'] * dp / 100)} so'm)</b>\n"
            f"• Kredit muddati: <b>{months} oy ({months // 12} yil)</b>\n"
            f"• Yillik foiz stavkasi: <b>{rate}%</b>\n\n"
            f"📌 <b>4-qadam: To'lov grafigini tanlang va «Hisoblash» tugmasini bosing:</b>\n\n"
            f"💡 <b>Oddiy izoh:</b>\n"
            f"🔹 <b>Annuitet (Har oy bir xil to'lov)</b> — Kredit muddati tugaguncha har oy bir xil summadan to'lab borasiz.\n\n"
            f"🔹 <b>Differensial (Kamayib boruvchi grafik)</b> — Dastlabki oylarda to'lov sal ko'proq bo'ladi, lekin har oy to'lov kamayib boradi va umumiy foizdan yutasiz."
        )
        keyboard = [
            [InlineKeyboardButton("🧮 Hisoblash: Har oy bir xil (Annuitet)", callback_data=f"kred_res:{m_key}:{inc_type}:{dp}:{months}:ann")],
            [InlineKeyboardButton("🧮 Hisoblash: Kamayib boruvchi (Differensial)", callback_data=f"kred_res:{m_key}:{inc_type}:{dp}:{months}:diff")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"kred_m:{m_key}:{inc_type}:{dp}")],
        ]
        await render_screen(update, text, keyboard)
        return

    # 5-qadam: Avtokredit Natijasi + Sug'urta + Mutaxassis bilan bog'lanish
    if parts[0] == "kred_res":
        _, m_key, inc_type, dp_str, m_str, sch = parts
        dp, months = int(dp_str), int(m_str)
        m = MODELS[m_key]
        rate = AVTOKREDIT_2_6[inc_type][dp][months]
        res = calculate_all(m["kredit_price"], dp, months, rate, sch)

        inc_names = {
            "payroll": "Ish haqi loyihasi",
            "official": "Rasmiy daromadga ega",
            "self": "O'zini o'zi band qilgan shaxs",
        }
        sch_label = "Har oy bir xil (Annuitet)" if sch == "ann" else "Kamayib boruvchi (Differensial)"

        if sch == "ann":
            pay_block = f"💳 <b>Har oylik to'lov (bir xil):</b>\n👉 <b>{fmt(res['first_payment'])} so'm</b>"
        else:
            pay_block = (
                f"💳 <b>Har oylik to'lov (kamayib boruvchi):</b>\n"
                f"• 1-oylik to'lov: <b>{fmt(res['first_payment'])} so'm</b>\n"
                f"• Oxirgi ({months}-oy) to'lov: <b>{fmt(res['last_payment'])} so'm</b>"
            )

        text = (
            f"✅ <b>AVTOKREDIT — HISOB-KITOB NATIJASI</b>\n\n"
            f"🚐 Model: <b>{m['name']}</b>\n"
            f"👤 Toifa: <b>{inc_names[inc_type]}</b>\n"
            f"📊 Grafik: <b>{sch_label}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Avtomobil narxi: <b>{fmt(res['price'])} so'm</b>\n"
            f"💰 Boshlang'ich to'lov ({dp}%): <b>{fmt(res['dp_amount'])} so'm</b>\n"
            f"🏦 Bank chiqaradigan kredit: <b>{fmt(res['loan_amount'])} so'm</b>\n"
            f"🗓 Kredit muddati: <b>{months} oy ({months // 12} yil)</b>\n"
            f"📈 Yillik foiz stavkasi: <b>{rate}%</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{pay_block}\n\n"
            f"🛡 <b>SUG'URTA BADALI (Avtomat hisoblandi):</b>\n"
            f"• 1 yillik sug'urta: <b>{fmt(res['yearly_insurance'])} so'm</b>\n"
            f"• Jami <b>{months} oy</b> uchun sug'urta badali:\n"
            f"👉 <b>{fmt(res['total_insurance'])} so'm</b>\n"
            f"📌 <b>Boshlang'ich to'lov + Sug'urta:</b>\n"
            f"👉 <b>{fmt(res['dp_amount'] + res['total_insurance'])} so'm</b>"
            f"{AUTHOR_FOOTER}"
        )
        keyboard = [
            [InlineKeyboardButton("📲 Bank mutaxassisi bilan bog'lanish", url=AUTHOR_TG_URL)],
            [InlineKeyboardButton("🔄 Grafik turini o'zgartirish", callback_data=f"kred_sch:{m_key}:{inc_type}:{dp}:{months}")],
            [InlineKeyboardButton("🧮 Boshqa foiz / muddatda hisoblash", callback_data=f"kred_dp:{m_key}:{inc_type}")],
            [InlineKeyboardButton("📋 Shartlar va talablar", callback_data=f"terms_kred:{m_key}")],
            [InlineKeyboardButton("🚐 Modelga qaytish", callback_data=f"model:{m_key}")],
        ]
        await render_screen(update, text, keyboard)
        return

    # =================================================================
    # RASSROCHKA (UzAuto Motors II — 0%) KALKULYATORI BOSQICHLARI
    # =================================================================
    # 1-qadam: Daromad turini tanlash
    if parts[0] == "ras_inc":
        m_key = parts[1]
        m = MODELS[m_key]
        text = (
            f"🚐 <b>{m['name']}</b>\n"
            f"💵 Rassrochka narxi: <b>{fmt(m['rasrochka_price'])} so'm</b>\n\n"
            f"📌 <b>1-qadam: Daromad turini tanlang:</b>\n"
            f"<i>(Rasmiy daromadli mijozlar uchun 25% dan, o'zini o'zi band qilganlar uchun 30% dan boshlanadi)</i>"
        )
        keyboard = [
            [InlineKeyboardButton("💼 Rasmiy daromadga ega shaxs (25% dan)", callback_data=f"ras_dp:{m_key}:official")],
            [InlineKeyboardButton("🛠 O'zini o'zi band qilgan shaxs (30% dan)", callback_data=f"ras_dp:{m_key}:self")],
            [InlineKeyboardButton("📋 Shartlar va talablar (Rassrochka)", callback_data=f"terms_ras:{m_key}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"model:{m_key}")],
        ]
        await render_screen(update, text, keyboard, photo_path=m["photo"])
        return

    # 2-qadam: Boshlang'ich to'lovni tanlash
    if parts[0] == "ras_dp":
        _, m_key, inc_type = parts
        m = MODELS[m_key]
        inc_label = "Rasmiy daromadga ega" if inc_type == "official" else "O'zini o'zi band qilgan shaxs"
        text = (
            f"🚐 <b>{m['name']} (Rassrochka)</b>\n"
            f"💵 Narxi: <b>{fmt(m['rasrochka_price'])} so'm</b>\n"
            f"👤 Toifa: <b>{inc_label}</b>\n\n"
            f"📌 <b>2-qadam: Boshlang'ich to'lov foizini tanlang:</b>"
        )
        keyboard = []
        for dp, months_list in RASROCHKA_DAMAS[inc_type].items():
            max_m = max(months_list)
            dp_sum = fmt(m["rasrochka_price"] * dp / 100)
            keyboard.append([
                InlineKeyboardButton(
                    f"💰 {dp}% ({dp_sum} so'm) — {max_m} oygacha",
                    callback_data=f"ras_m:{m_key}:{inc_type}:{dp}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"ras_inc:{m_key}")])
        await render_screen(update, text, keyboard, photo_path=m["photo"])
        return

    # 3-qadam: Muddatni tanlash (12 oydan maksimal oygacha)
    if parts[0] == "ras_m":
        _, m_key, inc_type, dp_str = parts
        dp = int(dp_str)
        m = MODELS[m_key]
        dp_sum = fmt(m["rasrochka_price"] * dp / 100)
        text = (
            f"🚐 <b>{m['name']} (Rassrochka)</b>\n"
            f"💵 Narxi: <b>{fmt(m['rasrochka_price'])} so'm</b>\n"
            f"💰 Boshlang'ich to'lov ({dp}%): <b>{dp_sum} so'm</b>\n\n"
            f"📌 <b>3-qadam: Kredit muddatini tanlang:</b>\n"
            f"<i>(Barcha muddatlarda yillik foiz stavkasi — <b>0%</b>)</i>"
        )
        keyboard = []
        for months in RASROCHKA_DAMAS[inc_type][dp]:
            keyboard.append([
                InlineKeyboardButton(
                    f"🗓 {months} oy — Yillik 0% (Foizsiz)",
                    callback_data=f"ras_sch:{m_key}:{inc_type}:{dp}:{months}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"ras_dp:{m_key}:{inc_type}")])
        await render_screen(update, text, keyboard)
        return

    # 4-qadam: Grafik turini tanlash (Oddiy xalq tushunadigan tilda)
    if parts[0] == "ras_sch":
        _, m_key, inc_type, dp_str, m_str = parts
        dp, months = int(dp_str), int(m_str)
        m = MODELS[m_key]
        text = (
            f"🚐 <b>{m['name']} (Rassrochka)</b>\n"
            f"• Boshlang'ich to'lov: <b>{dp}% ({fmt(m['rasrochka_price'] * dp / 100)} so'm)</b>\n"
            f"• Muddati: <b>{months} oy</b>\n"
            f"• Yillik foiz stavkasi: <b>0% (Foizsiz!)</b>\n\n"
            f"📌 <b>4-qadam: To'lov grafigini tanlang va «Hisoblash» tugmasini bosing:</b>\n\n"
            f"💡 <b>Oddiy izoh:</b>\n"
            f"🔹 <b>Annuitet (Har oy bir xil to'lov)</b> — Har oy bir xil summadan to'lab borasiz.\n"
            f"🔹 <b>Differensial (Kamayib boruvchi grafik)</b> — Foizli kreditlarda har oy kamayib boradi, "
            f"ammo rassrochka <b>0% (foizsiz)</b> bo'lgani uchun ikkala grafikda ham bir xil oylik to'lov chiqadi."
        )
        keyboard = [
            [InlineKeyboardButton("🧮 Hisoblash: Har oy bir xil (Annuitet)", callback_data=f"ras_res:{m_key}:{inc_type}:{dp}:{months}:ann")],
            [InlineKeyboardButton("🧮 Hisoblash: Kamayib boruvchi (Differensial)", callback_data=f"ras_res:{m_key}:{inc_type}:{dp}:{months}:diff")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"ras_m:{m_key}:{inc_type}:{dp}")],
        ]
        await render_screen(update, text, keyboard)
        return

    # 5-qadam: Rassrochka Natijasi + Sug'urta + Mutaxassis bilan bog'lanish
    if parts[0] == "ras_res":
        _, m_key, inc_type, dp_str, m_str, sch = parts
        dp, months = int(dp_str), int(m_str)
        m = MODELS[m_key]
        res = calculate_all(m["rasrochka_price"], dp, months, 0.0, sch)

        inc_label = "Rasmiy daromadga ega" if inc_type == "official" else "O'zini o'zi band qilgan shaxs"
        sch_label = "Har oy bir xil (Annuitet)" if sch == "ann" else "Kamayib boruvchi (Differensial)"

        text = (
            f"✅ <b>RASSROCHKA (0%) — HISOB-KITOB NATIJASI</b>\n\n"
            f"🚐 Model: <b>{m['name']}</b>\n"
            f"👤 Toifa: <b>{inc_label}</b>\n"
            f"📊 Grafik: <b>{sch_label}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Avtomobil narxi: <b>{fmt(res['price'])} so'm</b>\n"
            f"💰 Boshlang'ich to'lov ({dp}%): <b>{fmt(res['dp_amount'])} so'm</b>\n"
            f"🏦 Bank chiqaradigan kredit: <b>{fmt(res['loan_amount'])} so'm</b>\n"
            f"🗓 Muddati: <b>{months} oy</b>\n"
            f"📈 Yillik foiz stavkasi: <b>0% (Foizsiz)</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💳 <b>Har oylik to'lov:</b>\n"
            f"👉 <b>{fmt(res['first_payment'])} so'm</b>\n\n"
            f"🛡 <b>SUG'URTA BADALI (Avtomat hisoblandi):</b>\n"
            f"• 1 yillik sug'urta: <b>{fmt(res['yearly_insurance'])} so'm</b>\n"
            f"• 1 oylik sug'urta: <b>{fmt(res['monthly_insurance'])} so'm</b>\n"
            f"• Jami <b>{months} oy</b> uchun sug'urta badali:\n"
            f"👉 <b>{fmt(res['total_insurance'])} so'm</b>\n"
            f"📌 <b>Boshlang'ich to'lov + Sug'urta:</b>\n"
            f"👉 <b>{fmt(res['dp_amount'] + res['total_insurance'])} so'm</b>"
            f"{AUTHOR_FOOTER}"
        )
        keyboard = [
            [InlineKeyboardButton("📲 Bank mutaxassisi bilan bog'lanish", url=AUTHOR_TG_URL)],
            [InlineKeyboardButton("🧮 Boshqa foiz / muddatda hisoblash", callback_data=f"ras_dp:{m_key}:{inc_type}")],
            [InlineKeyboardButton("📋 Shartlar va talablar (Rassrochka)", callback_data=f"terms_ras:{m_key}")],
            [InlineKeyboardButton("🚐 Modelga qaytish", callback_data=f"model:{m_key}")],
        ]
        await render_screen(update, text, keyboard)
        return


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Asakabank universal boti (Muallif: Matrasulov Shahzod) ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()