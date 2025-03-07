import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import requests
from bs4 import BeautifulSoup
from groq import Groq  # Correct Groq import

# Set up Groq API key
groq_client = Groq(api_key="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")

# Function to scrape insurance data
def scrape_insurance_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()[:2000]  # Extract limited text for now
    except Exception as e:
        return f"❌ Error scraping {url}: {str(e)}"

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text("text")
    except Exception as e:
        text = f"❌ Error reading PDF: {str(e)}"
    return text[:3000]  # Limit text to 3000 characters

# Function to get AI-generated insurance advice with memory
def get_insurance_advice(user_input, pdf_text, scraped_data, chat_history):
    messages = chat_history + [
        {"role": "user", "content": f"Input: {user_input}\nPDF Data: {pdf_text}\nScraped Data: {scraped_data}"}
    ]
    response = groq_client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages
    )
    return response.choices[0].message.content, messages

# Streamlit UI
st.set_page_config(page_title="InsurAI - AI Insurance Advisor", page_icon="💡", layout="wide")
st.title("🔍 InsurAI - Your AI Insurance Advisor")
st.markdown("### 🤖 Get AI-powered, personalized insurance recommendations tailored to your needs! 🎯")

# User inputs
st.sidebar.header("📝 Personal Information")
age = st.sidebar.number_input("🧑 Enter your Age", min_value=18, max_value=100, step=1)
income = st.sidebar.number_input("💰 Monthly Income (INR)", min_value=5000, step=500)
preferences = st.sidebar.text_area("📝 Your Insurance Preferences (Health, Life, Travel, etc.)")

# File upload
st.sidebar.subheader("📂 Upload Your Insurance Policy")
uploaded_file = st.sidebar.file_uploader("📄 Upload your existing insurance policy (PDF) for analysis", type=["pdf"])
pdf_text = extract_text_from_pdf(uploaded_file) if uploaded_file else ""

# Scraping example site (Replace with real insurance sites)
insurance_url = "https://www.hdfcergo.com/campaigns/buy-travel-insurance-new?utm_source=bing_search_2&utm_medium=cpc&utm_campaign=Travel_Search_Core_Neev-Broad&utm_adgroup=Generic&adid=&utm_term=group%20travel%20insurance&utm_network=o&utm_matchtype=b&utm_device=c&utm_location=149772&utm_sitelink={sitelink}&utm_placement=&ci=bingsearch&SEM=1&msclkid=ca24b1152f2e1a3b645fd6ddb8bb6259"
scraped_data = scrape_insurance_data(insurance_url)

# Chat history
def get_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history

chat_history = get_chat_history()

# Get AI advice
st.markdown("---")
if st.button("🚀 Generate My AI Insurance Advice"):
    with st.spinner("⏳ Analyzing your details and generating the best advice..."):
        advice, chat_history = get_insurance_advice(preferences, pdf_text, scraped_data, chat_history)
        st.session_state.chat_history = chat_history  # Save conversation history
        st.subheader("📢 Your AI-Generated Insurance Advice")
        st.write(advice)
        st.success("✅ Advice generated successfully! You can ask follow-up questions below.")

# Chat follow-up section
st.markdown("### 💬 Ask Follow-up Questions")
user_query = st.text_input("🤔 Have more questions? Ask here!")
if st.button("📩 Send Query") and user_query:
    with st.spinner("⏳ Fetching response..."):
        response, chat_history = get_insurance_advice(user_query, pdf_text, scraped_data, chat_history)
        st.session_state.chat_history = chat_history
        st.subheader("💡 AI Response:")
        st.write(response)

# Footer
st.markdown("---")
st.markdown("💡 **InsurAI** helps you make informed decisions about insurance based on your budget, needs, and existing policies. Stay secure, stay insured! 🏆")
