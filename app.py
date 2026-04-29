import os
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from flask import Flask, jsonify, request, g, render_template

# ── App setup ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# ── PostgreSQL connection config ─────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "dbname":   os.getenv("DB_NAME",     "retail_chain"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "patthar"),
    "port":     os.getenv("DB_PORT",     "5433"),
}

# ── Database helpers ─────────────────────────────────────────────────
def connect_db(dbname=None):
    cfg = DB_CONFIG.copy()
    if dbname is not None:
        cfg["dbname"] = dbname
    try:
        return psycopg2.connect(**cfg)
    except psycopg2.OperationalError as exc:
        raise RuntimeError(
            f"PostgreSQL connection failed at {cfg['host']}:{cfg['port']} "
            f"for database {cfg['dbname']} with user {cfg['user']}: {exc}"
        ) from exc


def ensure_database_exists():
    if DB_CONFIG["dbname"] == "postgres":
        return

    conn = connect_db("postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (DB_CONFIG["dbname"],),
    )
    if cur.fetchone() is None:
        cur.execute(
            sql.SQL("CREATE DATABASE {}")
            .format(sql.Identifier(DB_CONFIG["dbname"]))
        )
        print(f"✔  Database {DB_CONFIG['dbname']} created")
    cur.close()
    conn.close()


def get_db():
    """Return a per-request PostgreSQL connection (stored on `g`)."""
    if "db" not in g:
        g.db = connect_db()
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_cursor(db):
    """Return a DictCursor so rows behave like dicts."""
    return db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    """Create tables & seed data from schema.sql (only if DB is empty)."""
    ensure_database_exists()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'stores'
        )
    """)
    exists = cur.fetchone()[0]
    if not exists:
        schema_path = os.path.join(BASE_DIR, "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit()
        print("✔  Database initialised from schema.sql")
    else:
        print("✔  Database already exists — skipping init")
    cur.close()
    conn.close()


# ── Frontend route ───────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── API: Stores ──────────────────────────────────────────────────────
@app.route("/api/stores", methods=["GET"])
def api_stores():
    cur = get_cursor(get_db())
    cur.execute(
        "SELECT storeid, location, contactnumber, managername FROM stores ORDER BY location"
    )
    rows = cur.fetchall()
    cur.close()
    return jsonify([dict(r) for r in rows])


# ── API: Products ────────────────────────────────────────────────────
@app.route("/api/products", methods=["GET"])
def api_products():
    cur = get_cursor(get_db())
    cur.execute(
        "SELECT productid, name, category, unitprice FROM products ORDER BY name"
    )
    rows = cur.fetchall()
    cur.close()
    return jsonify([dict(r) for r in rows])


# ── API: Inventory (joined view) ────────────────────────────────────
@app.route("/api/inventory", methods=["GET"])
def api_inventory():
    cur = get_cursor(get_db())
    cur.execute("""
        SELECT
            i.inventoryid,
            s.storeid,
            s.location      AS storelocation,
            p.productid,
            p.name          AS productname,
            p.category,
            p.unitprice,
            i.stockquantity
        FROM inventory i
        JOIN stores   s ON i.storeid   = s.storeid
        JOIN products p ON i.productid = p.productid
        ORDER BY s.location, p.name
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify([dict(r) for r in rows])


