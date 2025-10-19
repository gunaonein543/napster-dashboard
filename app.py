import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter
import re
import statsmodels.api as sm
from io import BytesIO
import requests

# Custom styling with markdown
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
        padding: 20px;
    }
    .stHeader {
        color: #1e90ff;
        font-size: 2.5em;
        text-align: center;
        font-weight: bold;
    }
    .stSubheader {
        color: #2e86c1;
        font-size: 1.5em;
        margin-top: 10px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Expanded positive and negative words (unchanged, just referenced)
positive_words = {'good', 'great', 'excellent', 'positive', 'success', 'improved', 'happy', 'satisfied', 'well', 'better', 'like', 'love', 'best'}  # Shortened for brevity
negative_words = {'bad', 'poor', 'negative', 'failed', 'issue', 'problem', 'delayed', 'urgent', 'escalation', 'risk'}  # Shortened for brevity
neutral_words = {'ok', 'average', 'neutral', 'fine', 'normal'}

def get_sentiment(text):
    words = re.findall(r'\w+', text.lower())
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    neu_count = sum(1 for word in words if word in neutral_words)
    total = pos_count + neg_count + neu_count + 1
    score = (pos_count - neg_count) / total
    if score > 0.1:
        return 'Positive', score
    elif score < -0.1:
        return 'Negative', score
    else:
        return 'Neutral', score

def summarize_transcript(text, num_sentences=3):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    word_freq = Counter(re.findall(r'\w+', text.lower()))
    common_words = [word for word, freq in word_freq.most_common(20)]
    key_sentences = sorted(sentences, key=lambda s: sum(1 for w in common_words if w in s.lower()), reverse=True)[:num_sentences]
    return ' '.join(key_sentences)

trigger_keywords = {
    'delayed': 'Suggest follow-up on delay', 'urgent': 'Flag as urgent', 'escalation': 'Escalate to management', 'risk': 'Highlight risk',
    'opportunity': 'Note opportunity', 'blocker': 'Flag as blocker', 'issue': 'Investigate issue', 'problem': 'Resolve problem'
}

def get_actions(text):
    actions = []
    for kw, action in trigger_keywords.items():
        if kw in text.lower():
            actions.append(action)
    return actions

# Password protection
st.sidebar.title("🔒 Login")
password = st.sidebar.text_input("Enter Password", type="password")
if password != "napster2025":
    st.error("❌ Incorrect password. Access denied.")
    st.stop()

# Fetch data from GitHub
github_url = "https://github.com/gunaonein543/napster-dashboard/blob/main/edo_meeting_cleaned%20(1).csv"  # Replace with your raw CSV URL
try:
    response = requests.get(github_url)
    response.raise_for_status()  # Raise an error for bad status codes
    df = pd.read_csv(BytesIO(response.content))
except requests.exceptions.RequestException as e:
    st.error("❌ Failed to fetch data from GitHub. Please check the URL or network connection.")
    # Fallback to sample data if GitHub fetch fails
    st.warning("⚠️ Using sample data as fallback.")
    sample_data = {
        'date': ['2025-09-14'] * 10 + ['2025-09-15'] * 5 + ['2025-10-14'] * 10,
        'team_member': ['Edo Segal', 'maryna.soroka@napster.com'] * 5 + ['kautik.mistry@napster.com'] * 5 + ['gselvanayagam@napster.com'] * 5 + ['tobin.mathew@napster.com'] * 5,
        'discussion_with_edo': ["Welcome! This is a quick 15-minute structured check-in...", "Haido, yes, I'm repeating that this is a test only, so...", "you may discard it from your memory.", "For the test's sake, yes, I've confirmed the rules and...", "It's all clear, clear now.", "Got it, the roles are now clear. What have you been able to accomplish last week?", "Last week, we were able to Create a lot of updates to the scrum tool...", "To your email and the email is the email subject is.", "Clear that it's about the blockers", "The view summary button appears at the very end..."] * 2
    }
    df = pd.DataFrame(sample_data)

df = df.groupby(['date', 'team_member'])['discussion_with_edo'].apply(' '.join).reset_index()
df['date'] = pd.to_datetime(df['date'])
df['sentiment_label'], df['sentiment_score'] = zip(*df['discussion_with_edo'].apply(get_sentiment))
df['summary'] = df['discussion_with_edo'].apply(summarize_transcript)
df['actions'] = df['discussion_with_edo'].apply(get_actions)

today = datetime.now()
last_week_start = today - timedelta(days=7)
last_four_weeks_start = today - timedelta(days=28)

df_last_week = df[(df['date'] >= last_week_start) & (df['date'] < today)]
df_last_four = df[(df['date'] >= last_four_weeks_start) & (df['date'] < today)]

# Sidebar filters
st.sidebar.title("⚙️ Filters")
filter_date = st.sidebar.date_input("📅 Select Date Range", (last_four_weeks_start.date(), today.date()))
filter_topic = st.sidebar.text_input("🔍 Filter by Topic/Keyword")
filter_sentiment = st.sidebar.selectbox("😊 Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"])
filter_member = st.sidebar.selectbox("👤 Filter by Team Member", ["All"] + list(df['team_member'].unique()))

