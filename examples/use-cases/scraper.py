import os
import asyncio
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.agent.service import BrowserContext

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

controller = Controller()

SURVEY_TASK = (
    "You are Jan Vermeulen, a 34-year-old man from Heemstede, Netherlands. "
    "You have 2 daughters (9 and 10) and 2 sons (11 and 13). "
    "You work in marketing as a market research analyst, earning €53,000 per year. "
    "You have a bachelor's degree in business administration, rent an apartment, own a mid-sized sedan, and are single. "
    "You regularly participate in surveys. "
    "Fill out the current survey naturally based on this background, making up reasonable details as needed."
)
NO_SURVEY_TASK = (
    ""
)

async def main():
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  
        )
    )
    llm = ChatGoogleGenerativeAI(
        model='gemini-2.0-flash-exp',
        api_key=SecretStr(os.getenv('GEMINI_API_KEY'))
    )

    async with await browser.new_context() as context:
        page = await context.get_current_page()
        url = page.url
        logger.info(f'Current page URL: {url}')

        if "survey" in url.lower():
            task = SURVEY_TASK
        else:
            task = NO_SURVEY_TASK

        agent = Agent(
            task=task,
            llm=llm,
            browser_context=context,
            controller=controller,
        )
        await agent.run()

    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())