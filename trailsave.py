import argparse
import json
import os
import requests


def fetch_project_board_issues(owner, repo, project_number, github_token):
    """
    Fetches issues from a GitHub Project board using the GraphQL API.
    """
    query = """
    query {
      repository(owner: "%s", name: "%s") {
        projectV2(number: %d) {
          items(first: 100) {
            nodes {
              id
              type
              content {
                ... on Issue {
                  title
                  url
                  number
                  assignees(first:5) {
                    nodes {
                      login
                    }
                  }
                  labels(first:5) {
                    nodes {
                      name
                    }
                  }
                  bodyText
                }
              }
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field {
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """ % (owner, repo, project_number)

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }
    request = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers=headers,
        timeout=10,
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Request failed with status code: {}. {}".format(
                request.status_code, request.content
            )
        )


def format_issues(data):
    """
    Formats the retrieved issues into a more readable JSON format.
    """
    formatted_issues = []
    try:
        items = data["data"]["repository"]["projectV2"]["items"]["nodes"]
        for item in items:
            if item["type"] == "ISSUE":
                issue = item["content"]
                status = "N/A"  # Default status

                # Extract status from fieldValues
                for fieldValue in item["fieldValues"]["nodes"]:
                    if "field" in fieldValue and "name" in fieldValue["field"] and fieldValue["field"]["name"] == "Status":
                        status = fieldValue["name"]
                        break

                assignees = [
                    assignee["login"] for assignee in issue["assignees"]["nodes"]
                ]
                labels = [label["name"] for label in issue["labels"]["nodes"]]

                formatted_issue = {
                    "title": issue["title"],
                    "url": issue["url"],
                    "number": issue["number"],
                    "assignees": assignees,
                    "labels": labels,
                    "status": status,
                    "body": issue["bodyText"],
                }
                formatted_issues.append(formatted_issue)
    except (KeyError, TypeError) as e:
        print(f"Error formatting issues: {e}")
        return None

    return formatted_issues


def main():
    """
    Main function to parse arguments, fetch issues, and display them.
    """
    # parser = argparse.ArgumentParser(
    #     description="Fetch issues from a GitHub Project board."
    # )
    # parser.add_argument(
    #     "--owner", required=True, help="Repository owner (e.g., your-org)"
    # )
    # parser.add_argument(
    #     "--repo", required=True, help="Repository name (e.g., your-repo)"
    # )
    # parser.add_argument(
    #     "--project_number", required=True, type=int, help="Project number (e.g., 1)"
    # )
    # parser.add_argument(
    #     "--github_token",
    #     required=True,
    #     help="GitHub token with read:project scope",
    # )

    # args = parser.parse_args()

    PROJECT_NUMBER = 1
    GITHUB_TOKEN = "TOKEN_HERE"  # Replace with your GitHub token
    OWNER = "kamsur"
    REPO = "HACKBAY_2k25_SAINT"

    try:
        # data = fetch_project_board_issues(
        #     args.owner, args.repo, args.project_number, args.github_token
        # )
        data = fetch_project_board_issues(
            OWNER, REPO, PROJECT_NUMBER, GITHUB_TOKEN
        )
        if data:
            formatted_issues = format_issues(data)
            if formatted_issues:
                print(json.dumps(formatted_issues, indent=2))
            else:
                print("No issues found or an error occurred during formatting.")
        else:
            print("Could not retrieve data from GitHub API.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()