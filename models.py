from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()  # No need to re-initialize db here

# Association table for many-to-many relationship between Order and Product
order_products = db.Table('order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)
# Your models...

# Category model
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category_rel = db.relationship('Category', backref='products')
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

# ProductImage model
class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)  
    product = db.relationship("Product", back_populates="images")

  # Customer model 
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    wishlist_items = db.relationship('Product', secondary='wishlist', backref=db.backref('users', lazy='dynamic'))

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_status = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', secondary=order_products, backref='orders')
    total_amount = db.Column(db.Float, nullable=False, default='unpaid')
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

# Cart model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('cart_items', lazy=True))

# Wishlist model
class Wishlist(db.Model):
    wishlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('wishlists', lazy=True))
    product = db.relationship('Product', backref=db.backref('wishlists', lazy=True))

# Admin model
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='moderator')