# ── API: Sales history ──────────────────────────────────────────────
@app.route("/api/sales", methods=["GET"])
def api_sales_list():
    cur = get_cursor(get_db())
    cur.execute("""
        SELECT
            sl.saleid,
            s.location      AS storelocation,
            p.name          AS productname,
            sl.saledate,
            sl.quantitysold,
            sl.totalamount
        FROM sales sl
        JOIN stores   s ON sl.storeid   = s.storeid
        JOIN products p ON sl.productid = p.productid
        ORDER BY sl.saledate DESC
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/sales/<int:sale_id>", methods=["DELETE"])
def api_delete_sale(sale_id):
    db = get_db()
    cur = get_cursor(db)

    try:
        cur.execute(
            "SELECT storeid, productid, quantitysold FROM sales WHERE saleid = %s",
            (sale_id,),
        )
        sale = cur.fetchone()

        if sale is None:
            return jsonify({"success": False, "errors": ["Sale not found."]}), 404

        cur.execute(
            """UPDATE inventory
               SET stockquantity = stockquantity + %s
               WHERE storeid = %s AND productid = %s""",
            (sale["quantitysold"], sale["storeid"], sale["productid"]),
        )

        if cur.rowcount == 0:
            raise RuntimeError("Unable to restore stock: inventory record not found.")

        cur.execute(
            "DELETE FROM sales WHERE saleid = %s",
            (sale_id,),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "errors": [str(exc)]}), 500
    finally:
        cur.close()

    return jsonify({"success": True, "message": "Sale deleted and inventory restored."})


# ── API: Record a sale (POST) ───────────────────────────────────────
@app.route("/api/sales", methods=["POST"])
def api_record_sale():
    data = request.get_json(force=True)

    store_id   = data.get("store_id")
    product_id = data.get("product_id")
    quantity   = data.get("quantity")

    # --- Basic validation ---
    errors = []
    if not store_id:
        errors.append("store_id is required.")
    if not product_id:
        errors.append("product_id is required.")
    if not quantity or int(quantity) <= 0:
        errors.append("quantity must be a positive integer.")
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    quantity = int(quantity)
    db  = get_db()
    cur = get_cursor(db)

    try:
        # --- Check inventory ---
        cur.execute(
            """SELECT inventoryid, stockquantity
               FROM inventory
               WHERE storeid = %s AND productid = %s""",
            (store_id, product_id),
        )
        inv = cur.fetchone()

        if inv is None:
            return jsonify({
                "success": False,
                "errors": ["This product is not stocked at the selected store."],
            }), 404

        if inv["stockquantity"] < quantity:
            return jsonify({
                "success": False,
                "errors": [
                    f"Insufficient stock. Available: {inv['stockquantity']}, Requested: {quantity}"
                ],
            }), 400

        # --- Fetch unit price ---
        cur.execute(
            "SELECT unitprice FROM products WHERE productid = %s", (product_id,)
        )
        product      = cur.fetchone()
        total_amount = round(product["unitprice"] * quantity, 2)

        # --- Transaction: insert sale + decrement stock ---
        cur.execute(
            """INSERT INTO sales (storeid, productid, quantitysold, totalamount)
               VALUES (%s, %s, %s, %s)""",
            (store_id, product_id, quantity, total_amount),
        )
        cur.execute(
            """UPDATE inventory
               SET stockquantity = stockquantity - %s
               WHERE inventoryid = %s""",
            (quantity, inv["inventoryid"]),
        )
        db.commit()

    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "errors": [str(exc)]}), 500
    finally:
        cur.close()

    return jsonify({
        "success":      True,
        "message":      f"Sale recorded! ₹{total_amount:,.2f} for {quantity} unit(s).",
        "total_amount": total_amount,
    }), 201


# ── API: Dashboard stats ────────────────────────────────────────────
@app.route("/api/stats", methods=["GET"])
def api_stats():
    db  = get_db()
    cur = get_cursor(db)

    cur.execute("SELECT COUNT(*) AS cnt FROM stores")
    total_stores = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM products")
    total_products = cur.fetchone()["cnt"]

    cur.execute("SELECT COALESCE(SUM(totalamount), 0) AS rev FROM sales")
    total_revenue = cur.fetchone()["rev"]

    cur.execute("SELECT COUNT(*) AS cnt FROM inventory WHERE stockquantity < 20")
    low_stock = cur.fetchone()["cnt"]

    cur.close()
    return jsonify({
        "total_stores":    total_stores,
        "total_products":  total_products,
        "total_revenue":   round(float(total_revenue), 2),
        "low_stock_alerts": low_stock,
    })


# ── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("🚀  Server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)