from flask import Flask, render_template, request, url_for, jsonify, redirect, session, make_response
from data import db_session, game_api
from flask_restful import reqparse, abort, Api, Resource
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user import RegisterForm

from data.users import User
from forms.loginform import LoginForm

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            about=form.about.data,
            bestscore=0,
            money=0,
            skin="20000",
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('info.html', title='Главная')

@app.route('/info')
def info():
    return render_template('help.html', title='О игре')

@app.route('/best')
def Best():
    db_sess = db_session.create_session()
    bestuser = db_sess.query(User).all()
    n = []
    for i in bestuser:
        n.append([i.name, i.bestscore, i.money])
    res = sorted(n, reverse=True, key=lambda x: x[1])
    res1 = sorted(n, reverse=True, key=lambda x: x[2])
    print(res, res1)
    return render_template('best.html', bestscore=res, money=res1, title='Лучшие результаты')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.username.data).first()
        if user and (user.check_password(form.password.data) or user.hashed_password == form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/shop', methods=['GET', 'POST'])
def Shop():
    a = request.form.get("shopp")
    n = current_user.skin

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == current_user.name).first()

    if a != None:
        if a[-1] == "0":
            lst = []
            for i in n:
                if i == "2":
                    lst.append("1")
                else:
                    lst.append(i)
            lst[int(a[0])] = "2"
            user.skin = "".join(lst)
            db_sess.commit()
        elif a[-1] != "0":
            lst = list(n)
            if a == "1":
                if user.money >= 200 and lst[1] != "1":
                    user.money -= 200
                    lst[1] = "1"
            elif a == "2" and lst[2] != "1":
                if user.money >= 200:
                    user.money -= 200
                    lst[2] = "1"
            elif a == "3" and lst[3] != "1":
                if user.money >= 500:
                    user.money -= 500
                    lst[3] = "1"
            elif a == "4"  and lst[4] != "1":
                if user.money >= 1000:
                    user.money -= 1000
                    lst[4] = "1"
            print(lst)
            user.skin = "".join(lst)
            db_sess.commit()
    return render_template('shop.html', title='Магазин')

@app.route('/game', methods=['GET', 'POST'])
def game():
    return render_template('index.html', item=url_for('static', filename='Build/wqe.loader.js'), title='Ползун')


@app.route('/data1', methods=['POST'])
def process_json():
    data = request.get_json()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == str(data["name"])).first()

    if user:
        user.money = data["money"]
        user.bestscore = data["bestscore"]
        db_sess.commit()
    return jsonify({'message': 'JSON received'})


@app.route('/data')
def data():
    print(current_user.name, current_user.money, current_user.bestscore)
    print(int(current_user.skin.find("2")))
    data = {'name': current_user.name, 'money': current_user.money, 'bestscore': current_user.bestscore, 'skin': int(current_user.skin.find("2"))}
    return jsonify(data)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.register_blueprint(game_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
