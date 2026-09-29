import aiosqlite
import logging
from datetime import datetime
import config

logger = logging.getLogger("informatika_bot.database")


async def init_db():
    """Ma'lumotlar bazasi jadvallarini yaratish"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        # 1. Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Test natijalari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                total_questions INTEGER,
                correct_answers INTEGER,
                percentage INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        await db.commit()
    logger.info("SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")


async def add_or_update_user(user_id: int, full_name: str, username: str | None):
    """Foydalanuvchini bazaga qo'shish yoki ma'lumotlarini yangilash"""
    try:
        async with aiosqlite.connect(config.DB_PATH) as db:
            await db.execute("""
                INSERT INTO users (user_id, full_name, username)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name=excluded.full_name,
                    username=excluded.username
            """, (user_id, full_name, username or ""))
            await db.commit()
    except Exception as e:
        logger.error(f"Foydalanuvchini saqlashda xatolik: {e}")


async def save_quiz_result(user_id: int, total: int, correct: int, percentage: int):
    """Test natijasini bazaga yozish"""
    try:
        async with aiosqlite.connect(config.DB_PATH) as db:
            await db.execute("""
                INSERT INTO quiz_results (user_id, total_questions, correct_answers, percentage)
                VALUES (?, ?, ?, ?)
            """, (user_id, total, correct, percentage))
            await db.commit()
    except Exception as e:
        logger.error(f"Test natijasini saqlashda xatolik: {e}")


async def get_user_stats(user_id: int) -> dict:
    """Foydalanuvchining shaxsiy test statistikasini olish"""
    try:
        async with aiosqlite.connect(config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total_quizzes,
                    COALESCE(SUM(total_questions), 0) as sum_questions,
                    COALESCE(SUM(correct_answers), 0) as sum_correct,
                    COALESCE(AVG(percentage), 0) as avg_percent
                FROM quiz_results
                WHERE user_id = ?
            """, (user_id,))
            row = await cursor.fetchone()
            if row:
                return {
                    "quizzes_count": row["total_quizzes"],
                    "total_questions": row["sum_questions"],
                    "correct_answers": row["sum_correct"],
                    "avg_percentage": round(row["avg_percent"], 1)
                }
    except Exception as e:
        logger.error(f"Statistikani olishda xatolik: {e}")

    return {
        "quizzes_count": 0,
        "total_questions": 0,
        "correct_answers": 0,
        "avg_percentage": 0.0
    }


async def get_global_stats() -> dict:
    """Umumiy bot statistikasi"""
    try:
        async with aiosqlite.connect(config.DB_PATH) as db:
            c1 = await db.execute("SELECT COUNT(*) FROM users")
            u_count = (await c1.fetchone())[0]

            c2 = await db.execute("SELECT COUNT(*) FROM quiz_results")
            q_count = (await c2.fetchone())[0]

            return {
                "users_count": u_count,
                "quizzes_count": q_count
            }
    except Exception:
        return {"users_count": 0, "quizzes_count": 0}
