from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm,  SearchForm
from models import Product, Customer, Order, db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
     with app.app_context():
      db.create_all()
      if not Product.query.first():
        products = []
        Product(name='Taifa Leo', category='Newspapers', price=65.00, image_url='/static/images/taifa_leo.jpg', description='The latest one.'),
        Product(name='Daily Nations', category='Newspapers', price=64.00, image_url='/static/images/daily_nations.jpg', description='Covers all what happens daily.'),
        Product(name='The Standards', category='Newspapers', price=68.00, image_url='/static/images/the_standards.jpg', description='Entails all the news of the nation.'),
        Product(name='Obama Smoothline', category='Pens', price=9.00, image_url='/static/images/obama_smoothline.jpg', description='Provides a short, smooth and neat writing experience.'),
        Product(name='Teepee', category='Pens', price=9.00, image_url='/static/images/teepee.jpg', description='Helps you outsmart all others in the contest for the durability and high resistance to high temperatures.'),
        Product(name='Bic', category='Pens', price=18.00, image_url='/static/images/bic.jpg', description='Professionally recognized and recommended pen for all users. Be it in the office or class, still perfect.'),
        Product(name='HB Pencil', category='Pencils', price=18.00, image_url='/static/images/hb_pencil.jpg', description='Deep dark, long lasting and recommended for drawing and national exams.'),
        Product(name='Mechanical Pencil', category='Pencils', price=19.00, image_url='/static/images/mechanical_pencil.jpg', description='Tedious sharpening taken away. Just replace the blunt graphite from the front to back and a sharp one pops up.'),
        Product(name='Pelikan', category='Erasers', price=9.00, image_url='/static/images/perikan.jpg', description='Classic eraser, long lasting and with quality results.'),
        Product(name='Neo', category='Erasers', price=4.00, image_url='/static/images/neo.jpg', description='Affordable and best for drawing. Highly recommended for national examinations.'),
        Product(name='Emerging Technology', category='Textbooks', price=109.00, image_url='/static/images/emerging_technology.jpg', description='Covers the latest technology in almost every sector. Also includes the future of technology.'),
        Product(name='C++ Programming', category='Textbooks', price=249.00, image_url='/static/images/c++_programming.jpg', description='Gets you started from a complete beginner to pro in C++ programming language.'),
        Product(name='Research Methods', category='Textbooks', price=99.00, image_url='/static/images/research_methods.jpg', description='Equips the learner with skills and guides to do research on any area.'),
        Product(name='Blossoms Of The Savannah', category='Novels', price=499.00, image_url='/static/images/blossoms_of_the_savannah.jpg', description='A book about two sisters who face the challenges of female genital mutilation, early marriage, and education in Maasailand.'),
        Product(name='The Pearl', category='Novels', price=299.00, image_url='/static/images/the_pearl.jpg', description='It tells the story of a pearl diver, Kino, and his family, who face hardship and violence after finding a valuable pearl.'),
        Product(name='A Doll\'s House', category='Novels', price=249.00, image_url='/static/images/a_dolls_house.jpg', description='A Doll\'s House is a three-act play written by Norwegian playwright Henrik Ibsen.'),
        
        db.session.bulk_save_objects(products)
        db.session.commit()
    app.db_initialized = True

@app.route('/',methods=['GET', 'POST'])
def index():
    form = SearchForm()
    products = []
    if form.validate_on_submit():
        search_query = form.search_query.data
        products = Product.query.filter((Product.name.contains(search_query)) | (Product.category.contains(search_query))).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products, form=form)
    

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    cart_items = session['cart']
    products = Product.query.filter(Product.id.in_(cart_items)).all()
    return render_template('cart.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    flash('Product added to cart!')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session and product_id in session['cart']:
        session['cart'].remove(product_id)
        session.modified = True
        flash('Product removed from cart!')
    return redirect(url_for('cart'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = Customer(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('profile'))
        else:
            flash('Login failed. Check your username and/or password.')
    return render_template('login.html', form=form)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    user = Customer.query.get(session['user_id'])
    orders = Order.query.filter_by(customer_id=user.id).all()
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/create_order')
def create_order():
    if 'user_id' not in session:
        flash('Please log in to place an order.')
        return redirect(url_for('login'))
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty.')
        return redirect(url_for('index'))
    cart_items = session['cart']
    products = Product.query.filter(Product.id.in_(cart_items)).all()
    total_amount = sum(product.price for product in products)
    new_order = Order(customer_id=session['user_id'], order_date=datetime.utcnow(), order_status='unpaid', total_amount=total_amount)
    db.session.add(new_order)
    db.session.commit()
    for product in products:
        new_order.products.append(product)
    db.session.commit()
    session['cart'] = []
    flash('Order created successfully! Please proceed to payment.')
    session.pop('cart', None)
    return redirect(url_for('view_order', order_id=new_order.id))

@app.route('/order/<int:order_id>')
def order(order_id):
    order = Order.query.get_or_404(order_id)
    products = order.products
    return render_template('order.html', order=order, products=products)
    
@app.route('/view_order')
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order.html', order=order)

@app.route('/pay/<int:order_id>')
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    if order.order_status == 'paid':
        flash('This order is already paid.')
    else:
        order.order_status = 'paid'
        db.session.commit()
        flash('Payment successful! Your order has been marked as paid.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
