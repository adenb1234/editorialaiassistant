import streamlit as st
import anthropic
import json
import requests
import re
from PIL import Image

# Set page config at the very beginning
st.set_page_config(page_title="Washington Post Editorial AI", layout="wide")

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
def find_relevant_editorials(query, top_k=7):
    query_words = set(re.findall(r'\w+', query.lower()))
    scores = []
    for i, ed in enumerate(editorials):
        text = ed['title'] + " " + ed['full_text']
        text_words = set(re.findall(r'\w+', text.lower()))
        score = len(query_words.intersection(text_words))
        scores.append((score, i))
    
    scores.sort(reverse=True)
    return [editorials[i] for _, i in scores[:top_k]]

# Function to convert URLs to hyperlinks
def convert_urls_to_hyperlinks(text):
    url_pattern = r'(Source:?\s*)?(\()?https?://\S+(\))?'
    
    def replace_url(match):
        full_match = match.group(0)
        url = re.search(r'(https?://\S+)', full_match).group(1)
        
        preceding_text = text[:match.start()].strip()
        preceding_words = preceding_text.split()[-5:]
        link_text = ' '.join(preceding_words) if preceding_words else url
        
        return f'[{link_text}]({url})'
    
    return re.sub(url_pattern, replace_url, text)

# Load editorials
editorials = load_editorials_from_github()

# Load and display Washington Post logo
logo_url = "https://raw.githubusercontent.com/adenb1234/editorialaiassistant/main/wapo_logo.png"
logo = Image.open(requests.get(logo_url, stream=True).raw)
st.image(logo, width=300)

st.title("Washington Post Editorial AI Assistant")

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: #f0f0f0;
    }
    .stButton > button {
        background-color: #1a1a1a;
        color: white;
    }
    .stMarkdown {
        font-family: 'Georgia', serif;
    }
    </style>
    """, unsafe_allow_html=True)

# User input
user_question = st.text_input("Ask a question about Washington Post editorials:")

# Process user input
if user_question:
    relevant_editorials = find_relevant_editorials(user_question)
    context = "\n\n".join([f"Title: {ed['title']}\nContent: {ed['full_text']}\nURL: {ed['url']}" for ed in relevant_editorials])
    
    prompt = f"""You are a helpful assistant that provides information about editorials from the Washington Post. 
    Be concise and use bullet points whenever possible. Whenever you reference an editorial, provide the full URL for it, prefaced with 'Source:'.

    Context:\n{context}\n\nQuestion: {user_question}\n\nPlease answer the question based on the provided editorial content, including source URLs for each point."""
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.5,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        st.subheader("AI Response:")
        
        if response.content:
            for content in response.content:
                if hasattr(content, 'text'):
                    hyperlinked_text = convert_urls_to_hyperlinks(content.text)
                    st.markdown(hyperlinked_text)
        else:
            st.write("No content in the response.")
        
    except Exception as e:
        st.error(f"Error processing AI response: {str(e)}")

st.sidebar.markdown("### About")
st.sidebar.write("This AI assistant is based on Washington Post editorials and powered by Claude AI.")
