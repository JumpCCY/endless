from unittest.mock import DEFAULT

from flask import Flask, render_template, request, jsonify, flash
import sqlite3
import secrets

app = Flask(__name__)

secret_key = secrets.token_hex(16)
app.secret_key = secret_key


@app.route('/')
def hello_world():
    return render_template('testmenu.html')


@app.route('/activities')
def activities():
    return render_template('activities.html')


@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    name_and_version = db.execute("SELECT * FROM items ORDER BY Item").fetchall()
    activities = db.execute("SELECT * FROM activities").fetchall()

    size_and_stocks = db.execute("SELECT * FROM size_and_stocks")
    if request.method == 'POST':
        item_name = request.form.get("item_name")
        size = request.form.get("size")
        version = request.form.get("version")
        customer = request.form.get("customer_name")
        address = request.form.get("address")
        phone = request.form.get("phone_no")

        if not item_name or not size or not version or not customer or not address or not phone:
            return render_template('stocks.html', message="Please fill out all the fields")

        if phone <= 0:
            return render_template('stocks.html', message="Please enter the valid number")

        db.execute("INSERT INTO activities(Item,Size,Version,CustomerName,Address,PhoneNumber) VALUES(?,?,?,?,?,?)")
    else:
        return render_template('stocks.html', stocks=size_and_stocks , items = name_and_version, activities = activities)


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
            check_version = db.execute("SELECT Version FROM items WHERE Item = ?", (check_name[0],)).fetchone()

            if not check_version:
                flash('Error, Version does not exist')
                return render_template('edit_items.html', item=items, size=size)

            if item_name == check_name[0] and version == check_version[0]:
                flash('Name already taken')
                return render_template('edit_items.html', item=items, size=size)



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

    items = db.execute("SELECT * FROM items").fetchall()
    size = db.execute("SELECT * FROM sizes").fetchall()

    con.close()
    return render_template('edit_items.html', item=items, size=size)

@app.route('/stock_check', methods=['GET'])
def stock_check():
    con = sqlite3.connect("endless.db")
    con.row_factory = sqlite3.Row
    db = con.cursor()

    id_request = request.args.get("item_id")

    rows = db.execute("SELECT item_id, size_id, Quantity FROM size_and_stocks WHERE item_id = ? ORDER BY size_id", (id_request,)).fetchall()
    data = [{"item_id": row[0] , "size_id": row[1] , "quantity": row[2]} for row in rows]
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



def update_stock(size_id, item_id, adjustAmount, is_addition = True):
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

    currentQuantity = db.execute("SELECT Quantity FROM size_and_stocks WHERE size_id = ? AND item_id = ?", (size_id, item_id)).fetchone()

    if is_addition:
        newQuantity = currentQuantity[0] + adjustAmount
    else:
        if currentQuantity[0] < adjustAmount:
            return jsonify({"error": "Not enough stock to remove"}), 400
        newQuantity = currentQuantity[0] - adjustAmount


    db.execute("UPDATE size_and_stocks SET Quantity = ? WHERE size_id = ? AND item_id = ?", (newQuantity,size_id,item_id))
    con.commit()

    Quantity = db.execute("SELECT Quantity FROM size_and_stocks WHERE size_id = ? AND item_id = ?", (size_id, item_id)).fetchone()
    con.close()
    return str(Quantity[0])


if __name__ == '__main__':
    app.run()


