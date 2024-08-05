import streamlit as st
import anthropic
import json
import requests
import re

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

# Function to find most relevant editorials
def find_relevant_editorials(query, top_k=5):
    query_words = set(re.findall(r'\w+', query.lower()))
    scores = []
    for i, ed in enumerate(editorials):
        text = ed['title'] + " " + ed['full_text']
        text_words = set(re.findall(r'\w+', text.lower()))
        score = len(query_words.intersection(text_words))
        scores.append((score, i))
    
    scores.sort(reverse=True)
    return [editorials[i] for _, i in scores[:top_k]]

# Load editorials
editorials = load_editorials_from_github()

# Streamlit app
st.title("Washington Post Editorial Board AI Bot")
st.write(f"Loaded {len(editorials)} editorials.")

# User input
user_question = st.text_input("Ask a question about Washington Post editorials:")

# Process user input
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
        
        if response.content:
            for content in response.content:
                if hasattr(content, 'text'):
                    st.write(content.text)
        else:
            st.write("No content in the response.")
        
    except Exception as e:
        st.error(f"Error processing AI response: {str(e)}")
        
st.sidebar.write("This AI bot is based on Washington Post editorials and powered by Claude AI.")
