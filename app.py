from datetime import datetime, timezone
from flask import Flask, flash, render_template, redirect, request, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import ProductForm, RegistrationForm, LoginForm,  SearchForm
from flask_sqlalchemy import SQLAlchemy
from models import Product, Customer, Wishlist, Order, ProductImage, Admin, Category, Cart, db  # Importing db from models
from config import Config
from flask_migrate import Migrate


# Initialize Flask app
app = Flask(__name__)

# Load configurations
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize database and migration
db.init_app(app)  
migrate = Migrate(app, db)

# Ensure upload folder exists
@app.before_request
def initialize_database():
    """Ensures database tables exist without preloading products."""
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True

# My routes...

# Home and Search
@app.route('/', methods=['GET', 'POST'])
def index():
    """Displays all products and supports search functionality."""
    form = SearchForm()
    products = Product.query

    if form.validate_on_submit():
        search_query = form.search_query.data

        # join Category so we can filter by category name
        products = products.join(Category).filter(
            (Product.name.contains(search_query)) |
            (Product.description.contains(search_query)) |
            (Category.name.contains(search_query))
        )

    products = products.all()

    #  Check wishlist for current customer
    wishlist_ids = []
    customer_id = session.get('customer_id')
    if customer_id:
        wishlist_ids = [
            w.product_id for w in Wishlist.query.filter_by(customer_id=customer_id).all()
        ]

    return render_template(
        'index.html',
        products=products,
        form=form,
        wishlist_ids=wishlist_ids
    )

# Product details
@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    customer_id = session.get('customer_id') 

    wishlist_ids = []
    if customer_id:
        wishlist_ids = [
            w.product_id
            for w in Wishlist.query.filter_by(customer_id=customer_id).all()
        ]

    return render_template(
        'product.html',
        product=product,
        wishlist_ids=wishlist_ids
    )

# Add Product (Admin only)
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()

    # Populate category choices dynamically inside the request context
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            category_id=form.category_id.data
        )
        db.session.add(new_product)
        db.session.commit()

        # Handle multiple image uploads
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image.filename:
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Save to filesystem
                    image.save(filepath)
                    #  Save only relative path in DB (Flask will serve from static/)
                    relative_path = os.path.join('images', filename)
                    product_image = ProductImage(
                        product_id=new_product.id,
                        image_url=relative_path
                    )
                    db.session.add(product_image)

            db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_product.html', form=form)

# Delete Product (Admin only, with cascading deletions)
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'admin_id' not in session:
        flash("Please log in as admin first.", "danger")
        return redirect(url_for('admin_login'))

    admin = Admin.query.get(session['admin_id'])
    if not admin or admin.role not in ['moderator', 'superadmin']:
        flash("You don’t have permission to delete products.", "danger")
        return redirect(url_for('dashboard'))

    product = Product.query.get_or_404(product_id)

    # 1. Delete product from carts
    Cart.query.filter_by(product_id=product.id).delete()

    # 2. Delete product from wishlists
    Wishlist.query.filter_by(product_id=product.id).delete()

    # 3. Delete product images
    for img in product.images:
        if img.image_url:
            import os
            image_path = os.path.join('static', 'images', os.path.basename(img.image_url))
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(img)

    # 4. Finally, delete the product itself
    db.session.delete(product)
    db.session.commit()

    flash("Product and all related data deleted successfully!", "success")
    return redirect(url_for('dashboard'))


# List Admins exept "Admin" (Admin only)
@app.route('/admin/list_admins')
def list_admins():
    admins = Admin.query.filter(Admin.role != 'superadmin').all()
    return render_template('list_admins.html', admins=admins)

# Example: check permissions
def is_superadmin(user):
    return user.role == 'superadmin'

# View Cart
@app.route('/cart')
def cart():
    customer_id = session.get('customer_id')
    if not customer_id:
        flash('You need to log in to view your cart.', 'warning')
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(customer_id=customer_id).all()
    return render_template('cart.html', cart_items=cart_items)


