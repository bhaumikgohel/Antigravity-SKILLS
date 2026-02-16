import sys
import argparse

def create_jira_bug(title, description, priority, severity, project="QA"):
    """
    Skeleton script for JIRA API integration.
    In a real scenario, this would use the 'requests' library to call:
    POST /rest/api/2/issue
    """
    print(f"--- SIMULATING JIRA TICKET CREATION ---")
    print(f"Project: {project}")
    print(f"Title: {title}")
    print(f"Priority: {priority}")
    print(f"Severity: {severity}")
    print(f"Description:\n{description}")
    print(f"----------------------------------------")
    return "JIRA-123"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a JIRA bug ticket.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--priority", default="Medium")
    parser.add_argument("--severity", default="S3")
    
    args = parser.parse_args()
    
    ticket_id = create_jira_bug(args.title, args.description, args.priority, args.severity)
    print(f"Successfully created ticket: {ticket_id}")
