from flask_login import UserMixin
from ans import db, manager


# таблица Personal -  содержит описание персонала
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    login = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)
    surname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    patronymic = db.Column(db.String(50))
    birth = db.Column(db.Date)
    object = db.Column(db.String(50))
    position = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    phone_mobile = db.Column(db.String(50))
    email = db.Column(db.String(50))
    address = db.Column(db.String(300))

# таблица Object -  содержит описание объекта
class Objects(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    object = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))

# таблица Item -  содержит описание записи
class Items(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    control = db.Column(db.Boolean, default = True)
    dtstart = db.Column(db.DateTime)
    dtend = db.Column(db.DateTime)
    object = db.Column(db.String(50))
    theme = db.Column(db.String(30))
    text = db.Column(db.String(1000))
    author = db.Column(db.String(50))
    author_correct = db.Column(db.String(50))
    dt_correct = db.Column(db.DateTime)

# таблица User -  содержит описание пользователей для логирования
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key = True, autoincrement = True)
#     login = db.Column(db.String(50), unique = True, nullable = False)
#     password = db.Column(db.String(50), nullable = False)


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
