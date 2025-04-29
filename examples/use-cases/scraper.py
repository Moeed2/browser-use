import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from browser_use import Agent, Browser, Controller
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContext

load_dotenv()

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
	f'Go to Prizerebel.com. Select a survey that starts with #. {SURVEY_TASK}'
)


async def main():
	browser = Browser(
		config=BrowserConfig(
			chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
		)
	)

	llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))

	agent = Agent(
		task=f"Analyse the current page's details you have been given, does it url contain 'survey' or 'screening'? or 'samplicio' or 'profiler'? If Yes your ultimate task is: {SURVEY_TASK}, else it is: {NO_SURVEY_TASK} ",
		llm=llm,
		browser=browser,
	)
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
