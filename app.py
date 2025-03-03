import streamlit as st
import pickle
import pandas as pd
import requests
import base64
from dotenv import load_dotenv
import os
import gzip


# Convert image to base64
def get_base64(image_file):
    """Convert local image to base64 encoding."""
    with open(image_file, "rb") as img_file:
        base64_bytes = base64.b64encode(img_file.read()).decode()
    return base64_bytes

# Set background function
def set_bg(image_file):
    base64_image = get_base64(image_file)
    bg_image_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0, 0.7)),  
                    url("data:image/jpg;base64,{base64_image}");
        background-size: cover;  
        background-position: center;  
        background-repeat: no-repeat;  
        background-attachment: fixed;  
        font-family: 'Poppins', sans-serif;
    }}

    h1 {{
        color: #ffffff;  
        text-align: center;
        font-weight: 600;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        font-size: 38px;
    }}

    h2 {{
        text-align: center;
        font-size: 32px;
        font-weight: 600;
        color: #ffcc00;
    }}

    p, label {{
        font-size: 20px !important;
        font-weight: 400;
        color: white !important;
    }}

    /* Fixing Selectbox, Button, and Input */
    .stSelectbox div div {{
        font-size: 18px !important;
        font-weight: 400 !important;
        color: white !important;
    }}

    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input {{
        font-size: 18px !important;
        padding: 8px !important;
    }}

    .stButton>button {{
        background-color: #ff5722 !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 12px 25px !important;
        border-radius: 10px !important;
        transition: all 0.3s ease-in-out;
        border: none;
    }}

    .stButton>button:hover {{
        background-color: #e64a19 !important;
        transform: scale(1.05);
    }}
    </style>
    """
    st.markdown(bg_image_css, unsafe_allow_html=True)

# Call the function with your image file
set_bg("banner.jpg")  # Ensure banner.jpg exists in the correct directory


# OMDb API Key (replace with your key)
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")


def fetch_movie_details(movie_title):
    """Fetch movie details (poster & IMDb rating) from OMDb API."""

    if not OMDB_API_KEY:
        print("Error: OMDB API Key is missing! Set it in an environment variable.")
        return "https://via.placeholder.com/500x750?text=No+Image", "N/A"

    movie_title = movie_title.replace(" ", "+")  # Replace spaces with '+'
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)  # Set timeout to avoid long waits
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        if data.get("Response") == "True":  # Check if API response is valid
            poster_url = data.get("Poster")
            rating = data.get("imdbRating", "N/A")

            # Handle missing poster URLs (sometimes OMDb returns "N/A")
            if not poster_url or poster_url == "N/A":
                poster_url = "https://via.placeholder.com/500x750?text=No+Image"

            return poster_url, rating
        else:
            print(f"OMDb API Error: {data.get('Error')}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return "https://via.placeholder.com/500x750?text=No+Image", "N/A"


# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]]['title']
        poster, rating = fetch_movie_details(title)  # Get poster & rating from OMDb
        recommended_movies.append((title, rating))
        recommended_posters.append(poster)

    # Sort by IMDb rating
    recommended_movies.sort(key=lambda x: x[1], reverse=True)

    return recommended_movies, recommended_posters


# Load Data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))



# Streamlit UI
st.title('🎬 Movie Recommender System')
st.subheader("Get movie recommendations based on your favorite film! 🍿")

# Dropdown for selecting a movie
selected_movie_name = st.selectbox(
    "Select a Movie:", movies['title'].values
)

# Recommendation Button
if st.button("Recommend"):
    recommendations, posters = recommend(selected_movie_name)

    st.markdown("### Recommended Movies 🎥")

    cols = st.columns(4)  # Display 4 movies per row
    for idx, (movie, rating) in enumerate(recommendations):
        with cols[idx % 4]:  # Arrange movies in a row
            st.image(posters[idx], width=150)
            st.markdown(f"**{movie}**  \n⭐ {rating}/10", unsafe_allow_html=True)
