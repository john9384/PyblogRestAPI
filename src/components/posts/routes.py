from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
import uuid
from src import db
from src.models import Post
from src.components.posts.forms import PostForm
from src.components.helpers import token_required, build_res_obj
from src.components.errors import CustomError, build_err_obj

# creating a blueprint of the post
posts = Blueprint('posts', __name__)


@posts.route("/post/create", methods=['GET', 'POST'])
@token_required
def create_post(current_user):
    try:
        form = PostForm()
        post = Post(post_id=str(uuid.uuid4()), title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        post_payload ={
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'author': {
                'username': post.author.username,
                'user_id': post.user_id
            },
            
            'date_posted': post.date_posted
        }
        return build_res_obj('Post created', 200, post_payload)
    # Error block
    except Exception as err:
        return build_err_obj(err, err.status_code or 404)
    

# Fetch all posts
@posts.route("/post/all", methods=['GET'])
def get_all_posts():
    try:
        posts = Post.query.all()
        arr_of_posts= []
        for post in posts:
            post_obj ={
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'author': {
                'username': post.author.username,
                'user_id': post.user_id
            },
            
            'date_posted': post.date_posted
        }
            arr_of_posts.append(post_obj)
        # Build Response
        return build_res_obj('Posts feteched', 200, arr_of_posts)
    # Error block
    except Exception as err:
        return build_err_obj(err, err.status_code or 404)

# Fetch posts by id
@posts.route("/post/<user_id>/all", methods=['GET'])
def get_all_posts_by_id(user_id):
    try:
        posts = Post.query.filter_by(user_id=user_id).all()
        arr_of_posts= []
        for post in posts:
            post_obj ={
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'author': {
                'username': post.author.username,
                'user_id': post.user_id
            },
            
            'date_posted': post.date_posted
        }
            arr_of_posts.append(post_obj)
        # Build Response
        return build_res_obj('Posts feteched', 200, arr_of_posts)
    # Error block
    except Exception as err:
        return build_err_obj(err, err.status_code or 404)
        
@posts.route("/post/single/<post_id>", methods=['GET'])
def post(post_id):
    try:
        post = Post.query.filter_by(post_id=post_id).first()
        if post is None:
            raise CustomError("No post with id specified", 400)
        post_obj ={
                'post_id': post.post_id,
                'title': post.title,
                'content': post.content,
                'author': {
                    'username': post.author.username,
                    'user_id': post.user_id
                },
                
                'date_posted': post.date_posted
        }
        return build_res_obj('Post feteched', 200, post_obj)
    # Error block
    except Exception as err:
        return build_err_obj(err, err.status_code or 404)   


@posts.route("/post/<post_id>/update", methods=['POST','PUT'])
@token_required
def update_post(current_user, post_id):
    try:
        post = Post.query.filter_by(post_id=post_id).first()
        if post is None:
            raise CustomError("No post with id specified", 400)
        if post.author != current_user:
            raise CustomError("User not authorized", 403)
        form = PostForm()
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        post_payload ={
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'author': {
                'username': post.author.username,
                'user_id': post.user_id
            },
            
            'date_posted': post.date_posted
        }
        return build_res_obj('Post updated', 200, post_payload)
    # Error block
    except Exception as err:
        return build_err_obj(err, err.status_code or 404)   

@posts.route("/post/<post_id>/delete", methods=['POST','DELETE'])
@token_required
def delete_post(current_user, post_id):
    try:
        post = Post.query.filter_by(post_id=post_id).first()
        if post is None:
            raise CustomError("No post with id specified", 400)
        if post.author != current_user:
            raise CustomError("User not authorized", 403)
        db.session.delete(post)
        db.session.commit()
        return build_res_obj('Post deleted', 200)
    except Exception as err:
        return build_err_obj(err, err.status_code or 404)   
