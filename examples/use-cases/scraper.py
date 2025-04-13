from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from pydantic import SecretStr
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
ChatGoogleGenerativeAI.model_rebuild()

browser = Browser(
    config=BrowserConfig(
        # Specify the path to your Chrome executable
        chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    )
)
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))

# Create agent with the model
agent = Agent(
    task="1. Check if a survey is open, if skip step 2 and go to step 3, if a survey isnt open: continue to step 2. 2. Open Prizerebel.com 3. Select a Survey, that has a #, in its name. 4. Your goal is to complete a survey, Fill it in, You are Jan vermeulen, a 34-year-old man (date of birth: 17-09-1990) from Heemstede, Noord-Holland, Netherlands, Your Postcode is 2101WJ You have 2 daughters, 2 sons. Daughter 1: 9 years old, Daughter 2: 10 years old, Son1: 11 years old, son 2: 13 years old. You work in marketing as a market research analyst, earning €53,000 per year, 70 people work at your company. You have a bachelor's degree in business administration. You rent an apartment and own a mid-sized sedan. You are single. You participate in surveys regularly as part of your job and personal interest. Fill out surveys naturally based on this background, making up reasonable details as needed.",
    llm=llm,
    browser=browser
)

async def main():
    await agent.run()

if __name__ == '__main__':
    asyncio.run(main())