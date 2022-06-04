from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

# создаем объект flask и задаем конфигурацию БД
app = Flask(__name__)
app.secret_key = 'es1kgH75'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userans.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

from ans import models, routes

db.create_all()

app.run(host = "127.0.0.1", port = 2021, debug = True)
