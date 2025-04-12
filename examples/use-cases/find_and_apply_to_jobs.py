# --- Docstring ---
"""
Goal: Searches for job listings, evaluates relevance based on a CV, and applies

@dev You need to add OPENAI_API_KEY to your environment variables.
Also you have to install PyPDF2 to read pdf files: pip install PyPDF2
"""

# --- Standard Library Imports ---
import asyncio  # For running asynchronous operations
import csv  # For reading and writing CSV files (jobs.csv)
import logging  # For logging information and errors
import os  # For accessing environment variables and file system paths
import sys  # For manipulating Python runtime environment (like sys.path)
from pathlib import Path  # For object-oriented filesystem paths (CV path)
from typing import Optional  # For type hinting optional values

# --- Add Project Root to Python Path ---
# This allows importing modules from the parent directory (e.g., browser_use)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Third-Party Library Imports ---
from dotenv import load_dotenv  # For loading environment variables from a .env file
from langchain_openai import AzureChatOpenAI  # For interacting with Azure OpenAI models
from pydantic import BaseModel, SecretStr  # For data validation and settings management (Job model, API keys)
from PyPDF2 import PdfReader  # For reading text content from PDF files (CV)

# --- Local Application/Library Specific Imports ---
from browser_use import ActionResult, Agent, Controller  # Core components for the agent and actions
from browser_use.browser.browser import Browser, BrowserConfig  # Browser automation setup
from browser_use.browser.context import BrowserContext  # Browser context management

# --- Environment Variable Validation ---
load_dotenv()  # Load variables from .env file into environment
required_env_vars = ['AZURE_OPENAI_KEY', 'AZURE_OPENAI_ENDPOINT']  # List of required environment variables
for var in required_env_vars:  # Loop through the required variables
	if not os.getenv(var):  # Check if the variable is set in the environment
		# If a required variable is missing, raise an error
		raise ValueError(f'{var} is not set. Please add it to your environment variables.')

# --- Logging Setup ---
logger = logging.getLogger(__name__)  # Get a logger instance for this module

# --- Controller Initialization ---
# The Controller manages available actions for the agent
controller = Controller()

# --- Configuration: CV Path ---
# NOTE: This is the path to your cv file
# Define the path to the Curriculum Vitae (CV) PDF file relative to the current working directory
CV = Path.cwd() / 'cv_04_24.pdf'

# --- CV File Existence Check ---
if not CV.exists():  # Check if the specified CV file exists
	# If the CV file is not found, raise an error
	raise FileNotFoundError(f'You need to set the path to your cv file in the CV variable. CV file not found at {CV}')

# --- Data Model Definition ---
# Define a Pydantic model to structure job information
class Job(BaseModel):
	title: str  # Job title
	link: str  # Link to the job posting
	company: str  # Company name
	fit_score: float  # Score indicating how well the job fits the profile (assigned by the LLM)
	location: Optional[str] = None  # Optional: Job location
	salary: Optional[str] = None  # Optional: Job salary information

# --- Agent Action: Save Jobs ---
# Decorator registers the function as an action the agent can perform
# 'Save jobs to file...' is the description shown to the LLM
# param_model=Job specifies the expected input structure for this action
@controller.action('Save jobs to file - with a score how well it fits to my profile', param_model=Job)
def save_jobs(job: Job):  # Function takes a Job object as input
	# Open 'jobs.csv' in append mode ('a') so new jobs are added without overwriting
	with open('jobs.csv', 'a', newline='') as f:
		writer = csv.writer(f)  # Create a CSV writer object
		# Write the job details as a new row in the CSV file
		writer.writerow([job.title, job.company, job.link, job.salary, job.location])

	return 'Saved job to file'  # Return a confirmation message to the agent

# --- Agent Action: Read Jobs ---
# Register the function as an action to read the saved jobs file
@controller.action('Read jobs from file')
def read_jobs():
	# Open 'jobs.csv' in read mode ('r')
	with open('jobs.csv', 'r') as f:
		return f.read()  # Read the entire content of the file and return it

# --- Agent Action: Read CV ---
# Register the function as an action to read the content of the CV PDF
@controller.action('Read my cv for context to fill forms')
def read_cv():
	pdf = PdfReader(CV)  # Create a PdfReader object with the CV file path
	text = ''  # Initialize an empty string to store the extracted text
	for page in pdf.pages:  # Iterate through each page in the PDF
		text += page.extract_text() or ''  # Extract text from the page and append it; use empty string if extraction fails
	logger.info(f'Read cv with {len(text)} characters')  # Log the number of characters read
	# Return an ActionResult containing the CV text; include_in_memory=True tells the agent to remember this content
	return ActionResult(extracted_content=text, include_in_memory=True)

