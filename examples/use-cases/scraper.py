from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from pydantic import SecretStr
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
ChatGoogleGenerativeAI.model_rebuild()

controller = Controller()

@controller.action("Checks if the current page is a survey.")
def check_if_survey(browser: Browser):
    page = browser.get_current_page()


async def main():
    browser = Browser(
        config=BrowserConfig(
            # Specify the path to your Chrome executable
            chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        )
    )
    api_key = os.getenv("GEMINI_API_KEY")

    # Initialize the model
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))

    agent = Agent(
        task="Run the check_if_survey tool",
        llm=llm,
        browser=browser
    )
    await agent.run()

if __name__ == '__main__':
    asyncio.run(main())