import streamlit as st
import pandas as pd
import random
import json
import os

movies_df = pd.read_csv("movies.csv")
movies_df.dropna(subset=["Director", "Star1", "IMDB_Rating", "Released_Year", "Gross"], inplace=True)

st.set_page_config(page_title="🎬 Movie Facts & Trivia Game", layout="wide")

# --- SESSION STATE INIT ---
for key, default in {
    "name": "",
    "question_index": 0,
    "score": 0,
    "questions": [],
    "answer_selected": None,
    "leaderboard": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- LEADERBOARD PERSISTENCE ---
LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return {}

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

# Loading leaderboard at the start
if "leaderboard" not in st.session_state or not st.session_state.leaderboard:
    st.session_state.leaderboard = load_leaderboard()

# --- QUESTION GENERATION LOGIC ---
def get_options(column, correct_answer):
    candidates = movies_df[column].dropna().unique().tolist()
    candidates = [val for val in candidates if val != correct_answer]
    options = random.sample(candidates, min(3, len(candidates))) + [correct_answer]
    random.shuffle(options)
    return options

def question_director(movie):
    return {
        "type": "director",
        "movie": movie,
        "question": f"🎬 Who directed the movie **{movie['Series_Title']}**?",
        "answer": movie["Director"],
        "options": get_options("Director", movie["Director"])
    }

def question_actor(movie):
    return {
        "type": "actor",
        "movie": movie,
        "question": f"👤 Who played the main role in **{movie['Series_Title']}**?",
        "answer": movie["Star1"],
        "options": get_options("Star1", movie["Star1"])
    }

def question_rating(movie):
    return {
        "type": "rating",
        "movie": movie,
        "question": f"⭐ What is the IMDB rating of **{movie['Series_Title']}**?",
        "answer": movie["IMDB_Rating"],
        "options": get_options("IMDB_Rating", movie["IMDB_Rating"])
    }

def question_year(movie):
    return {
        "type": "year",
        "movie": movie,
        "question": f"📅 In what year was **{movie['Series_Title']}** released?",
        "answer": movie["Released_Year"],
        "options": get_options("Released_Year", movie["Released_Year"])
    }

def question_gross(movie):
    return {
        "type": "gross",
        "movie": movie,
        "question": f"💰 What are the gross earnings of **{movie['Series_Title']}**?",
        "answer": movie["Gross"],
        "options": get_options("Gross", movie["Gross"])
    }

def generate_questions(n=10):
    return [random.choice([question_director, question_actor, question_rating, question_year, question_gross])(movies_df.sample().iloc[0]) for _ in range(n)]

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Player Info")
    if st.button("New Player"):
        for key in ["name", "question_index", "score", "questions", "answer_selected"]:
            st.session_state[key] = "" if key == "name" else 0 if key in ["question_index", "score"] else []
        st.session_state.questions = generate_questions(10)

    if st.session_state.name == "":
        st.session_state.name = st.text_input("Enter your name to start the game:")

    if st.session_state.name and st.session_state.question_index == 0 and not st.session_state.questions:
        st.session_state.questions = generate_questions(10)

    st.markdown(f"**Current Player:** {st.session_state.name}")
    st.markdown("---")
    st.header("🏆 Leaderboard")
    if st.session_state.leaderboard:
        top_players = sorted(st.session_state.leaderboard.items(), key=lambda x: -x[1])[:10]
        for player, score in top_players:
            st.markdown(f"**{player}**: {score} pts")
    else:
        st.caption("No players yet. Be the first to play!")

    if st.button("🔄 Refresh Leaderboard"):
        st.session_state.leaderboard = {}
        save_leaderboard(st.session_state.leaderboard)
        st.rerun()

# --- UI ---
if not st.session_state.name:
    st.warning("Please enter your name in the sidebar to begin.")
    st.stop()

# Centered game layout
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.question_index < 10:
            q = st.session_state.questions[st.session_state.question_index]

            st.image(q["movie"]["Poster_Link"], width=250)
            st.markdown(f"### ❓ Question {st.session_state.question_index + 1}/10")
            st.markdown(q["question"])

            selected_option = st.radio("Choose your answer:", q["options"], index=None, key=f"q_{st.session_state.question_index}")

            if st.button("🎯 Submit Answer"):
                if selected_option is not None:
                    st.session_state.answer_selected = selected_option
                    if selected_option == q["answer"]:
                        st.session_state.score += 1
                st.session_state.question_index += 1
                st.rerun()

        else:
            st.balloons()
            st.markdown(f"## 🎉 Game Over, **{st.session_state.name}**!")
            st.markdown(f"### Your Final Score: 🎯 **{st.session_state.score} / 10**")

            # Update leaderboard
            st.session_state.leaderboard[st.session_state.name] = st.session_state.score
            save_leaderboard(st.session_state.leaderboard)

            col_play, col_new = st.columns(2)
            with col_play:
                if st.button("🔁 Play Again"):
                    for key in ["question_index", "score", "questions", "answer_selected"]:
                        st.session_state[key] = 0 if key in ["question_index", "score"] else []
                    st.session_state.questions = generate_questions(10)
                    st.rerun()
            with col_new:
                if st.button("🙋 New Player"):
                    for key in ["name", "question_index", "score", "questions", "answer_selected"]:
                        st.session_state[key] = "" if key == "name" else 0 if key in ["question_index", "score"] else []
                    st.session_state.questions = generate_questions(10)
                    st.rerun()
