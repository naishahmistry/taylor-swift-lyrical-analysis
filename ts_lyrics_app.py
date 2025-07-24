"""
Naisha Mistry and Olivia Yeung
DS3500
Homework 6

File: ts_lyrics_app.py
Description: use LyricsLab and GeniusAPI to retrieve Taylor Swift albums and conduct lyrical analysis.
"""
from genius_api import GeniusAPI
from lyrics_lab import LyricsLab

ACCESS_TOKEN = "dtTzXw9vQf4u9SxPHOgShUt4UmaFPXTdmBislSkqDCrVjg3PU_tA2tRtg0qkIv9j"

def main():
    genius = GeniusAPI(ACCESS_TOKEN)

    # Save lyrics from select Taylor Swift albums
    artist = "Taylor Swift"
    albums = ["1989", "Folklore", "Lover", "Midnights", "Red", "Reputation", "Taylor Swift",
              "The Tortured Poets Department"]

    for album in albums:
        genius.save_album_lyrics(artist, album)

    # Initialize nlp library
    L = LyricsLab()

    album_jsons = ["lyrics/1989_lyrics.json", "lyrics/Folklore_lyrics.json", "lyrics/Lover_lyrics.json",
                   "lyrics/Midnights_lyrics.json", "lyrics/Red_lyrics.json", "lyrics/Reputation_lyrics.json",
                   "lyrics/Taylor_Swift_lyrics.json", "lyrics/The_Tortured_Poets_Department_lyrics.json"]

    for i in range(len(album_jsons)):
        L.load_stop_words("stopfile.csv", album_jsons[i])
        L.load_text(album_jsons[i], label=albums[i], parser = L.json_parser)

    common = ["love", "heart", "dreams", "night", "time", "red", "golden", "black", "white", "want", "need", "life",
              "eyes", "name", "stay", "revenge", "promise", "cry", "kiss", "tears", "screaming", "die", "dead", "wish"]

    # Visualizations
    L.wordcount_sankey(word_list=common)
    L.sentiment_analysis(album_jsons, albums)
    L.heatmap(album_jsons, albums, artist)


if __name__ == "__main__":
    main()