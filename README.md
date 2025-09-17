# c0mrade Shop - E-commerce

Welcome to **c0mrade Shop**, an online e-commerce platform built with Flask, designed to provide a seamless shopping experience with features like product browsing, cart management, wishlists, orders, and an admin panel.

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [User Accounts & Permissions](#user-accounts--permissions)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

c0mrade Shop is designed to make online shopping intuitive and efficient. Users can browse products, manage carts and wishlists, and track their orders. Admins have access to manage products, categories, and users.

---

## Features

- **User Authentication**: Register, login, and manage accounts.
- **Product Listings**: Browse products, search, and view details.
- **Shopping Cart**: Add products, view cart, update quantities, and checkout.
- **Wishlist**: Save favorite products for later purchase.
- **Order Management**: View order history and track status.
- **Admin Panel**: Manage products, categories, and user accounts.
- **Responsive Design**: Optimized for both desktop and mobile.

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Flask
- SQLAlchemy
- Jinja2

### Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Njorodev/c0mrade-shop.git
    cd c0mrade-shop
    ```

2. **Create a Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up the Database:**

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. **Run the Application:**

    ```bash
    flask run
    ```

6. **Access the Application:**

    Open your browser at `http://127.0.0.1:5000`.

---

## Usage

### User Authentication

- **Register**: Create a new account.
- **Login**: Access your account.
- **Profile**: View and edit your profile.

### Browsing Products

- **Home Page**: Featured products and categories.
- **Product Page**: Product details, add to cart or wishlist.
- **Search**: Use the search bar to find products.

### Cart and Wishlist

- **Cart**: Add, update quantities, and checkout.
- **Wishlist**: Save favorite products for later.

### Order Management

- **Order History**: View past orders.
- **Order Details**: Check order information.

### Admin Panel

- **Manage Products**: Add, edit, delete products.
- **Manage Categories**: Create and manage categories.
- **Manage Users**: View and manage user accounts.

---

## Folder Structure


```
c0mrade-shop
├── .flaskenv
├── .git
├── .vscode
├── CODE_OF_CONDUCT.md
├── LICENSE
├── README.md
├── pycache
├── app.py
├── c0mrade/
├── config.py
├── contributors.md
├── create_migration.py
├── forms.py
├── instance/
│ └── shop.db
├── models.py
├── requirements.txt
├── screenshots/
│ ├── cart.png
│ ├── home page.png
│ ├── login.png
│ ├── order details.png
│ ├── product details.png
│ ├── register.png
│ └── wishlist.png
├── static/
│ ├── images/
│ └── styles.css
├── templates/
│ ├── add_product.html
│ ├── admin_login.html
│ ├── admin_register.html
│ ├── base.html
│ ├── cart.html
│ ├── dashboard.html
│ ├── index.html
│ ├── login.html
│ ├── order.html
│ ├── product.html
│ ├── profile.html
│ ├── register.html
│ └── wishlist.html
├── tree_gen.py
└── users permissions and passwords.md
```

## User Accounts & Permissions

⚠️ Note to Developers:

The user accounts listed in this project are created for testing and demonstration purposes only.  
- **Admin / Superadmin**: Admin@c0mrade.com  
- **Moderator**: JohnDoe@c0mrade.com  
- **Customer**: TestUser@example.com  

**Important:** Do **not** use these credentials in a production environment.  
Passwords and accounts are meant to help you test the application functionality safely.  

Always create secure, unique accounts when deploying the project to production.

___**USERS AND THEIR CREDENTIALS**___
________________________________________________________________________
| User      | Email                    | Role       | Password         |
| --------- | ------------------------ | ---------- | ---------------- |
| Admin     | Admin@c0mrade.com        | superadmin | Adm1n!Secure2025 |
| John Doe  | JohnDoe@c0mrade.com      | moderator  | J0hnD03!2025     |
| Test User | TestUser@example.com     | customer   | T3stUser#123     |
------------------------------------------------------------------------

___**USER PERMISSIONS**___
____________________________________________________________________________________________
| Action / Permission   | Superadmin (Admin) | Moderator (John Doe)       | Customer (Test User) |
| --------------------- | ------------------ | -------------------------- | -------------------- |
| View all admins       | ✔                  | ✔                          | ✘                    |
| View superadmin       | ✔                  | ✘                          | ✘                    |
| View all moderators   | ✔                  | ✔                          | ✘                    |
| View all customers    | ✔                  | ✔                          | ✘                    |
| View carts            | ✔                  | ✔                          | ✔ (own only)         |
| View wishlists        | ✔                  | ✔                          | ✔ (own only)         |
| View orders           | ✔                  | ✔                          | ✔ (own only)         |
| Add products          | ✔                  | ✔                          | ✘                    |
| Delete products       | ✔                  | ✔                          | ✘                    |
| Delete customers      | ✔                  | ✘                          | ✘                    |
| Delete moderators     | ✔                  | ✘                          | ✘                    |
| Add items to cart     | ✘                  | ✘                          | ✔                    |
| Add items to wishlist | ✘                  | ✘                          | ✔                    |
| Place orders          | ✘                  | ✘                          | ✔                    |
| Full dashboard access | ✔                  | ✔ (except superadmin info) | ✘                    |
--------------------------------------------------------------------------------------------------


## Contributing

1. Fork the repository.
2. Clone your fork:

    ```bash
    git clone https://github.com/yourusername/c0mrade-shop.git
    ```

3. Create a new branch:

    ```bash
    git checkout -b feature/your-feature
    ```

4. Make changes, commit, and push.
5. Create a pull request.

---

## License

c0mrade Shop is licensed under the [MIT License](LICENSE).

---

Thank you for using **c0mrade Shop**! For questions, contact the maintainers.