import httpx
from datetime import datetime
from config import config

# Базовые настройки для запросов к Notion
HEADERS = {
    "Authorization": f"Bearer {config.NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
BASE_URL = "https://api.notion.com/v1"

async def notion_request(method, endpoint, json_data=None):
    async with httpx.AsyncClient(headers=HEADERS) as client:
        url = f"{BASE_URL}/{endpoint}"
        if method == "POST":
            response = await client.post(url, json=json_data)
        elif method == "PATCH":
            response = await client.patch(url, json=json_data)

        # Если ошибка, выведем детальный ответ от Notion
        if response.status_code != 200:
            print(f"NOTION ERROR: {response.json()}")

        response.raise_for_status()
        return response.json()

# === HABITS ===
async def get_today_habit():
    today = datetime.now().strftime("%Y-%m-%d")
    data = await notion_request("POST", f"databases/{config.NOTION_HABITS_DB_ID}/query", {
        "filter": {"property": "Date", "date": {"equals": today}}
    })

    if not data.get("results"): return None
    page = data["results"][0]
    props = page["properties"]

    rate = props.get("Completion Rate", {}).get("formula", {}).get("number", 0.0)
    note_arr = props.get("Operator Note", {}).get("rich_text", [])
    note = note_arr[0]["plain_text"] if note_arr else ""
    return {"page_id": page["id"], "rate": rate, "note": note}

async def update_habit_verdict(page_id, verdict):
    await notion_request("PATCH", f"pages/{page_id}", {
        "properties": {"AI Verdict": {"rich_text": [{"text": {"content": verdict}}]}}
    })

# === TASKS (Функции 2, 3, 4) ===
# В функции create_task:
async def create_task(task, date, severity):
    await notion_request("POST", "pages", {
        "parent": {"database_id": config.NOTION_MEMORY_DB_ID},
        "properties": {
            "Task": {"title": [{"text": {"content": task}}]},
            "Execution Date": {"date": {"start": date}},
            "Status": {"status": {"name": "Pending"}},
            "Severity": {"select": {"name": severity}}
        }
    })

async def get_all_pending_tasks():
    data = await notion_request("POST", f"databases/{config.NOTION_MEMORY_DB_ID}/query", {
        "filter": {"property": "Status", "status": {"equals": "Pending"}}
    })
    tasks = []
    for page in data.get("results", []):
        title_arr = page["properties"].get("Task", {}).get("title", [])
        title = title_arr[0]["plain_text"] if title_arr else "Без названия"
        tasks.append({"page_id": page["id"], "title": title})
    return tasks

async def get_today_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    data = await notion_request("POST", f"databases/{config.NOTION_MEMORY_DB_ID}/query", {
        "filter": {
            "and": [
                {"property": "Execution Date", "date": {"equals": today}},
                {"property": "Status", "status": {"equals": "Pending"}}
            ]
        }
    })

    tasks = []
    for page in data.get("results", []):
        props = page["properties"]
        title_arr = props.get("Task", {}).get("title", [])
        title = title_arr[0]["text"]["content"] if title_arr else "Без названия"
        sev = props.get("Severity", {}).get("select", {}).get("name", "Medium")
        tasks.append({"page_id": page["id"], "title": title, "severity": sev})
    return tasks

async def update_task_status(page_id, status):
    await notion_request("PATCH", f"pages/{page_id}", {
        "properties": {"Status": {"status": {"name": status}}}
    })

async def update_task_log(page_id, log_text):
    await notion_request("PATCH", f"pages/{page_id}", {
        "properties": {"AI Log": {"rich_text": [{"text": {"content": log_text}}]}}
    })

async def create_today_habit_page():
    """Создает пустую запись на сегодня. Возвращает (page_id, is_new)"""
    today = datetime.now().strftime("%Y-%m-%d")

    existing = await get_today_habit()
    if existing:
        return existing["page_id"], False # False = не новая, уже была

    payload = {
        "parent": {"database_id": config.NOTION_HABITS_DB_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": "Created by AI"}}]},
            "Date": {"date": {"start": today}}
        }
    }
    res = await notion_request("POST", "pages", payload)
    return res["id"], True # True = только что создали

async def update_habit_checkboxes(page_id: str, habit_names: list):
    """Ставит галочки сразу в нескольких колонках"""
    properties = {name: {"checkbox": True} for name in habit_names}
    payload = {"properties": properties}
    await notion_request("PATCH", f"pages/{page_id}", payload)
