import os
from app import create_app, db
from app.models import Category

app = create_app(os.environ.get('FLASK_ENV', 'production'))

with app.app_context():
    db.create_all()
    try:
        Category.seed_defaults()
    except Exception as e:
        app.logger.warning(f"Could not seed default categories: {e}")

if __name__ == '__main__':
    app.run()
