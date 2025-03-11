import secrets
import sqlite3

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

app = Flask(__name__)

secret_key = secrets.token_hex(16)
app.secret_key = secret_key


@app.route('/')
def hello_world():
    return render_template('testmenu.html')


@app.route('/activities')
def activities():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()
    activities = db.execute("SELECT * FROM activities ORDER BY Date").fetchall()

    return render_template('activities.html', activities=activities)


@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    name_and_version = db.execute("SELECT * FROM items ORDER BY Item").fetchall()
    activities = db.execute("SELECT * FROM activities").fetchall()
    size = db.execute("SELECT Size FROM sizes").fetchall()

    size_and_stocks = db.execute("SELECT * FROM size_and_stocks")
    if request.method == 'POST' and 'submit_txn' in request.form:
        item_name = request.form.get("item_name")
        size = request.form.get("size")
        version = request.form.get("version")
        customer = request.form.get("customer_name")
        address = request.form.get("address")
        phone = request.form.get("phone_no")
        phone = int(phone)

        if size == 'XS':
            sizeID = 1
        elif size == 'S':
            sizeID = 2
        elif size == 'M':
            sizeID = 3
        elif size == 'L':
            sizeID = 4
        elif size == 'XL':
            sizeID = 5
        elif size == 'XXL':
            sizeID = 6
        else:
            return render_template('stocks.html', message="invalid size")

        if not item_name or not size or not version or not customer or not address or not phone:
            return render_template('stocks.html', message="Please fill out all the fields")

        if phone <= 0:
            return render_template('stocks.html', message="Please enter the valid number")

        # check stock
        item_id = db.execute("SELECT ID FROM items WHERE Item = ? AND Version = ?", (item_name, version)).fetchall()
        item_id = item_id[0][0]
        if not item_id:
            return render_template('stocks.html', message="Item not found")

        quantity = db.execute(
            "SELECT Quantity from size_and_stocks JOIN sizes ON size_and_stocks.size_id = sizes.ID WHERE item_id = ? AND sizes.Size = ?",
            (item_id, size)).fetchall()
        quantity = quantity[0][0]

        if quantity < 1:
            flash("Out of stock")
            return redirect(url_for('stocks'))
        else:
            item_id = db.execute("SELECT ID FROM items WHERE Item = ? AND Version = ?", (item_name, version)).fetchall()
            quantity = quantity - 1
            db.execute("UPDATE size_and_stocks SET Quantity = ? WHERE item_id = ? AND size_id = ?",
                       (quantity, item_id[0][0], sizeID))
            db.execute(
                "INSERT INTO activities(Item,Size,Version,CustomerName,Address,PhoneNumber, Date, item_id) VALUES(?,?,?,?,?,?,DATETIME('now'),?)",
                (item_name, size, version, customer, address, phone, item_id[0][0]))
            con.commit()
            return redirect(url_for('stocks'))


    elif request.method == 'POST' and 'ship' in request.form:

        activity_id = request.form.get("txID")
        id = db.execute("SELECT * FROM activities WHERE ID = ?", (activity_id,)).fetchall()
        db.execute("UPDATE activities SET Status = 'ORDER_done' WHERE ID = ?", (activity_id,))

        db.execute(
            "INSERT INTO activities(Status, Item,Size,Version,CustomerName,Address,PhoneNumber,Date,item_id) VALUES(?,?,?,?,?,?,?,DATETIME('now'), ?)",
            ("SHIPPED", id[0][2], id[0][3], id[0][4], id[0][5], id[0][6], id[0][7], id[0][9]))

        con.commit()
        return redirect(url_for('stocks'))

    elif request.method == 'POST' and 'complete' in request.form:

        activity_id = request.form.get("txID")
        id = db.execute("SELECT * FROM activities WHERE ID = ?", (activity_id,)).fetchall()
        db.execute("UPDATE activities SET Status = 'SHIP_done' WHERE ID = ?", (activity_id,))
        db.execute(
            "INSERT INTO activities(Status, Item,Size,Version,CustomerName,Address,PhoneNumber, Date, item_id) VALUES(?,?,?,?,?,?,?,DATETIME('now'), ?)",
            ("COMPLETED", id[0][2], id[0][3], id[0][4], id[0][5], id[0][6], id[0][7], id[0][9]))

        con.commit()
        return redirect(url_for('stocks'))

    else:
        txn_query = db.execute("""
        SELECT * FROM activities
        WHERE Status <> ? 
    """, ("COMPLETED",)).fetchall()
        return render_template('stocks.html', stocks=size_and_stocks, items=name_and_version, activities=activities,
                               size=size, txn_query=txn_query)


