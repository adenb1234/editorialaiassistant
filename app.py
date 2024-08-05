import streamlit as st
import anthropic
import json

# Initialize the Anthropic client
client = anthropic.Client(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Load your editorials
def load_editorials():
    try:
        with open('/path/to/your/editorials.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading editorials: {e}")
        return []

editorials = load_editorials()

st.title("Washington Post Editorial Board AI Bot")

if not editorials:
    st.warning("No editorials loaded. Please check your data source.")
else:
    user_question = st.text_input("Ask a question about Washington Post editorials:")

    if user_question:
        # Prepare the context (you might want to limit this to relevant editorials)
        context = "\n\n".join([f"Title: {ed['title']}\nContent: {ed['full_text']}" for ed in editorials[:5]])

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
