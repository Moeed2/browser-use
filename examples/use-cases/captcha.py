"""
Goal: Automates CAPTCHA solving on a demo website.


Simple try of the agent.
@dev You need to add OPENAI_API_KEY to your environment variables.
NOTE: captchas are hard. For this example it works. But e.g. for iframes it does not.
for this example it helps to zoom in.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent

# Load environment variables
load_dotenv()
if not os.getenv('GOOGLE_API_KEY'):
	raise ValueError('GOOGLE_API_KEY is not set. Please add it to your environment variables.')


async def main():
	# Use Gemini Flash 2.0
	llm = ChatGoogleGenerativeAI(model='gemini-flash-2.0')
	agent = Agent(
		task='go to https://captcha.com/demos/features/captcha-demo.aspx and solve the captcha',
		llm=llm,
	)
	await agent.run()
	input('Press Enter to exit')


if __name__ == '__main__':
	asyncio.run(main())
