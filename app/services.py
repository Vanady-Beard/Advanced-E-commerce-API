from flask import jsonify
from .models import db, Customer

def create_customer(data):
    new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer created'}), 201

def get_customer(id):
    customer = Customer.query.get(id)
    if customer:
        return jsonify({'name': customer.name, 'email': customer.email, 'phone': customer.phone})
    return jsonify({'message': 'Customer not found'}), 404

def update_customer(id, data):
    customer = Customer.query.get(id)
    if customer:
        customer.name = data['name']
        customer.email = data['email']
        customer.phone = data['phone']
        db.session.commit()
        return jsonify({'message': 'Customer updated'})
    return jsonify({'message': 'Customer not found'}), 404

def delete_customer(id):
    customer = Customer.query.get(id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted'})
    return jsonify({'message': 'Customer not found'}), 404
