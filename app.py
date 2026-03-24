import gdown
import streamlit as st
import pickle
import pandas as pd
import requests
import os

st.markdown("""
    <style>
    body {
        background-color: #0e1117;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_files():
    # File IDs
    movies_id = "1YbzfZN1gc8RlqbyPXNYIl4q35DAOFO9U"
    similarity_id = "1yLt6h_Cy3wvHTj7Ir5YCORoDt0RyaPDD"

    # Download only if not exists
    if not os.path.exists("movies.pkl"):
        gdown.download(movies_id, output="movies.pkl", quiet=False)

    if not os.path.exists("similarity.pkl"):
        gdown.download(similarity_id, output="similarity.pkl", quiet=False)

    # Load files
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    return movies, similarity

movies, similarity_count = load_files()

DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

def fetch_poster(title):
    # API call to fetch poster
    url = f"https://www.omdbapi.com/?t={title}&apikey=8edc8f55"
    data = requests.get(url).json()
    return data['Poster'] if 'Poster' in data else "https://via.placeholder.com/150"

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

st.title("🎬 Movie Recommender System")

st.write("Get movie recommendations instantly!")

# dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", movie_list)

# button
if st.button("Recommend"):
    recommendations = recommend(selected_movie)

    st.subheader("Recommended Movies:")

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
                <div style="text-align: center; margin-bottom:20px;">
                    <img src="{poster}" width="200" height="300"
                    style="border-radius:10px; object-fit:cover;" />
                    <p style="font-size:14px; margin-top:10px;">
                        {movie["title"]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )