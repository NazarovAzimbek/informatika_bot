# 🤖 "Informatika yordamchi" Telegram Boti

Maktab o‘quvchilariga Informatika fanini o‘rganishda yordam beradigan sodda, tezkor, qulay va professional Telegram bot.

---

## 🌟 Asosiy imkoniyatlar

1. 🔢 **Sanoq sistemalari konvertori:**
   - 2-lik, 8-lik, 10-lik va 16-lik sanoq sistemalari o'rtasida to'liq 12 ta konvertatsiya yo'nalishi;
   - Qadamma-qadam yechim formulalari bilan ko'rsatiladi ($1\times 2^5 + 0\times 2^4 + \dots$);
   - O'nlikdan bo'lish bosqichlari va qoldiqlari aniq ifodalanadi;
   - Noto'g'ri kiritilgan raqamlar aniqlanib, qaysi belgi xato ekanligi tushuntiriladi;
   - Foydalanuvchi to'g'ridan-to'g'ri son yuborganida (`101101` yoki `255`) avtomatik aniqlanadi.

2. 💾 **Axborot o‘lchov birliklari konvertori:**
   - `bit`, `Byte`, `KB`, `MB`, `GB`, `TB`, `PB` birliklari;
   - Standart 1024 karrali kompyuter arxitekturasi ($1 \text{ Byte} = 8 \text{ bit}$);
   - Ko'paytirish va bo'lish qoidalari formulasi;
   - Berilgan qiymatni bir vaqtda barcha 7 ta birlikda jadval ko'rinishida ko'rsatish;
   - Matndan avtomatik aniqlash (masalan `100 MB`, `5 GB`).

3. 🔤 **ASCII va Unicode bo'limi:**
   - Belgidan (`A`) ➔ ASCII (`65`), Hex (`41`), Binary (`01000001`);
   - Koddan (`65`) ➔ Belgi (`A`);
   - Standart 7-bitli ASCII (0–127) va ko'p tilli zamonaviy Unicode (UTF-8) haqida tushuntirish.

4. 📁 **Fayl kengaytmalari bazasi:**
   - 26 ta eng mashhur kengaytma (.docx, .xlsx, .pptx, .pdf, .png, .mp4, .zip, .py, .exe ...);
   - Hujjatlar, Rasmlar, Media, Arxivlar, Kodlar toifalari bo'yicha ko'rish;
   - To'liq fayl nomi yuborilsa ham (`rasm.png`, `darslik.pdf`) kengaytmani avtomatik ajratib olish.

5. 💻 **Kompyuter qurilmalari ma'lumotnomasi:**
   - 16 ta kompyuter qurilmasi (CPU, RAM, HDD, SSD, GPU, Motherboard, Monitor, Keyboard, Mouse, Printer, Scanner, Webcam, Microphone, Speaker, USB Flash, Router);
   - Nomi, vazifasi, turi va afzalliklari ko'rsatilgan kartochkalar;
   - Kategoriya va nom bo'yicha qidiruv.

6. 🧠 **Interaktiv mini test (Viktorina):**
   - 30 ta darslikka moslashtirilgan sifatli test savollari;
   - Tasodifiy (random) tartibda 5, 10 yoki 20 talik test to'plamlari;
   - Har bir javobdan so'ng to'g'ri/noto'g'ri ekanligi tushuntiriladi;
   - Test yakunida foiz, to'g'ri/noto'g'ri javoblar va baho beriladi.

7. 📚 **Informatika lug‘ati:**
   - 21 ta asosiy informatika va dasturlash terminlari;
   - Aniq ta'rif va hayotiy misollar;
   - Sahifalangan ro'yxat, qidiruv va tasodifiy "Kun termini".

8. 📊 **Statistika va SQLite bazasi:**
   - Har bir foydalanuvchining shaxsiy natijalari (`/stats`);
   - O'zlashtirish foizi va yechilgan testlar soni monitoringi.

---

## 📂 Loyiha strukturasi

