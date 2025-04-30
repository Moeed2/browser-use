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
	'You speak english and dutch.'
	'You are from Heemstede, Noord-Holland, Netherlands. '
	'Your postcode is 2101WJ, '
	'You have 2 daughters (9 and 10) and 2 sons (11 and 13). '
	'You work in marketing as a market research analyst, earning €53,000 per year. '
	"You have a bachelor's degree in business administration, rent an apartment, own a mid-sized sedan, and are single. "
	'You regularly participate in surveys. '
	'Fill out the current survey naturally based on this background, making up reasonable details as needed, avoid saying "i dont know".'
	'When doing the survey, Your goal as a test agent is to be accepted into as many surveys as possible while being realistic in your answers. Follow this protocol for answering survey questions:'
	'''- Read the question.
	- Read the answers, scroll down, to see more answers, keep scrolling down until you see a button that would take you to the next question. 
	- Determine which answer(s) You will be selecting and select those and then scroll down and click continue.
	- do not change your answer after it has been selected, you move on to the next question and then you repeat the above procedure, so you go question to question like this. When finishing a survey, never close the tab, make sure you keep pressing continue button until they redirect you to app.fivesurveys.com.'''
)
NO_SURVEY_TASK = (
	f'Go to app.fivesurveys.com Select a survey. {SURVEY_TASK}'
)


async def main():
	browser = Browser(
		config=BrowserConfig(
			chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',browser_window_size={'width': 1920, 'height': 3000},
			viewport_expansion=-1,
		)
	)
	llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-preview-04-17', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))

	agent = Agent(
		task=f"Analyse all the tabs open and check for each page, does it url contain 'survey' or 'screening'? or 'samplicio' or 'profiler'? If Yes your ultimate task is: {SURVEY_TASK}, else it is: {NO_SURVEY_TASK} ",
		llm=llm,
		browser=browser,
	)
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
