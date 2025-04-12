import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Assuming survey_actions.py is in the browser_use package
# Adjust the import path if you placed survey_actions.py elsewhere
from browser_use.agent.survey_actions import (
    FillTextFieldByLabelParams,
    SelectRadioButtonParams,
    fill_text_field_by_label,
    select_radio_button,
)
from browser_use import Agent, Controller, BrowserContext # Added BrowserContext import

load_dotenv()

# Initialize the controller
# If you need context specific to surveys, you might define a context class
# controller = Controller[SurveyContext]()
controller = Controller()


# Register the custom survey actions
# The agent will now be able to use these actions if the LLM decides they are appropriate
@controller.registry.action(
    description=select_radio_button.__doc__, # Use docstring for description
    param_model=SelectRadioButtonParams,
)
async def register_select_radio_button(params: SelectRadioButtonParams, browser: BrowserContext):
    # This registration function just calls the actual implementation
    # It ensures the function signature matches what the registry expects
    # (i.e., includes the 'browser' parameter if needed)
    return await select_radio_button(params, browser)

@controller.registry.action(
    description=fill_text_field_by_label.__doc__,
    param_model=FillTextFieldByLabelParams,
)
async def register_fill_text_field_by_label(params: FillTextFieldByLabelParams, browser: BrowserContext):
    # Similarly, call the actual implementation
    return await fill_text_field_by_label(params, browser)


# --- You would still need a way to signal completion ---
# Option 1: Keep a simple 'done' action
# from browser_use.agent.actions import DoneAction # Import default DoneAction
# @controller.registry.action(description="Signal that the task is complete.", param_model=DoneAction)
# async def done(params: DoneAction):
#     # The default DoneAction just needs a 'result' text
#     return {"result": params.result, "is_done": True}

# Option 2: Or define your own completion action if needed


async def main():
    # Example task using the new actions
    task = 'Go to https://example-survey.com, answer the first question "Your Name" with "Test User", select "Option 2" for the question "Preferred Choice", and then submit the form.'
    # NOTE: The actual implementation of the survey actions in survey_actions.py is still needed!

    model = ChatOpenAI(model='gpt-4o', temperature=0.0) # Use low temperature for predictable actions

    # The Agent needs the controller with the registered actions
    # It also needs a browser instance to pass to the actions
    # We'll create a dummy agent run here, assuming browser setup happens elsewhere
    # In a real scenario, you'd initialize Browser and BrowserContext:
    # browser = Browser()
    # async with BrowserContext(browser=browser) as context:
    #     agent = Agent(task=task, llm=model, controller=controller, browser=context)
    #     await agent.run()

    print("Example setup complete. Agent would run with the following configuration:")
    print(f"Task: {task}")
    print(f"LLM: {model.model_name}")
    print("Registered Actions:")
    for name, action in controller.registry.registry.actions.items():
        print(f"- {name}: {action.description[:60]}...") # Print first 60 chars of description

    # Placeholder for actual agent run
    print("\nNote: Agent run is commented out. Implement survey action logic and browser setup to run.")


if __name__ == '__main__':
	asyncio.run(main())
