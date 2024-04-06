import flask_login

from spotifyportfolio import app, bcrypt
from spotifyportfolio import sp, sp_oauth

from flask import render_template, redirect, url_for, request, session, jsonify, flash
from spotifyportfolio import cache_handler
from spotifyportfolio.forms import RegistrationForm, LoginForm
from spotifyportfolio.models import User, Song, FavoriteSong, load_user, FavoriteAlbum, Album

from flask_login import login_user, current_user, logout_user, login_required

from spotifyportfolio import db


@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    if current_user.is_authenticated:
        favorite_songs = FavoriteSong.query.filter_by(user_id=current_user.id).all()
        song_ids = [favorite.song_id for favorite in favorite_songs]

        favorite_albums = FavoriteAlbum.query.filter_by(user_id=current_user.id).all()
        album_ids = [favorite.album_id for favorite in favorite_albums]
        return render_template('home.html', song_ids=song_ids, album_ids=album_ids)
    else:
        # Handle the case where the user is not authenticated
        return render_template('home.html')


@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('home'))


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

    is_setup = current_user.is_setup
    if current_user.is_authenticated and not is_setup:
        return render_template('setup.html')
    else:
        return redirect(url_for('login'))


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
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        song_id = song_info['song_id']

        user = User.query.get(int(user_id))
        song = Song.query.get(song_id)

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        if song is None:
            add_song = Song(name=song_info['song_name'], artist=song_info['artist_name'], song_id=song_id)
            db.session.add(add_song)
            db.session.commit()

        session['song_id'] = song_id

    return jsonify(song_info)


@app.route('/favourite_album', methods=['POST'])
def favorite_album():
    # Get the song's information from the POST request
    album_info = {
        'album_name': request.form['album_name'],
        'album_artist': request.form['album_artist'],
        'album_id': request.form['album_id'],
    }

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        album_id = album_info['album_id']

        user = User.query.get(int(user_id))
        album = Album.query.get(album_id)

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        if album is None:
            add_album = Album(name=album_info['album_name'], artist_name=album_info['album_artist'], album_id=album_id)
            db.session.add(add_album)
            db.session.commit()

        session['album_id'] = album_id

    return jsonify(album_info)


@app.route('/submit_setup', methods=['POST'])
def submit_setup():
    if request.method == 'POST':

        user_id = current_user.get_id()
        album_id = session['album_id']
        song_id = session['song_id']

        current_user.is_setup = True

        favorite_song = FavoriteSong(user_id=user_id, song_id=song_id)
        db.session.add(favorite_song)
        favorite_album = FavoriteAlbum(user_id=user_id, album_id=album_id)
        db.session.add(favorite_album)
        db.session.commit()
    else:
        session.clear()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
