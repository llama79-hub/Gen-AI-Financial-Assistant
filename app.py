import streamlit as st
import google.generativeai as genai

# Set up Gemini API key (Replace with your actual API key)
API_KEY = "AIzaSyCm7xqjOcx_ddNaFU6RntsDWoYD_y0SKQ4"
genai.configure(api_key=API_KEY)

# Streamlit Page Configuration
st.set_page_config(page_title="GenAI Financial Assistant", layout="wide")
st.title("📈 GenAI-Powered Financial Assistant")
st.write("Your AI-powered guide to smarter investing decisions!")

# Sidebar for instructions and navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "About", "Investment Tips"])

if page == "About":
    st.header("📌 About the Financial Assistant")
    st.write(
        "This AI-powered financial assistant helps new and experienced investors make informed decisions."
        " With millions of new investors entering the market, our AI-driven chatbot is here to provide insights,"
        " answer basic and advanced investing questions, and suggest products tailored to your needs."
    )
    st.image("https://via.placeholder.com/800x400", caption="AI-driven Investment Assistance")

elif page == "Investment Tips":
    st.header("💡 Investment Tips")
    st.write("Here are some general tips for smart investing:")
    st.markdown("""
    - Diversify your investments to manage risk.
    - Start with index funds if you're a beginner.
    - Don't try to time the market.
    - Invest with a long-term perspective.
    - Stay informed about market trends and economic conditions.
    """)

else:
    st.header("🤖 Chat with the AI Financial Assistant")
    user_prompt = st.text_area("Ask a financial question:", "What are the best investment options for beginners?")
    
    if st.button("Get Advice"):
        if user_prompt.strip() == "":
            st.warning("Please enter a question.")
        else:
            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content(user_prompt)
                st.subheader("💡 AI Response:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("📌 **Disclaimer:** This AI provides general financial insights and should not be considered professional financial advice. Always do your own research before investing.")
