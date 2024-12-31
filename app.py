from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

with app.app_context():
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        first_name = db.Column(db.String(80))
        last_name = db.Column(db.String(80))
        age = db.Column(db.Integer)
        email = db.Column(db.String(80))
        role = db.Column(db.String(80))
        phone = db.Column(db.String(80))
        offer = relationship("Offer")

    class Order(db.Model):
        __tablename__ = 'orders'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80))
        description = db.Column(db.String(80))
        start_date = db.Column(db.Date)
        end_date = db.Column(db.Date)
        address = db.Column(db.String(80))
        price = db.Column(db.Integer)

        customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    class Offer(db.Model):
        __tablename__ = 'offers'
        id = db.Column(db.Integer, primary_key=True)

        order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
        executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    db.drop_all()
    db.create_all()

    with open('Data/users.json', 'r', encoding='utf8') as f:  # Загрузка в БД пользователей из файла JSON
        data = f.read()  # Прочитал файл, получил строку
        users_list = eval(data)  # Превратил строку в список
        for user in users_list:
            data = json.dumps(user, ensure_ascii=False)  # Подогнал под требования JSON, получил строку
            one_user = json.loads(data)  # Превратил в словарь Python
            add_user = User(**one_user)
            db.session.add(add_user)
            db.session.commit()

    with open('Data/orders.json', 'r', encoding='utf8') as f:  # Загрузка в БД заказов из файла JSON
        data = f.read()
        orders_list = eval(data)
        for order in orders_list:
            data = json.dumps(order, ensure_ascii=False)
            one_order = json.loads(data)
            order["start_date"] = datetime.strptime(order["start_date"], "%m/%d/%Y")
            order["end_date"] = datetime.strptime(order["end_date"], "%m/%d/%Y")
            add_order = Order(**order)
            db.session.add(add_order)
            db.session.commit()

    with open('Data/offers.json', 'r', encoding='utf8') as f:  # Загрузка в БД предложений из файла JSON
        data = f.read()
        offers_list = eval(data)
        for offer in offers_list:
            data = json.dumps(offer, ensure_ascii=False)
            one_offer = json.loads(data)
            add_offer = Offer(**one_offer)
            db.session.add(add_offer)
            db.session.commit()


def instance_to_dict(instance):
    return {"id" : instance.id,
            "first_name" : instance.first_name,
            "last_name" : instance.last_name,
            "age" : instance.age,
            "email" : instance.email,
            "phone" : instance.phone,
            }

@app.route('/users')  # Получение всех пользователей, а также одного пользователя по id (Шаг 5)
def get_users():
    users_list = User.query.all()
    user_response = []
    for user in users_list:
        user_response.append(instance_to_dict(user))
    return jsonify(user_response)

@app.route('/users/<int:user_id>')  # Получение одного пользователя по его id (Шаг 5)
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    return jsonify(instance_to_dict(user))

@app.route('/users', methods=['POST'])  # Создание нового пользователя (Шаг 6)
def add_user():
    datas = request.json()
    for data in datas:
        new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
    return 'Completed', 201

@app.route('/users/<int:user_id>', methods=['PUT'])  # Обновление пользователя (Шаг 6)
def update_user(user_id):
    user = User.query.get(user_id)
    data = request.json

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.age = data['age']
    user.email = data['email']
    user.phone = data['phone']
    user.offer = data['offer']

    db.session.add(user)
    db.session.commit()
    return 'Completed', 201

@app.route('/users/<int:user_id>', methods=['DELETE'])  # Удаление пользователя (Шаг 6)
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return 'Removed', 201

@app.route('/orders', methods=['GET', 'POST'])  # Создание заказа, получение всех заказов (Шаг 7)
def orders_page():
    if request.method == 'GET':
        return jsonify([{
            "name" : order.name,
            "description" : order.description,
            "start_date" : order.start_date,
            "end_date" : order.end_date,
            "address" : order.address,
            "price" : order.price
        } for order in db.session.query(Order).all()])
    elif request.method == 'POST':
        datas = request.json
        for data in datas:
            new_order = Order(**data)
            db.session.add(new_order)
            db.session.commit()
            return 'Completed', 201

@app.route('/orders/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])  # Получение, обновление, удаление конкретного заказа (Шаг 7)
def order_page_by_id(user_id):
    order = Order.query.get(user_id)
    if request.method == "GET":
        return jsonify({
            "name" : order.name,
            "description" : order.description,
            "start_date" : order.start_date,
            "end_date" : order.end_date,
            "address" : order.address,
            "price" : order.price
        })

    elif request.method == 'PUT':
        order = Order.query.get(user_id)
        data = request.json

        order.id = data['id']
        order.name = data['name']
        order.description = data['description']
        order.start_date = data['start_data']
        order.end_date = data['end_data']
        order.address = data['address']
        order.price = data['price']
        order.customer_id = data['customer_id']
        order.execution_id = data['execution_id']

        db.session.add(order)
        db.session.commit()
        return 'Completed', 201

    elif request.method == 'DELETE':
        order = Order.query.get(user_id)
        db.session.delete(order)
        db.session.commit()
        return 'Removed', 201

@app.route('/offers', methods=['GET', 'POST'])  # Создание предложения, получение всех предложений (Шаг 8)
def offers_page():
    if request.method == 'GET':
        return jsonify([{
            "order_id" : offer.order_id,
            "executor_id" : offer.executor_id
        } for offer in db.session.query(Offer).all()])

    elif request.method == 'POST':
        datas = request.json
        for data in datas:
            new_offer = Offer(**data)
            db.session.add(new_offer)
            db.session.commit()
            return 'Completed', 201

@app.route('/offers/<int:offer_id>', methods=["GET", "PUT", "DELETE"])  # Получение, обновление, удаление конкретного предложения (Шаг 8)
def offers_by_id(offer_id):
    offer = Offer.query.get(offer_id)

    if request.method == 'GET':
        return jsonify({
            "order_id" : offer.order_id,
            "executor_id" : offer.executor_id
        })

    elif request.method == 'PUT':
        offer = Offer.query.get(offer_id)
        data = request.json
        offer.order_id = data['order_id']
        offer.executor_id = data['executor_id']

        db.session.add(offer)
        db.session.commit()
        return 'Completed', 201

    elif request.method == 'DELETE':
        offer = Offer.query.get(offer_id)

        db.session.delete(offer)
        db.session.commit()
        return 'Removed', 201


if __name__ == '__main__':
    app.run(debug=False)
