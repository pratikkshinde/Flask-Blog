"""
Database Seeding Script for FlaskBlog.
Populates initial categories, demo users, sample blog posts, and comments.
Run with: python seed.py
"""
import sys
from app import create_app, db
from app.models import User, Category, Post, Comment


def seed_database():
    app = create_app('development')
    with app.app_context():
        print("Ensuring tables are created...")
        db.create_all()

        print("Seeding categories...")
        Category.seed_defaults()

        # Check if users already exist
        demo_user = User.query.filter_by(username='alex_dev').first()
        if not demo_user:
            print("Creating demo users...")
            user1 = User(
                username='alex_dev',
                email='alex@example.com'
            )
            user1.set_password('Password123!')

            user2 = User(
                username='sarah_codes',
                email='sarah@example.com'
            )
            user2.set_password('Password123!')

            db.session.add_all([user1, user2])
            db.session.commit()
            print("Demo users created: alex_dev, sarah_codes (password: Password123!)")
        else:
            user1 = demo_user
            user2 = User.query.filter_by(username='sarah_codes').first()

        # Check if posts already exist
        if Post.query.count() == 0:
            print("Creating sample blog posts...")
            cat_tech = Category.query.filter_by(slug='technology').first()
            cat_web = Category.query.filter_by(slug='web-development').first()
            cat_prog = Category.query.filter_by(slug='programming').first()
            cat_ai = Category.query.filter_by(slug='artificial-intelligence').first()

            post1 = Post(
                title="Building Production-Ready Web Applications with Flask",
                content="""# Building Production-Ready Web Applications with Flask

Flask is renowned for its lightweight simplicity, but scaling it into a robust, maintainable architecture requires thoughtful patterns.

## 1. The Application Factory Pattern
Using an application factory decouples your Flask application from global state:

```python
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    return app
```

## 2. Blueprint Modularization
Organizing routes into Blueprints keeps auth, blog, and api domains cleanly separated.

> "Simplicity is prerequisite for reliability." — Edsger W. Dijkstra

Happy coding with Flask!
""",
                category_id=cat_web.id if cat_web else 1,
                author=user1
            )

            post2 = Post(
                title="Demystifying Generative AI and Retrieval Augmented Generation",
                content="""# Understanding Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) has transformed how large language models interact with proprietary enterprise data.

### Why RAG Matters
1. **Reduces Hallucinations**: Grounds responses in real factual chunks.
2. **Dynamic Knowledge**: No expensive retraining needed when policies update.
3. **Data Security**: Context vectors remain inside your private perimeter.

Vector databases like Chroma, Pinecone, or pgvector provide high-dimensional similarity searches that power modern AI workflows.
""",
                category_id=cat_ai.id if cat_ai else 1,
                author=user2
            )

            post3 = Post(
                title="Mastering Modern Python: Clean Code & Typing Best Practices",
                content="""# Clean Code in Python 3.12+

Modern Python brings powerful typing features, pattern matching, and performance boosts.

## Key Recommendations
- Always use type annotations (`typing.Optional`, `list[str]`, etc.).
- Prefer dataclasses or Pydantic models for structured data containers.
- Write expressive unit tests using `pytest` fixtures.

```python
def calculate_reading_time(word_count: int, wpm: int = 200) -> int:
    return max(1, round(word_count / wpm))
```
""",
                category_id=cat_prog.id if cat_prog else 1,
                author=user1
            )

            db.session.add_all([post1, post2, post3])
            db.session.commit()
            print("Sample posts created.")

            # Create sample comments
            c1 = Comment(
                content="Exceptional walkthrough! The Application Factory pattern saved our team from circular import headaches.",
                author=user2,
                post=post1
            )
            c2 = Comment(
                content="Great explanation of RAG. Could you also write an article on hybrid keyword-vector search?",
                author=user1,
                post=post2
            )
            db.session.add_all([c1, c2])
            db.session.commit()
            print("Sample comments created.")

        print("Database seeding completed successfully!")


if __name__ == '__main__':
    seed_database()
