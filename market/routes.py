from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()

    if request.method == "POST":
        # Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_obj = Item.query.filter_by(name=purchased_item).first()
        if p_item_obj:
            if current_user.can_purchase(p_item_obj.price):
                p_item_obj.assign_to_user(current_user)
                flash(f"Congratulations! You purchased {p_item_obj.name} for {p_item_obj.price}$", category='success')
            else:
                flash(f'Unfortunately, you don\'t have enough money to purchase {p_item_obj.name}', category='danger')

        # Sell Items Logic
        sold_item = request.form.get('sold_item')
        s_item_obj = Item.query.filter_by(name=sold_item).first()
        if s_item_obj:
            if current_user.can_sell(s_item_obj):
                s_item_obj.sell(current_user)
                flash(f"Congratulations! You sold {s_item_obj.name} for {s_item_obj.price}$", category='success')
            else:
                flash(f'Something went wrong with selling {p_item_obj.name}', category='danger')

        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        current_user_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html',
                               items=items,
                               purchase_form=purchase_form,
                               sell_form=sell_form,
                               current_user_items=current_user_items)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data,
                              )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash('Account created successfully! You are logged in.', category='success')
        return redirect(url_for('market_page'))

    if form.errors != {}:
        for err_msg in form.errors:
            flash(f'There was an error with creating a user, invalid {err_msg} field: {form.errors[err_msg][0]}',
                  category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash('Success! You are logged in.', category='success')
            return redirect(url_for('market_page'))
        flash('Username and password did not match. Please, try again.', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return render_template('home.html')
