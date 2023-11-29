from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from data_for_db import *

engine = create_engine("postgresql+psycopg2://postgres:123go@localhost:5432/computer_club_db")

metadata = MetaData()
metadata.reflect(bind=engine)

table_names = metadata.tables

Session = sessionmaker(engine)
with Session() as session:

    # snacks
    for snack in snack_names:
        data_to_insert = {"name": snack, "calories": snack_calories[snack], "price": snack_price[snack]}
        session.execute(table_names['snack'].insert().values(data_to_insert))

    # category
    for category in category_names:
        data_to_insert = {"name": category, "discount": discount[category], "money_required": required_money[category]}
        session.execute(table_names['category'].insert().values(data_to_insert))

    # client
    for client_id in range(COUNT_CLIENTS):

        name = client_names[randint(0, len(client_names) - 1)]
        surname = client_surnames[randint(0, len(client_surnames) - 1)]
        category_id = randint(1, len(category_names))
        sex_for_db = sex[randint(0, 1)]
        email = f'{name}_{surname}@gmail.com'
        data_to_insert = {"name": name,
                          "surname": surname,
                          "email": email,
                          "category_id": category_id,
                          "sex": sex_for_db}
        session.execute(table_names['client'].insert().values(data_to_insert))

    # order
    computer_duration = [0] * (COUNT_COMPUTER + 1)
    count_orders = 0

    for order_id in range(COUNT_CLIENTS * 3):

        client_id = randint(1, COUNT_CLIENTS)
        computer = randint(1, 5)
        session_start, session_end = get_time_session(client_id, computer, computer_duration)
        if session_start:

            data_to_insert = {
                "client_id": client_id,
                "session_start": session_start,
                "session_end": session_end,
                "computer": computer
            }

            session.execute(table_names['orders'].insert().values(data_to_insert))

    # snack_order
    for snack_order_id in range(COUNT_CLIENTS * 3):
        order_id = randint(1, COUNT_CLIENTS)
        snack_id = randint(1, len(snack_names))
        amount = get_amount_snack(10)

        data_to_insert = {
            "order_id": order_id,
            "snack_id": snack_id,
            "amount": amount
            }

        session.execute(table_names['snack_orders'].insert().values(data_to_insert))
    session.commit()
