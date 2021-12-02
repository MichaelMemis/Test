from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EmptyForm, RestaurantForm, DishForm
from app.models import User, Dish, Restaurant, Review, Vote, RestaurantToDish
import requests

@app.route('/')
@app.route('/index')
@login_required
def index():
    #request.get(https://api.documenu.com/v2/restaurant/4072702673999819?key=c1da345dda931faa152f8c3b15e54250)
    return render_template('index.html', title='Home')


@app.route('/newrestaurant', methods=['GET', 'POST'])
@login_required
def newrestaurant():
    form = RestaurantForm()
    dish = {}
    if form.validate_on_submit():
        flash('New Restaurant added: {}'.format(form.name.data))
        restaurant = Restaurant(name=form.name.data, rating=form.rating.data,
                                description=form.description.data, location=form.location.data)
        db.session.add(restaurant)
        db.session.commit()
        return render_template('index.html')
    return render_template('newrestaurant.html', title='Add a Restaurant', form=form)


@app.route('/restaurants')
def restaurants():
    restaurantlist = Restaurant.query.all()
    return render_template('restaurants.html', title='Restaurants', restaurants=restaurantlist)


@app.route('/restaurant/<name>')
@login_required
def restaurant(name):
    restaurant = Restaurant.query.filter_by(name=name).first()
    if restaurant is None:
        flash("Restaurant does not exist")
        return render_template("index.html")
    else:
        return render_template("restaurant.html", title=restaurant.name, restaurant=restaurant)


@app.route('/newdish', methods=['GET', 'POST'])
@login_required
def newdish():
    form = DishForm()
    form.restaurantID.choices = [(r.id, r.name) for r in Restaurant.query.all()]
    dish = {}
    if form.validate_on_submit():
        flash('New Dish added: {}'.format(form.name.data))
        dish = Dish(name=form.name.data, rating=form.rating.data,
                    description=form.description.data, venueID=form.venueID.data)
        db.session.add(dish)
        db.session.commit()
        return render_template('index.html')
    return render_template('newdish.html', title='Add a Dish', form=form)


@app.route('/dishes')
def dishes():
    dishlist = Dish.query.all()
    return render_template('dishes.html', title='Dishes', dishes=dishlist)


@app.route('/dish/<name>')
@login_required
def dish(name):
    dish = Dish.query.filter_by(name=name).first()
    if dish is None:
        flash("Dish does not exist")
        return render_template("index.html")
    else:
        return render_template("dish.html", title=dish.name, dish=dish)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    reviews = user.posts.order_by(Review.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=reviews.next_num) \
        if reviews.has_next else None
    prev_url = url_for('user', username=user.username, page=reviews.prev_num) \
        if reviews.has_prev else None
    form = EmptyForm()
    return render_template('user.html', title=user.username, user=user, posts=reviews.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/populate_db', methods=['GET', 'POST'])
def populate_db():
    clear_db()
    r1 = Restaurant(name='Ithaca Beer Co.',
                    rating=5,
                    description='This craft brewery features a taproom with '
                                'industrial decor & offers tours on the weekends.',
                    location='122 Ithaca Beer Dr, Ithaca, NY')
    r2 = Restaurant(name='Texas Roadhouse',
                    rating=3,
                    description='Lively chain steakhouse serving American fare '
                                'with a Southwestern spin amid Texas-themed decor.',
                    location='719-25 S Meadow St, Ithaca, NY')
    r3 = Restaurant(name='Old Mexico',
                    rating=4,
                    description='Vibrant, casual Mexican joint serving classic '
                                'standards from fajitas to tequila drinks & beers.',
                    location='357 Elmira Rd, Ithaca, NY')
    db.session.add_all([r1, r2, r3])

    d1 = Dish(name='Pepperoni Pizza',
              rating=4,
              price=16.00,
              description='Garlic tomato sauce, fresh mozzarella, garlic-parm blend, pepperoni')
    d2 = Dish(name='Smokehouse Burger',
              rating=5,
              price=12.50,
              description='Sautéed mushrooms, onions, BBQ sauce, lettuce, tomato and onion '
                          'with American and jack cheeses served on a Texas-sized bun with steak '
                          'fries and a pickle spear')
    d3 = Dish(name='Fajitas Texanas',
              rating=4,
              price=14.75,
              description='A tempting combination of chicken, '
                          'steak, and shrimp served piping hot.')
    db.session.add_all([d1, d2, d3])

    t1 = RestaurantToDish(restaurantID=1, dishID=1)
    t2 = RestaurantToDish(restaurantID=2, dishID=2)
    t3 = RestaurantToDish(restaurantID=3, dishID=3)
    db.session.add_all([t1, t2, t3])
    db.session.commit()

    return render_template('index.html')


def clear_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())


@app.route('/_restaurant_autocomplete')
def restaurant_autocomplete():
    q = request.args.get('q', "")

    matches = list()
    for a in restaurant:
        if a.lower().startswith(q.lower()):
            matches.append(a)

    return jsonify(result=matches)


@app.route('/_dish_autocomplete')
def dish_autocomplete():
    q = request.args.get('q', "")

    matches = list()
    for a in dish:
        if a.lower().startswith(q.lower()):
            matches.append(a)

    return jsonify(result=matches)
