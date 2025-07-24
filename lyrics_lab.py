"""
Naisha Mistry and Olivia Yeung
DS3500
Homework 6

File: lyrics_lab.py
Description: nlp library to process album lyrics and create visualizations
(word frequency sankey, sentiment analysis bar chart, similarity heatmap between albums)
"""
from collections import defaultdict, Counter
import random as rnd
import json
import pandas as pd
import sankey as sk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

class LyricsLab:

    def __init__(self):
        """ Constructor: datakey --> (filelabel --> datavalue) """
        self.data = defaultdict(dict)

    def default_parser(self, filename):
        """ Parse a standard text file and produce extract data results in the form of a dictionary. """
        results = {
            "wordcount": Counter("Shake it off".split(" ")),
            "numwords" : rnd.randrange(10, 50)
        }
        return results

    def json_parser(self, filename):
        """
        Load json of album songs and lyrics and calculate the word frequency and number of words.
        """
        f = open(filename)
        raw = json.load(f)

        word_count = Counter()
        total_words = 0

        for song in raw:
            lyrics = song["lyrics"]
            words = lyrics.split()
            word_count.update(words)
            total_words += len(words)

        results = {"word_count": word_count, "num_words": total_words}
        return results

    def load_text(self, filename, label="", parser=None):
        """ Register a document with the framework.
            Extract and store data to be used later by the visualizations
        """
        if parser is None:
            results = self.default_parser(filename)
        else:
            results = parser(filename)

        if label is None:
            label = filename

        for k, v in results.items():
            self.data[k][label] = v

        return results

    def load_stop_words(self, stopfile, lyricfile):
        """
        Process words in file of stopwords and filter them out of the lyrics json.
        """
        df = pd.read_csv(stopfile, header=None)
        stopwords = df[0].to_list()
        punc = [",", ".", "?", "-", "!", "(", ")"]

        f = open(lyricfile)
        lyrics_data = json.load(f)

        for song in lyrics_data:
            lyrics = song["lyrics"].lower().split()
            # ChatGPT helped with syntax for stripping punctuation
            lyrics = [word.strip("".join(punc)) for word in lyrics]
            filtered_lyrics = [word for word in lyrics if word not in stopwords]
            song["lyrics"] = " ".join(filtered_lyrics)

        # ChatGPT helped with syntax for overwriting
        with open(lyricfile, "w", encoding="utf-8") as file:
            json.dump(lyrics_data, file, ensure_ascii=False, indent=4)

        return lyrics_data

    def wordcount_sankey(self, word_list=None, k=None):
        """
        Create a sankey diagram with albums as source nodes, top words as target nodes, and frequency as weights.
        Filter top words using k most common or user-given word list.
        """
        sankey_data = []

        for album, word_count in self.data["word_count"].items():
            if k:
                top_words = word_count.most_common(k)
            else:
                # ChatGPT helped with syntax for getting word count
                top_words = [(word, word_count.get(word, 0)) for word in word_list]

            for word, count in top_words:
                sankey_data.append({"Album": album, "Word": word, "Count": count})

        sankey_df = pd.DataFrame(sankey_data)
        fig = sk.make_sankey(sankey_df, src="Album", targ="Word", vals="Count", width=1200, height=800)
        fig.show()

    def sentiment_analysis(self, album_jsons, album_titles):
        """
        Perform sentiment analysis for each song per album and plot subplots by album.
        """
        for i in range(len(album_jsons)):
            lyric_file = album_jsons[i]
            album_title = album_titles[i]

            f = open(lyric_file)
            lyrics_data = json.load(f)

            song_titles = []
            polarities = []
            for song in lyrics_data:
                song_titles.append(song["title"])
                polarities.append(TextBlob(song["lyrics"]).sentiment.polarity)

            plt.bar(song_titles, polarities)
            plt.title(f"Polarity Scores for {album_title}")
            plt.ylabel("Polarity")
            plt.xlabel("Songs")
            plt.xticks(rotation=45, ha="right")
            plt.show()


    def heatmap(self, album_jsons, album_titles, artist):
        """
        Create a heatmap that calculates the correlation score between all albums based on lyrics.
        """
        lyrics_lst= []
        for album_json in album_jsons:
            f = open(album_json)
            lyrics_data = json.load(f)
            lyrics = " ".join([song["lyrics"] for song in lyrics_data])
            lyrics_lst.append(lyrics)

        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(lyrics_lst)

        cosine_sim = cosine_similarity(matrix, matrix)

        sns.heatmap(cosine_sim, annot=True, xticklabels=album_titles, yticklabels=album_titles)
        plt.title(f"{artist} Album Similarity Heatmap")
        plt.xticks(rotation=45, ha="right")
        plt.yticks()
        plt.show()


# References
# https://textblob.readthedocs.io/en/dev/quickstart.html
# https://gist.github.com/sebleier/554280
# https://www.geeksforgeeks.org/find-k-frequent-words-data-set-python/
# OpenAI. (2024). ChatGPT (May 13 version) [Large language model]. https://chat.openai.com
# https://memgraph.com/blog/cosine-similarity-python-scikit-learn

