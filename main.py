import sqlite3

# --- 問題データ ---
questions = [
    {
        "chapter": 1,
        "number": 1,
        "description": "このデータベースに存在するテーブル名をすべて表示してください。",
        "answer": "SELECT name FROM sqlite_master WHERE type='table';",
        "hint": "sqlite_master はSQLiteが持つメタ情報テーブルです。",
    },
    {
        "chapter": 1,
        "number": 2,
        "description": "users テーブルのすべての列とデータを表示してください。",
        "answer": "SELECT * FROM users;",
        "hint": "* を使うとすべての列を表示できます。",
    },
    {
        "chapter": 1,
        "number": 3,
        "description": "orders テーブルのすべての列とデータを表示してください。",
        "answer": "SELECT * FROM orders;",
        "hint": "orders テーブルにデータが入っているか確認しましょう。",
    },
    {
        "chapter": 1,
        "number": 4,
        "description": "users テーブルのカラム構造（列名と型）を表示してください。",
        "answer": "PRAGMA table_info(users);",
        "hint": "SQLiteでは PRAGMA table_info() を使います。",
    },
    {
        "chapter": 1,
        "number": 5,
        "description": "orders テーブルのカラム構造を確認してください。",
        "answer": "PRAGMA table_info(orders);",
        "hint": "PRAGMA table_info(テーブル名) で確認できます。",
    },
    {
        "chapter": 1,
        "number": 6,
        "description": "users テーブルにある name カラムだけをすべて表示してください。",
        "answer": "SELECT name FROM users;",
        "hint": "SELECT カラム名 FROM テーブル名 の形式です。",
    },
    {
        "chapter": 1,
        "number": 7,
        "description": "users テーブルの行数（データ数）を調べてください。",
        "answer": "SELECT COUNT(*) FROM users;",
        "hint": "COUNT(*) はすべての行を数えます。",
    },
    {
        "chapter": 1,
        "number": 8,
        "description": "orders テーブルのテーブル名を確認してください（sqlite_masterを使う）。",
        "answer": "SELECT name FROM sqlite_master WHERE name = 'orders';",
        "hint": "sqlite_master はテーブル一覧を持っています。",
    },
    {
        "chapter": 1,
        "number": 9,
        "description": "users テーブルの id, name を表示してください。",
        "answer": "SELECT id, name FROM users;",
        "hint": "カンマ区切りで複数カラムを指定できます。",
    },
    {
        "chapter": 1,
        "number": 10,
        "description": "orders テーブルの user_id カラムだけを表示してください。",
        "answer": "SELECT user_id FROM orders;",
        "hint": "orders に user_id というカラムがあるか確認しましょう。",
    },
]

# --- DBセットアップ ---
conn = sqlite3.connect(":memory:")
cur = conn.cursor()

# usersテーブル
cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
)
''')
cur.executemany('INSERT INTO users (name, age) VALUES (?, ?)', [
    ('Alice', 25),
    ('Bob', 30),
    ('Charlie', 22),
])

# ordersテーブル
cur.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product TEXT,
    amount INTEGER
)
''')
cur.executemany('INSERT INTO orders (user_id, product, amount) VALUES (?, ?, ?)', [
    (1, 'Book', 2),
    (2, 'Pen', 5),
    (1, 'Notebook', 1),
])

# --- 出題ループ ---
for q in questions:
    print(f"\n【第{q['number']}問】 {q['description']}")
    user_sql = input("あなたのSQL > ")

    try:
        cur.execute(user_sql)
        user_result = cur.fetchall()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print(f"💡 ヒント: {q['hint']}")
        continue

    try:
        cur.execute(q['answer'])
        correct_result = cur.fetchall()
    except:
        print("❌ 正解データの取得に失敗しました。")
        continue

    if user_result == correct_result:
        print("✅ 正解です！")
    else:
        print("❌ 間違いです。")
        print("あなたの結果:", user_result)
        print("正しい結果 :", correct_result)
        print(f"💡 ヒント: {q['hint']}")

conn.close()
print("\n🎉 お疲れさまでした！第1章の問題はすべて終了です。")
