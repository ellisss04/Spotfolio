from spotifyportfolio import app
from spotifyportfolio.models import User, Playlist, FavoritePlaylist
from spotifyportfolio import sp, sp_oauth

from flask import render_template, redirect, url_for, request, session, jsonify
from spotifyportfolio import cache_handler

@app.route('/')
def home():
    # set up this as method
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return render_template('index.html')


@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('base_page'))


@app.route('/base_page')
def base_page():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    session_fav_song = session.get('favorite_song')
    session_fav_album = session.get('favorite_album')

    if session_fav_song and session_fav_album:
        return render_template('profile.html', favourite_song=session_fav_song, favourite_album=session_fav_album)
    else:
        return render_template('index.html')


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
    session['song_chosen'] = True

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


def user_playlists():
    playlists = sp.current_user_playlists()
    return render_template('user_playlists.html', playlists=playlists['items'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
