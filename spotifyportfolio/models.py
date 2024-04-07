from spotifyportfolio import db
from flask_login import UserMixin
from spotifyportfolio import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_setup = db.Column(db.Boolean, default=False, nullable=False)

    # favorite_songs = db.relationship('Song', secondary='favorite_song', backref='users')
    # favorite_albums = db.relationship('Album', secondary='favorite_album', backref='users')
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    song_id = db.Column(db.String(40))


class FavoriteSong(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.String(40))
    # Other artist-related fields such as popularity, followers, etc.


class FavoriteArtist(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100))
    album_id = db.Column(db.String(100))
    # artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    # release_date = db.Column(db.Date)
    # genre = db.Column(db.String(50))
    # Other album-related fields such as popularity, track count, etc.


class FavoriteAlbum(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), primary_key=True)
