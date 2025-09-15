from datetime import datetime
from flask import Flask, flash, render_template, redirect, request, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm,  SearchForm
from flask_sqlalchemy import SQLAlchemy
from models import Product, Customer, Wishlist, Order, ProductImage, db  # Importing db from models
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)  # Initialize the db here, no need to assign it again

@app.before_request
def initialize_database():
    """Ensures database tables exist without preloading products."""
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True

# Your routes...


@app.route('/', methods=['GET', 'POST'])
def index():
    """Displays all products and supports search functionality."""
    form = SearchForm()
    products = Product.query

    if form.validate_on_submit():
        search_query = form.search_query.data
        products = products.filter(
            (Product.name.contains(search_query)) | (Product.category.contains(search_query))
        )

    return render_template('index.html', products=products.all(), form=form)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    categories = Category.query.all()  # Fetch all categories from the database
    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']  # Get selected category
        price = float(request.form['price'])
        description = request.form['description']
        images = request.files.getlist('images')
        
        new_product = Product(name=name, category_id=category_id, price=price, description=description)
        db.session.add(new_product)
        db.session.commit()
        
        for image in images:
            if image.filename:
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                product_image = ProductImage(product_id=new_product.id, image_url=filepath)
                db.session.add(product_image)
                db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_product.html', categories=categories)
# Example: fetch admins but hide superadmin details
@app.route('/admin/list_admins')
def list_admins():
    admins = Admin.query.filter(Admin.role != 'superadmin').all()
    return render_template('list_admins.html', admins=admins)

# Example: check permissions
def is_superadmin(user):
    return user.role == 'superadmin'

# Example: deleting a customer
@app.route('/admin/delete_customer/<int:id>', methods=['POST'])
def delete_customer(id):
    if not is_superadmin(current_user):  # Only superadmin can delete
        flash("You don't have permission to delete customers.", "danger")
        return redirect(url_for('dashboard'))

    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted successfully.", "success")
    return redirect(url_for('dashboard'))

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
# Customer registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if the email already exists in the database
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Customer(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('You have successfully registered', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)
# Admin registration
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Enforce email rule
        if not email.endswith('@c0mrade.com'):
            flash('Admin email must end with @c0mrade.com', 'danger')
            return redirect(url_for('admin_register'))

        # Enforce username rule (alphanumeric only)
        if not username.isalnum():
            flash('Username must be alphanumeric (letters and numbers only)', 'danger')
            return redirect(url_for('admin_register'))

        # Check if email already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email address already exists', 'danger')
            return redirect(url_for('admin_register'))

        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Default role = moderator
        role = 'moderator'

        # Special case: only one superadmin
        if username == 'Admin' and email == 'Admin@c0mrade.com':
            role = 'superadmin'

        new_admin = Admin(username=username, email=email, password=hashed_password, role=role)

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin account created successfully', 'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('admin_register'))

    return render_template('admin_register.html', form=form)


# Customer login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile'))
        else:
            flash('Login failed. Check your username and/or password.')
    return render_template('login.html', form=form)
# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password, form.password.data):
            session['admin_id'] = admin.id
            session['role'] = admin.role  # store role in session
            flash('Admin login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('admin_login.html', form=form)
@app.route('/dashboard')
def dashboard():
    # Only allow access if logged-in user is super admin
    if 'admin_id' not in session:
        flash("Please log in as admin to access the dashboard.", "danger")
        return redirect(url_for('admin_login'))

    admin = Admin.query.get(session['admin_id'])
    if not admin or admin.role != 'superadmin':
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('admin_login'))

    # Fetch all records from tables
    admins = Admin.query.all()
    customers = Customer.query.all()
    orders = Order.query.all()
    carts = Cart.query.all()
    products = Product.query.all()
    wishlists = Wishlist.query.all()

    return render_template(
        'dashboard.html',
        admins=admins,
        customers=customers,
        orders=orders,
        carts=carts,
        products=products,
        wishlists=wishlists
    )
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    admin = Admin.query.get(session['admin_id'])
    if not admin or admin.role != 'superadmin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))

    customer = Customer.query.get_or_404(customer_id)

    try:
        # Delete related data
        Order.query.filter_by(customer_id=customer.id).delete()
        Cart.query.filter_by(customer_id=customer.id).delete()
        Wishlist.query.filter_by(customer_id=customer.id).delete()

        db.session.delete(customer)
        db.session.commit()
        flash("Customer and related data deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting customer: {str(e)}", "danger")

    return redirect(url_for('dashboard'))
@app.route('/delete_admin/<int:admin_id>', methods=['POST'])
def delete_admin(admin_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    super_admin = Admin.query.get(session['admin_id'])
    if not super_admin or super_admin.role != 'superadmin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))

    admin = Admin.query.get_or_404(admin_id)

    if admin.role == 'superadmin':
        flash("You cannot delete the superadmin account.", "danger")
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(admin)
        db.session.commit()
        flash("Admin deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting admin: {str(e)}", "danger")

    return redirect(url_for('dashboard'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    user = Customer.query.get(session['user_id'])
    order = Order.query.filter_by(customer_id=user.id).all()
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
    
@app.route('/view_order/<int:order_id>')
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


@app.route('/wishlist')
def wishlist():
    customer_id = session.get('customer_id')
    wishlist_items = Wishlist.query.filter_by(customer_id=customer_id).all()
    product_ids = [item.product_id for item in wishlist_items]
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    if not products:
        flash('Your wishlist is empty.', 'info')

    return render_template('wishlist.html', products=products)

@app.route('/add_to_wishlist/<int:product_id>')
def add_to_wishlist(product_id):
    customer_id = session.get('customer_id')
    wishlist_item = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first()

    if not wishlist_item:
        wishlist_item = Wishlist(customer_id=customer_id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Item added to your wishlist.', 'success')
    else:
        flash('Item is already in your wishlist.', 'info')
        
    return redirect(url_for('index'))

@app.route('/remove_from_wishlist/<int:product_id>')
def remove_from_wishlist(product_id):
    customer_id = session.get('customer_id')
    wishlist_item = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Product removed from your wishlist.', 'success')
    else:
        flash('Product is not in your wishlist.', 'info')
    return redirect(url_for('wishlist'))


if __name__ == '__main__':
    app.run(debug=True)