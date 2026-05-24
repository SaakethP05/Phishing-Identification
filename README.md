# Phishinng Email & SMS Detector
- Conatins code powerd by ML that detects phishing emails and smishing.
- real time responses, meant to detect threats for those uneducated.

# Overview
PhishGuard is a machine learning classifier that identifies phishing emails and SMS messages. Built using NLP techniques and trained on real-world messages, it helps everyday users recognize cyber threats before they cause harm.
This project was built to extend the mission of DIH (dihumanity.org) — a cybersecurity nonprofit that has educated 300+ people across 10+ facilities with a 96% retention rate — by turning awareness into action through technology.

# Early Data Insights
- Spam messages are on average nearly double the length of real messages
- Current Dataset has 4,824 legitimate vs 747 spam messages

# Process
- I began working with a single dataset from Kaggle and rendered many distributions to understand the data as well as some early patterns.
- Then I cut the words down into their stems to further clean the data and make it easier to evaluate.
- Filler words were also cut but some words were left out of this cut due to their importance in phishing. For example: until, now, immediately
- After finding additional datasets, all were combined to create a combined dataset of 88,058 messages almost perfectly split with 44,420 legitamate messages and 43,468 phishing emails.
- Using the combined dataset, I bagan training the model starting with Naive Bayes. However, Random Forest worked better than it as well as better than XGBoost.
- After working with only the words using TF-IDF, I added more columns in addition to words such as links or exclamation points using hstack.
- This improved accuracy to 98.05 Recall, the most important when identifying phishing messages

# Tech Stack
- Python
- Pandas, Numpy
- Scikit-learn
- Matplotlib/Seaborn

# Real World Impact
This tool is being developed to help the uneducated avoid the risk of being a victim to phishing attacks. Individuals with doubts regarding true vs. false emails or SMS messages can paste the text and get immediate responsess on whether the prompt is trustworthy or not. 
