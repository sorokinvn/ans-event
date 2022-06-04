import datetime
import ntplib
from datetime import date

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from ans import app, db
from ans.models import Users, Items, Objects


# обработчик главной страницы (переход на авторизацию пользователя)
@app.route("/", methods=["POST", "GET"])
@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('items_page'))
    log_user = str(request.form.get('login'))
    password_user = str(request.form.get('password'))

    if request.method == "POST":
        if log_user and password_user:
            user_man = Users.query.filter_by(login=log_user).first()
            if user_man and check_password_hash(user_man.password, password_user):
                login_user(user_man)
                return redirect(url_for('items_page'))
            else:
                flash('Логин или Пароль не верны!')
                return render_template("login.html")
        else:
            flash('Ошибка Авторизации')
            return render_template("login.html")
    else:
        return render_template("login.html")


# обработчик окна регистрации нового пользователя
@app.route("/register", methods=["POST", "GET"])
def register():
    login_user = request.form.get('login')
    password_user = request.form.get('password')
    surname = request.form.get('surname')
    name = request.form.get('name')
    patronymic = request.form.get('patronymic')
    birth = request.form.get('birth')
    object = request.form.get('object')
    position = request.form.get('position')
    phone_mobile = request.form.get('phone_mobile')
    phone = request.form.get('phone')
    email = request.form.get('email')
    objects = Objects.query.order_by(Objects.object).all()
    dn = date.today()

    if request.method == "GET":
        return render_template("register.html", dn=dn, objects=objects)

    if request.method == "POST":
        hash_pwd = generate_password_hash(password_user)
        birth = datetime.datetime.strptime(birth, "%Y-%m-%d").date()
        new_user = Users(login=login_user, password=hash_pwd, surname=surname, name=name, patronymic=patronymic, birth=birth,
                         object=object, position=position, phone=phone, phone_mobile = phone_mobile, email = email)
        if len(str(login_user)) > 5 and len(str(password_user)) > 5:
            if not Users.query.filter_by(login=login_user).first():
                try:
                    db.session.add(new_user)
                    db.session.commit()
                except:
                    return "ВНИМАНИЕ ПРОИЗОШЛА ОШИБКА В БД"
            else:
                flash(f'Логин {login_user} уже есть в базе!')
                return render_template("register.html", dn=dn, objects=objects)
        else:
            flash(f'Логин и Пароль должны быть длиннее пяти символов!')
            return render_template("register.html", dn=dn, objects=objects)
        return redirect(url_for('login'))

# обработчик главной страницы
@app.route("/items_page", methods=["POST", "GET"])
@login_required
def items_page():
    if request.method == "POST":
        pass
    else:
        user_man = Users.query.filter_by(login=current_user.login).first()
        personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic

        item = Items.query.order_by(Items.dtstart.desc()).all()
        return render_template("items_page.html", user = current_user.login, personal = personal, data = item)

# обработчик страницы создания записи
@app.route("/items_create_page", methods=["POST", "GET"])
@login_required
def items_create_page():
    user_man = Users.query.filter_by(login=current_user.login).first()
    if request.method == "POST":
        if request.form.get('inlineCheckbox1'):
            control = True
        else:
            control = False
        dstart = request.form['dstart']
        tstart = request.form['tstart']
        dend = request.form['dend']
        tend = request.form['tend']
        object = request.form['object']
        theme = request.form['theme']
        text = request.form['textarea1']
        author = request.form['author']

        dtstart = datetime.datetime.strptime(dstart + ' ' + tstart, "%Y-%m-%d %H:%M:%S")
        dtend = datetime.datetime.strptime(dend + ' ' + tend, "%Y-%m-%d %H:%M:%S")

        item = Items(control=control, dtstart=dtstart, dtend=dtend, object=object, theme=theme, text=text, author=author)

        try:
            db.session.add(item)
            db.session.commit()
        except:
            return "ВНИМАНИЕ ПРОИЗОШЛА ОШИБКА В БД"
        return redirect(f"/object_one_page/{user_man.object}")
        # return redirect("/items_page")
    else:
        # получаем всемирное время с сервера синхронизации
        conn = ntplib.NTPClient()
        response = conn.request('ru.pool.ntp.org', version=3)
        now = datetime.datetime.fromtimestamp(response.tx_time, datetime.timezone.utc)

        # получаем системное время сервера UTC
        # now = datetime.datetime.utcnow()

        dn = now.date()
        tn = now.time().strftime("%H:%M:%S")
        # получаем системное время сервера локальное (местное)
        # dn = date.today()
        # tn = datetime.datetime.now().time().strftime("%H:%M:%S")

        # user_man = Users.query.filter_by(login=current_user.login).first()
        return render_template("items_create_page.html", user = current_user.login, dn = dn, tn = tn, personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic, object = user_man.object)

