# Как развернуть проект локально

Склонировать к себе репозиторий:
```
git clone git@github.com:TIoJIuHa/computer_club.git
```
Установить и активировать виртуальное окружение:
```
cd computer_club
python -m venv venv
source venv/bin/activate
(source venv/Scripts/activate - на Windows)
```
Установить необходимые зависимости:
```
pip install -r requirements.txt
```
Перейти в рабочую папку и установить переменные окружения:
```
cd computer_club
export FLASK_APP=app
export FLASK_ENV=development (для режима разработки)
```
Инициализировать базу данных
```
python init_db.py
```
Заполнить базу данных 
```
python fill_database.py
```
Поменять параметры можно в одноименном файле
Теперь можно запускать проект:
```
flask run
```
*Примечание:*
*Перед работой у вас должна быть создана база данных, и в файле `.env` в корне репозитория необходимо прописать имя пользователя и пароль для подключения к базе.*
*Пример файла `.env`:*
```
DB_USERNAME=psql_user
DB_PASSWORD=psql1234
```
