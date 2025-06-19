import os
import pytest
import requests
import requests_mock
from hypothesis import given, strategies as st
from trailsave import get_github_issues  # Replace your_module

# --- Fixtures ---
@pytest.fixture
def github_token():
    """Provides a mock GitHub token."""
    return "test_github_token"

@pytest.fixture
def repo_owner():
    """Provides a mock repo owner."""
    return "test_owner"

@pytest.fixture
def repo_name():
    """Provides a mock repo name."""
    return "test_repo"

@pytest.fixture
def project_number():
    """Provides a mock project number."""
    return 12345

@pytest.fixture
def column_names():
    """Provides mock column names."""
    return ["To Do", "In Progress"]

@pytest.fixture
def mock_github_api(requests_mock, github_token, repo_owner, repo_name, project_number, column_names):
    """Mocks the GitHub API endpoints."""
    # Mock project columns
    columns_url = f"https://api.github.com/projects/{project_number}/columns"
    columns_data = [
        {"id": 1, "name": "To Do"},
        {"id": 2, "name": "In Progress"},
        {"id": 3, "name": "Done"}
    ]
    requests_mock.get(columns_url, json=columns_data)

    # Mock column cards
    for column in columns_data:
        cards_url = f"https://api.github.com/projects/columns/{column['id']}/cards"
        cards_data = [{"content_url": f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/1"}]
        requests_mock.get(cards_url, json=cards_data)

    # Mock issue details
    issue_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/1"
    issue_data = {"title": "Test Issue", "number": 1}
    requests_mock.get(issue_url, json=issue_data)

    return requests_mock

# --- Unit Tests ---
def test_get_github_issues_success(mock_github_api, github_token, repo_owner, repo_name, project_number, column_names):
    """Tests the successful retrieval of GitHub issues."""
    issues = get_github_issues(repo_owner, repo_name, project_number, github_token, column_names)
    assert len(issues) == 2
    assert issues[0]["title"] == "Test Issue"
    assert issues[0]["number"] == 1

def test_get_github_issues_no_columns_found(requests_mock, github_token, repo_owner, repo_name, project_number):
    """Tests the scenario when no matching columns are found."""
    columns_url = f"https://api.github.com/projects/{project_number}/columns"
    columns_data = [{"id": 1, "name": "Not To Do"}]
    requests_mock.get(columns_url, json=columns_data)

    issues = get_github_issues(repo_owner, repo_name, project_number, github_token, ["To Do"])
    assert issues == []

def test_get_github_issues_request_exception(requests_mock, github_token, repo_owner, repo_name, project_number, column_names):
    """Tests the function's behavior when a request exception occurs."""
    columns_url = f"https://api.github.com/projects/{project_number}/columns"
    requests_mock.get(columns_url, exc=requests.exceptions.RequestException("API Error"))

    issues = get_github_issues(repo_owner, repo_name, project_number, github_token, column_names)
    assert issues == []

def test_get_github_issues_column_name_not_found(requests_mock, github_token, repo_owner, repo_name, project_number):
    """Tests the scenario when a column name is not found."""
    columns_url = f"https://api.github.com/projects/{project_number}/columns"
    columns_data = [{"id": 1, "name": "To Do"}]
    requests_mock.get(columns_url, json=columns_data)

    issues = get_github_issues(repo_owner, repo_name, project_number, github_token, ["NonExistentColumn"])
    assert issues == []

# --- Property-Based Tests ---
@given(project_number=st.integers(max_value=0))
def test_get_github_issues_invalid_project_number(project_number):
    github_token = "test_github_token"
    repo_owner = "test_owner"
    repo_name = "test_repo"
    column_names = ["To Do", "In Progress"]

    columns_url = f"https://api.github.com/projects/{project_number}/columns"
    with requests_mock.Mocker() as m:
        m.get(columns_url, json=[])
        issues = get_github_issues(repo_owner, repo_name, project_number, github_token, column_names)
        assert issues == []

@given(column_names=st.lists(st.text(), min_size=0, max_size=0))
def test_get_github_issues_empty_column_names(column_names):
    github_token = "test_github_token"
    repo_owner = "test_owner"
    repo_name = "test_repo"
    project_number = 12345

    columns_url = f"https://api.github.com/projects/{project_number}/columns"
    with requests_mock.Mocker() as m:
        m.get(columns_url, json=[])
        issues = get_github_issues(repo_owner, repo_name, project_number, github_token, column_names)
        assert issues == []


# --- Integration Tests ---
def test_get_github_issues_integration(github_token, repo_owner, repo_name, project_number, column_names):
    """
    Integration test to verify the interaction with the GitHub API.
    This test requires a real GitHub repository and project. It is currently configured to return an empty list,
    as real tokens and repository details are required. To enable this test, replace the mock values with real values
    and ensure that the GITHUB_TOKEN environment variable is set.
    """
    # This test will likely fail without proper setup (real repo, project, and token).
    # It's designed to verify the end-to-end flow when properly configured.
    issues = get_github_issues(repo_owner, repo_name, project_number, github_token, column_names)
    assert issues == []