# обработчик страницы конкретного объекта
@app.route("/object_one_page/<object>", methods = ["POST", "GET"])
@login_required
def object_one_page(object):
    if request.method == "GET":
        user_man = Users.query.filter_by(login=current_user.login).first()
        personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic
        item = Items.query.order_by(Items.dtstart.desc()).filter_by(object=object).all()
        return render_template("object_one_page.html", user = current_user.login, personal = personal, data = item, object = object, object_user_man = user_man.object)
    else:
        pass


# обработчик удаления записи
@app.route("/del_item/<int:id>", methods = ["POST", "GET"])
@login_required
def del_item(id):
    user_man = Users.query.filter_by(login=current_user.login).first()
    personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic
    item = Items.query.get_or_404(id)
    # if item.object != user_man.object:
    if item.author != personal:
        flash(f'Нельзя удалять чужие записи!')
        return redirect(f"/items_correct/{id}")
    else:
        try:
            db.session.delete(item)
            db.session.commit()
            return redirect(f"/object_one_page/{user_man.object}")
        except:
            return "ВНИМАНИЕ ПРОИЗОШЛА ОШИБКА В БД"


# обработчик страницы корректировки записи
@app.route("/items_correct/<int:id>", methods = ["POST", "GET"])
@login_required
def items_correct(id):
    ch = ''
    item = Items.query.get(id)
    user_man = Users.query.filter_by(login=current_user.login).first()
    if request.method == "GET":
        if item.control == True:
            ch = 'checked'
        # user_man = Users.query.filter_by(login=current_user.login).first()
        return render_template("items_correct.html", item = item, personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic, user = current_user.login, ch = ch)

    if request.method == "POST":
        if request.form.get('inlineCheckbox1'):
            item.control = True
        else:
            item.control = False

        now = datetime.datetime.utcnow()
        dn = now.date().strftime("%Y-%m-%d")
        tn = now.time().strftime("%H:%M:%S")

        user_man = Users.query.filter_by(login=current_user.login).first()
        dstart = request.form['dstart']
        tstart = request.form['tstart']
        dend = request.form['dend']
        tend = request.form['tend']

        item.dtstart = datetime.datetime.strptime(dstart + ' ' + tstart, "%Y-%m-%d %H:%M:%S")
        item.dtend = datetime.datetime.strptime(dend + ' ' + tend, "%Y-%m-%d %H:%M:%S")

        item.dt_correct = datetime.datetime.strptime(dn + ' ' + tn, "%Y-%m-%d %H:%M:%S")

        item.object = request.form['object']
        item.theme = request.form['theme']
        item.text = request.form['textarea1']
        item.author = request.form['author']
        item.author_correct = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic

        try:
            db.session.commit()
        except:
            return "ВНИМАНИЕ ПРОИЗОШЛА ОШИБКА В БД"
        return redirect(f"/object_one_page/{user_man.object}")
        # return redirect("/items_page")
    # else:
    #     return render_template("items_correct.html")

# обработчик страницы объекты
@app.route("/objects_page", methods=["POST", "GET"])
@login_required
def objects_page():
    if request.method == "POST":
        pass
    else:
        user_man = Users.query.filter_by(login=current_user.login).first()
        personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic

        object = Objects.query.order_by(Objects.object).all()
        return render_template("objects_page.html", user = current_user.login, personal = personal, data = object)

# обработчик страницы персонал
@app.route("/users_page", methods=["POST", "GET"])
@login_required
def users_page():
    if request.method == "POST":
        pass
    else:
        user_man = Users.query.filter_by(login=current_user.login).first()
        personal = user_man.surname + ' ' + user_man.name + ' ' + user_man.patronymic

        user = Users.query.order_by(Users.surname).all()
        return render_template("users_page.html", user = current_user.login, personal = personal, data = user)

# обработчик разлогирования пользователя
@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