```text
TG BOT/
│
├── bot.py                     # Botning asosiy kirish nuqtasi (Dispatcher, Polling)
├── config.py                  # Sozlamalar va .env dan token yuklash
├── database.py                # SQLite (aiosqlite) orqali statistika va foydalanuvchilar
├── keyboards.py               # Barcha inline tugmalar va navigatsiya
├── requirements.txt           # Kutubxonalar ro'yxati (aiogram, python-dotenv, aiosqlite)
├── .env                       # Shaxsiy BOT_TOKEN (git ga yuklanmaydi)
├── .env.example               # Namunaviy token konfiguratsiyasi
├── .gitignore                 # Xavfsizlik qoidalari
├── README.md                  # Ushbu qo'llanma
│
├── handlers/                  # Telegram xabarlari va tugmalari ishlovchilari
│   ├── __init__.py
│   ├── start.py               # /start, /help, /about, /menu, /stats
│   ├── number_systems.py      # Sanoq sistemalari handlerlari
│   ├── information_units.py   # Axborot birliklari handlerlari
│   ├── ascii_handler.py       # ASCII handlerlari
│   ├── file_extensions.py     # Fayl kengaytmalari handlerlari
│   ├── computer_devices.py    # Kompyuter qurilmalari handlerlari
│   ├── quiz.py                # Mini test viktorinasi
│   ├── dictionary.py          # Informatika lug'ati
│   └── common.py              # Matndan avto-aniqlash va xatoliklar filtri
│
├── services/                  # Sof mantiqiy va hisoblash funksiyalari
│   ├── __init__.py
│   ├── converter.py           # Sanoq sistemalari va birliklar formulalari
│   ├── ascii_service.py       # ASCII kodlash/dekodlash mantiqi
│   └── quiz_service.py        # Test savollarini random saralash
│
└── data/                      # JSON formatidagi ma'lumotlar bazasi
    ├── extensions.json        # 26 ta fayl kengaytmasi
    ├── devices.json           # 16 ta kompyuter qurilmasi
    ├── dictionary.json        # 21 ta informatika termini
    └── questions.json         # 30 ta test savollari
```

---

## 🚀 Windows tizimida noldan ishga tushirish yo'riqnomasi

### 1-qadam: Virtual muhitni faollashtirish
Loyihaning asosiy papkasida (`c:\Users\ASUS\Desktop\TG BOT`) buyruqlar satri (PowerShell yoki CMD)ni oching va virtual muhitni yoqing:
```powershell
.\venv\Scripts\activate
```

### 2-qadam: Tokenni `.env` fayliga kiritish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga o'tib, `/newbot` buyrug'i orqali yangi bot yarating.
2. BotFather bergan API tokenni nusxalang (masalan: `789123456:AAFl1aBcDeFgHiJkLmNoPqRsTuVwXyZ`).
3. Loyiha papkasidagi `.env` faylini ochib, quyidagicha yozing va saqlang:
```env
BOT_TOKEN=789123456:AAFl1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

### 3-qadam: Botni ishga tushirish
Quyidagi buyruqni bering:
```powershell
python bot.py
```
Konsolda quyidagi xabarni ko'rasiz:
```text
2026-09-28 22:25:00 - [INFO] - informatika_bot.database - SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.
2026-09-28 22:25:00 - [INFO] - informatika_bot - 🚀 Informatika yordamchi boti muvaffaqiyatli ishga tushmoqda...
```
Endi Telegramda botingizga kirib `/start` bosing!

---

## 🛠 Xatoliklarni tuzatish (Troubleshooting)

1. **`❌ DIQQAT: BOT_TOKEN topilmadi!`**
   - Sabab: `.env` faylida token ko'rsatilmagan yoki fayl nomi noto'g'ri.
   - Yechim: `.env` faylini ochib, `BOT_TOKEN=...` qatoriga tokenni joylang.

2. **`TelegramUnauthorizedError: Unauthorized`**
   - Sabab: Kiritilgan token xato yoki BotFather'dan o'chirilgan.
   - Yechim: BotFather'dan tokenni qayta tekshirib, `.env` fayliga to'g'ri nusxalang.

3. **`TelegramNetworkError / ConnectTimeoutError`**
   - Sabab: Internet ulanishi yo'q yoki Telegram serverlariga ulanishda to'siq mavjud.
   - Yechim: Internet aloqangizni tekshiring.

---

## 🌐 Botni 24/7 VPS Serverda (Linux / Ubuntu) ishga tushirish

Bot doimiy ishlab turishi uchun uni arzon Linux VPS serveriga (masalan: Ubuntu 22.04 / 24.04) joylashtirish mumkin.

### 1. Serverda paketlarni o'rnatish
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

### 2. Loyihani yuklash va venv yaratish
```bash
cd /opt
git clone <sizning_repo_linki> informatika_bot
cd informatika_bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. `.env` faylini sozlash
```bash
nano .env
```
Tokeningizni yozib, `Ctrl+O` va `Enter` (saqlash), `Ctrl+X` (chiqish) bosing.

### 4. Systemd xizmati (Doimiy 24/7 avtomatik ishlashi uchun)
Server qayta yoqilganda ham bot avtomatik ishlab turishi uchun tizim xizmati yaratamiz:
```bash
sudo nano /etc/systemd/system/informatika_bot.service
```

Quyidagi matnni joylashtiring:
```ini
[Unit]
Description=Informatika Yordamchi Telegram Boti
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/informatika_bot
ExecStart=/opt/informatika_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Xizmatni ishga tushiramiz:
```bash
sudo systemctl daemon-reload
sudo systemctl enable informatika_bot
sudo systemctl start informatika_bot
```

Botning holatini tekshirish:
```bash
sudo systemctl status informatika_bot
```
Endi kompyuteringiz o'chiq bo'lsa ham bot serverda uzluksiz ishlayveradi!