# --- Agent Action: Upload CV ---
# Register the function as an asynchronous action to upload the CV file to a web element
@controller.action(
	'Upload cv to element - call this function to upload if element is not found, try with different index of the same upload element',
)
async def upload_cv(index: int, browser: BrowserContext):  # Takes element index and browser context
	path = str(CV.absolute())  # Get the absolute path of the CV file as a string
	# Try to get the DOM element corresponding to the given index from the browser context
	dom_el = await browser.get_dom_element_by_index(index)

	# If no element is found at the specified index
	if dom_el is None:
		return ActionResult(error=f'No element found at index {index}')  # Return an error result

	# Check if the found element (or its siblings) is a file input element
	file_upload_dom_el = dom_el.get_file_upload_element()

	# If no suitable file upload element is associated with the index
	if file_upload_dom_el is None:
		logger.info(f'No file upload element found at index {index}')
		return ActionResult(error=f'No file upload element found at index {index}')  # Return an error result

	# Get the actual Playwright element handle for the file upload input
	file_upload_el = await browser.get_locate_element(file_upload_dom_el)

	# If the Playwright element handle couldn't be obtained
	if file_upload_el is None:
		logger.info(f'No file upload element found at index {index}')
		return ActionResult(error=f'No file upload element found at index {index}')  # Return an error result

	# Try to set the input files for the located element handle
	try:
		await file_upload_el.set_input_files(path)  # Perform the file upload via Playwright
		msg = f'Successfully uploaded file "{path}" to index {index}'  # Success message
		logger.info(msg)  # Log the success
		return ActionResult(extracted_content=msg)  # Return a success result with the message
	except Exception as e:  # Catch any exception during the upload process
		logger.debug(f'Error in set_input_files: {str(e)}')  # Log the specific error for debugging
		return ActionResult(error=f'Failed to upload file to index {index}')  # Return a generic error result

# --- Browser Initialization ---
# Create a Browser instance with specific configuration
browser = Browser(
	config=BrowserConfig(
		# Specify the path to the Chrome executable (adjust if necessary for your system)
		browser_binary_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
		# Disable web security features (useful for automation, but use with caution)
		disable_security=True,
	)
)

# --- Main Asynchronous Function ---
async def main():
	# Define the base instruction/prompt for the agent
	# (Commented out section shows an alternative task focused on applying to a specific job)
	# ground_task = (
	# 	'You are a professional job finder. '
	# 	'1. Read my cv with read_cv'
	# 	'2. Read the saved jobs file '
	# 	'3. start applying to the first link of Amazon '
	# 	'You can navigate through pages e.g. by scrolling '
	# 	'Make sure to be on the english version of the page'
	# )
	ground_task = (  # The primary task description for the LLM agent
		'You are a professional job finder. '
		'1. Read my cv with read_cv'  # Instruct the agent to first read the CV
		'find ml internships in and save them to a file'  # Instruct the agent to find and save ML internships
		'search at company:'  # Base instruction, company name will be appended
	)
	# Define a list of tasks, each combining the ground task with a specific company
	tasks = [
		ground_task + '\n' + 'Google',  # Task: Find ML internships at Google
		# ground_task + '\n' + 'Amazon', # Example of other potential tasks (commented out)
		# ground_task + '\n' + 'Apple',
		# ground_task + '\n' + 'Microsoft',
		# Example of a task navigating to a specific URL (commented out)
		# ground_task
		# + '\n'
		# + 'go to https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Taiwan%2C-Remote/Fulfillment-Analyst---New-College-Graduate-2025_JR1988949/apply/autofillWithResume?workerSubType=0c40f6bd1d8f10adf6dae42e46d44a17&workerSubType=ab40a98049581037a3ada55b087049b7 NVIDIA',
		# ground_task + '\n' + 'Meta',
	]
	# --- Language Model Initialization ---
	# Configure and initialize the Azure OpenAI chat model
	model = AzureChatOpenAI(
		model='gpt-4o',  # Specify the model version to use
		api_version='2024-10-21',  # Specify the API version
		azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', ''),  # Get Azure endpoint from environment variables
		api_key=SecretStr(os.getenv('AZURE_OPENAI_KEY', '')),  # Get Azure API key from environment variables (as SecretStr)
	)

	# --- Agent Creation ---
	agents = []  # Initialize an empty list to hold the agent instances
	for task in tasks:  # Loop through each defined task
		# Create an Agent instance for each task
		agent = Agent(
			task=task,  # The specific instruction for this agent instance
			llm=model,  # The language model the agent will use
			controller=controller,  # The controller providing available actions
			browser=browser  # The shared browser instance for web interaction
		)
		agents.append(agent)  # Add the created agent to the list

	# --- Run Agents Concurrently ---
	# Use asyncio.gather to run the 'run' method of all agents concurrently
	# This allows multiple job searches/applications to happen in parallel
	await asyncio.gather(*[agent.run() for agent in agents])

# --- Script Execution Entry Point ---
if __name__ == '__main__':  # Standard Python check: ensures the code runs only when the script is executed directly
	asyncio.run(main())  # Run the main asynchronous function using asyncio's event loop
