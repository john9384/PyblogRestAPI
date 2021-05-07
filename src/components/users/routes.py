from flask import Blueprint, render_template, url_for, flash, redirect, current_app
from flask import request, jsonify, make_response
from flask_login import login_user, current_user, logout_user, login_required
import uuid
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src import db, bcrypt
from src.models import User, Post
from src.components.users import UpdateAccountForm, RequestResetForm, ResetPasswordForm
from src.components.users import save_picture, send_reset_email
from src.components.helpers import token_required, build_res_obj
from src.components.errors import CustomError, build_err_obj

# Creating a Blueprint for users
users = Blueprint('users', __name__)


@users.route("/test/test", methods=['GET', 'POST'])
@token_required
def testRoute(current_user):
    data = request.get_json()
    print('Gets here')
    print(data)
    return jsonify({'message': 'User routes now working'})

# Get all users route
@users.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    output = []
    for user in all_users:
        user_data = {'password': user.password, 'user_id': user.user_id, 'username': user.username, 'email': user.email}
        output.append(user_data)
    return jsonify({'users': output})


# Get Single user
@users.route('/users/<user_id>', methods=['GET'])
@token_required
def get_single_user(current_user, user_id):
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify("msg: user not found")

    user_data = {'user_id': user.user_id, 'username': user.username, 'email': user.email}

    return jsonify({'user': user_data})


# Sign Up route and function
@users.route("/sign-up", methods=['POST'])
def sign_up():
    try:
        data = request.get_json()
        user_email = User.query.filter_by(email=data['email']).first()
        user_username = User.query.filter_by(username=data['username']).first()

        if user_email or user_username:
            raise CustomError('User exists', 200)

        hashed_password = generate_password_hash(data['password'], method='sha256')
        user = User(user_id=str(uuid.uuid4()), username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Build User obj
        user_obj = {
            "username": user.username,
            "email": user.email,
            "image": user.image_file
        }
        # Build response
        return build_res_obj("User account created", 200, user_obj)
        
    except Exception as e:
        return build_err_obj(e, 404)



# Sign In route and function
@users.route("/sign-in", methods=['GET', 'POST'])
def sign_in():
    try:
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        user = User.query.filter_by(username=auth.username).first()

        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        # swapped the auth.password for data['password']
        if check_password_hash(user.password, auth.password):
            token = jwt.encode({'user_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},current_app.config['SECRET_KEY'])
            print(type(token))
                    # Build User obj
            token_obj = {
             'token': str(token, "UTF-8")
            }
            # Build response
            return  build_res_obj("User account created", 200, token_obj)

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    except Exception as e:
        return build_err_obj(e, 404)


# The logout route and function
@users.route("/logout")
def sign_out():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.sign_in'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.sign_in'))
    return render_template('reset_token.html', title='Reset Password', form=form)


# Delete user
@users.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify("msg: user not found")

    db.session.delete(user)
    db.session.commit()

    return jsonify({'msg': 'User has been deleted'})
