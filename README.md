# PhishGuard — Phishing Email & SMS Detector

**🔴 Live Demo:** [phishing-identification-caleb-dih.streamlit.app](https://phishing-identification-caleb-dih.streamlit.app/)

- Contains code powered by ML that detects phishing emails and smishing.
- Real time responses, meant to detect threats for those uneducated.

# Overview
PhishGuard is a machine learning classifier that identifies phishing emails and SMS messages. Built using NLP techniques and trained on real-world messages, it helps everyday users recognize cyber threats before they cause harm.

This project was built to extend the mission of DIH (dihumanity.org) — a cybersecurity nonprofit that has educated 300+ people across 10+ facilities with a 96% retention rate — by turning awareness into action through technology.

# Early Data Insights
- Spam messages are on average nearly double the length of real messages
- Current dataset has 4,824 legitimate vs 747 spam messages (SMS subset)

# Process
- I began working with a single dataset from Kaggle and rendered many distributions to understand the data as well as some early patterns.
- Then I cut the words down into their stems to further clean the data and make it easier to evaluate.
- Filler words were also cut but some words were left out of this cut due to their importance in phishing. For example: until, now, immediately
- After finding additional datasets, all were combined to create a combined dataset of 88,058 messages almost perfectly split with 44,420 legitimate messages and 43,468 phishing emails.
- Using the combined dataset, I began training the model starting with Naive Bayes. However, Random Forest worked better than it as well as better than XGBoost.
- After working with only the words using TF-IDF, I added more columns in addition to words such as links or exclamation points using hstack.
- This improved accuracy to 98.05 recall, the most important metric when identifying phishing messages.
- For deployment, the final model was scaled down to 10 trees (from 100) to keep the model file small enough for reliable hosting, trading a small amount of accuracy for stability.

# Model Performance

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Naive Bayes | 94.19% | 95.34% | 92.84% | 94.07% |
| Random Forest (100 trees) | 97.10% | 96.93% | 97.25% | 97.09% |
| XGBoost | 95.33% | 93.61% | 97.24% | 95.39% |
| Random Forest + engineered features (100 trees) | 98.14% | 98.20% | 98.05% | 98.13% |
| **Random Forest + engineered features (10 trees, deployed)** | **96.84%** | **97.80%** | **95.81%** | **96.79%** |

# Tech Stack
- Python
- Pandas, NumPy
- Scikit-learn, XGBoost
- NLTK
- Matplotlib/Seaborn
- Streamlit (deployment)

# Real World Impact
This tool is being developed to help the uneducated avoid the risk of being a victim to phishing attacks. Individuals with doubts regarding true vs. false emails or SMS messages can paste the text and get immediate responses on whether the prompt is trustworthy or not.
