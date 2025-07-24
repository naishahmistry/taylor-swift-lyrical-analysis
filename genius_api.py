"""
Naisha Mistry and Olivia Yeung
DS3500
Homework 6

File: genius_api.py
Description: library to collect songs from albums by artist
Functions sourced from Github page referenced below.
"""
from bs4 import BeautifulSoup
import json
import lyricsgenius
from lyricsgenius import Genius
import requests
from pathlib import Path

class GeniusAPI:
    def __init__(self, access_token):
        """
        Initialize the GeniusAPI object with the provided access token.
        """
        self.genius = Genius(access_token)
        self.genius.remove_section_headers = True

    def clean_song_title(self, song_title):
        """
        Clean up song titles to remove unnecessary text and special characters.
        """
        if "Ft" in song_title:
            song_title = song_title.split("(Ft")[0].strip()
        else:
            song_title = song_title.replace("Lyrics", "").strip()
        return song_title.replace("/", "-")

    def get_album_songs(self, artist_name, album_name):
        """
        Fetch all song titles from an album on Genius.com. Returns cleaned list of song titles.
        """
        artist = artist_name.replace(" ", "-")
        album = album_name.replace(" ", "-")

        response = requests.get(f"https://genius.com/albums/{artist}/{album}", timeout=360)
        if response.status_code != 200:
            print(f"Failed to fetch album: {album_name}")
            return []

        html = BeautifulSoup(response.text, "html.parser")
        song_tags = html.find_all("h3", class_="chart_row-content-title")
        song_titles = [self.clean_song_title(tag.text) for tag in song_tags]
        return song_titles

    def save_album_lyrics(self, artist_name, album_name):
        """
        Save all song lyrics from an album to a JSON file. Returns path to JSON file.
        """
        song_titles = self.get_album_songs(artist_name, album_name)
        if not song_titles:
            return None

        songs_lyrics = []
        for song_title in song_titles:
            song = self.genius.search_song(song_title, artist_name)
            if song:
                songs_lyrics.append({"title": song_title, "lyrics": song.lyrics})

        # Syntax help from ChatGPT to save as JSON since website function saves as txt
        filename = f"{album_name.replace(' ', '_')}_lyrics.json"
        Path("lyrics").mkdir(parents=True, exist_ok=True)
        filepath = Path("lyrics") / filename

        with open(filepath, "w", encoding="utf-8") as json_file:
            json.dump(songs_lyrics, json_file, ensure_ascii=False, indent=4)

        return str(filepath)

# References
# OpenAI. (2024). ChatGPT (May 13 version) [Large language model]. https://chat.openai.com
# https://melaniewalsh.github.io/Intro-Cultural-Analytics/04-Data-Collection/08-Collect-Genius-Lyrics.html
