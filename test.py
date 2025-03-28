import streamlit as st
import fitz  
import requests
from bs4 import BeautifulSoup
from groq import Groq
import pandas as pd
import plotly.express as px

groq_client = Groq(api_key="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")

def scrape_insurance_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()[:2000]  # Extract limited text for now
    except Exception as e:
        return f"❌ Error scraping {url}: {str(e)}"

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text("text")
    except Exception as e:
        text = f"❌ Error reading PDF: {str(e)}"
    return text[:3000]  


def get_insurance_advice(user_input, pdf_text, scraped_data, chat_history):
    messages = chat_history + [
        {"role": "user", "content": f"Input: {user_input}\nPDF Data: {pdf_text}\nScraped Data: {scraped_data}"}
    ]
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",  
        messages=messages
    )
    return response.choices[0].message.content, messages

# Streamlit UI Enhancements
st.set_page_config(page_title="InsurAI - AI Insurance Advisor", page_icon="💡", layout="wide")
st.markdown("""
    <style>
        .main-title { text-align: center; font-size: 36px; font-weight: bold; color: #0078FF; }
        .sidebar { background-color: #F7F9FC; padding: 20px; border-radius: 10px; }
        .button { background-color: #0078FF; color: white; font-size: 18px; }
        .section-title { font-size: 24px; font-weight: bold; color: #333; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='main-title'>🔍 InsurAI - Your AI Insurance Advisor</p>", unsafe_allow_html=True)
st.markdown("### 🤖 Get AI-powered, personalized insurance recommendations tailored to your needs! 🎯")


with st.sidebar:
    
    st.header("📝 Personal Information")
    age = st.number_input("🧑 Enter your Age", min_value=18, max_value=100, step=1)
    income = st.number_input("💰 Monthly Income (INR)", min_value=5000, step=500)
    family_members = st.number_input("👨‍👩‍👧‍👦 Number of Dependents", min_value=0, step=1)
    health_conditions = st.text_area("🏥 Health Conditions (if any)")
    financial_liabilities = st.text_area("💳 Financial Liabilities (Loans, EMIs, etc.)")
    

    insurance_types = st.multiselect("📜 Select Insurance Type", ["Health", "Life", "Vehicle", "Travel"])
    
    
    uploaded_file = st.file_uploader("📄 Upload your existing insurance policy (PDF) for analysis", type=["pdf"])
    st.markdown("</div>", unsafe_allow_html=True)

pdf_text = extract_text_from_pdf(uploaded_file) if uploaded_file else ""
preferences = f"Looking for {', '.join(insurance_types)} coverage with {family_members} dependents, income {income} INR, and health conditions: {health_conditions}. Liabilities: {financial_liabilities}."


insurance_urls = [
    "https://www.policybazaar.com/?utm_source=yahoo_brand&utm_medium=cpc&utm_term=policybazaar&utm_campaign=PolicyBazaar00PolicyBazaar&msclkid=4e1dc7af948d1430df53a07361f417e9",
    "https://www.hdfcergo.com/campaigns/all-in-one-product-new?&utm_source=bing_search_1&utm_medium=cpc&utm_campaign=AIO_Search_Brand_Neev-Phrase&utm_adgroup=HDFC-ERGO&utm_term=hdfc%20ergo%20general%20insurance%20company&utm_network=o&utm_matchtype=e&utm_device=c&utm_location=156830&utm_sitelink={sitelink}&utm_placement=&ci=aiobsearch&SEM=1&msclkid=c37dd2bf7d601de87ad2b56388f7af74",
    "https://www.maxlifeinsurance.com/"
]
scraped_data = "\n".join([scrape_insurance_data(url) for url in insurance_urls])


def get_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history

chat_history = get_chat_history()


st.markdown("---")
if st.button("🚀 Generate My AI Insurance Advice", key="generate_advice"):
    with st.spinner("⏳ Analyzing your details and generating the best advice..."):
        advice, chat_history = get_insurance_advice(preferences, pdf_text, scraped_data, chat_history)
        st.session_state.chat_history = chat_history
        st.subheader("📢 Your AI-Generated Insurance Advice")
        st.write(advice)
        st.success("✅ Advice generated successfully! You can ask follow-up questions below.")


st.markdown("### 💬 Ask Follow-up Questions")
user_query = st.text_input("🤔 Have more questions? Ask here!")
if st.button("📩 Send Query", key="send_query") and user_query:
    with st.spinner("⏳ Fetching response..."):
        response, chat_history = get_insurance_advice(user_query, pdf_text, scraped_data, chat_history)
        st.session_state.chat_history = chat_history
        st.subheader("💡 AI Response:")
        st.write(response)


st.markdown("### 📊 Insurance Market Insights")
data = pd.DataFrame({"Company": ["PolicyBazaar", "HDFC Ergo", "Max Life"], "Satisfaction": [85, 78, 90]})
fig = px.bar(data, x="Company", y="Satisfaction", title="Customer Satisfaction Ratings")
st.plotly_chart(fig)


st.markdown("### 🔗 Useful Insurance Links")
for url in insurance_urls:
    st.markdown(f"🔹 [Explore {url}]({url})")


st.markdown("---")
st.markdown("💡 **InsurAI** helps you make informed decisions about insurance based on your budget, needs, and existing policies. Stay secure, stay insured! 🏆")
