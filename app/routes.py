from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EmptyForm
from app.models import User, Dish, Restaurant, Review, Vote


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/restaurant/<restaurant>')
@login_required
def index():
    return render_template('restaurant.html')

@app.route('/dish/<dish>')
@login_required
def index():
    return render_template('dish.html')


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
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@app.route('/populate_db', methods=['GET', 'POST'])
def populate_db():
    clear_db()
    a1 = Artist(name='The Gun Poets',
                hometown='Ithaca',
                description='Ithaca Hip Hop Band')
    a2 = Artist(name='Stone Cold Miracle',
                hometown='Fall Creek',
                description='Funky Soul')
    a3 = Artist(name='The New Team',
                hometown='San Francisco',
                description='They play new-age music. It sux.')
    a4 = Artist(name='The Beatles',
                hometown='England',
                description='Old time classics.')
    a5 = Artist(name='Sleepy Hallow',
                hometown='Jamaica',
                description='Party in the sky like its 2055.')
    db.session.add_all([a1, a2, a3, a4, a5])

    v1 = Venue(name='Madison Square Garden', address='4 Pennsylvania Plaza, New York, NY', capacity=21000)
    v2 = Venue(name='The Greek Theatre', address='2700 N Vermont Ave, Los Angeles, CA', capacity=6000)
    v3 = Venue(name='The Dock', address='415 Old Taughannock Blvd, Ithaca, NY', capacity=250)
    db.session.add_all([v1, v2, v3])

    e1 = Event(name='Coachella', date=datetime(2022, 6, 12), venueID=3)
    e2 = Event(name='Governors Ball', date=datetime(2021, 12, 21), venueID=3)
    e3 = Event(name='Lalapalozza', date=datetime(2055, 2, 2), venueID=3)
    e4 = Event(name='Woodstock', date=datetime(2023, 7, 30), venueID=2)
    e5 = Event(name='Riot Fest', date=datetime(2024, 11, 30), venueID=1)
    e6 = Event(name='Octoberfest', date=datetime(2022, 10, 31), venueID=2)
    e7 = Event(name='Pitchfork Music Festival', date=datetime(2024, 1, 17), venueID=1)
    db.session.add_all([e1, e2, e3, e4, e5, e6, e7])

    t1 = ArtistToEvent(artistID=2, eventID=6)
    t2 = ArtistToEvent(artistID=2, eventID=2)
    t3 = ArtistToEvent(artistID=3, eventID=4)
    t4 = ArtistToEvent(artistID=1, eventID=3)
    t5 = ArtistToEvent(artistID=4, eventID=5)
    db.session.add_all([t1, t2, t3, t4, t5])
    db.session.commit()

    return render_template('index.html')

