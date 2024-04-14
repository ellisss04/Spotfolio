from sqlalchemy import PrimaryKeyConstraint

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

    def get_id(self):
        return str(self.id)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    song_id = db.Column(db.String(40))


class FavoriteSong(db.Model):
    __tablename__ = 'favorite_song'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
    is_favourite = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'song_id'),
        {},
    )


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.String(40))


class FavoriteArtist(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    is_favourite = db.Column(db.Boolean, default=False, nullable=False)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100))
    album_id = db.Column(db.String(100))
    image_url = db.Column(db.String(255))


class FavoriteAlbum(db.Model):
    __tablename__ = 'favorite_album'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), primary_key=True)
    is_favourite = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'album_id'),
        {},
    )
