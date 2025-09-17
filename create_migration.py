from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Category, Product

app = Flask(__name__)

# Configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'  # Update with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Create migration script
@app.before_first_request
def init_db():
    with app.app_context():
        # Initialize the database
        db.create_all()
        print("Database and tables created successfully!")

if __name__ == '__main__':
    app.run(debug=True)
