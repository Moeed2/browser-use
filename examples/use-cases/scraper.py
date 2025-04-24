import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.agent.service import BrowserContext

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

controller = Controller()

# Define your two tasks
SURVEY_TASK = (
	'You are Jan Vermeulen, a 34-year-old man (1 Januari 1990).' 
	'You are from Heemstede, Noord-Holland, Netherlands. '
	'Your postcode is 2101WJ, '
	'You have 2 daughters (9 and 10) and 2 sons (11 and 13). '
	'You work in marketing as a market research analyst, earning €53,000 per year. '
	"You have a bachelor's degree in business administration, rent an apartment, own a mid-sized sedan, and are single. "
	'You regularly participate in surveys. '
	'Fill out the current survey naturally based on this background, making up reasonable details as needed.'
)
NO_SURVEY_TASK = (
	f'Select a survey that starts with #. {SURVEY_TASK}'
)


async def check_if_survey_in_url(browser: BrowserContext):
	try:
		page = await browser.get_current_page()
		url = page.url
		logger.info(f'Current page URL: {url}')
		return SURVEY_TASK if 'survey' in url.lower() or "screening" in url.lower else NO_SURVEY_TASK
	except Exception as e:
		logger.error(f'Error checking page URL: {e}', exc_info=True)
		return 'error'


async def main():
	browser = Browser(
		config=BrowserConfig(
			chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # type: ignore
		)
	)
	llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))

	agent = Agent(
		task= check_if_survey_in_url(browser),
		llm=llm,
		browser=browser,
		controller=controller,
	)
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
