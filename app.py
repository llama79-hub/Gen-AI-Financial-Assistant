import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "AAPL"
if 'selected_period' not in st.session_state:
    st.session_state.selected_period = "1 Year"

def fetch_stock_data(ticker, period):
    """Fetch stock data based on ticker and period"""
    try:
        
        end_date = datetime.today()
        if period == "1 Week":
            start_date = end_date - timedelta(weeks=1)
        elif period == "1 Month":
            start_date = end_date - timedelta(days=30)
        elif period == "3 Months":
            start_date = end_date - timedelta(days=90)
        elif period == "6 Months":
            start_date = end_date - timedelta(days=180)
        elif period == "1 Year":
            start_date = end_date - timedelta(days=365)
        else:  
            start_date = end_date - timedelta(days=5*365)
        
        # Fetch stock data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        
        if stock_data.empty:
            return None, None, f"No data found for ticker: {ticker}"
        
        
        stock_data = stock_data.reset_index()
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        
       
        stock_info = yf.Ticker(ticker).info
        
        return stock_data, stock_info, None
    
    except Exception as e:
        return None, None, f"Error fetching stock data: {str(e)}"

# Streamlit Page Configuration
st.set_page_config(page_title="GenAI Financial Assistant", layout="wide")
st.title("📈 GenAI-Powered Financial Assistant")
st.write("Your AI-powered guide to smarter investing decisions!")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Stock Analysis", "Insurance Policies", "Investment Tips", "About"])

# 📌 About Section
if page == "About":
    st.header("📌 About the Financial Assistant")
    st.write(
        "This AI-powered financial assistant helps new and experienced investors make informed decisions."
        " With millions of new investors entering the market, our AI-driven chatbot is here to provide insights,"
        " answer basic and advanced investing questions, and suggest products tailored to your needs."
    )
    st.image("https://via.placeholder.com/800x400", caption="AI-driven Investment Assistance")
# 💡 Investment Tips
elif page == "Investment Tips":
    st.header("💡 Investment Tips")
    st.markdown("""
    - Diversify your investments to manage risk.
    - Start with index funds if you're a beginner.
    - Don't try to time the market.
    - Invest with a long-term perspective.
    - Stay informed about market trends and economic conditions.
    """)

# 📊 Stock Analysis Section
elif page == "Stock Analysis":
    st.header("📊 Stock Analysis")
    
   
    analysis_mode = st.radio("Analysis Mode", ["Single Stock", "Compare Stocks"], key="analysis_mode")
    
    if analysis_mode == "Single Stock":
       
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.text_input("Enter Stock Ticker", "AAPL").upper()
        with col2:
            period = st.selectbox("Select Time Period", 
                                ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
                                index=4)
        
        if st.button("Analyze Stock"):
            stock_data, stock_info, error = fetch_stock_data(ticker, period)
            
            if error:
                st.error(error)
            else:
                # Display stock information
                st.subheader(f"{stock_info.get('longName', ticker)} ({ticker})")
                
                cols = st.columns(3)
                cols[0].metric("Current Price", f"${stock_info.get('currentPrice', 'N/A')}")
                cols[1].metric("52 Week High", f"${stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
                cols[2].metric("52 Week Low", f"${stock_info.get('fiftyTwoWeekLow', 'N/A')}")
                
                
                st.subheader("Historical Data")
                st.dataframe(
                    stock_data.style.format({
                        'Open': '{:.2f}',
                        'High': '{:.2f}',
                        'Low': '{:.2f}',
                        'Close': '{:.2f}',
                        'Adj Close': '{:.2f}',
                        'Volume': '{:,}'
                    }),
                    height=400
                )
                
                # Price chart
                st.subheader(f"Price Chart ({period})")
                chart = alt.Chart(stock_data).mark_line().encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Close:Q', title='Price (USD)'),
                    tooltip=[
                        alt.Tooltip('Date:T', title='Date'),
                        alt.Tooltip('Close:Q', title='Price', format='$.2f')
                    ]
                ).properties(
                    width=800,
                    height=400
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
                
                # AI Analysis
                with st.spinner("Generating analysis..."):
                    prompt = f"Analyze {ticker} stock performance over {period}"
                    response = model.generate_content(prompt)
                    st.subheader("💡 AI Analysis")
                    st.write(response.text)

    elif analysis_mode == "Compare Stocks":
        st.subheader("Compare Two Stocks")
    
        col1, col2 = st.columns(2)
        with col1:
            ticker1 = st.text_input("First Stock", "AAPL").upper()
        with col2:
            ticker2 = st.text_input("Second Stock", "MSFT").upper()
    
        period = st.selectbox("Comparison Period", 
                        ["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
                        index=3)
    
        if st.button("Compare Stocks"):
            with st.spinner("Fetching data..."):
                data1, info1, err1 = fetch_stock_data(ticker1, period)
                data2, info2, err2 = fetch_stock_data(ticker2, period)
            
                if err1:
                    st.error(f"Error fetching {ticker1}: {err1}")
                if err2:
                    st.error(f"Error fetching {ticker2}: {err2}")
            
                if not err1 and not err2:
               
                    st.subheader("Key Metrics")
                
                    cols = st.columns(3)
                    cols[0].metric(
                        label=f"{ticker1} Price",
                        value=f"${info1.get('currentPrice', 'N/A')}",
                        delta=f"{info1.get('regularMarketChangePercent', 'N/A')}%"
                    )
                    cols[1].metric(
                        label=f"{ticker2} Price",
                        value=f"${info2.get('currentPrice', 'N/A')}",
                        delta=f"{info2.get('regularMarketChangePercent', 'N/A')}%"
                    )
                    price_diff = info1.get('currentPrice', 0) - info2.get('currentPrice', 0)
                    cols[2].metric(
                        label="Difference",
                        value=f"${abs(price_diff):.2f}",
                        delta=f"{ticker1} {'higher' if price_diff > 0 else 'lower'}"
                    )
                
                   
                    st.subheader("Price Comparison Chart")
                
                    
                    data1['Ticker'] = ticker1
                    data2['Ticker'] = ticker2
                
                    
                    combined = pd.concat([data1, data2]).reset_index(drop=True)
                
                   
                    line1 = alt.Chart(data1).mark_line().encode(
                        x=alt.X('Date:T', title='Date'),
                        y=alt.Y('Close:Q', title='Price (USD)'),
                        color=alt.Color('Ticker:N', legend=alt.Legend(title="Stocks")),
                        tooltip=[
                            alt.Tooltip('Ticker:N', title='Stock'),
                            alt.Tooltip('Date:T', title='Date'),
                            alt.Tooltip('Close:Q', title='Price', format='$.2f')
                        ]
                    )
                
                    line2 = alt.Chart(data2).mark_line().encode(
                        x=alt.X('Date:T', title='Date'),
                        y=alt.Y('Close:Q', title='Price (USD)'),
                        color=alt.Color('Ticker:N'),
                        tooltip=[
                            alt.Tooltip('Ticker:N', title='Stock'),
                            alt.Tooltip('Date:T', title='Date'),
                            alt.Tooltip('Close:Q', title='Price', format='$.2f')
                        ]
                    )
                
                    
                    chart = (line1 + line2).properties(
                        width=800,
                        height=400
                    ).interactive()
                
                    st.altair_chart(chart, use_container_width=True)
                
                    
                    with st.spinner("Generating comparison analysis..."):
                        prompt = f"""
                        Compare {ticker1} and {ticker2} performance over {period} based on:
                        - Current prices: {info1.get('currentPrice')} vs {info2.get('currentPrice')}
                        - 52-week ranges
                        - Recent price trends
                        Provide detailed comparison for investors.
                        """
                        response = model.generate_content(prompt)
                        st.subheader("💡 Comparison Analysis")
                        st.write(response.text)
                        
# 🛡️ Insurance Policies Section
elif page == "Insurance Policies":
    st.header("🛡️ Insurance Policy Advisor")
    st.write("Explore key insurance policies relevant to your financial planning.")

    st.subheader("📋 Categories of Insurance Policies")
    st.markdown("""
    - **Health Insurance**
    - **Life Insurance**
    - **Term Insurance**
    - **Critical Illness Insurance**
    - **Personal Accident Insurance**
    - **Motor Insurance**
    - **Home Insurance**
    - **Travel Insurance**
    - **Retirement Plans (Pension Insurance)**
    - **Child Plans**
    - **ULIPs (Unit Linked Insurance Plans)**
    - **Endowment Plans**
    - **Whole Life Insurance**
    """)
    st.info("📌 More personalized suggestions will be available when linked to user profiles in the future.")

# 🤖 Chatbot Section
elif page == "Chatbot":
    st.header("🤖 Chat with the AI Financial Assistant")
    user_prompt = st.text_area("Ask a financial question:", "What are the best investment options for beginners?")

    if st.button("Get Advice"):
        if user_prompt.strip() == "":
            st.warning("Please enter a financial question.")
        else:
            try:
                
                ticker = None
                period = "1 Year"  
                
               
                time_keywords = {
                    "week": "1 Week",
                    "month": "1 Month",
                    "year": "1 Year",
                    "5 years": "5 Years",
                    "five years": "5 Years"
                }
                
                for keyword, time_period in time_keywords.items():
                    if keyword in user_prompt.lower():
                        period = time_period
                        break
                
               
                def extract_ticker(user_query):
                    
                    import re
                    ticker_pattern = r'\b[A-Z]{1,5}\b'
                    potential_tickers = re.findall(ticker_pattern, user_query)
                    
                    
                    valid_tickers = []
                    for t in potential_tickers:
                        try:
                            info = yf.Ticker(t).info
                            if info.get('regularMarketPrice') is not None:
                                valid_tickers.append(t)
                        except:
                            continue
                    
                    if valid_tickers:
                        return valid_tickers[0]
                    
                    
                    company_keywords = {
                        'apple': 'AAPL',
                        'microsoft': 'MSFT',
                        
                    }
                    
                    for name, t in company_keywords.items():
                        if name in user_query.lower():
                            return t
                    
                   
                    words = user_query.split()
                    for word in words:
                        if len(word) <= 5 and word.isupper():
                            try:
                                info = yf.Ticker(word).info
                                if info.get('regularMarketPrice') is not None:
                                    return word
                            except:
                                continue
                    return None
                
                ticker = extract_ticker(user_prompt)
                
               
                if ticker:
                    with st.spinner(f"Fetching {ticker} data..."):
                        stock_data, stock_info, error = fetch_stock_data(ticker, period)
                        
                        if error:
                            response_text = f"I couldn't fetch data for {ticker}. Please check if the ticker symbol is correct."
                        else:
                           
                            data_summary = {
                                'Company': stock_info.get('longName', ticker),
                                'Ticker': ticker,
                                'Current Price': f"${stock_info.get('currentPrice', 'N/A')}",
                                '52 Week Range': f"${stock_info.get('fiftyTwoWeekLow', 'N/A')} - ${stock_info.get('fiftyTwoWeekHigh', 'N/A')}",
                                'Market Cap': f"${stock_info.get('marketCap', 'N/A'):,}" if stock_info.get('marketCap') else 'N/A',
                                'PE Ratio': stock_info.get('trailingPE', 'N/A'),
                                'Sector': stock_info.get('sector', 'N/A')
                            }
                            
                            # Generate analysis
                            analysis_prompt = f"""
                            The user asked: "{user_prompt}"
                            
                            Here's the stock data we have:
                            {data_summary}
                            
                            Recent price data (last 5 days):
                            {stock_data[['Date', 'Close']].tail().to_string(index=False)}
                            
                            Please provide:
                            1. A direct answer to the user's question
                            2. Analysis of the stock's recent performance
                            3. Any relevant warnings or considerations
                            """
                            
                            response = model.generate_content(analysis_prompt)
                            response_text = response.text
                            
                            
                            st.subheader(f"💡 {ticker} Analysis")
                            st.write(response_text)
                            
                            # Show interactive chart
                            st.subheader(f"📈 {ticker} Price Chart ({period})")
                            chart = alt.Chart(stock_data).mark_line().encode(
                                x=alt.X('Date:T', title='Date'),
                                y=alt.Y('Close:Q', title='Price (USD)'),
                                tooltip=[
                                    alt.Tooltip('Date:T', title='Date'),
                                    alt.Tooltip('Close:Q', title='Price', format='$.2f')
                                ]
                            ).properties(
                                width=800,
                                height=400
                            ).interactive()
                            st.altair_chart(chart, use_container_width=True)
                            
                           
                            with st.expander("🔍 Detailed Metrics"):
                                st.table(pd.DataFrame.from_dict(data_summary, orient='index', columns=['Value']))
                
                else:
                    
                    financial_prompt = (
                        "You are a financial advisor. Answer this question professionally: " + user_prompt + 
                        "\nIf this is about a specific stock, remind the user to mention the company name or ticker symbol."
                    )
                    response = model.generate_content(financial_prompt)
                    st.subheader("💡 Financial Advice")
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")
                st.info("Please try being more specific, like 'Show me Microsoft stock data' or 'What is AAPL's current price?'")
# Footer
st.sidebar.markdown("---")
st.sidebar.write("ℹ️ **Disclaimer:**This AI provides general financial insights and should not be considered professional financial advice. Always do your own research before investing.")
