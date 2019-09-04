import os.path

"""
Base settings
"""

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_WEBSITE_RETRIES = 3
CLEANING_TASK_LIST_URL = 'https://www.os3.nl/{}/students/playground/cleaning'
EMAIL_TEMPLATE = 'this_weeks_cleaning_tasks.email.jn2'
