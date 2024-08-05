import streamlit as st
import anthropic
import json
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize the Anthropic client
client = anthropic.Client(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Load editorials (only once when the app starts)
@st.cache_data
def load_editorials_from_github():
    github_raw_url = "https://raw.githubusercontent.com/adenb1234/editorialaiassistant/main/editorials.json"
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error loading editorials from GitHub: {e}")
        return []

editorials = load_editorials_from_github()

# Initialize sentence transformer model
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Create embeddings for all editorials (only once)
@st.cache_data
def create_embeddings(editorials):
    return model.encode([ed['title'] + " " + ed['full_text'] for ed in editorials])

editorial_embeddings = create_embeddings(editorials)

# Function to find most relevant editorials
def find_relevant_editorials(query, top_k=5):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, editorial_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [editorials[i] for i in top_indices]

st.title("Washington Post Editorial Board AI Bot")

st.write(f"Loaded {len(editorials)} editorials.")
user_question = st.text_input("Ask a question about Washington Post editorials:")

if user_question:
    relevant_editorials = find_relevant_editorials(user_question)
    context = "\n\n".join([f"Title: {ed['title']}\nContent: {ed['full_text']}" for ed in relevant_editorials])

    message = f"Context:\n{context}\n\nQuestion: {user_question}\n\nPlease answer the question based on the provided editorial content."

    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.5,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        st.write("AI Response:")
        st.write(response.content)
    except Exception as e:
        st.error(f"Error calling Claude API: {e}")

st.sidebar.write("This AI bot is based on Washington Post editorials and powered by Claude AI.")