# Add to Cart
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    customer_id = session.get('customer_id')
    if not customer_id:
        flash('You need to log in to add items to your cart.', 'warning')
        return redirect(url_for('login', next=url_for('product', product_id=product_id)))

    cart_item = Cart.query.filter_by(customer_id=customer_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(customer_id=customer_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash('Product added to your cart!', 'success')
    return redirect(url_for('cart'))


# Remove from Cart
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    customer_id = session.get('customer_id')
    if not customer_id:
        flash('You need to log in to modify your cart.', 'warning')
        return redirect(url_for('login'))

    cart_item = Cart.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from your cart!', 'success')
    else:
        flash('Item not found in your cart.', 'info')

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
            session['customer_id'] = user.id
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

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        flash("Please log in as admin to access the dashboard.", "danger")
        return redirect(url_for('admin_login'))

    admin = Admin.query.get(session['admin_id'])
    if not admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('admin_login'))

    # Common data
    customers = Customer.query.all()
    orders = Order.query.all()
    products = Product.query.all()
    wishlists = Wishlist.query.all()
    carts = Cart.query.all()   # ✅ simpler, uses relationships

    if admin.role == 'superadmin':
        admins = Admin.query.all()
    else:
        admins = Admin.query.filter(Admin.role != 'superadmin').all()

    return render_template(
        'dashboard.html',
        admins=admins,
        customers=customers,
        orders=orders,
        carts=carts,
        products=products,
        wishlists=wishlists,
        role=admin.role
    )

# Delete Customer (Admin only, with cascading deletions)
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    admin = Admin.query.get(session['admin_id'])
    if not admin or admin.role != 'superadmin':
        flash("Unauthorized access. You don't have permission to delete Customer", "danger")
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

# Delete Admin (Admin only, with checks)
@app.route('/delete_admin/<int:admin_id>', methods=['POST'])
def delete_admin(admin_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    super_admin = Admin.query.get(session['admin_id'])
    if not super_admin or super_admin.role != 'superadmin':
        flash("Unauthorized access. You don't have permision to delete admins info", "danger")
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

# Customer Profile
@app.route('/profile')
def profile():
    if 'customer_id' not in session:
        flash("Please log in to view your profile.", "danger")
        return redirect(url_for('login'))

    customer_id = session['customer_id']
    user = Customer.query.get_or_404(customer_id)

    wishlist = Wishlist.query.filter_by(customer_id=customer_id).all()
    cart = Cart.query.filter_by(customer_id=customer_id).all()

    return render_template(
        'profile.html',
        user=user,
        wishlist=wishlist,
        cart=cart
    )

# Logout for both customer and admin
@app.route('/logout')
def logout():
    session.pop('customer_id', None)  # remove customer session
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)  # remove admin session
    flash('You have been logged out as admin.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/create_order', methods=['POST', 'GET'])
def create_order():
    if 'customer_id' not in session:
        flash('Please log in to place an order.')
        return redirect(url_for('login'))

    customer_id = session['customer_id']

    # Fetch cart items from DB
    cart_items = Cart.query.filter_by(customer_id=customer_id).all()
    if not cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('index'))

    # Calculate total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # Create new order
    new_order = Order(
        customer_id=customer_id,
        order_date=datetime.utcnow(),
        order_status='unpaid',
        total_amount=total_amount
    )
    db.session.add(new_order)
    db.session.commit()  # commit to get order ID

    # Link products to the order safely
    for item in cart_items:
        if item.product not in new_order.products:
            new_order.products.append(item.product)
        # If you want to track quantities, use an association table with a quantity column

    db.session.commit()

    # Clear cart after checkout
    Cart.query.filter_by(customer_id=customer_id).delete()
    db.session.commit()

    flash('Order created successfully! Please proceed to payment.')
    return redirect(url_for('view_order', order_id=new_order.id))

# Order details
@app.route('/order/<int:order_id>')
def order(order_id):
    order = Order.query.get_or_404(order_id)
    products = order.products
    return render_template('order.html', order=order, products=products)

# View Order    
@app.route('/view_order/<int:order_id>')
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order.html', order=order)

# Simulate payment (for demo purposes)
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

# Wishlist routes
# View Wishlist
@app.route('/wishlist')
def wishlist():
    customer_id = session.get('customer_id')
    if not customer_id:
        flash('You need to log in to view your wishlist.', 'warning')
        return redirect(url_for('login'))

    # Join Wishlist + Product
    wishlist_items = (
        db.session.query(Wishlist, Product)
        .join(Product, Wishlist.product_id == Product.id)
        .filter(Wishlist.customer_id == customer_id)
        .all()
    )

    return render_template(
        'wishlist.html',
        wishlist_items=wishlist_items
    )

# Add to Wishlist
@app.route('/add_to_wishlist/<int:product_id>', methods=['POST', 'GET'])
def add_to_wishlist(product_id):
    customer_id = session.get('customer_id')   # ✅ fixed
    if not customer_id:
        flash('You need to log in to add items to your wishlist.', 'warning')
        return redirect(url_for('login', next=url_for('product', product_id=product_id)))

    wishlist_item = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first()

    if not wishlist_item:
        wishlist_item = Wishlist(customer_id=customer_id, product_id=product_id)  # ✅ fixed
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Item added to your wishlist.', 'success')
    else:
        flash('Item is already in your wishlist.', 'info')

    return redirect(url_for('wishlist'))

# Remove from Wishlist
@app.route('/remove_from_wishlist/<int:product_id>')
def remove_from_wishlist(product_id):
    customer_id = session.get('customer_id')   # ✅ fixed
    if not customer_id:
        flash('You need to log in to modify your wishlist.', 'warning')
        return redirect(url_for('login'))

    wishlist_item = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Product removed from your wishlist.', 'success')
    else:
        flash('Product is not in your wishlist.', 'info')
    return redirect(url_for('wishlist'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)