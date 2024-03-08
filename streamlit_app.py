import sqlite3
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import streamlit as st

# List of Coldplay songs
coldplay_songs = ["Yellow", "Fix You", "Clocks", "Viva La Vida", "Paradise", "Amsterdam", 
                  "Adventure Of A Lifetime", "Every Teardrop Is A Waterfall", "A Sky Full Of Stars", 
                  "Magic", "Speed Of Sound", "Hymn For The Weekend", "Trouble", "In My Place", 
                  "Charlie Brown", "Everglow", "Talk", "Princess Of China", "Shiver", "Lost!", 
                  "Violet Hill", "Midnight", "Sparks", "Spies", "Orphans"]

# Step 1: Collect lyrics using an online API
def get_lyrics(song_title):
    api_endpoint = f"https://api.lyrics.ovh/v1/Coldplay/{song_title}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        data = response.json()
        if 'lyrics' in data:
            return data['lyrics']
    return None

# Step 2: Create SQLite database and store song details
def create_database():
    conn = sqlite3.connect('coldplay_songs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs
                 (title TEXT PRIMARY KEY, lyrics TEXT, sentiment TEXT)''')
    conn.commit()
    conn.close()

def insert_song(title, lyrics, sentiment):
    conn = sqlite3.connect('coldplay_songs.db')
    c = conn.cursor()
    existing_entry = c.execute("SELECT * FROM songs WHERE title=?", (title,)).fetchone()
    if not existing_entry:
        c.execute("INSERT INTO songs VALUES (?, ?, ?)", (title, lyrics, sentiment))
        conn.commit()
    conn.close()

# Step 3: Function to perform sentiment analysis using VADER
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    if sentiment_scores['compound'] >= 0.05:
        return "Happy"
    elif sentiment_scores['compound'] <= -0.05:
        return "Sad"
    else:
        return "Neutral"

# Step 4: Function to count happy and sad songs from the provided list
def count_sentiments():
    conn = sqlite3.connect('coldplay_songs.db')
    c = conn.cursor()
    happy_count = sum(1 for song in coldplay_songs if c.execute("SELECT COUNT(*) FROM songs WHERE title=? AND sentiment='Happy'", (song,)).fetchone()[0] > 0)
    sad_count = sum(1 for song in coldplay_songs if c.execute("SELECT COUNT(*) FROM songs WHERE title=? AND sentiment='Sad'", (song,)).fetchone()[0] > 0)
    conn.close()
    return happy_count, sad_count

# Step 5: Streamlit web application
def main():
    st.set_page_config(page_title="Coldplay Song Sentiment Analyzer", page_icon=":musical_note:")
    st.title("Coldplay Sentiment Analyzer")
    st.markdown("---")
    st.markdown("### Analyze a Coldplay Song")

    # Display background image
    st.markdown(
        """
        <style>
        .reportview-container {
            background: url("https://www.pixelstalk.net/wp-content/uploads/2016/07/Music-Note-Desktop-Photo.jpg");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display music logo
    logo = st.image("https://www.pixelstalk.net/wp-content/uploads/2016/07/Music-Note-HD-Wallpaper.jpg", width=400)

    create_database()
    for song_title in coldplay_songs:
        lyrics = get_lyrics(song_title)
        if lyrics:
            sentiment = analyze_sentiment(lyrics)
            insert_song(song_title, lyrics, sentiment)

    song_title = st.text_input("Enter a Coldplay song title:")
    analyze_button = st.button("Analyze")
    if analyze_button:
        if not song_title:
            st.error("Please enter a song title.")
        else:
            song_title = song_title.strip().title()  # Capitalize first letter of each word
            lyrics = get_lyrics(song_title)
            if lyrics:
                sentiment = analyze_sentiment(lyrics)
                insert_song(song_title, lyrics, sentiment)
                love_count = lyrics.lower().count("love")
                hate_count = lyrics.lower().count("hate")
                st.success("Sentiment analyzed successfully!")
                st.markdown("---")
                st.markdown(f"**Sentiment of the song:** {sentiment}")
                st.markdown(f"**Count of the word 'love':** {love_count}")
                st.markdown(f"**Count of the word 'hate':** {hate_count}")
                total_count = len(coldplay_songs)
                happy_count, sad_count = count_sentiments()
                st.markdown("---")
                st.markdown(f"**Total count of songs:** {total_count}")
                st.markdown(f"**Number of songs with Happy mood:** {happy_count}")
                st.markdown(f"**Number of songs with Sad mood:** {sad_count}")
            else:
                st.error("Lyrics not found for the provided song title.")

    display_lyrics = st.button("Display Lyrics")
    if display_lyrics:
        if song_title:
            lyrics = get_lyrics(song_title)
            if lyrics:
                st.markdown("---")
                st.markdown("### Lyrics")
                st.write(lyrics)
                st.success("Lyrics displayed successfully!")
            else:
                st.error("Lyrics not found for the provided song title.")
        else:
            st.error("Please enter a song title to display lyrics.")

if __name__ == "__main__":
    main()
