from spotifyportfolio import db, app
from spotifyportfolio.models import Song, FavoriteSong


with app.app_context():
    delete1 = Song.query.get(1)
    delete2 = Song.query.get(2)
    db.session.delete(delete1)
    db.session.delete(delete2)
    db.session.commit()

with app.app_context():
    delete1 = FavoriteSong.query.filter_by(user_id=1, song_id='7jEfLF7XLMzBNj9w1PBmCq').first()
    delete2 = FavoriteSong.query.get(user_id=1, song_id='4qYlBtzkmby4r1N7etPnUv').first()
    db.session.delete(delete1)
    db.session.delete(delete2)
    db.session.commit()


