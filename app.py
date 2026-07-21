import streamlit as st
import joblib
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from scipy.sparse import hstack, csr_matrix
from PIL import Image
import pytesseract

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

# --- Signal explanations: (flag_name, one-line explanation) ---
SIGNAL_EXPLANATIONS = {
    'urgency': "Urgency language pressures you to act fast, before you have time to think it through.",
    'link': "Links can lead to fake login pages designed to steal your credentials.",
    'exclamation': "Excessive exclamation marks are a classic tactic to create false excitement or panic.",
    'caps': "Excessive capitalization is used to grab attention and simulate alarm or importance.",
    'money': "Dollar signs or mentions of money often signal a financial scam or fraud attempt.",
}

def get_flagged_signals(message):
    """Returns list of (signal_key, detail_text) tuples for triggered signals."""
    flagged = []
    found_urgency = [w for w in urgency_words if w in message.lower()]
    if found_urgency:
        flagged.append(('urgency', f"Urgency words found: {', '.join(found_urgency)}"))
    links = re.findall(r'http\S+|www\.\S+', message)
    if links:
        flagged.append(('link', f"{len(links)} link(s) detected"))
    if message.count('!') > 2:
        flagged.append(('exclamation', f"{message.count('!')} exclamation marks"))
    if sum(1 for c in message if c.isupper()) > 10:
        flagged.append(('caps', "Excessive capital letters"))
    if message.count('$') > 0:
        flagged.append(('money', f"{message.count('$')} dollar sign(s) found"))
    return flagged

def extract_text_from_image(image):
    """Run OCR on an uploaded image and return extracted text."""
    return pytesseract.image_to_string(image)

def run_prediction(message):
    """Runs the full pipeline and displays results. Shared by text and image input paths."""
    with st.spinner("Loading model..."):
        rf_model, tfidf = load_model()

    cleaned = clean_text(message)
    tfidf_vector = tfidf.transform([cleaned])
    extra = extract_features_single(message)
    combined_vector = hstack([tfidf_vector, extra])

    prediction = rf_model.predict(combined_vector)[0]
    confidence = rf_model.predict_proba(combined_vector)[0]

    if prediction == 1:
        st.error(f"🚨 PHISHING DETECTED — {confidence[1]*100:.1f}% confidence")
    else:
        st.success(f"✅ LEGITIMATE — {confidence[0]*100:.1f}% confidence")

    st.write("### Confidence Breakdown")
    st.progress(int(confidence[1] * 100))
    st.caption(f"Phishing probability: {confidence[1]*100:.1f}%")

    flagged = get_flagged_signals(message)
    if flagged:
        st.write("### ⚠️ Suspicious Signals Detected")
        for key, detail in flagged:
            explanation = SIGNAL_EXPLANATIONS.get(key, "")
            st.markdown(f"- **{detail}** — {explanation}")

    st.write("### 🛡️ What To Do")
    if prediction == 1:
        st.markdown("""
- **Don't click any links** or download attachments from this message.
- **Don't reply** or provide any personal/financial information.
- **Verify independently** — contact the supposed sender directly using a known phone number or website, not the contact info in the message itself.
- **Report it** — forward phishing emails to your email provider's abuse address, or report smishing texts by forwarding to 7726 (SPAM) on most US carriers.
- **Block the sender** if your email/messaging app allows it.
        """)
    else:
        st.markdown("""
- This message appears legitimate, but always stay cautious with unexpected requests for personal info or money.
- If anything about the message still feels off, verify with the sender through a separate, trusted channel before acting.
        """)

# --- UI ---
st.set_page_config(page_title="PhishGuard", page_icon="🎣", layout="centered")
st.title("🎣 PhishGuard")
st.subheader("Phishing Email & SMS Detector")
st.write("Paste a message or upload a screenshot to check if it's a phishing attempt.")

tab1, tab2 = st.tabs(["📝 Paste Text", "📷 Upload Screenshot"])

with tab1:
    user_input = st.text_area("Paste your message here:", height=200)
    if st.button("🔍 Analyze Message", key="text_analyze"):
        if not user_input.strip():
            st.warning("Please paste a message first.")
        else:
            run_prediction(user_input)

with tab2:
    uploaded_image = st.file_uploader("Upload a screenshot of an email or text message", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded screenshot", use_container_width=True)

        if st.button("🔍 Extract & Analyze", key="image_analyze"):
            with st.spinner("Reading text from image..."):
                extracted_text = extract_text_from_image(image)

            if not extracted_text.strip():
                st.warning("Couldn't extract any text from this image. Try a clearer screenshot.")
            else:
                st.write("### 📄 Extracted Text")
                st.text_area("This is what OCR read from your image:", extracted_text, height=100, disabled=True)
                run_prediction(extracted_text)
