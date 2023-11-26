import os
import re
import psycopg2
from flask import Flask, redirect, render_template, request

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='computer_club_db',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients;')
    clients = cur.fetchall()
    cur.execute('SELECT * FROM snacks;')
    snacks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', clients=clients, snacks=snacks)


@app.route('/clients', methods=['GET'])
def clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients ORDER BY id DESC;')
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('clients.html', clients=clients)


@app.route('/clients/create', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        sex = ''

        if request.form['sex'] == 'male':
            sex = 'М'
        else:
            sex = 'Ж'

        errors = validate_user(name, surname, email)

        try:
            cur.execute(f"INSERT INTO clients (name, surname, email, sex) VALUES ('{name}', '{surname}', '{email}', '{sex}');")
        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('client_form.html', client=None, errors=errors)

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/clients")
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


@app.route('/clients/<int:client_id>', methods=['GET', 'POST', 'DELETE'])
def get_client(client_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM clients WHERE id={client_id};')
    client = cur.fetchone()
    male = False
    if client[4] == "М":
        male = True

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        sex = ''

        errors = validate_user(name, surname, email)

        if request.form['sex'] == 'male':
            sex = 'М'
        else:
            sex = 'Ж'

        try:
            cur.execute(f"UPDATE clients SET name = '{name}', surname = '{surname}', email = '{email}', sex = '{sex}' WHERE id={client_id};")
        except Exception as e:
            errors.append(str(e))

        if errors:
            return render_template('client_form.html', client=client, male=male, errors=errors)

        conn.commit()
        return redirect("/clients")

    cur.close()
    conn.close()
    return render_template('client_form.html', client=client, male=male)


@app.route('/clients/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM clients WHERE id = {client_id};")
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/clients")

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    pass


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    pass


@app.route('/snacks', methods=['GET', 'POST'])
def snacks():
    pass
