from flask import Blueprint, render_template, request
from src.models import Post


main = Blueprint('main', __name__)


# Home page route
@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    # posts=[]
    return render_template('index.html', posts=posts)


# About Route
@main.route("/about")
def about():
    return render_template('about.html', title='About')

