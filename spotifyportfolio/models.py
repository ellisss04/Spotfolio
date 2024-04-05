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
    # favorite_songs = db.relationship('Song', secondary='favorite_song', backref='users')
    # favorite_albums = db.relationship('Album', secondary='favorite_album', backref='users')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    artist = db.Column(db.String(100))


# class Album(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     artist = db.Column(db.String(100))
#
#
# # Intermediate table for many-to-many relationship between User and Song
# favorite_song = db.Table('favorite_song',
#                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#                          db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
#                          )
#
# # Intermediate table for many-to-many relationship between User and Album
# favorite_album = db.Table('favorite_album',
#                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#                           db.Column('album_id', db.Integer, db.ForeignKey('album.id'))
#                           )
#
#
# class Playlist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     # Add more playlist-related fields as needed
#
#
# class FavoritePlaylist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
#     # Add more fields as needed
#
#     # Define relationships
#     user = db.relationship('User', backref=db.backref('favorite_playlists', lazy=True))
#     playlist = db.relationship('Playlist', backref=db.backref('favorited_by', lazy=True))
