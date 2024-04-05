from spotifyportfolio import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Add more user-related fields as needed


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # Add more playlist-related fields as needed


class FavoritePlaylist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    # Add more fields as needed

    # Define relationships
    user = db.relationship('User', backref=db.backref('favorite_playlists', lazy=True))
    playlist = db.relationship('Playlist', backref=db.backref('favorited_by', lazy=True))
