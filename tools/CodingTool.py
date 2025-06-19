import os
import google.generativeai as genai
from GitHubTool import GithubTool


os.environ["API_KEY"] = 'KEY_HERE'

class DeveloperTool():
    def __init__(self):
        GOOGLE_API_KEY  = os.environ["API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
   
    def generate_code(self):
        GITHUB_TOKEN = "TOKEN_HERE"
        OWNER = "kamsur"
        REPO = "HACKBAY_2k25_SAINT"
        TARGET_PROJECT = "HACKBAY_2025"

        tool = GithubTool(OWNER, GITHUB_TOKEN)
        tool.fetch_kanban_board(REPO,TARGET_PROJECT)

        description = tool.fetch_issue_description(2)
        
        print(description)
        response = self.model.generate_content(f"Write python code for the following:\n{description}")
        print(response.text)


if __name__ == "__main__":
    tool = CodingTool()
    tool.generate_code()





