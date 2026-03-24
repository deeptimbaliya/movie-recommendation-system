from dotenv import load_dotenv
import gdown
import streamlit as st
import pickle
import pandas as pd
import requests
import os
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Background */
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

/* Subtitle */
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
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    background-color: #ff1e2d;
}

/* Movie Card */
.movie-card {
    background: linear-gradient(145deg, #1c1f26, #111318);
    padding: 12px;
    border-radius: 14px;
    text-align: center;
    transition: all 0.4s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}

/* Poster */
.movie-card img {
    border-radius: 10px;
    width: 100%;
    height: 300px;
    object-fit: cover;
    transition: transform 0.4s ease;
}

/* Title */
.movie-title {
    color: white;
    margin-top: 10px;
    font-size: 15px;
    transition: color 0.3s ease;
}

/* Hover Effects */
.movie-card:hover {
    transform: translateY(-10px) scale(1.05);
    box-shadow: 0 10px 30px rgba(229,9,20,0.6);
}

.movie-card:hover img {
    transform: scale(1.08);
}

.movie-card:hover .movie-title {
    color: #E50914;
}

/* Fade-in animation */
.fade-in {
    animation: fadeIn 0.8s ease-in-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Section title glow */
.section-title {
    text-align:center;
    color:white;
    text-shadow: 0px 0px 10px #E50914;
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
        if os.path.exists("movies.pkl"):
            os.remove("movies.pkl")
        if os.path.exists("similarity.pkl"):
            os.remove("similarity.pkl")

        if movies_url:
            gdown.download(movies_url, "movies.pkl", quiet=True)
        if similarity_url:
            gdown.download(similarity_url, "similarity.pkl", quiet=True)

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

        st.markdown(
            '<h2 class="section-title">🎯 Recommended Movies</h2>',
            unsafe_allow_html=True
        )

        cols = st.columns(6)

        for idx, movie in enumerate(recommendations):
            col = cols[idx % 6]

            with col:
                time.sleep(0.08)  # stagger animation

                poster = movie["poster"] or DEFAULT_POSTER

                st.markdown(
                    f"""
                    <div class="movie-card fade-in">
                        <img src="{poster}" />
                        <div class="movie-title">{movie["title"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )