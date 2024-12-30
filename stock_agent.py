import streamlit as st
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
os.environ["PHIDATA_API_KEY"] = os.getenv('PHIDATA_API_KEY')

# Agents
web_search_agent = Agent(
    name='Web Search Agent',
    role="Search the web for the interview",
    model=Groq(id="llama3-groq-70b-8192-tool-use-preview"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=False,
    markdown=True,
)

finance_agent = Agent(
    name="Finance AI Agent",
    model=Groq(id="llama3-groq-70b-8192-tool-use-preview"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True)],
    instructions=["Use table to display the data"],
    show_tool_calls=False,
    markdown=True,
)

multi_ai_agent = Agent(
    model=Groq(id="llama3-groq-70b-8192-tool-use-preview"),
    team=[web_search_agent, finance_agent],
    instructions=["Always include sources", "Use table to display the data"],
    show_tool_calls=False,
    markdown=True,
)

# Streamlit App
st.title("AI-Powered Stock Information and Analysis")
st.subheader("Powered by Groq and Streamlit")

options = ["Reliance", "TCS", "Infosys", "HDFC", "ICICI"]
selected_stocks = st.multiselect("Select up to 5 companies to analyze:", options, default=options[:5])

if st.button("Get Stock Information"):
    for stock_name in selected_stocks:
        st.subheader(f"Information for {stock_name}")
        with st.spinner(f"Fetching data for {stock_name}..."):
            response_parts = []
            for delta in multi_ai_agent.run(f"Summarize analyst recommendation and share the latest news for {stock_name}"):
                if isinstance(delta, tuple) and delta[0] == 'content':
                    response_parts.append(delta[1].strip())
                elif isinstance(delta, str): 
                    response_parts.append(delta.strip())
            response = "\n\n".join(response_parts).strip()
        st.markdown(response)
