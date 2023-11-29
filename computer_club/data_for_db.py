from collections import defaultdict
from datetime import datetime
from random import randint

import pytz

# clients

client_names = [
    "Райан",
    "Абоба",
    "Ким пять с плюсом",
    "Гаечка",
    "Бубылда",
    "Ярик",
    "Полина",
    "Алиса",
    "Пятница",
    "Владимир",
    "Олег",
    "Колготочек",
    "Би",
    "X Æ A-12",
    "Никита",
    "Мегафон",
]

client_surnames= [
            "Абобов",
            "Барагозин",
            "Гослингова",
            "Самокат",
            "МТС",
            "Горин",
            "Милос",
            "Свитабобовна",
            "re",
            "Кудрин",
            "Бейтман",
            "Эссовна",
            "Ляпотун",
            "Путин",
            "Котик",
            "Смолик",
            "Агеева",
            "Елистратова"
            ]

sex = ["f", "m"]

# category
category_names = [
                "brilliant",
                "gold",
                "silver",
                "bronze",
                "ordinary"
                ]

discount = {
            "brilliant": 45,
            "gold": 30,
            "silver": 20,
            "bronze": 10,
            "ordinary": 0
            }

required_money = {
            "brilliant": 90000,
            "gold": 80000,
            "silver": 60000,
            "bronze": 10000,
            "ordinary": 0
            }


# order

COUNT_CLIENTS = 50
COUNT_COMPUTER = 5

year = 2023
month = 11
day = 1
timezone = pytz.timezone('Europe/Moscow')
sessions = [[None, None]] * (COUNT_CLIENTS * 2)
prev_session_end = 0

for i in range(COUNT_CLIENTS * 2):
    if_flag = 0
    duration = randint(1, 6)
    end_session = prev_session_end + duration

    if end_session > 23:
        if_flag = 1
        day += 1
        end_session %= 24

    sessions[i] = [timezone.localize(datetime(year, month, day - if_flag, prev_session_end)),
                   timezone.localize(datetime(year, month, day, end_session))]
    prev_session_end = end_session

computer_duration = [0] * (COUNT_COMPUTER + 1)

# хранит конец сессии для каждого клиента
clients_session = [timezone.localize(datetime(year, month, 1, 0))] * (COUNT_CLIENTS + 1)


def get_time_session(client_id, computer_id, computer_duration):
    if clients_session[client_id] > sessions[computer_duration[computer_id]][0]:
        return None, None
    previous_session_id = computer_duration[computer_id]
    clients_session[client_id] = sessions[previous_session_id][1]
    computer_duration[computer_id] += 1
    return sessions[previous_session_id][0], sessions[previous_session_id][1]


# d = {}
# for order_id in range(COUNT_CLIENTS*2):
#     computer = randint(1, 5)
#     client_id = randint(1, COUNT_CLIENTS)
#     start, end = get_time_session(client_id, computer, computer_duration)
#     if start:
#         d.setdefault(computer, [])
#         d[computer].append((client_id, start, end))
#     else:
#         print("collidion")


#
# for k in d:
#     print(k, ": ", len(d[k]))
#     for session in d[k]:
#         print("Client: ", session[0], "Start: ", session[1], end=' ')
#         print("End: ", session[2])
#     print()
#     print()


# snack order

def get_amount_snack(end):
    return randint(1, end)


# snack

snack_names = [
    "сникерс",
    "чебупели",
    "крабовый салат",
    "корейская морковка",
    "милкшейк",
    "баблти",
    "кортошка"
    ]

snack_calories = {
    "сникерс": 100,
    "чебупели": 450,
    "крабовый салат": 3400,
    "корейская морковка": 560,
    "милкшейк": 550,
    "баблти": 450,
    "кортошка": 1200
    }


snack_price = {
    "сникерс": 990,
    "чебупели": 2490,
    "крабовый салат": 10000,
    "корейская морковка": 79,
    "милкшейк": 299,
    "баблти": 10900,
    "кортошка": 3990
    }


# cost for full orders
# common_bil = 0
# amount = randint(1, 10)
# for i in range(amount):
#     snack = snack_names[randint(0, len(snack_names) - 1)]
#     common_bil += snack_price[snack]
# common_bil += randint(1, 6) * 300
# print(common_bil)
