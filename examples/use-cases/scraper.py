import logging # Add logging
from langchain_google_genai import ChatGoogleGenerativeAI
# Import BrowserContext
from browser_use import Agent, Browser, BrowserConfig, Controller, BrowserContext
from pydantic import SecretStr
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
ChatGoogleGenerativeAI.model_rebuild()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Configure basic logging for visibility

controller = Controller()

@controller.action("Checks if the current page URL contains the word 'survey'.")
# Make the function async and request BrowserContext
async def check_if_survey(browser_context: BrowserContext):
    """Checks the current page URL for the word 'survey' and returns a descriptive string."""
    try:
        # Await the async call to get the current page
        page = await browser_context.get_current_page()
        url = page.url
        logger.info(f"Current page URL: {url}")
        # Check if 'survey' is in the lowercase URL
        if "survey" in url.lower():
            result = "The current page appears to be a survey page (URL contains 'survey')."
            logger.info(result)
            return result
        else:
            result = "The current page does not appear to be a survey page (URL does not contain 'survey')."
            logger.info(result)
            return result
    except Exception as e:
        # Log errors and return an informative message
        logger.error(f"Error checking if page is a survey: {e}", exc_info=True)
        return f"Error occurred while checking the page URL: {e}"


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
