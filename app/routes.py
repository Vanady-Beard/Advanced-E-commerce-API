from flask import Blueprint, request, jsonify
from .models import db, Customer, CustomerAccount, Product, Order
from .services import create_customer, get_customer, update_customer, delete_customer
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/login', methods=['POST'])
def login():
    data = request.json
    account = CustomerAccount.query.filter_by(username=data['username']).first()
    if account and account.check_password(data['password']):
        token = create_access_token(identity=account.id)
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@main.before_app_request
def create_default_admin():
    if not CustomerAccount.query.filter_by(username='admin').first():
        admin_user = CustomerAccount(username='admin', password=generate_password_hash('password'))
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created")

@main.route('/customers', methods=['POST'])
@jwt_required()
def create_customer_route():
    data = request.json
    return create_customer(data)

@main.route('/customers/<int:id>', methods=['GET'])
@jwt_required()
def get_customer_route(id):
    return get_customer(id)

@main.route('/customers/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer_route(id):
    data = request.json
    return update_customer(id, data)

@main.route('/customers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer_route(id):
    return delete_customer(id)

@main.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    data = request.json
    new_product = Product(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created'}), 201

@main.route('/products/<int:id>', methods=['GET'])
@jwt_required()
def get_product(id):
    product = Product.query.get(id)
    if product:
        return jsonify({'name': product.name, 'price': product.price})
    return jsonify({'message': 'Product not found'}), 404

@main.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    data = request.json
    product = Product.query.get(id)
    if product:
        product.name = data['name']
        product.price = data['price']
        db.session.commit()
        return jsonify({'message': 'Product updated'})
    return jsonify({'message': 'Product not found'}), 404

@main.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'})
    return jsonify({'message': 'Product not found'}), 404

@main.route('/orders', methods=['POST'])
@jwt_required()
def place_order():
    data = request.json
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    
    # Convert the order_date string to a datetime object
    try:
        order_date = datetime.fromisoformat(data['order_date'])
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    new_order = Order(order_date=order_date, customer_id=customer.id)
    db.session.add(new_order)
    db.session.commit()

    for product_id in data['product_ids']:
        product = Product.query.get(product_id)
        if product:
            new_order.products.append(product)
    
    db.session.commit()
    return jsonify({'message': 'Order placed'}), 201

@main.route('/orders/<int:id>', methods=['GET'])
@jwt_required()
def get_order(id):
    order = Order.query.get(id)
    if order:
        return jsonify({
            'order_date': order.order_date,
            'customer': order.customer.name,
            'products': [{'name': p.name, 'price': p.price} for p in order.products]
        })
    return jsonify({'message': 'Order not found'}), 404

