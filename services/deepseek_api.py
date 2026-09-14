import json
from datetime import datetime
from openai import AsyncOpenAI
from config import config

client = AsyncOpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

async def parse_user_intent(user_text: str, pending_tasks: list = None) -> dict:
    current_year = datetime.now().year
    current_date = datetime.now().strftime("%Y-%m-%d")
    tasks_info = "\n".join([f"- ID: {t['page_id']} | Заголовок: {t['title']}" for t in (pending_tasks or [])])

    prompt = f"""
    Ты ИИ-ассистент. Сегодня: {current_date}. Имя пользователя: {config.USER_NAME}.
    Твой характер: {config.BOT_PERSONA}.
    Определи намерение: СОЗДАТЬ, ЗАКРЫТЬ, ПРИВЫЧКИ или НЕИЗВЕСТНО.

    Правила важности:
    Используй СТРОГО один из трех тегов: Low, Medium, CRITICAL.
    - Если пользователь пишет "пиздец", "очень важно", "критично", "срочно", "изгонят" -> CRITICAL.
    - Если пишет обычную задачу -> Medium.
    - Если "не важно", "когда-нибудь" -> Low.

    Действие 1: СОЗДАТЬ (задачу)
    JSON: {{"action": "create", "task": "суть", "date": "YYYY-MM-DD", "severity": "тег"}}

    Действие 2: ЗАКРЫТЬ (задачу)
    Список задач: {tasks_info if tasks_info else "Нет задач"}
    JSON: {{"action": "close", "page_id": "ID"}}

    Действие 3: СОЗДАТЬ_ОТЧЕТ (пользователь просит создать запись/отчет за сегодня)
    JSON: {{"action": "create_habit_page"}}

    Действие 4: ОТМЕТИТЬ_ПРИВЫЧКУ (выполнили рутину)
    # ТУТ ЮЗЕР ДОЛЖЕН ВПИСАТЬ СВОИ КОЛОНКИ ИЗ NOTION:
    Доступные колонки: "Habit 1", "Habit 2", "Habit 3".
    Найди подходящие колонки по смыслу.
    JSON: {{"action": "update_habit", "habits": ["Имя 1"]}}

    Действие 5: НЕИЗВЕСТНО (если бред или нет совпадений)
    JSON: {{"action": "unknown"}}

    Текст: "{user_text}"
    """
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

async def analyze_habits(rate: float, note: str) -> str:
    sys_prompt = f"""
    Твой характер: {config.BOT_PERSONA}. Пользователь: {config.USER_NAME}.
    Оцени результаты дня. Completion Rate: {rate * 100}%. Заметка: "{note}".

    1. 100% — похвали.
    2. 50-90% — дай наставление.
    3. Меньше 50%: Уважительная причина? -> прояви понимание. Нет причины? -> отчитай согласно твоему характеру.

    Используй <i> для действий, <b> для акцентов. Без **. Начинай сразу с прямой речи.
    """
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": sys_prompt}]
    )
    return response.choices[0].message.content

async def generate_morning_reminder(task: str, severity: str) -> str:
    prompt = f"""
    Твой характер: {config.BOT_PERSONA}. Напомни {config.USER_NAME} о задаче: "{task}". Важность: {severity}.
    В зависимости от важности и твоего характера, сгенерируй креативное напоминание.
    Используй <i> для действий, <b> для акцентов. Без **.
    """
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content
