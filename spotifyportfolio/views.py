from spotifyportfolio import app, bcrypt
from spotifyportfolio import sp, sp_oauth

from flask import render_template, redirect, url_for, request, session, jsonify, flash
from spotifyportfolio import cache_handler
from spotifyportfolio.forms import RegistrationForm, LoginForm
from spotifyportfolio.models import User, Song, FavoriteSong,  FavoriteAlbum, Album, Artist, FavoriteArtist

from flask_login import login_user, current_user

from spotifyportfolio import db


@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    if current_user.is_authenticated:
        return redirect(url_for('get_info'))
    else:
        # Handle the case where the user is not authenticated
        return render_template('home.html')


@app.route('/get_info')
def get_info():
    favorite_songs = FavoriteSong.query.filter_by(user_id=current_user.id).all()
    song_ids = [favorite.song_id for favorite in favorite_songs]

    favorite_albums = FavoriteAlbum.query.filter_by(user_id=current_user.id, is_favourite=True).all()
    album_ids = [favorite.album_id for favorite in favorite_albums]

    favorite_artists = FavoriteArtist.query.filter_by(user_id=current_user.id).all()
    artist_ids = [favorite.artist_id for favorite in favorite_artists]

    favorite_selected = FavoriteAlbum.query.filter_by(user_id=current_user.id, is_favourite=False).all()

    return render_template('home.html', song_ids=song_ids, album_ids=album_ids, artist_ids=artist_ids,
                           favorite_selected=favorite_selected)


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

    if current_user.is_authenticated:
        if current_user.is_setup:
            # User is already set up, return JSON response for confirmation
            return redirect(url_for('setup_confirm'))
        else:
            # User is not set up yet, proceed with setup
            return render_template('setup.html')
    else:
        return redirect(url_for('login'))


@app.route('/setup_confirm')
def setup_confirm():
    try:
        favourite_songs = FavoriteSong.query.filter_by(user_id=current_user.id).all()
        for favourite_song in favourite_songs:
            db.session.delete(favourite_song)

        favourite_albums = FavoriteAlbum.query.filter_by(user_id=current_user.id, is_favourite=True).all()
        for favourite_album in favourite_albums:
            db.session.delete(favourite_album)

        favourite_artists = FavoriteArtist.query.filter_by(user_id=current_user.id).all()
        for favourite_artist in favourite_artists:
            db.session.delete(favourite_artist)

        current_user.is_setup = False
        db.session.commit()
        return render_template('setup.html')
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while attempting to remove your preferences")
    return redirect(url_for('home'))


@app.route('/search_track')
def search_track():
    query = request.args.get('query')
    if query:
        results = sp.search(q=query, type='track', limit=5)
        search_results = []
        for track in results['tracks']['items']:
            album_name = track['album']['name']
            album_images = [image['url'] for image in track['album']['images']]
            track_data = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'id': track['id'],
                'album': {
                    'name': album_name,
                    'images': album_images
                }
            }
            search_results.append(track_data)
        return jsonify(search_results)
    else:
        return jsonify([])


@app.route('/search_album')
def search_album():
    query = request.args.get('query')
    limit = request.args.get('limit')
    if query:
        results = sp.search(q=query, type='album', limit=limit)
        search_results = []
        for album in results['albums']['items']:
            album_details = sp.album(album['id'])
            image_url = album_details['images'][0]['url'] if album_details['images'] else None
            search_results.append({'name': album['name'], 'artist': album['artists'][0]['name'], 'id': album['id'],
                                   'image_url': image_url})
        return jsonify(search_results)
    else:
        return jsonify([])


@app.route('/search_artist')
def search_artist():
    query = request.args.get('query')

    if query:
        results = sp.search(q=query, type='artist', limit=5)

        search_results = [{'artist': artist['name'],  'id': artist['id']} for
                          artist in
                          results['artists']['items']]
        return jsonify(search_results)
    else:
        return jsonify([])


