import os
import re
from datetime import datetime

import psycopg2
import pytz
from flask import Flask, redirect, render_template, request

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='computer_club_db',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


timezone = pytz.timezone('Europe/Moscow')
year = 2023
month = 11

@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM client;')
    clients = cur.fetchall()
    cur.execute('SELECT * FROM snack;')
    snacks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', clients=clients, snacks=snacks)


@app.route('/client', methods=['GET'])
def clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM client ORDER BY id DESC;')
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('clients.html', clients=clients)


@app.route('/client/create', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        category_id = request.form['category_id']
        sex = ''

        if request.form['sex'] == 'male':
            sex = 'm'
        else:
            sex = 'f'

        errors = validate_user(name, surname, email)

        try:
            cur.execute(f"INSERT INTO client (name, surname, email, category_id, sex) VALUES ('{name}', '{surname}', '{email}', {int(category_id)}, '{sex}');")
        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('client_form.html', client=None, errors=errors)

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/client")
    return render_template('client_form.html', client=None)


def validate_email(email_string):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if not re.fullmatch(regex, email_string):
        return "Invalid email"
    return ""


def validate_user(name, surname, email):
    errors = []
    name_length = len(name.strip())
    surname_length = len(surname.strip())
    if not name_length or name_length > 30:
        errors.append('Field "Name" should have 0 < length < 30')
    if not surname_length or surname_length > 50:
        errors.append('Field "Surname" should have 0 < length < 50')
    msg = validate_email(email)
    if msg:
        errors.append(msg)
    return errors


@app.route('/client/<int:client_id>', methods=['GET', 'POST', 'DELETE'])
def get_client(client_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM client WHERE id={client_id};')
    client = cur.fetchone()
    male = False
    if client[5] == "М":
        male = True

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        category_id = request.form['category_id']
        sex = ''

        errors = validate_user(name, surname, email)

        if request.form['sex'] == 'male':
            sex = 'm'
        else:
            sex = 'f'

        try:
            cur.execute(f"UPDATE client SET name = '{name}', surname = '{surname}', email = '{email}', category_id = {int(category_id)}, sex = '{sex}' WHERE id={client_id};")
        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('client_form.html', client=client, male=male, errors=errors)

        conn.commit()
        return redirect("/client")

    cur.close()
    conn.close()
    return render_template('client_form.html', client=client, male=male)


@app.route('/client/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM client WHERE id = {client_id};")
    except Exception as e:
        err = [str(e)]
        return render_template('client_form.html', errors=err)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/client")


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM category ORDER BY id')
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('categories.html', categories=categories)


def validate_category(name, discount):
    errors = []
    if not name:
        errors.append("Category name cannot be empty.")
    if not name.isalpha():
        errors.append("Category name should only contain alphabetic characters.")
    if int(float(discount)) < 0:
        errors.append("Discount have to be positive or zero")
    return errors


@app.route('/category/create', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()
        name = request.form['name']
        discount = request.form['discount']
        money_required = request.form['money_required']

        err = validate_category(name, discount)

        try:
            cur.execute(f"INSERT INTO category (name, discount, money_required) VALUES ('{name}', '{discount}', '{money_required}');")
        except Exception as e:
            err.append(str(e))

        if err:
            return render_template('category_form.html', category=None, errors=err)

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/categories")
    return render_template('category_form.html', category=None)


@app.route('/category/<int:category_id>', methods=['GET', 'POST'])
def single_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM category WHERE id={category_id};')
    category = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        discount = request.form['discount']
        money_required = request.form['money_required']

        errors = validate_category(name, discount)

        try:
            cur.execute(f"UPDATE category SET name = '{name}', discount = '{int(float(discount))}', money_required = '{int(float(money_required))}' WHERE id={category_id};")
        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('category_form.html', category=category, errors=errors)

        conn.commit()
        return redirect("/categories")

    cur.close()
    conn.close()

    return render_template('category_form.html', category=category)


@app.route('/category/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM category WHERE id = {category_id};")
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/categories")

@app.route('/snacks', methods=['GET', 'POST'])
def snacks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM snack ORDER BY id')
    snacks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('snacks.html', snacks=snacks)


def validate_snack(name: str, calories: float):
    errors = []
    if not name:
        errors.append("Snack name cannot be empty.")
    if not name.isalpha():
        errors.append("Snack name should only contain alphabetic characters.")
    if int(calories) < 0:
        errors.append("Calories have to be positive or zero")
    return errors


@app.route('/snack/create', methods=['GET', 'POST'])
def create_snack():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()
        name = request.form['name']
        calories = request.form['calories']
        price = request.form['price']

        err = validate_snack(name, float(calories))

        try:
            cur.execute(f"INSERT INTO snack (name, calories, price) VALUES ('{name}', '{int(calories)}', '{int(float(price))}');")
        except Exception as e:
            err.append(str(e))

        if err:
            return render_template('snack_form.html', snack=None, errors=err)

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/snacks")
    return render_template('snack_form.html', snack=None)


@app.route('/snacks/<int:snack_id>', methods=['GET', 'POST'])
def single_snack(snack_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM snack WHERE id={snack_id};')
    snack = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        calories = request.form['calories']
        price = request.form['price']

        errors = validate_snack(name, float(calories))

        try:
            cur.execute(f"UPDATE snack SET name = '{name}', calories = '{int(float(calories))}', price = '{int(float(price))}' WHERE id={snack_id};")
        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('snack_form.html', snack=snack, errors=errors)

        conn.commit()
        return redirect("/snacks")

    cur.close()
    conn.close()

    return render_template('snack_form.html', snack=snack)


@app.route('/snacks/<int:snack_id>/delete', methods=['POST'])
def delete_snack(snack_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM snack WHERE id = {snack_id};")
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/snacks")


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM orders ORDER BY id')
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('orders.html', orders=orders)


@app.route('/orders/create', methods=['GET', 'POST'])
def create_order():
    err = []

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT MAX(id) from client')

    max_id = cur.fetchone()[0]

    if request.method == 'POST':
        cur.execute('SELECT MAX(id) from client')

        max_id = cur.fetchone()[0]

        client_id = request.form['client_id']
        session_start_day = request.form['session_start_day']
        session_start_hour = request.form['session_start_hour']
        session_end_day = request.form['session_end_day']
        session_end_hour = request.form['session_end_hour']
        computer = request.form['computer']

        try:
            cur.execute(f"INSERT INTO orders (client_id, session_start, session_end,"
                        f" computer) VALUES ('{int(client_id)}', '{timezone.localize(datetime(year, month, int(session_start_day), int(session_start_hour)))}', "
                        f"'{timezone.localize(datetime(year, month, int(session_end_day), int(session_end_hour)))}', '{int(computer)}');")
        except Exception as e:
            err.append(str(e))

        if err:
            return render_template('order_form.html', order=None, errors=err)

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/orders")
    return render_template('order_form.html', max_id=max_id, order=None)


@app.route('/orders/<int:order_id>', methods=['GET', 'POST'])
def single_order(order_id):
    errors = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM orders WHERE id={order_id};')
    order = cur.fetchone()

    if request.method == 'POST':
        client_id = request.form['client_id']
        session_start_day = request.form['session_start_day']
        session_start_hour = request.form['session_start_hour']
        session_end_day = request.form['session_end_day']
        session_end_hour = request.form['session_end_hour']
        computer = request.form['computer']

        try:
            cur.execute(f"UPDATE orders SET client_id = '{client_id}',"
                        f" session_start = '{timezone.localize(datetime(year, month, int(session_start_day), int(session_start_hour)))}',"
                        f" session_end = '{timezone.localize(datetime(year, month, int(session_end_day), int(session_end_hour)))}',"
                        f" computer = {int(computer)} WHERE id={order_id};")

        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('order_form.html', order=order, errors=errors)

        conn.commit()
        return redirect("/orders")

    cur.close()
    conn.close()

    return render_template('order_form.html', order=order)


@app.route('/orders/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM orders WHERE id = {order_id};")
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/orders")

app.run(debug=True)
