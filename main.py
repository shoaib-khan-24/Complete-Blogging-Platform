from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

ckeditor = CKEditor(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

# creating form
class PostForm(FlaskForm):
    title = StringField(Markup('<strong>Blog Post Title</strong>'), validators=[DataRequired()])
    subtitle = StringField(Markup('<strong>Subtitle</strong>'), validators=[DataRequired()])
    author = StringField(Markup('<strong>Your Name</strong>'), validators=[DataRequired()])
    img_url = StringField(Markup('<strong>Blog Image URL</strong>'), validators=[DataRequired(), URL()])
    body = CKEditorField(Markup('<strong>Body Content</strong>'), validators=[DataRequired()])
    submit = SubmitField('Submit Post')


@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route("/new-post", methods=['GET', 'POST'])
def new_post():
    form = PostForm()

    if form.validate_on_submit():

        curr_date = date.today().strftime("%B %d, %Y")

        new_blog_post = BlogPost(title=form.title.data, subtitle=form.subtitle.data, author=form.author.data, img_url=form.img_url.data, body=form.body.data, date=curr_date)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post_to_edit = db.get_or_404(BlogPost, post_id)
    form = PostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        img_url=post_to_edit.img_url,
        author=post_to_edit.author,
        body=post_to_edit.body
    )
    if form.validate_on_submit():

        post_to_edit.title = form.title.data
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.author = form.author.data
        post_to_edit.img_url = form.img_url.data
        post_to_edit.body = form.body.data

        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("make-post.html", form=form, editing=True)


@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