@app.route('/favourite_song', methods=['POST'])
def favorite_song():
    # Get the song's information from the POST request
    song_info = {
        'song_name': request.form['song_name'],
        'artist_name': request.form['artist_name'],
        'song_id': request.form['song_id'],

    }
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        song_id = song_info['song_id']

        user = User.query.get(int(user_id))
        song = Song.query.filter_by(song_id=song_id).first()

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
        'album_img': request.form['album_img']
    }

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        album_id = album_info['album_id']

        user = User.query.get(int(user_id))
        album = Album.query.filter_by(album_id=album_id).first()

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        if album is None:
            add_album = Album(name=album_info['album_name'], artist_name=album_info['album_artist'],
                              album_id=album_id, image_url=album_info['album_img'])
            db.session.add(add_album)
            db.session.commit()

        session['album_id'] = album_id

    return jsonify(album_info)


@app.route('/favourite_artist', methods=['POST'])
def favorite_artist():
    # Get the artist's information from the POST request
    artist_info = {
        'artist_name': request.form['artist_name'],
        'artist_id': request.form['artist_id'],
    }

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        artist_id = artist_info['artist_id']

        user = User.query.get(int(user_id))
        artist = Artist.query.filter_by(artist_id=artist_id).first()

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        if artist is None:
            add_artist = Artist(name=artist_info['artist_name'], artist_id=artist_info['artist_id'])
            db.session.add(add_artist)
            db.session.commit()

        session['artist_id'] = artist_id

    return jsonify(artist_info)


@app.route('/submit_setup', methods=['POST'])
def submit_setup():
    if request.method == 'POST':

        user_id = current_user.get_id()
        album_id = session['album_id']
        song_id = session['song_id']
        artist_id = session['artist_id']

        current_user.is_setup = True

        favorite_song = FavoriteSong(user_id=user_id, song_id=song_id, is_favourite=True)
        db.session.add(favorite_song)
        favorite_album = FavoriteAlbum(user_id=user_id, album_id=album_id, is_favourite=True)
        db.session.add(favorite_album)
        favorite_artist = FavoriteArtist(user_id=user_id, artist_id=artist_id, is_favourite=True)
        db.session.add(favorite_artist)

        db.session.commit()
    else:
        session.clear()
    return redirect(url_for('home'))


@app.route('/save_album', methods=['POST'])
def save_album():
    if request.method == 'POST':
        album_info = {
            'album_name': request.form['album_name'],
            'album_artist': request.form['album_artist'],
            'album_id': request.form['album_id'],
            'album_img': request.form['album_img']
        }
        user_id = current_user.get_id()
        album_exists = Album.query.filter_by(album_id=album_info['album_id']).first()

        if not album_exists:
            new_album = Album(name=album_info['album_name'], artist_name=album_info['album_artist'],
                              album_id=album_info['album_id'], image_url=album_info['album_img'])
            db.session.add(new_album)

        new_album_exists = FavoriteAlbum.query.filter_by(user_id=user_id, album_id=album_info['album_id'],
                                                         is_favourite=False)
        if not new_album_exists:
            new_favorite_album = FavoriteAlbum(user_id=user_id, album_id=album_info['album_id'], is_favourite=False)
            db.session.add(new_favorite_album)
        else:
            db.session.commit()
            return jsonify({'message': 'Album already selected'})

        db.session.commit()
        return jsonify({'message': 'Album saved successfully'}), 200
    else:
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/delete_album', methods=['POST'])
def delete_album():
    if request.method == 'POST':
        image_url = request.form['image_url']
        if image_url is None:
            return jsonify({'error': 'Method not allowed'}), 405


        album = Album.query.filter_by(image_url=image_url).first()
        if album:
            deleted_album = FavoriteAlbum.query.filter_by(album_id=album.album_id, user_id=current_user.id).first()
            db.session.delete(deleted_album)
            db.session.commit()
            return jsonify({'message': 'Album deleted successfully'}), 200
        else:
            return jsonify({'error': 'Method not allowed'}), 405

    else:
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
