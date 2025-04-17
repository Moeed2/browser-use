import logging  # Add logging
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

# Import BrowserContext
from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.agent.service import Agent, Browser, BrowserContext, Controller

load_dotenv()
import asyncio

ChatGoogleGenerativeAI.model_rebuild()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Configure basic logging for visibility

controller = Controller()


@controller.action('Goes to the webpage')
def go_to_webpage(browser: BrowserContext):
	print('ran this')


@controller.action('Initial Check.')
# Make the function async and request BrowserContext
async def initial_check(browser: BrowserContext):
	"""Checks the current page URL for the word 'survey' and returns a descriptive string."""
	try:
		# Await the async call to get the current page
		page = await browser.get_current_page()
		url = page.url
		logger.info(f'Current page URL: {url}')

		# Check if 'survey' is in the lowercase URL
		if 'survey' in url.lower():
			result = "The current page appears to be a survey page (URL contains 'survey')."
			logger.info(result)
			task = 'Your goal is to complete the current survey,  Fill it in,'
			' You are Jan vermeulen, a 34-year-old man (date of birth: 17-09-1990) from Heemstede, Noord-Holland, Netherlands, Your Postcode is 2101WJ'
			' You have 2 daughters, 2 sons. Daughter 1: 9 years old, Daughter 2: 10 years old, Son1: 11 years old, son 2: 13 years old.'
			' You work in marketing as a market research analyst, earning €53,000 per year, 70 people work at your company.'
			" You have a bachelor's degree in business administration. You rent an apartment and own a mid-sized sedan."
			' You are single. You participate in surveys regularly as part of your job and personal interest.'
			' Fill out surveys naturally based on this background, making up reasonable details as needed.'

			return task

		else:
			result = "The current page does not appear to be a survey page (URL does not contain 'survey')."
			logger.info(result)
			return 'Run go_to_webpage tool. and exit'

	except Exception as e:
		# Log errors and return an informative message
		logger.error(f'Error checking if page is a survey: {e}', exc_info=True)
		return f'Error occurred while checking the page URL: {e}'


async def main():
	browser = Browser(
		config=BrowserConfig(
			# Specify the path to your Chrome executable
			chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # type: ignore
		)
	)
	# Initialize the model
	llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))  # type: ignore

	agent = Agent(task='Run the initial_check tool', llm=llm, browser=browser)
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
