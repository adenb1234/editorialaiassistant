import streamlit as st
import anthropic
import json
import requests
import re
import ast

# ... (previous code remains the same) ...

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
        
        # Parse the response content
        parsed_content = ast.literal_eval(response.content)
        if parsed_content and isinstance(parsed_content, list) and parsed_content[0]:
            # Extract the text from the TextBlock
            text_block = parsed_content[0]
            if isinstance(text_block, str) and text_block.startswith("TextBlock"):
                # Extract the text content from the TextBlock string
                text_content = re.search(r'text="(.*?)"', text_block, re.DOTALL)
                if text_content:
                    st.write(text_content.group(1))
                else:
                    st.write("Unable to extract text content from the response.")
            else:
                st.write(text_block)
        else:
            st.write("Unexpected response format.")
    except Exception as e:
        st.error(f"Error processing AI response: {e}")

st.sidebar.write("This AI bot is based on Washington Post editorials and powered by Claude AI.")
