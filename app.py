import streamlit as st
import time
from openai import OpenAI, AuthenticationError, RateLimitError, APIError

# --- App Title ---
st.title("🧠 Smart Resume Checker")
st.write("Upload your resume text and get instant feedback powered by GPT!")

# --- Securely load API key ---
# Make sure your Streamlit Secrets contain:
# OPENAI_API_KEY = "sk-your-api-key"
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("❌ API key not found! Please add OPENAI_API_KEY to your Streamlit secrets.")
    st.stop()

# --- User Input ---
resume_text = st.text_area("📄 Paste your resume text here:", height=200)

# --- Define a safe GPT call with retry logic ---
def get_resume_feedback(prompt, retries=5):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # You can change to gpt-3.5-turbo for lower cost
                messages=[
                    {"role": "system", "content": "You are a professional HR resume evaluator."},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content

        except RateLimitError:
            wait = 2 ** attempt
            st.warning(f"⚠️ Rate limit hit. Retrying in {wait} seconds...")
            time.sleep(wait)

        except AuthenticationError:
            st.error("❌ Authentication failed. Check your OpenAI API key.")
            st.stop()

        except APIError as e:
            st.error(f"⚠️ API error: {e}. Retrying...")
            time.sleep(2)

    st.error("❌ Failed after multiple retries due to rate limits or API issues.")
    return None

# --- When user clicks the button ---
if st.button("🔍 Analyze Resume"):
    if not resume_text.strip():
        st.warning("Please paste your resume text first.")
    else:
        with st.spinner("Analyzing your resume..."):
            prompt = f"Please evaluate the following resume and give suggestions for improvement:\n\n{resume_text}"
            feedback = get_resume_feedback(prompt)

            if feedback:
                st.success("✅ Analysis Complete!")
                st.subheader("🧩 Feedback:")
                st.write(feedback)

