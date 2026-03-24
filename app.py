from dotenv import load_dotenv
import gdown
import streamlit as st
import pickle
import pandas as pd
import requests
import os

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
/* Background */
body {
    background-color: #0e1117;
}

/* Main container */
.main {
    background-color: #0e1117;
}

/* Title */
h1 {
    text-align: center;
    color: #E50914;
    font-weight: bold;
}

/* Subtext */
p {
    text-align: center;
    color: #cfcfcf;
}

/* Button styling */
.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}

/* Selectbox */
.stSelectbox {
    margin-bottom: 20px;
}
            
div:hover {
    transform: scale(1.05);
    transition: 0.3s;
</style>
""", unsafe_allow_html=True)

Omdb_api_key = st.secrets["OMDB_API_KEY"]

@st.cache_resource
def load_files():
    movies_url = st.secrets["MOVIES_DATA_URL"]
    similarity_url = st.secrets["SIMILARITY_DATA_URL"]

    try:
        # Remove old corrupted files
        if os.path.exists("movies.pkl"):
            os.remove("movies.pkl")
        if os.path.exists("similarity.pkl"):
            os.remove("similarity.pkl")

        # Correct download
        gdown.download(movies_url, "movies.pkl", quiet=False)
        gdown.download(similarity_url, "similarity.pkl", quiet=False)

        # Load
        with open("movies.pkl", "rb") as f:
            movies = pickle.load(f)

        with open("similarity.pkl", "rb") as f:
            similarity = pickle.load(f)

        return movies, similarity

    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None, None

movies, similarity_count = load_files()

DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

def fetch_poster(title):
    url = f"https://www.omdbapi.com/?t={title}&apikey={Omdb_api_key}"
    data = requests.get(url).json()

    if data.get('Poster') and data['Poster'] != "N/A":
        return data['Poster']
    return DEFAULT_POSTER

# recommendation function
def recommend(movie):
    try:
        print(f"Selected movie: {movie}")
        index = movies[movies['title'] == movie].index[0]

        # get similarity scores
        distances = similarity_count[index]

        movies_list = sorted(
            list(enumerate(distances)), reverse=True, key=lambda x: x[1])

        recommendations = []

        for i in movies_list[1:7]:  # top 6 recommendations
            title = movies.iloc[i[0]].title
            poster = fetch_poster(title)
            recommendations.append({
                "title": title,
                "poster": poster
            })
        return recommendations
    except IndexError:
        st.error("Movie not found. Please select a valid movie from the dropdown.")
        return []

# UI Design
st.set_page_config(page_title="Movie Recommender", layout="centered")

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.title("🎬 Movie Recommender")
    st.write("Get movie recommendations instantly!")

# dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", movie_list, index=0)
st.markdown("<br>", unsafe_allow_html=True)
# button
if st.button("Recommend"):
    with st.spinner("Finding best movies for you... 🍿"):
        recommendations = recommend(selected_movie)
    st.markdown("---")
    st.subheader("🎯 Recommended Movies")

    cols = st.columns(3)

    for idx, movie in enumerate(recommendations):
        col = cols[idx % 3]

        with col:
            poster = movie["poster"]

            # Fix missing poster
            if not poster or poster == "N/A":
                poster = DEFAULT_POSTER

            # ALWAYS render
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    background-color:#1c1f26;
                    padding:10px;
                    border-radius:12px;
                    transition:0.3s;
                ">
                    <img src="{poster}" width="100%" 
                    style="border-radius:10px;" />
                    
                    <h4 style="color:white; margin-top:10px;">
                        {movie["title"]}
                    </h4>
                </div>
                """,
                unsafe_allow_html=True
            )