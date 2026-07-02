import streamlit as st
import joblib
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from scipy.sparse import hstack, csr_matrix

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# --- Setup ---
stop_words = set(stopwords.words('english'))
urgency_words = {'until', 'now', 'immediately', 'urgent', 'free', 'won', 'winner', 'claim', 'limited', 'expires'}
stop_words = stop_words - urgency_words
lemmatizer = WordNetLemmatizer()

# --- Lazy model loading ---
@st.cache_resource
def load_model():
    rf = joblib.load('models/rf_model.pkl')
    tfidf = joblib.load('models/tfidf_vectorizer.pkl')
    return rf, tfidf

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

def extract_features_single(message):
    features = {
        'exclamation_count': message.count('!'),
        'question_count': message.count('?'),
        'link_count': len(re.findall(r'http\S+|www\.\S+', message)),
        'caps_count': sum(1 for c in message if c.isupper()),
        'digit_count': sum(1 for c in message if c.isdigit()),
        'message_length': len(message),
        'dollar_count': message.count('$'),
        'urgency_count': sum(1 for w in message.lower().split() if w in urgency_words)
    }
    return csr_matrix(list(features.values()))

def get_flagged_words(message):
    flagged = []
    for word in urgency_words:
        if word in message.lower():
            flagged.append(word)
    if re.findall(r'http\S+|www\.\S+', message):
        flagged.append('link detected')
    if message.count('!') > 2:
        flagged.append(f"{message.count('!')} exclamation marks")
    if sum(1 for c in message if c.isupper()) > 10:
        flagged.append('excessive caps')
    return flagged

# --- UI ---
st.set_page_config(page_title="PhishGuard", page_icon="🎣", layout="centered")
st.title("🎣 PhishGuard")
st.subheader("Phishing Email & SMS Detector")
st.write("Paste any email or text message below to check if it's a phishing attempt.")

user_input = st.text_area("📩 Paste your message here:", height=200)

if st.button("🔍 Analyze Message"):
    if not user_input.strip():
        st.warning("Please paste a message first.")
    else:
        with st.spinner("Loading model..."):
            rf_model, tfidf = load_model()

        cleaned = clean_text(user_input)
        tfidf_vector = tfidf.transform([cleaned])
        extra = extract_features_single(user_input)
        combined_vector = hstack([tfidf_vector, extra])

        prediction = rf_model.predict(combined_vector)[0]
        confidence = rf_model.predict_proba(combined_vector)[0]

        if prediction == 1:
            st.error(f"🚨 PHISHING DETECTED — {confidence[1]*100:.1f}% confidence")
        else:
            st.success(f"✅ LEGITIMATE — {confidence[0]*100:.1f}% confidence")

        flagged = get_flagged_words(user_input)
        if flagged:
            st.warning("⚠️ Suspicious signals detected: " + ", ".join(flagged))

        st.write("### Confidence Breakdown")
        st.progress(int(confidence[1] * 100))
        st.caption(f"Phishing probability: {confidence[1]*100:.1f}%")