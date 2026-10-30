import os
from app import create_app, db
from app.models import User, Post, Category, Comment

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'Category': Category,
        'Comment': Comment
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        try:
            Category.seed_defaults()
        except Exception as e:
            app.logger.warning(f"Could not seed default categories: {e}")

    app.run(host='127.0.0.1', port=5000, debug=True)

