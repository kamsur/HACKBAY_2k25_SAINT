import requests
import sqlite3

class GithubTool():
    def __init__(self, owner, repo, token):
        self.owner = owner       
        self.repo = repo
        self.token = token

    def fetch_kanban_board(self, target_project):       

        conn = sqlite3.connect("GitHub_Issues.db")
        cursor = conn.cursor()


        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json"
        }

        url = "https://api.github.com/graphql"

        query = f"""
        query {{
        repository(owner: "{self.owner}", name: "{self.repo}") {{
            projectsV2(first: 10) {{
            nodes {{
                title
                id
                items(first: 100) {{
                nodes {{
                    content {{
                    ... on Issue {{
                        title
                        number
                        url
                        state
                    }}
                    }}
                    fieldValues(first: 20) {{
                    nodes {{
                        ... on ProjectV2ItemFieldSingleSelectValue {{
                        name
                        field {{
                            ... on ProjectV2SingleSelectField {{
                            name
                            }}
                        }}
                        }}
                    }}
                    }}
                }}
                }}
            }}
            }}
        }}
        }}
        """

        response = requests.post(url, headers=headers, json={"query": query})
        response.raise_for_status()
        data = response.json()

        projects = data["data"]["repository"]["projectsV2"]["nodes"]

        # Find the target project
        project = next((p for p in projects if p["title"] == target_project), None)
        if not project:
            print(f"❌ Project '{target_project}' not found.")
            return

        print(f"\n📘 Project: {project['title']}")

        # Buckets for status
        status_buckets = {
            "Product Backlog": [],
            "Sprint Backlog": [],
            "In Progress": [],
            "Awaiting Review": [],
            "Feature Archive": []
        }

     
        # Process items
        for item in project["items"]["nodes"]:
            content = item["content"]
            if not content:
                continue

            # Extract status field value
            status = None
            for field in item["fieldValues"]["nodes"]:
                if field.get("field", {}).get("name") == "Status":
                    status = field.get("name")
                    break

            if status in status_buckets:
                status_buckets[status].append([content['number'], content['title'], content['url']])

        #Print grouped items
        for status, items in status_buckets.items():
            table_name = status.replace(" ", "").replace("-", "").replace(".", "")

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                ID INTEGER PRIMARY KEY,
                TITLE TEXT NOT NULL,
                URL TEXT NOT NULL
            )
            """)
          
            for item in items:
                cursor.execute(f"""
                INSERT OR IGNORE INTO {table_name} (ID, Title, URL) VALUES (?, ?, ?)
                """, (item[0], item[1], item[2]))


        conn.commit()
        conn.close()


    def fetch_issue_description(self, issue_number):
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{issue_number}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}"
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("body")
        else:
            return f'Failed {response.status_code}'
        
    
    def post_to_kanban_board(self, target_project, issue_title, issue_body, kanban_board_column):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        def run_graphql(query, variables=None):
            url = "https://api.github.com/graphql"
            json_data = {"query": query}
            if variables:
                json_data["variables"] = variables
            response = requests.post(url, json=json_data, headers=headers)
            data = response.json()
            if "errors" in data:
                raise Exception(data["errors"])
            return data["data"]

        def get_project_id_by_name(target_project):
            query = """
            query($projectName: String!) {
                viewer {
                projectsV2(first: 20, query: $projectName) {
                    nodes {
                    id
                    title
                    }
                }
                }
            }
            """
            data = run_graphql(query, {"projectName": target_project})
            projects = data["viewer"]["projectsV2"]["nodes"]
            for project in projects:
                if project["title"].lower() == target_project.lower():
                    return project["id"]
            raise Exception(f"Project named '{target_project}' not found.")

        def get_repository_id(owner, name):
            query = """
            query($owner: String!, $name: String!) {
                repository(owner: $owner, name: $name) {
                id
                }
            }
            """
            data = run_graphql(query, {"owner": owner, "name": name})
            return data["repository"]["id"]

        def create_issue(repository_id, title, body):
            mutation = """
            mutation($repositoryId: ID!, $title: String!, $body: String!) {
                createIssue(input: {
                repositoryId: $repositoryId,
                title: $title,
                body: $body
                }) {
                issue {
                    id
                    url
                }
                }
            }
            """
            data = run_graphql(mutation, {"repositoryId": repository_id, "title": title, "body": body})
            issue = data["createIssue"]["issue"]
            print("✅ Created issue:", issue["url"])
            return issue["id"]

        def add_issue_to_project(project_id, issue_id):
            mutation = """
            mutation($projectId: ID!, $contentId: ID!) {
                addProjectV2ItemById(input: {
                projectId: $projectId,
                contentId: $contentId
                }) {
                item {
                    id
                }
                }
            }
            """
            data = run_graphql(mutation, {"projectId": project_id, "contentId": issue_id})
            return data["addProjectV2ItemById"]["item"]["id"]

        def get_field_and_option_id(project_id, field_name, option_name):
            query = """
            query($projectId: ID!) {
                node(id: $projectId) {
                ... on ProjectV2 {
                    fields(first: 50) {
                    nodes {
                        __typename
                        ... on ProjectV2SingleSelectField {
                        id
                        name
                        options {
                            id
                            name
                        }
                        }
                    }
                    }
                }
                }
            }
            """
            data = run_graphql(query, {"projectId": project_id})
            fields = data["node"]["fields"]["nodes"]
            for field in fields:
                if field["__typename"] != "ProjectV2SingleSelectField":
                    continue  # Skip non-single-select fields
                if field["name"].lower() == field_name.lower():
                    for option in field["options"]:
                        if option["name"].lower() == option_name.lower():
                            return field["id"], option["id"]
                    raise Exception(f"Option '{option_name}' not found in field '{field_name}'.")
            raise Exception(f"Field '{field_name}' not found.")

        def update_project_item_field(project_id, item_id, field_id, option_id):
            mutation = """
            mutation(
                $projectId: ID!,
                $itemId: ID!,
                $fieldId: ID!,
                $value: ProjectV2FieldValue!
            ) {
                updateProjectV2ItemFieldValue(input: {
                projectId: $projectId,
                itemId: $itemId,
                fieldId: $fieldId,
                value: $value
                }) {
                projectV2Item {
                    id
                }
                }
            }
            """
            value = {"singleSelectOptionId": option_id}
            run_graphql(
                mutation,
                {
                    "projectId": project_id,
                    "itemId": item_id,
                    "fieldId": field_id,
                    "value": value,
                },
            )
            print(f"✅ Set project field '{field_id}' to option '{option_id}' on item '{item_id}'.")

        # === Main execution flow ===

        project_id = get_project_id_by_name(target_project)
        repository_id = get_repository_id(self.owner, self.repo)
        issue_id = create_issue(repository_id, issue_title, issue_body)
        project_item_id = add_issue_to_project(project_id, issue_id)
        field_id, option_id = get_field_and_option_id(project_id, "Status", kanban_board_column)
        update_project_item_field(project_id, project_item_id, field_id, option_id)






# Run
if __name__ == "__main__":
    # GitHub configuration
    GITHUB_TOKEN = "TOKEN_HERE"
    OWNER = "kamsur"
    REPO = "HACKBAY_2k25_SAINT"
    TARGET_PROJECT = "HACKBAY_2025"

    # GITHUB_TOKEN = "TOKEN_HERE"
    # OWNER = "amosproj"
    # REPO = "amos2025ss02-building-documentation-management-system"
    # TARGET_PROJECT = "amos2025ss02-feature-board"

    tool = GithubTool(OWNER, REPO, GITHUB_TOKEN)
    tool.fetch_kanban_board(TARGET_PROJECT)

    print(tool.fetch_issue_description(2))

    ISSUE_TITLE = "Pipeline Test"
    ISSUE_BODY = "This is a test issue created via script."
    KANBAN_BOARD_COLUMN = "Product Backlog"  # The option inside that field

    tool.post_to_kanban_board(TARGET_PROJECT, ISSUE_TITLE, ISSUE_BODY, KANBAN_BOARD_COLUMN)
 
