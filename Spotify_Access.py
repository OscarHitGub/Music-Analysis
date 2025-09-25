# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 14:43:08 2025

@author: oscar
"""

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import numpy as np
import string

# Hiermee krijg je access tot de spotify web API
CLIENT_ID = 'b87f7c4564b94a8482eb06c3b1c643fb'
CLIENT_SECRET = 'e9266877b0d64a73a9011127afb7a706'
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Nu maken we een lijst van artiesten gebaseerd op hun eerste letter
artist_list = []
for letter in string.ascii_lowercase:  # 'a' t/m 'z'
    results = sp.search(q=letter, type="artist", limit=25, offset=0)
    
    # Zet al deze data in de lijst
    for artist in results['artists']['items']:
        artist_list.append({
            "Name": artist['name'],
            "Popularity": artist['popularity'],
            "Followers": artist['followers']['total'],
            "Genres": artist['genres'],
            "Spotify_ID": artist['id'],
            "Spotify_URL": artist['external_urls']['spotify']
            })

# Lijst omzetten tot dataframe
df_artists = pd.DataFrame(artist_list)

# Voeg de gemiddelde lengte van de top nummers van een artiest toe als kolom
df_artists['Average_top_song_length_in_min'] = [
    round(np.mean([track['duration_ms'] for track in sp.artist_top_tracks(art_id)['tracks']]) / 60000, 2)
    for art_id in df_artists['Spotify_ID']
]

col = df_artists.pop("Average_top_song_length_in_min")
df = df_artists.insert(4, col.name, col)

# Drop de duplicates
Artist_Data = df_artists.drop_duplicates(subset="Name")

# Exporteer de data zodat deze code niet steeds opnieuw gerunt hoeft te worden
Artist_Data.to_csv('Artist_Data.csv', index=False)

