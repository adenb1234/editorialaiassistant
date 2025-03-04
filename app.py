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
    def replace_source_url(match):
        before_source = match.group(1)
        url = match.group(2)
        return f'{before_source} [Article Link]({url})'

    # Replace "Source:" followed by URL, changing it to "Article Link" hyperlink
    text = re.sub(r'(.*?)Source:\s*(https?://\S+)', replace_source_url, text, flags=re.DOTALL)
    
    # Remove any remaining "Source:" without a URL
    text = re.sub(r'\bSource:\s*', '', text)
    
    return text
# The rest of your code remains the same

# Load editorials
editorials = load_editorials_from_github()

# Load and display Washington Post logo
logo_url = "https://raw.githubusercontent.com/adenb1234/editorialaiassistant/main/wapo_logo.png"
logo = Image.open(requests.get(logo_url, stream=True).raw)
st.image(logo, width=300)

st.title("Editorial Board AI Assistant")

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
