from core.database import Database

db = Database("data/test.db")
print("数据库创建成功")

with db.get_connection() as conn:
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    print("表结构:", [t[0] for t in tables])