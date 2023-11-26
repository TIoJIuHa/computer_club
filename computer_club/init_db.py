import os
import psycopg2


conn = psycopg2.connect(
        host="localhost",
        database="computer_club_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS clients;")
cur.execute("CREATE TABLE clients (id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
                                  "name varchar (30) NOT NULL,"
                                  "surname varchar (50) NOT NULL,"
                                #   "category_id INT REFERENCES category (id),"
                                  "email varchar (30) UNIQUE,"
                                  "sex varchar (1) NOT NULL,"
                                  "CONSTRAINT valid_sex CHECK (sex = 'М' OR sex = 'Ж'));"
                                )


cur.execute("INSERT INTO clients (name, surname, email, sex)"
            "VALUES (%s, %s, %s, %s)",
            ('Rayan',
             'Гослингов',
             'gosling@gmail.com',
             'М')
            )


cur.execute('INSERT INTO clients (name, surname, email, sex)'
            'VALUES (%s, %s, %s, %s)',
            ('Барби',
             'Петрова',
             'sweet@yandex.ru',
             'Ж')
            )

conn.commit()

cur.close()
conn.close()
