from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from app.blueprints.blog import blog_bp
from app.models import Post, Category, Comment
from app.forms import PostForm, CommentForm


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    # Populate category choices
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        post = Post(
            title=form.title.data.strip(),
            content=form.content.data,
            category_id=form.category_id.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Your blog post has been published successfully!', 'success')
        return redirect(url_for('blog.post_detail', post_id=post.id))

    return render_template('blog/create_post.html', title='Create New Post', form=form)


@blog_bp.route('/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = db.get_or_404(Post, post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to leave a comment.', 'warning')
            return redirect(url_for('auth.login', next=url_for('blog.post_detail', post_id=post.id)))

        comment_content = comment_form.content.data.strip()
        if not comment_content:
            flash('Comment content cannot be empty.', 'danger')
            return redirect(url_for('blog.post_detail', post_id=post.id))

        comment = Comment(
            content=comment_content,
            author=current_user,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added successfully!', 'success')
        return redirect(url_for('blog.post_detail', post_id=post.id, _anchor='comments-section'))

    comments = post.comments.order_by(Comment.created_at.asc()).all()

    # Query related articles (same category or recent)
    related_posts = Post.query.filter(Post.id != post.id, Post.category_id == post.category_id).order_by(Post.created_at.desc()).limit(3).all()
    if len(related_posts) < 3:
        existing_ids = [p.id for p in related_posts] + [post.id]
        additional = Post.query.filter(~Post.id.in_(existing_ids)).order_by(Post.created_at.desc()).limit(3 - len(related_posts)).all()
        related_posts.extend(additional)

    return render_template(
        'blog/post_detail.html',
        title=post.title,
        post=post,
        comments=comments,
        comment_form=comment_form,
        related_posts=related_posts
    )


@blog_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)

    # Authorization check: only post owner can edit
    if post.author != current_user:
        abort(403)

    form = PostForm()
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.category_id = form.category_id.data
        post.content = form.content.data
        db.session.commit()
        flash('Your blog post has been updated successfully!', 'success')
        return redirect(url_for('blog.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.category_id.data = post.category_id
        form.content.data = post.content

    return render_template('blog/edit_post.html', title='Edit Post', form=form, post=post)


@blog_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)

    # Authorization check: only post owner can delete
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Blog post has been deleted successfully.', 'success')
    return redirect(url_for('auth.dashboard'))


@blog_bp.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)

    # Authorization check: only comment author can edit
    if comment.author != current_user:
        abort(403)

    form = CommentForm()
    if form.validate_on_submit():
        new_content = form.content.data.strip()
        if not new_content:
            flash('Comment cannot be empty.', 'danger')
            return redirect(url_for('blog.edit_comment', comment_id=comment.id))

        comment.content = new_content
        db.session.commit()
        flash('Comment updated successfully.', 'success')
        return redirect(url_for('blog.post_detail', post_id=comment.post_id, _anchor='comments-section'))
    elif request.method == 'GET':
        form.content.data = comment.content

    return render_template('blog/edit_comment.html', title='Edit Comment', form=form, comment=comment)


@blog_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)

    # Authorization check: only comment author can delete
    if comment.author != current_user:
        abort(403)

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')
    return redirect(url_for('blog.post_detail', post_id=post_id, _anchor='comments-section'))
