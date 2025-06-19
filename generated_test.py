# test_fetch_project_board_issues.py
import pytest
from unittest.mock import patch
from trailsave import fetch_project_board_issues

@pytest.fixture
def mock_response():
    return {
        "data": {
            "repository": {
                "projectV2": {
                    "items": {
                        "nodes": [
                            {
                                "id": "1",
                                "type": "ISSUE",
                                "content": {
                                    "title": "Test Issue",
                                    "url": "https://github.com/test/issue",
                                    "number": 1,
                                    "assignees": {
                                        "nodes": [{"login": "test-user"}]
                                    },
                                    "labels": {
                                        "nodes": [{"name": "test-label"}]
                                    },
                                    "bodyText": "Test issue body"
                                },
                                "fieldValues": {
                                    "nodes": [
                                        {
                                            "name": "In Progress",
                                            "field": {"name": "Status"}
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

@pytest.fixture
def mock_error_response():
    return {"error": "Invalid token"}

def test_fetch_project_board_issues_success(mock_response):
    with patch('requests.post') as mock_post:
        mock_post.return_value.json = lambda: mock_response
        mock_post.return_value.status_code = 200
        
        result = fetch_project_board_issues(
            "test-owner", "test-repo", 1, "test-token"
        )
        
        assert result is not None
        assert "data" in result
        assert "repository" in result["data"]
        assert "projectV2" in result["data"]["repository"]
        assert "items" in result["data"]["repository"]["projectV2"]

def test_fetch_project_board_issues_error(mock_error_response):
    with patch('requests.post') as mock_post:
        mock_post.return_value.json = lambda: mock_error_response
        mock_post.return_value.status_code = 404
        
        with pytest.raises(Exception):
            fetch_project_board_issues(
                "test-owner", "test-repo", 1, "test-token"
            )

def test_fetch_project_board_issues_connection_error():
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(Exception):
            fetch_project_board_issues(
                "test-owner", "test-repo", 1, "test-token"
            )

# test_format_issues.py
import json
from trailsave import format_issues

def test_format_issues_success():
    sample_data = {
        "data": {
            "repository": {
                "projectV2": {
                    "items": {
                        "nodes": [
                            {
                                "id": "1",
                                "type": "ISSUE",
                                "content": {
                                    "title": "Test Issue",
                                    "url": "https://github.com/test/issue",
                                    "number": 1,
                                    "assignees": {
                                        "nodes": [{"login": "test-user"}]
                                    },
                                    "labels": {
                                        "nodes": [{"name": "test-label"}]
                                    },
                                    "bodyText": "Test issue body"
                                },
                                "fieldValues": {
                                    "nodes": [
                                        {
                                            "name": "In Progress",
                                            "field": {"name": "Status"}
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    
    result = format_issues(sample_data)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    
    issue = result[0]
    assert "title" in issue
    assert "url" in issue
    assert "number" in issue
    assert "assignees" in issue
    assert "labels" in issue
    assert "status" in issue
    assert "body" in issue

def test_format_issues_empty_data():
    result = format_issues({})
    assert result == []

def test_format_issues_invalid_data():
    result = format_issues("invalid_data")
    assert result is None

def test_format_issues_key_error():
    sample_data = {
        "data": {
            "repository": {
                "projectV2": {
                    "items": {
                        "nodes": [
                            {
                                "id": "1",
                                "type": "ISSUE",
                                "content": {},
                                "fieldValues": {
                                    "nodes": []
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    
    result = format_issues(sample_data)
    assert result == []

# test_integration.py
import pytest
from trailsave import fetch_project_board_issues, format_issues

@pytest.fixture
def mock_api_response():
    return {
        "data": {
            "repository": {
                "projectV2": {
                    "items": {
                        "nodes": [
                            {
                                "id": "1",
                                "type": "ISSUE",
                                "content": {
                                    "title": "Test Issue",
                                    "url": "https://github.com/test/issue",
                                    "number": 1,
                                    "assignees": {
                                        "nodes": [{"login": "test-user"}]
                                    },
                                    "labels": {
                                        "nodes": [{"name": "test-label"}]
                                    },
                                    "bodyText": "Test issue body"
                                },
                                "fieldValues": {
                                    "nodes": [
                                        {
                                            "name": "In Progress",
                                            "field": {"name": "Status"}
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

def test_integration_fetch_and_format(mock_api_response):
    with patch('requests.post') as mock_post:
        mock_post.return_value.json = lambda: mock_api_response
        mock_post.return_value.status_code = 200
        
        data = fetch_project_board_issues(
            "test-owner", "test-repo", 1, "test-token"
        )
        formatted = format_issues(data)
        
        assert formatted is not None
        assert isinstance(formatted, list)
        assert len(formatted) == 1
        
        issue = formatted[0]
        assert issue["title"] == "Test Issue"
        assert issue["url"] == "https://github.com/test/issue"
        assert issue["number"] == 1
        assert issue["assignees"] == ["test-user"]
        assert issue["labels"] == ["test-label"]
        assert issue["status"] == "In Progress"
        assert issue["body"] == "Test issue body"

# conftest.py
import pytest

@pytest.fixture
def mock_api_response():
    return {
        "data": {
            "repository": {
                "projectV2": {
                    "items": {
                        "nodes": [
                            {
                                "id": "1",
                                "type": "ISSUE",
                                "content": {
                                    "title": "Test Issue",
                                    "url": "https://github.com/test/issue",
                                    "number": 1,
                                    "assignees": {
                                        "nodes": [{"login": "test-user"}]
                                    },
                                    "labels": {
                                        "nodes": [{"name": "test-label"}]
                                    },
                                    "bodyText": "Test issue body"
                                },
                                "fieldValues": {
                                    "nodes": [
                                        {
                                            "name": "In Progress",
                                            "field": {"name": "Status"}
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

@pytest.fixture
def mock_error_response():
    return {"error": "Invalid token"}