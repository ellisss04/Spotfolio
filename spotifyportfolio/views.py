
from spotifyportfolio import app, bcrypt
from spotifyportfolio import sp, sp_oauth

from flask import render_template, redirect, url_for, request, session, jsonify, flash
from spotifyportfolio import cache_handler
from spotifyportfolio.forms import RegistrationForm, LoginForm
from spotifyportfolio.models import User

from flask_login import login_user, current_user, logout_user, login_required

from spotifyportfolio import db


@app.route('/')
def home():
    # set up this as method
    # if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    #     auth_url = sp_oauth.get_authorize_url()
    #     return redirect(auth_url)
    return render_template('home.html')


@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('setup'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/setup')
def setup():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    return render_template('setup.html')


@app.route('/search_track')
def search_track():
    query = request.args.get('query')
    print("Received query:", query)  # Add this line for debugging
    if query:
        results = sp.search(q=query, type='track', limit=5)
        search_results = [{'name': track['name'], 'artist': track['artists'][0]['name'], 'id': track['id']} for
                          track in
                          results['tracks']['items']]
        return jsonify(search_results)
    else:
        return jsonify([])


@app.route('/search_album')
def search_album():
    query = request.args.get('query')
    if query:
        results = sp.search(q=query, type='album', limit=5)
        search_results = [{'name': album['name'], 'artist': album['artists'][0]['name'], 'id': album['id']} for
                          album in
                          results['albums']['items']]
        return jsonify(search_results)
    else:
        return jsonify([])


@app.route('/favourite_song', methods=['POST'])
def favorite_song():
    # Get the song's information from the POST request
    song_info = {
        'song_name': request.form['song_name'],
        'artist_name': request.form['artist_name'],
        'song_id': request.form['song_id']
    }

    session['favorite_song'] = song_info

    return jsonify(song_info)


@app.route('/favourite_album', methods=['POST'])
def favorite_album():
    # Get the song's information from the POST request
    album_info = {
        'album_name': request.form['album_name'],
        'album_artist': request.form['album_artist'],
        'album_id': request.form['album_id'],
    }

    session['favorite_album'] = album_info

    return jsonify(album_info)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