@app.route('/edit_item', methods=['GET', 'POST'])
def edit_items():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    if request.method == 'POST' and request.form.get("action") == "add":
        item_name = request.form.get("item_name")
        version = request.form.get("version")
        price = request.form.get("price")

        items = db.execute("SELECT * FROM items").fetchall()
        size = db.execute("SELECT * FROM sizes").fetchall()

        # check of fake inputs
        if not item_name or not version or not price:
            flash('Please fill out all the fields')
            return render_template('edit_items.html', item=items, size=size)

        price = int(price)

        if price < 0:
            flash('Please enter the valid number')
            return render_template('edit_items.html', item=items, size=size)

        check_name = db.execute("SELECT Item FROM items WHERE Item = ?", (item_name,)).fetchone()
        if check_name:
            check_version = db.execute("SELECT Version FROM items WHERE Version = ?", (version,)).fetchone()

            if not check_version:
                check_version = 'no'

            if item_name == check_name[0] and version == check_version[0]:
                flash('Name already taken')
                return redirect(url_for('edit_items'))

        db.execute("INSERT INTO items(Item, Version, Price) VALUES(?,?,?)", (item_name, version, price,))
        item_id = db.lastrowid
        size_id = db.execute("SELECT sizes.ID FROM sizes").fetchall()

        for size in size_id:
            db.execute("INSERT INTO size_and_stocks(item_id, size_id, Quantity) VALUES(?,?,?)",
                       (item_id, size[0], 0,))

        con.commit()

    if request.method == 'POST' and request.form.get("action") == "remove":
        item_id = request.form.get("item_id")
        db.execute("DELETE FROM items WHERE ID = ?", item_id)
        db.execute("DELETE FROM size_and_stocks WHERE item_id = ?", item_id)
        con.commit()

    items = db.execute("SELECT * FROM items ORDER BY Version").fetchall()
    size = db.execute("SELECT * FROM sizes").fetchall()

    con.close()
    return render_template('edit_items.html', item=items, size=size)


@app.route('/stock_check', methods=['GET'])
def stock_check():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    id_request = request.args.get("item_id")

    rows = db.execute("SELECT item_id, size_id, Quantity FROM size_and_stocks WHERE item_id = ? ORDER BY size_id",
                      (id_request,)).fetchall()
    data = [{"item_id": row[0], "size_id": row[1], "quantity": row[2]} for row in rows]
    return jsonify(data)


@app.route('/add_specific_size_quantity', methods=['GET'])
def add_specific_size_quantity():
    size_id = request.args.get("size_id")
    item_id = request.args.get("item_id")
    adjustAmount = request.args.get("quantity")

    return update_stock(size_id, item_id, adjustAmount, True)


@app.route('/remove_specific_size_quantity', methods=['GET'])
def remove_specific_size_quantity():
    size_id = request.args.get("size_id")
    item_id = request.args.get("item_id")
    adjustAmount = request.args.get("quantity")

    return update_stock(size_id, item_id, adjustAmount, False)


def update_stock(size_id, item_id, adjustAmount, is_addition=True):
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    if adjustAmount is None:
        return jsonify({"error": "Missing quantity"}), 400  # HTTP 400 for bad request

    try:
        adjustAmount = int(adjustAmount)
    except ValueError:
        return jsonify({"error": "Invalid quantity format"}), 400

    if adjustAmount <= 0:
        return jsonify({"error": "Invalid quantity format"}), 400

    currentQuantity = db.execute("SELECT Quantity FROM size_and_stocks WHERE size_id = ? AND item_id = ?",
                                 (size_id, item_id)).fetchone()

    if is_addition:
        newQuantity = currentQuantity[0] + adjustAmount
    else:
        if currentQuantity[0] < adjustAmount:
            return jsonify({"error": "Not enough stock to remove"}), 400
        newQuantity = currentQuantity[0] - adjustAmount

    db.execute("UPDATE size_and_stocks SET Quantity = ? WHERE size_id = ? AND item_id = ?",
               (newQuantity, size_id, item_id))
    con.commit()

    Quantity = db.execute("SELECT Quantity FROM size_and_stocks WHERE size_id = ? AND item_id = ?",
                          (size_id, item_id)).fetchone()
    con.close()
    return str(Quantity[0])


@app.route('/change_price', methods=['GET'])
def change_price():
    item_id = request.args.get("item_id")
    price = request.args.get("price")
    version = request.args.get("version")

    if price is None or price == "":
        flash("Invalid Value")
        return jsonify({"error": "Missing price"}), 400
    if version is None or version == "":
        flash("Invalid Value")
        return jsonify({"error": "Missing version"}), 400
    if item_id is None or item_id == "":
        flash("Invalid Value")
        return jsonify({"error": "Missing item_id"}), 400

    try:
        price = int(price)
    except ValueError:
        flash("Invalid Value")
        return jsonify({"error": "Invalid price"}), 400

    if price < 0:
        flash("Invalid Value")
        return jsonify({"error": "Invalid price"}), 400

    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    db.execute("UPDATE items SET Price = ? WHERE Item = ? AND Version = ?", (price, item_id, version))
    con.commit()
    con.close()

    return jsonify(1)


@app.route("/search")
def search():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    query = request.args.get("q")
    search_term = f"%{query}%"

    # Modified query to handle both text and numeric searches
    items = db.execute("""
        SELECT Item, Version, Price 
        FROM items 
        WHERE Item LIKE ? COLLATE NOCASE 
        OR Item = ?
        OR CAST(Item AS TEXT) LIKE ? ORDER BY Version
    """, (search_term, query, search_term)).fetchall()

    items_list = [dict(item) for item in items]

    return jsonify(items_list)


if __name__ == '__main__':
    app.run()
