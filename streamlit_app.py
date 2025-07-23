import streamlit as st
import sqlite3

# --- セッション管理 ---
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

if "sql_input_key" not in st.session_state:
    st.session_state.sql_input_key = 0

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


# --- DB初期化 ---
@st.cache_resource
def init_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER
    )
    ''')
    cur.executemany("INSERT INTO users (name, age) VALUES (?, ?)",
                    [("Alice", 25), ("Bob", 30), ("Charlie", 22)])

    cur.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product TEXT,
        amount INTEGER
    )
    ''')
    cur.executemany(
        "INSERT INTO orders (user_id, product, amount) VALUES (?, ?, ?)",
        [(1, "Book", 2), (2, "Pen", 5), (1, "Notebook", 1)])

    return conn


conn = init_db()
cur = conn.cursor()

# --- UI ---
st.title("🎯 SQL学習アプリ")
# 進行状況メーター（上部）
progress = min((st.session_state.current_question + 1) / len(questions), 1.0)
st.progress(progress)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("現在の問題",
              f"{st.session_state.current_question + 1}/{len(questions)}")
with col2:
    st.metric("正解数", st.session_state.score)
with col3:
    if st.session_state.current_question > 0:
        accuracy = st.session_state.score / (
            st.session_state.current_question) * 100
    else:
        accuracy = 0
    st.metric("正解率", f"{accuracy:.0f}%")
    
def clear_text():
    st.session_state.sql_input = ""
    
if st.session_state.current_question >= len(questions):
    st.success("🎉 お疲れさまでした！すべての問題が終了しました。")
    st.write(f"正解数: {st.session_state.score}/{len(questions)}")
    st.balloons()
    if st.button("最初からやり直す"):
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.rerun()
    st.stop()

# --- 出題 ---
q = questions[st.session_state.current_question]

st.markdown(f"### 【第{q['number']}問】")
st.write(q["description"])

user_sql = st.text_area("あなたのSQLを入力してください", key=f"sql_input_{st.session_state.sql_input_key}")


if not st.session_state.answered:
    if st.button("実行", type="primary"):
        try:
            cur.execute(user_sql)
            user_result = cur.fetchall()

            cur.execute(q["answer"])
            correct_result = cur.fetchall()

            if user_result == correct_result:
                st.success("✅ 正解です！")
                st.session_state.score += 1
            else:
                st.error("❌ 間違いです。")
                st.markdown("**あなたの結果:**")
                st.dataframe(user_result)
                st.markdown("**正しい結果:**")
                st.dataframe(correct_result)

            st.session_state.answered = True

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.info(f"💡 ヒント: {q['hint']}")

if st.session_state.answered:
    if st.button("次の問題へ",key=f"next_button_{q['number']}"):
        st.session_state.current_question += 1
        st.session_state.answered = False
        st.session_state.sql_input_key += 1 
        st.rerun()

# --- ヒント・答えボタン ---
with st.expander("💡 ヒントを見る"):
    st.write(q["hint"])

with st.expander("✅ 正解を見る"):
    st.code(q["answer"], language="sql")

# Sidebar with database schema
with st.sidebar:
    st.markdown("### 📊 データベース構造")

    # Show tables
    if st.button("テーブル一覧を表示"):
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        for table in tables:
            st.write(f"• {table[0]}")

    # Show table structures
    st.markdown("#### users テーブル")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users);")
    users_info = cur.fetchall()
    for col in users_info:
        st.write(f"• {col[1]} ({col[2]})")

    st.markdown("#### orders テーブル")
    cur.execute("PRAGMA table_info(orders);")
    orders_info = cur.fetchall()
    for col in orders_info:
        st.write(f"• {col[1]} ({col[2]})")

    # Sample data preview
    if st.button("サンプルデータを表示"):
        st.markdown("**users:**")
        cur.execute("SELECT * FROM users LIMIT 3;")
        st.dataframe(cur.fetchall())

        st.markdown("**orders:**")
        cur.execute("SELECT * FROM orders LIMIT 3;")
        st.dataframe(cur.fetchall())
