# Goal: Checks for available visa appointment slots on the Greece MFA website.

import asyncio
import logging # Added for logging
import os

# Imports for recording hook
import requests
from pyobjtojson import obj_to_json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr

# Import BrowserContext if needed by hooks (though agent_obj has it)
from browser_use.agent.service import Agent, BrowserContext
from browser_use.controller.service import Controller

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Configure basic logging for visibility
if not os.getenv('OPENAI_API_KEY'):
	raise ValueError('OPENAI_API_KEY is not set. Please add it to your environment variables.')

controller = Controller()


class WebpageInfo(BaseModel):
	"""Model for webpage link."""

	link: str = 'https://appointment.mfa.gr/en/reservations/aero/ireland-grcon-dub/'


@controller.action('Go to the webpage', param_model=WebpageInfo)
def go_to_webpage(webpage_info: WebpageInfo):
	"""Returns the webpage link."""
	return webpage_info.link


# --- Recording Hook Functions ---

def send_agent_history_step(data):
	"""Sends agent step data to the recording API."""
	url = 'http://127.0.0.1:9000/post_agent_history_step' # Ensure the API server is running
	try:
		response = requests.post(url, json=data, timeout=10) # Added timeout
		response.raise_for_status() # Raise an exception for bad status codes
		logger.info(f"Successfully sent step data to recording API: {response.json()}")
		return response.json()
	except requests.exceptions.RequestException as e:
		logger.error(f"Failed to send step data to recording API: {e}")
		return None # Return None or indicate failure

async def record_activity(agent_obj: Agent):
	"""Hook function called before each agent step to record activity."""
	website_html = None
	website_screenshot = None
	urls_json_last_elem = None
	model_thoughts_last_elem = None
	model_outputs_json_last_elem = None
	model_actions_json_last_elem = None
	extracted_content_json_last_elem = None

	logger.info('--- ON_STEP_START HOOK: Recording Activity ---')
	try:
		# Ensure browser_context is available and get page data
		if agent_obj.browser_context:
			website_html: str = await agent_obj.browser_context.get_page_html()
			# Limit screenshot size if needed, or omit if too large/slow
			website_screenshot: str = await agent_obj.browser_context.take_screenshot()
		else:
			logger.warning("Browser context not available in agent object for recording.")
			website_html = "Browser context not available"
			website_screenshot = "Browser context not available"


		# Safely access history and its components
		history = getattr(agent_obj.state, 'history', None)
		if history:
			# Use safe_serialization for potentially complex/unserializable objects
			model_thoughts = obj_to_json(obj=history.model_thoughts(), check_circular=False, safe_serialization=True)
			if model_thoughts:
				model_thoughts_last_elem = model_thoughts[-1]

			model_outputs = history.model_outputs()
			model_outputs_json = obj_to_json(obj=model_outputs, check_circular=False, safe_serialization=True)
			if model_outputs_json:
				model_outputs_json_last_elem = model_outputs_json[-1]

			model_actions = history.model_actions()
			model_actions_json = obj_to_json(obj=model_actions, check_circular=False, safe_serialization=True)
			if model_actions_json:
				model_actions_json_last_elem = model_actions_json[-1]

			extracted_content = history.extracted_content()
			extracted_content_json = obj_to_json(obj=extracted_content, check_circular=False, safe_serialization=True)
			if extracted_content_json:
				extracted_content_json_last_elem = extracted_content_json[-1]

			urls = history.urls()
			urls_json = obj_to_json(obj=urls, check_circular=False, safe_serialization=True)
			if urls_json:
				urls_json_last_elem = urls_json[-1]
		else:
			logger.warning("Agent state or history not available for recording.")


		model_step_summary = {
			'website_html': website_html, # Consider truncating or omitting if too large
			'website_screenshot': website_screenshot, # Consider omitting if too large/slow
			'url': urls_json_last_elem,
			'model_thoughts': model_thoughts_last_elem,
			'model_outputs': model_outputs_json_last_elem,
			'model_actions': model_actions_json_last_elem,
			'extracted_content': extracted_content_json_last_elem,
		}

		logger.info('--- Sending Model Step Summary to API ---')
		send_agent_history_step(data=model_step_summary)

	except Exception as e:
		logger.error(f"Error during record_activity hook: {e}", exc_info=True)

# --- Main Execution ---

async def main():
	"""Main function to execute the agent task."""
	task = (
		'Go to the Greece MFA webpage via the link I provided you.'
		'Check the visa appointment dates. If there is no available date in this month, check the next month.'
		'If there is no available date in both months, tell me there is no available date.'
	)

	model = ChatOpenAI(model='gpt-4o-mini', api_key=SecretStr(os.getenv('OPENAI_API_KEY', '')))
	# Note: Browser instance is created internally by Agent if not provided
	agent = Agent(task, model, controller=controller, use_vision=True)

	# Add the hook to the run call
	await agent.run(on_step_start=record_activity)


if __name__ == '__main__':
	# Ensure the recording API server is running before executing main()
	# Example: Run the server part of custom_hooks_before_after_step.py in a separate terminal:
	# python examples/custom-functions/custom_hooks_before_after_step.py

	# Run the agent
	asyncio.run(main())