filtered_df = df_last_four[(df['date'] >= pd.to_datetime(filter_date[0])) & (df['date'] <= pd.to_datetime(filter_date[1]))]
if filter_topic:
    filtered_df = filtered_df[filtered_df['discussion_with_edo'].str.contains(filter_topic, case=False)]
if filter_sentiment != "All":
    filtered_df = filtered_df[filtered_df['sentiment_label'] == filter_sentiment]
if filter_member != "All":
    filtered_df = filtered_df[filtered_df['team_member'] == filter_member]

# KPI Section
st.markdown('<div class="stHeader">Napster Scrum Intelligence Dashboard 🌟</div>', unsafe_allow_html=True)
st.markdown('<div class="stSubheader">📊 Key Metrics</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6 = st.columns(6)
overall_health = round(filtered_df['sentiment_score'].mean() * 100, 1)
active_members = len(filtered_df['team_member'].unique())
critical_blockers = len(filtered_df[filtered_df['discussion_with_edo'].str.contains('blocker|critical', case=False)])
sprint_velocity = round(len(filtered_df) / max(1, len(filtered_df['date'].unique())), 1)
code_review_queue = 2
team_morale = '🌱 Stable/Positive' if overall_health > 50 else '⚠️ Needs Attention'

with col1:
    st.markdown('<div class="stMetric">', unsafe_allow_html=True)
    st.metric("Overall Health", f"{overall_health}/100")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stMetric">', unsafe_allow_html=True)
    st.metric("Active Members", active_members)
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stMetric">', unsafe_allow_html=True)
    st.metric("Critical Blockers", critical_blockers)
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stMetric">', unsafe_allow_html=True)
    st.metric("Sprint Velocity", f"{sprint_velocity}%")
    st.markdown('</div>', unsafe_allow_html=True)
with col5:
    st.markdown('<div class="stMetric">', unsafe_allow_html=True)
    st.metric("Code Review Queue", code_review_queue)
    st.markdown('</div>', unsafe_allow_html=True)
with col6:
    st.markdown('<div class="stMetric">', unsafe_allow_html=True)
    st.metric("Team Morale", team_morale)
    st.markdown('</div>', unsafe_allow_html=True)

# Technology & Project Focus
st.markdown('<div class="stSubheader">💻 Technology & Project Focus</div>', unsafe_allow_html=True)
tech_keywords = {'react': 0, 'typescript': 0, 'nodejs': 0, 'graphql': 0, 'azure': 0, 'oracle': 0, 'migration': 0, 'ai': 0}
all_text = ' '.join(filtered_df['discussion_with_edo'])
for kw in tech_keywords:
    tech_keywords[kw] = all_text.lower().count(kw)

labels = list(tech_keywords.keys())
values = list(tech_keywords.values())
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(labels, values, color=['#1e90ff', '#2e86c1', '#4682b4', '#5dade2', '#76b7e5', '#a3d8f4', '#d6eaf8', '#ebecf0'])
ax.set_title("Top Technology Areas 🎯", fontsize=14, color='#2e86c1')
ax.set_xticklabels(labels, rotation=45)
for i, v in enumerate(values):
    ax.text(i, v + 0.5, str(v), ha='center', color='#2e86c1')
st.pyplot(fig)

# Active Projects
st.markdown('<div class="stSubheader">🚀 Active Projects</div>', unsafe_allow_html=True)
st.success("[Spaces] Goal: Complete Node.js migration for endpoints - Blocked - needs attention")
st.success("[Napster] Goal: Finalize Oracle to Azure migration - Blocked - needs attention")

# Team Engagement & Top Contributors
st.markdown('<div class="stSubheader">🤝 Team Engagement & Top Contributors</div>', unsafe_allow_html=True)
contributors = filtered_df['team_member'].value_counts().head(5)
for name, count in contributors.items():
    st.write(f"👤 {name}: {count} updates")

# Activity Distribution
st.markdown('<div class="stSubheader">📈 Activity Distribution</div>', unsafe_allow_html=True)
activity_categories = {'Accomplishments': all_text.lower().count('accomplish') + all_text.lower().count('complete') + all_text.lower().count('progress'),
                      'Blockers': all_text.lower().count('block') + all_text.lower().count('issue') + all_text.lower().count('problem'),
                      'In Progress': all_text.lower().count('working') + all_text.lower().count('ongoing'),
                      'Planning': all_text.lower().count('plan') + all_text.lower().count('next')}
fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(activity_categories.values(), labels=activity_categories.keys(), autopct='%1.1f%%', colors=['#1e90ff', '#2e86c1', '#4682b4', '#5dade2'], startangle=90)
ax.axis('equal')
st.pyplot(fig)

# Sprint Progress
st.markdown('<div class="stSubheader">🏃 Sprint Progress</div>', unsafe_allow_html=True)
st.progress(0.7)
st.write("[Spaces] Goal: Complete Node.js migration for endpoints - 70%")
st.progress(0.5)
st.write("[Napster] Goal: Finalize Oracle to Azure migration - 50%")

# Strategic Insights & Recommendations
st.markdown('<div class="stSubheader">💡 Strategic Insights & Recommendations</div>', unsafe_allow_html=True)
st.markdown('### Positive Trends 🌱')
positive_texts = filtered_df[filtered_df['sentiment_label'] == 'Positive']['summary'].tolist()
for t in positive_texts[:3]:
    st.success(t)

# Critical Alerts & Blockers
st.markdown('### Critical Alerts & Blockers 🚨')
blockers = filtered_df[filtered_df['discussion_with_edo'].str.contains('blocker', case=False)]
for idx, row in blockers.iterrows():
    st.warning(f"[{row['team_member']}] 🔧 Blocker: {row['summary']}")

st.markdown('### Areas of Concern ⚠️')
negative_texts = filtered_df[filtered_df['sentiment_label'] == 'Negative']['summary'].tolist()
for t in negative_texts[:3]:
    st.warning(t)

st.markdown('### Immediate Action Items 🚀')
actions_list = [a for actions in filtered_df['actions'] for a in actions]
for a in set(actions_list):
    st.info(a)

# Team Sentiment Analysis
st.markdown('<div class="stSubheader">📉 Team Sentiment Analysis</div>', unsafe_allow_html=True)
daily_sentiment = filtered_df.groupby('date')['sentiment_score'].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(daily_sentiment['date'], daily_sentiment['sentiment_score'], marker='o', color='#1e90ff', linewidth=2)
ax.set_title("Team Sentiment Over Time 📅", fontsize=14, color='#2e86c1')
ax.set_xlabel("Date", color='#2e86c1')
ax.set_ylabel("Sentiment Score", color='#2e86c1')
ax.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig)

