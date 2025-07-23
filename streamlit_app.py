
import streamlit as st
import sqlite3

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

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

@st.cache_resource
def init_database():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
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
    
    return conn

# Initialize database
conn = init_database()

st.title("🎯 SQL学習アプリ")
st.markdown("SQLの基本を学びましょう！")

# Progress bar
progress = (st.session_state.current_question) / len(questions)
st.progress(progress)

# Score display
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("現在の問題", f"{st.session_state.current_question + 1}/{len(questions)}")
with col2:
    st.metric("正解数", st.session_state.score)
with col3:
    st.metric("正解率", f"{(st.session_state.score / max(1, st.session_state.current_question + 1) * 100):.0f}%" if st.session_state.current_question > 0 else "0%")

# Check if quiz is completed
if st.session_state.current_question >= len(questions):
    st.success("🎉 お疲れさまでした！第1章の問題はすべて終了です。")
    st.balloons()
    
    if st.button("最初からやり直す"):
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.rerun()
else:
    # Current question
    q = questions[st.session_state.current_question]
    
    st.markdown(f"### 【第{q['number']}問】")
    st.markdown(q['description'])
    
    # SQL input
    user_sql = st.text_area("あなたのSQL:", height=100, key=f"sql_input_{st.session_state.current_question}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("実行", type="primary"):
            if user_sql.strip():
                try:
                    cur = conn.cursor()
                    cur.execute(user_sql)
                    user_result = cur.fetchall()
                    
                    # Get correct answer
                    cur.execute(q['answer'])
                    correct_result = cur.fetchall()
                    
                    if user_result == correct_result:
                        st.success("✅ 正解です！")
                        st.session_state.score += 1
                        
                        # Show results
                        if user_result:
                            st.markdown("**結果:**")
                            st.dataframe(user_result)
                        
                        # Auto advance after a short delay
                        if st.button("次の問題へ"):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        st.error("❌ 間違いです。")
                        st.markdown("**あなたの結果:**")
                        if user_result:
                            st.dataframe(user_result)
                        else:
                            st.write("結果なし")
                        
                        st.markdown("**正しい結果:**")
                        if correct_result:
                            st.dataframe(correct_result)
                        
                        st.info(f"💡 ヒント: {q['hint']}")
                        
                        if st.button("次の問題へ"):
                            st.session_state.current_question += 1
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {e}")
                    st.info(f"💡 ヒント: {q['hint']}")
            else:
                st.warning("SQLクエリを入力してください。")
    
    with col2:
        if st.button("ヒントを見る"):
            st.info(f"💡 {q['hint']}")
        
        if st.button("答えを見る"):
            st.code(q['answer'], language="sql")

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
