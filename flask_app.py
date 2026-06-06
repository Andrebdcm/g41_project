import sqlite3
import bcrypt
import io
import base64
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB_PATH = Path(__file__).parent / "data" / "publishers_magazines.db"

app = Flask(__name__)
app.secret_key = "g41_project_secret_key_2024"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para aceder a esta página."


# ── DB helpers ──
def get_conn():
    return sqlite3.connect(str(DB_PATH))


def query_db(query, args=(), one=False):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def query_df(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


# ── Auth helpers ──
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def init_users_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_users_table()


# ── Flask-Login user class ──
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1])
    return None


# ── Matplotlib helper ──
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return img


# ── Routes ──

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if row and verify_password(password, row[1]):
            user = User(row[0], username)
            login_user(user)
            flash("Login efetuado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        flash("Username ou password incorretos.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        if not username or not password:
            flash("Preencha todos os campos.", "warning")
        elif password != password2:
            flash("As passwords não coincidem.", "warning")
        else:
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hash_password(password))
                )
                conn.commit()
                conn.close()
                flash("Conta criada! Pode fazer login.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username já existe.", "danger")
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout efetuado.", "info")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    df_pub = query_df("SELECT * FROM publishers")
    df_mag = query_df("SELECT * FROM magazines")
    df_wh = query_df("SELECT * FROM warehouses")
    df_tx = query_df("SELECT * FROM transactions")

    # Gráfico resumo por categoria
    df_tx_mag = df_tx.merge(df_mag, on="magazine_id", how="left")
    sales = df_tx_mag.groupby("magazine_category")["amount"].sum().reset_index().sort_values("amount", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(sales["magazine_category"], sales["amount"], color="skyblue")
    ax.set_title("Total de Vendas por Categoria")
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Total de Vendas")
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    chart_cat = fig_to_base64(fig)

    return render_template(
        "dashboard.html",
        publishers=len(df_pub),
        magazines=len(df_mag),
        warehouses=len(df_wh),
        transactions=len(df_tx),
        latest=df_tx.sort_values("transaction_date", ascending=False).head(10).to_dict("records"),
        chart_cat=chart_cat,
    )


@app.route("/publishers")
def publishers():
    f_name = request.args.get("f_name", "").strip()
    query = "SELECT * FROM publishers WHERE 1=1"
    params = []
    if f_name:
        query += " AND publisher_name LIKE ?"
        params.append(f"%{f_name}%")
    query += " ORDER BY publisher_id"
    df = query_df(query, params)
    return render_template("publishers.html", rows=df.to_dict("records"), f_name=f_name)


@app.route("/magazines", methods=["GET", "POST"])
@login_required
def magazines():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            title = request.form.get("title", "").strip()
            category = request.form.get("category", "").strip()
            new_id_df = query_df("SELECT COALESCE(MAX(magazine_id), 0) + 1 AS next_id FROM magazines")
            new_id = int(new_id_df.iloc[0]["next_id"])
            query_db(
                "INSERT INTO magazines (magazine_id, magazine_title, magazine_category) VALUES (?, ?, ?)",
                (new_id, title, category),
            )
            flash(f"Magazine {new_id} criada!", "success")
        elif action == "delete":
            mid = int(request.form.get("magazine_id", 0))
            query_db("DELETE FROM magazines WHERE magazine_id = ?", (mid,))
            flash("Magazine excluída!", "warning")
        return redirect(url_for("magazines"))

    f_title = request.args.get("f_title", "").strip()
    f_cat = request.args.get("f_cat", "").strip()
    query = "SELECT * FROM magazines WHERE 1=1"
    params = []
    if f_title:
        query += " AND magazine_title LIKE ?"
        params.append(f"%{f_title}%")
    if f_cat:
        query += " AND magazine_category LIKE ?"
        params.append(f"%{f_cat}%")
    query += " ORDER BY magazine_id"
    df = query_df(query, params)
    existing_cats = sorted(query_df("SELECT DISTINCT magazine_category FROM magazines WHERE magazine_category IS NOT NULL")["magazine_category"].tolist())
    return render_template("magazines.html", rows=df.to_dict("records"), categories=existing_cats, f_title=f_title, f_cat=f_cat)


@app.route("/warehouses")
def warehouses():
    f_info = request.args.get("f_info", "").strip()
    query = "SELECT * FROM warehouses WHERE 1=1"
    params = []
    if f_info:
        query += " AND warehouses_info LIKE ?"
        params.append(f"%{f_info}%")
    query += " ORDER BY warehouses_id"
    df = query_df(query, params)
    return render_template("warehouses.html", rows=df.to_dict("records"), f_info=f_info)


@app.route("/transactions", methods=["GET", "POST"])
def transactions():
    if request.method == "POST":
        f_start = request.form.get("f_start", "").strip()
        f_end = request.form.get("f_end", "").strip()
        f_pub = request.form.get("f_pub", "").strip()

        query = """
            SELECT t.*, p.publisher_name
            FROM transactions t
            JOIN publishers p ON t.publisher_id = p.publisher_id
            WHERE 1=1
        """
        params = []
        if f_start:
            query += " AND t.transaction_date >= ?"
            params.append(f_start)
        if f_end:
            query += " AND t.transaction_date <= ?"
            params.append(f_end)
        if f_pub:
            query += " AND p.publisher_name LIKE ?"
            params.append(f"%{f_pub}%")

        df = query_df(query, params)
        return render_template("transactions.html", rows=df.to_dict("records"), filtered=True)

    df = query_df("SELECT * FROM transactions")
    return render_template("transactions.html", rows=df.to_dict("records"), filtered=False)


@app.route("/analysis")
def analysis():
    f_cat = request.args.get("f_cat", "").strip()
    f_pub = request.args.get("f_pub", "").strip()

    # base queries
    tx_query = "SELECT * FROM transactions WHERE 1=1"
    tx_params = []

    if f_pub:
        # filter transactions by publisher name via subquery/join
        tx_query = """
            SELECT t.* FROM transactions t
            JOIN publishers p ON t.publisher_id = p.publisher_id
            WHERE 1=1
        """
        tx_query += " AND p.publisher_name LIKE ?"
        tx_params.append(f"%{f_pub}%")

    df_tx = query_df(tx_query, tx_params)
    df_mag = query_df("SELECT * FROM magazines")
    df_pub = query_df("SELECT * FROM publishers")

    # 1. Vendas por categoria
    df_tx_mag = df_tx.merge(df_mag, on="magazine_id", how="left")
    if f_cat:
        df_tx_mag = df_tx_mag[df_tx_mag["magazine_category"].str.contains(f_cat, case=False, na=False)]
    sales_cat = df_tx_mag.groupby("magazine_category")["amount"].sum().reset_index().sort_values("amount", ascending=False)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    if not sales_cat.empty:
        ax1.bar(sales_cat["magazine_category"], sales_cat["amount"], color="steelblue")
    ax1.set_title("Total de Vendas por Categoria")
    ax1.set_xlabel("Categoria")
    ax1.set_ylabel("Total de Vendas")
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")
    fig1.tight_layout()
    chart1 = fig_to_base64(fig1)

    # 2. Top 5 editores
    df_tx_pub = df_tx.merge(df_pub, on="publisher_id", how="left")
    if f_pub:
        df_tx_pub = df_tx_pub[df_tx_pub["publisher_name"].str.contains(f_pub, case=False, na=False)]
    sales_pub = df_tx_pub.groupby("publisher_name")["amount"].sum().reset_index().sort_values("amount", ascending=False).head(5)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    if not sales_pub.empty:
        ax2.barh(sales_pub["publisher_name"], sales_pub["amount"], color="teal")
    ax2.set_title("Top 5 Editores por Volume de Vendas")
    ax2.set_xlabel("Total de Vendas")
    ax2.invert_yaxis()
    fig2.tight_layout()
    chart2 = fig_to_base64(fig2)

    # 3. Pie chart
    fig3, ax3 = plt.subplots(figsize=(8, 8))
    if not sales_cat.empty:
        ax3.pie(sales_cat["amount"], labels=sales_cat["magazine_category"], autopct="%1.1f%%", startangle=140)
    ax3.set_title("Distribuição das Vendas por Categoria")
    chart3 = fig_to_base64(fig3)

    cat_list = sorted(df_mag["magazine_category"].dropna().unique().tolist())

    return render_template(
        "analysis.html",
        sales_cat=sales_cat.to_dict("records"),
        sales_pub=sales_pub.to_dict("records"),
        chart1=chart1,
        chart2=chart2,
        chart3=chart3,
        f_cat=f_cat,
        f_pub=f_pub,
        cat_list=cat_list,
    )


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")
            if not username or not password:
                flash("Preencha todos os campos.", "warning")
            elif password != password2:
                flash("As passwords não coincidem.", "warning")
            else:
                try:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, hash_password(password)),
                    )
                    conn.commit()
                    conn.close()
                    flash(f"Utilizador '{username}' criado!", "success")
                except sqlite3.IntegrityError:
                    flash("Username já existe.", "danger")
        elif action == "update":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")
            if not username or not password:
                flash("Preencha todos os campos.", "warning")
            elif password != password2:
                flash("As passwords não coincidem.", "warning")
            else:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (hash_password(password), username),
                )
                updated = cur.rowcount
                conn.commit()
                conn.close()
                if updated > 0:
                    flash(f"Password de '{username}' atualizada!", "success")
                else:
                    flash("Utilizador não encontrado.", "danger")
        elif action == "delete":
            username = request.form.get("username", "").strip()
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE username = ?", (username,))
            deleted = cur.rowcount
            conn.commit()
            conn.close()
            if deleted > 0:
                flash(f"Utilizador '{username}' excluído!", "warning")
            else:
                flash("Utilizador não encontrado.", "danger")
        return redirect(url_for("users"))

    f_user = request.args.get("f_user", "").strip()
    query = "SELECT user_id, username, created_at FROM users WHERE 1=1"
    params = []
    if f_user:
        query += " AND username LIKE ?"
        params.append(f"%{f_user}%")
    query += " ORDER BY user_id"
    df = query_df(query, params)
    return render_template("users.html", rows=df.to_dict("records"), f_user=f_user)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