# Predictive Trend
st.markdown('<div class="stSubheader">🔮 Predictive Sentiment Trend for Next Week</div>', unsafe_allow_html=True)
if len(daily_sentiment) > 1:
    X = np.arange(len(daily_sentiment)).reshape(-1, 1)
    y = daily_sentiment['sentiment_score']
    model = sm.OLS(y, sm.add_constant(X)).fit()
    next_week = np.arange(len(daily_sentiment), len(daily_sentiment) + 7).reshape(-1, 1)
    predictions = model.predict(sm.add_constant(next_week))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(len(y)), y, label='Historical', color='#1e90ff', marker='o')
    ax.plot(range(len(y), len(y)+7), predictions, label='Predicted', linestyle='--', color='#2e86c1')
    ax.set_title("Predicted Sentiment Trend 📈", fontsize=14, color='#2e86c1')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)
else:
    st.write("⚠️ Insufficient data for prediction.")

# AI Chatbot
st.markdown('<div class="stSubheader">🤖 AI Chatbot for Data Queries</div>', unsafe_allow_html=True)
user_input = st.text_input("💬 Ask about the data (e.g., 'What are the blockers?')")
if user_input:
    if 'blocker' in user_input.lower():
        blockers = [row['summary'] for _, row in filtered_df.iterrows() if 'blocker' in row['discussion_with_edo'].lower()]
        st.write("🔧 Identified Blockers:", blockers)
    elif 'trend' in user_input.lower():
        st.write("📊 Current sentiment trend: Average score is", filtered_df['sentiment_score'].mean())
    elif 'summary' in user_input.lower():
        st.write("📝 Overall Summary:", summarize_transcript(' '.join(filtered_df['discussion_with_edo'])))
    else:
        st.write("❓ Sorry, try asking about blockers, trends, or summaries.")

# Export
st.markdown('<div class="stSubheader">📥 Export Reports</div>', unsafe_allow_html=True)
buffer = BytesIO()
filtered_df.to_csv(buffer, index=False)
st.download_button("⬇️ Download Filtered Data", buffer.getvalue(), "napster_transcripts.csv")

# Gamified: Progress Bar for Positive Sentiment
st.markdown('<div class="stSubheader">🎮 Gamified KPI: Positive Sentiment Progress</div>', unsafe_allow_html=True)
pos_percentage = (len(filtered_df[filtered_df['sentiment_label'] == 'Positive']) / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
st.progress(pos_percentage / 100)
st.write(f"😊 Positive Sentiment: {pos_percentage:.2f}%")

# Bonus: Notifications simulation
if any(filtered_df['sentiment_label'] == 'Negative'):
    st.warning("🚨 Negative sentiment detected - Consider scheduling a team check-in.")

st.info("📱 This dashboard is mobile-responsive. For live voice-to-text, integrate speech_recognition library in production.")

