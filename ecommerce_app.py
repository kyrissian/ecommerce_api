"""
E-Commerce API
==============

A Flask application that manages Users, Products, and Orders for a simple
e-commerce system, using Flask-SQLAlchemy for the database and
Flask-Marshmallow for serializing data to/from JSON.
"""

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db_password = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{db_password}@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


order_product = db.Table(
    'order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class User(db.Model):
    """Represents a customer who can place orders.

    Columns:
        id (int): Primary key, auto-incremented.
        name (str): The user's full name.
        address (str): The user's mailing address.
        email (str): The user's email address (must be unique).
        orders (list[Order]): All orders placed by this user.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)

    orders = db.relationship('Order', back_populates='user')


class Product(db.Model):
    """Represents a product that can be purchased and included in orders.

    Columns:
        id (int): Primary key, auto-incremented.
        product_name (str): The name of the product.
        price (float): The price of the product.
        orders (list[Order]): All orders that include this product.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    orders = db.relationship('Order', secondary=order_product, back_populates='products')


class Order(db.Model):
    """Represents an order placed by a user.

    Columns:
        id (int): Primary key, auto-incremented.
        order_date (datetime): The date and time the order was placed.
        user_id (int): Foreign key referencing the User who placed the order.
        user (User): The User who placed this order.
        products (list[Product]): Products included in this order.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='orders')
    products = db.relationship('Product', secondary=order_product, back_populates='orders')


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing/deserializing User objects."""
    class Meta:
        """Configuration telling Marshmallow which model to build the schema from."""
        model = User


class ProductSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing/deserializing Product objects."""
    class Meta:
        """Configuration telling Marshmallow which model to build the schema from."""
        model = Product


class OrderSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing/deserializing Order objects.

    include_fk = True is required so that user_id (a foreign key) is
    recognized and included as a schema field automatically.
    """
    class Meta:
        """Configuration telling Marshmallow which model to build the schema from,
        with include_fk=True so foreign key fields are included."""
        model = Order
        include_fk = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


@app.route('/users', methods=['GET'])
def get_users():
    """Retrieve all users.

    Returns:
        Response: JSON array of all users with HTTP 200.
    """
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users)), 200


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user.

    Expects a JSON body with name, address, and email.

    Returns:
        Response: JSON object of the newly created user with HTTP 201.
    """
    data = request.json
    new_user = User(name=data['name'], address=data['address'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema.dump(new_user)), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieve a single user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        Response: JSON object of the user with HTTP 200, or an error
        message with HTTP 404 if the user does not exist.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user_schema.dump(user)), 200



@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user's details.

    Args:
        user_id (int): The ID of the user to update.

    Returns:
        Response: JSON object of the updated user with HTTP 200,
        or an error message with HTTP 404 if the user does not exist.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if 'name' in data:
        user.name = data['name']
    if 'address' in data:
        user.address = data['address']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify(user_schema.dump(user)), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by their ID.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        Response: Success message with HTTP 200, or an error message
        with HTTP 404 if the user does not exist.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {user_id} deleted successfully'}), 200



@app.route('/products', methods=['GET'])
def get_products():
    """Retrieve all products.

    Returns:
        Response: JSON array of all products with HTTP 200.
    """
    all_products = Product.query.all()
    return jsonify(products_schema.dump(all_products)), 200


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Retrieve a single product by its ID.

    Args:
        product_id (int): The ID of the product to retrieve.

    Returns:
        Response: JSON object of the product with HTTP 200, or an error
        message with HTTP 404 if the product does not exist.
    """
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product_schema.dump(product)), 200


@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product.

    Expects a JSON body with product_name and price.

    Returns:
        Response: JSON object of the newly created product with HTTP 201.
    """
    data = request.json
    new_product = Product(product_name=data['product_name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify(product_schema.dump(new_product)), 201


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product's details.

    Args:
        product_id (int): The ID of the product to update.

    Returns:
        Response: JSON object of the updated product with HTTP 200,
        or an error message with HTTP 404 if the product does not exist.
    """
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.json
    if 'product_name' in data:
        product.product_name = data['product_name']
    if 'price' in data:
        product.price = data['price']

    db.session.commit()
    return jsonify(product_schema.dump(product)), 200


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product by its ID.

    Args:
        product_id (int): The ID of the product to delete.

    Returns:
        Response: Success message with HTTP 200, or an error message
        with HTTP 404 if the product does not exist.
    """
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Product {product_id} deleted successfully'}), 200


@app.route('/orders', methods=['POST'])
def create_order():
    """Create a new order for a user.

    Expects a JSON body with user_id and order_date
    (ISO format, e.g. "2026-07-17T10:00:00").

    Returns:
        Response: JSON object of the newly created order with HTTP 201,
        or an error message with HTTP 404 if the user does not exist.
    """
    data = request.json

    user = db.session.get(User, data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_order = Order(user_id=data['user_id'], order_date=data['order_date'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify(order_schema.dump(new_order)), 201


@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    """Add a product to an existing order, preventing duplicate entries.

    Args:
        order_id (int): The ID of the order.
        product_id (int): The ID of the product to add.

    Returns:
        Response: JSON object of the updated order with HTTP 200,
        an error if the product is already in the order (HTTP 400),
        or HTTP 404 if the order or product does not exist.
    """
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product in order.products:
        return jsonify({'error': 'Product already exists in this order'}), 400

    order.products.append(product)
    db.session.commit()
    return jsonify(order_schema.dump(order)), 200



@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    """Remove a product from an existing order.

    Args:
        order_id (int): The ID of the order.
        product_id (int): The ID of the product to remove.

    Returns:
        Response: JSON object of the updated order with HTTP 200,
        or HTTP 404 if the order, product, or association is not found.
    """
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product not in order.products:
        return jsonify({'error': 'Product is not in this order'}), 404

    order.products.remove(product)
    db.session.commit()
    return jsonify(order_schema.dump(order)), 200


@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_for_user(user_id):
    """Retrieve all orders placed by a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        Response: JSON array of the user's orders with HTTP 200,
        or HTTP 404 if the user does not exist.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(orders_schema.dump(user.orders)), 200


@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_for_order(order_id):
    """Retrieve all products included in a specific order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        Response: JSON array of products with HTTP 200,
        or HTTP 404 if the order does not exist.
    """
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify(products_schema.dump(order.products)), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
