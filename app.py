from dotenv import load_dotenv
import gdown
import streamlit as st
import pickle
import pandas as pd
import requests
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}

.main {
    background-color: #0e1117;
}

/* Title */
h1 {
    text-align: center;
    color: #E50914;
    font-weight: bold;
}

/* Text */
p {
    text-align: center;
    color: #cfcfcf;
}

/* Button */
.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}

/* Card Hover */
.card:hover {
    transform: scale(1.05);
    transition: 0.3s;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API KEY ----------------
Omdb_api_key = st.secrets.get("OMDB_API_KEY", "")

# ---------------- LOAD FILES ----------------
@st.cache_resource
def load_files():
    movies_url = st.secrets.get("MOVIES_DATA_URL", "")
    similarity_url = st.secrets.get("SIMILARITY_DATA_URL", "")

    try:
        # Remove old files
        if os.path.exists("movies.pkl"):
            os.remove("movies.pkl")
        if os.path.exists("similarity.pkl"):
            os.remove("similarity.pkl")

        # Download
        if movies_url:
            gdown.download(movies_url, "movies.pkl", quiet=True)
        if similarity_url:
            gdown.download(similarity_url, "similarity.pkl", quiet=True)

        # Load safely
        if os.path.exists("movies.pkl"):
            with open("movies.pkl", "rb") as f:
                movies = pickle.load(f)
        else:
            movies = pd.DataFrame(columns=["title"])

        if os.path.exists("similarity.pkl"):
            with open("similarity.pkl", "rb") as f:
                similarity = pickle.load(f)
        else:
            similarity = None

        return movies, similarity

    except Exception as e:
        st.error(f"Error loading files: {e}")
        return pd.DataFrame(columns=["title"]), None

movies, similarity_count = load_files()

# ---------------- DEFAULT POSTER ----------------
DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

# ---------------- FETCH POSTER ----------------
def fetch_poster(title):
    try:
        if not Omdb_api_key:
            return DEFAULT_POSTER

        url = f"https://www.omdbapi.com/?t={title}&apikey={Omdb_api_key}"
        data = requests.get(url).json()

        if data.get('Poster') and data['Poster'] != "N/A":
            return data['Poster']

        return DEFAULT_POSTER

    except:
        return DEFAULT_POSTER

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie):
    try:
        if movies is None or similarity_count is None:
            return []

        if movie not in movies['title'].values:
            return []

        index = movies[movies['title'] == movie].index[0]
        distances = similarity_count[index]

        movies_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )

        recommendations = []

        for i in movies_list[1:7]:
            title = movies.iloc[i[0]].title
            poster = fetch_poster(title)

            recommendations.append({
                "title": title,
                "poster": poster
            })

        return recommendations

    except Exception as e:
        st.error(f"Recommendation error: {e}")
        return []

# ---------------- UI ----------------

# Center Title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("🎬 Movie Recommender")
    st.write("Get movie recommendations instantly!")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- MOVIE LIST SAFETY ----------------
if movies is not None and 'title' in movies:
    movie_list = movies['title'].values
else:
    movie_list = []

# Handle empty movie list
if len(movie_list) == 0:
    st.warning("⚠️ Movie list not available. Please try again later.")
    st.stop()

# ---------------- INPUT ----------------
selected_movie = st.selectbox("Select a movie", movie_list)

# ---------------- BUTTON ----------------
if st.button("Recommend"):
    with st.spinner("Finding best movies for you... 🍿"):
        recommendations = recommend(selected_movie)

    if not recommendations:
        st.warning("😕 No recommendations found.")
    else:
        st.markdown("---")
        st.subheader("🎯 Recommended Movies")

        cols = st.columns(6)

        for idx, movie in enumerate(recommendations):
            col = cols[idx % 6]

            with col:
                poster = movie["poster"] or DEFAULT_POSTER

                st.image(poster, use_container_width=True)
                st.markdown(
                    f"<p style='text-align:center; color:white; font-size:16px; margin-top:5px;'>{movie['title']}</p>",
                    unsafe_allow_html=True
                )