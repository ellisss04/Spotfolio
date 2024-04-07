# from spotifyportfolio import db, app
# from spotifyportfolio.models import Song, FavoriteSong
#
#
# with app.app_context():
#     delete1 = Song.query.get(1)
#     delete2 = Song.query.get(2)
#     db.session.delete(delete1)
#     db.session.delete(delete2)
#     db.session.commit()
#
# with app.app_context():
#     delete1 = FavoriteSong.query.filter_by(user_id=1, song_id='7jEfLF7XLMzBNj9w1PBmCq').first()
#     delete2 = FavoriteSong.query.get(user_id=1, song_id='4qYlBtzkmby4r1N7etPnUv').first()
#     db.session.delete(delete1)
#     db.session.delete(delete2)
#     db.session.commit()

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set your Spotify API credentials
client_id = '1e6b51e8331d48d083c9d1830e1e4050'
client_secret = 'a7ea44994e984d889997fd4f5960a780'

# Authenticate Spotipy using client credentials flow
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_artist_id(artist_name):
    try:
        # Search for the artist by name
        results = sp.search(q='artist:' + artist_name, type='artist', limit=1)

        # Log the entire search results for debugging
        logging.debug("Search results: %s", results)

        # Get the first artist from the search results
        artists = results['artists']['items']

        if artists:
            # Return the ID of the first artist found
            artist_id = artists[0]['id']
            return artist_id
        else:
            # If no artists were found, log a warning
            logging.warning("No artists found for query: %s", artist_name)
            return None
    except Exception as e:
        # Log any errors that occur during the search
        logging.error("Error occurred during artist search: %s", e)
        return None


# Example usage:
artist_name = 'Taylor Swift'
artist_id = get_artist_id(artist_name)
if artist_id:
    print("Artist ID:", artist_id)
else:
    print("Artist ID not found")

