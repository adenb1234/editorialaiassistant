import streamlit as st
import anthropic
import json
import requests

# Initialize the Anthropic client
client = anthropic.Client(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Function to load editorials from GitHub
def load_editorials_from_github():
    github_raw_url = "https://raw.githubusercontent.com/yourusername/yourrepository/main/editorials.json"
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error loading editorials from GitHub: {e}")
        return []

# Load editorials
editorials = load_editorials_from_github()

st.title("Washington Post Editorial Board AI Bot")

if not editorials:
    st.warning("No editorials loaded. Please check your data source.")
else:
    st.write(f"Loaded {len(editorials)} editorials.")
    user_question = st.text_input("Ask a question about Washington Post editorials:")

    if user_question:
        # Prepare the context (using all available editorials)
        context = "\n\n".join([f"Title: {ed['title']}\nContent: {ed['full_text']}" for ed in editorials[:5]])  # Limiting to first 5 for brevity

        # Prepare the message for Claude
        message = f"Context:\n{context}\n\nQuestion: {user_question}\n\nPlease answer the question based on the provided editorial content."

        try:
            # Make the API call
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": message}
                ]
            )

            # Display the response
            st.write("AI Response:")
            st.write(response.content)
        except Exception as e:
            st.error(f"Error calling Claude API: {e}")

st.sidebar.write("This AI bot is based on Washington Post editorials and powered by Claude AI.")
