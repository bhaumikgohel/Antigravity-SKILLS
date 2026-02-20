#!/usr/bin/env python3
"""
n8n Workflow Generator
Generates minimal n8n workflow JSON files from user prompts.
"""

import argparse
import json
import uuid
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class NodeConfig:
    """Configuration for a node type."""
    node_type: str
    type_version: float
    default_params: Dict[str, Any]
    category: str


# Node type registry - minimal configurations
NODE_REGISTRY = {
    "webhook": NodeConfig(
        node_type="n8n-nodes-base.webhook",
        type_version=1,
        default_params={
            "httpMethod": "POST",
            "path": "webhook-{{random}}",
            "responseMode": "responseNode",
            "options": {}
        },
        category="trigger"
    ),
    "schedule": NodeConfig(
        node_type="n8n-nodes-base.scheduleTrigger",
        type_version=1.1,
        default_params={
            "rule": {
                "interval": [{"field": "hours", "hoursInterval": 1}]
            }
        },
        category="trigger"
    ),
    "manual": NodeConfig(
        node_type="n8n-nodes-base.manualTrigger",
        type_version=1,
        default_params={},
        category="trigger"
    ),
    "http": NodeConfig(
        node_type="n8n-nodes-base.httpRequest",
        type_version=4.1,
        default_params={
            "method": "GET",
            "url": "",
            "authentication": "none",
            "sendBody": False,
            "options": {}
        },
        category="action"
    ),
    "slack": NodeConfig(
        node_type="n8n-nodes-base.slack",
        type_version=2,
        default_params={
            "operation": "post",
            "channel": "",
            "text": "",
            "attachments": [],
            "otherOptions": {}
        },
        category="action"
    ),
    "email": NodeConfig(
        node_type="n8n-nodes-base.emailSend",
        type_version=2,
        default_params={
            "toEmail": "",
            "subject": "",
            "text": "",
            "html": "",
            "options": {}
        },
        category="action"
    ),
    "code": NodeConfig(
        node_type="n8n-nodes-base.code",
        type_version=2,
        default_params={
            "jsCode": "// Process data\nreturn items;",
            "mode": "runOnceForAllItems"
        },
        category="action"
    ),
    "postgres": NodeConfig(
        node_type="n8n-nodes-base.postgres",
        type_version=2.2,
        default_params={
            "operation": "executeQuery",
            "query": "",
            "options": {}
        },
        category="action"
    ),
    "telegram": NodeConfig(
        node_type="n8n-nodes-base.telegram",
        type_version=1.1,
        default_params={
            "operation": "sendMessage",
            "chatId": "",
            "text": "",
            "additionalOptions": {}
        },
        category="action"
    ),
    "if": NodeConfig(
        node_type="n8n-nodes-base.if",
        type_version=2,
        default_params={
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "type": "boolean"
                },
                "conditions": [
                    {
                        "id": "cond-1",
                        "leftValue": "",
                        "rightValue": "",
                        "operator": {
                            "type": "equals",
                            "operation": "equals"
                        }
                    }
                ]
            }
        },
        category="logic"
    ),
    "set": NodeConfig(
        node_type="n8n-nodes-base.set",
        type_version=3.2,
        default_params={
            "mode": "manual",
            "fields": {
                "values": [
                    {
                        "name": "data",
                        "type": "string",
                        "value": ""
                    }
                ]
            },
            "options": {}
        },
        category="transform"
    ),
    "webhookResponse": NodeConfig(
        node_type="n8n-nodes-base.respondToWebhook",
        type_version=1.1,
        default_params={
            "options": {}
        },
        category="action"
    )
}


def generate_uuid() -> str:
    """Generate a unique ID for n8n node."""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """Generate short random ID for paths."""
    return uuid.uuid4().hex[:8]


def parse_prompt(prompt: str) -> Dict[str, Any]:
    """Parse user prompt to extract workflow requirements."""
    prompt_lower = prompt.lower()
    
    # Detect trigger type
    trigger = "manual"  # default
    if any(word in prompt_lower for word in ["webhook", "http", "api call", "endpoint"]):
        trigger = "webhook"
    elif any(word in prompt_lower for word in ["schedule", "cron", "daily", "hourly", "every", "periodic"]):
        trigger = "schedule"
    elif any(word in prompt_lower for word in ["manual", "click", "button"]):
        trigger = "manual"
    
    # Detect actions
    actions = []
    if any(word in prompt_lower for word in ["slack", "slack message"]):
        actions.append("slack")
    if any(word in prompt_lower for word in ["email", "send email", "mail"]):
        actions.append("email")
    if any(word in prompt_lower for word in ["http", "api", "request", "call url", "fetch"]):
        actions.append("http")
    if any(word in prompt_lower for word in ["database", "postgres", "sql", "query"]):
        actions.append("postgres")
    if any(word in prompt_lower for word in ["telegram", "telegram message"]):
        actions.append("telegram")
    if any(word in prompt_lower for word in ["code", "transform", "process data", "javascript"]):
        actions.append("code")
    if any(word in prompt_lower for word in ["condition", "if", "check", "filter"]):
        actions.append("if")
    
    # If no specific action detected, default to http
    if not actions:
        actions.append("http")
    
    return {
        "trigger": trigger,
        "actions": actions,
        "name": extract_workflow_name(prompt)
    }


def extract_workflow_name(prompt: str) -> str:
    """Extract or generate workflow name from prompt."""
    # Try to extract first 5 words
    words = prompt.split()[:5]
    name = " ".join(words)
    # Clean up
    name = re.sub(r'[^\w\s-]', '', name).strip()
    if len(name) > 50:
        name = name[:47] + "..."
    if not name:
        name = "Generated Workflow"
    return name


def create_node(node_key: str, name: str, position: List[int], custom_params: Optional[Dict] = None) -> Dict:
    """Create a node configuration."""
    config = NODE_REGISTRY.get(node_key, NODE_REGISTRY["http"])
    
    node = {
        "id": generate_uuid(),
        "name": name,
        "type": config.node_type,
        "typeVersion": config.type_version,
        "position": position,
        "parameters": {**config.default_params}
    }
    
    # Apply custom parameters
    if custom_params:
        node["parameters"].update(custom_params)
    
    # Replace template values
    if "path" in node["parameters"] and "{{random}}" in str(node["parameters"]["path"]):
        node["parameters"]["path"] = f"webhook-{generate_short_id()}"
    
    return node


def generate_workflow(prompt: str) -> Dict:
    """Generate complete n8n workflow from prompt."""
    requirements = parse_prompt(prompt)
    
    nodes = []
    connections = {}
    
    # Create trigger node
    trigger_type = requirements["trigger"]
    trigger_pos = [250, 300]
    trigger_node = create_node(trigger_type, "Trigger", trigger_pos)
    nodes.append(trigger_node)
    
    # Create action nodes
    prev_node_name = "Trigger"
    current_x = 450
    
    for i, action_key in enumerate(requirements["actions"]):
        # Determine node name
        if len(requirements["actions"]) == 1:
            node_name = "Action"
        else:
            node_name = f"Action {i + 1}"
        
        position = [current_x, 300]
        
        # Handle specific node configurations
        custom_params = {}
        if action_key == "slack":
            custom_params["text"] = "Message from n8n workflow"
        elif action_key == "email":
            custom_params["subject"] = "n8n Workflow Notification"
            custom_params["text"] = "This is an automated message from n8n."
        elif action_key == "http":
            custom_params["url"] = "https://api.example.com/data"
        elif action_key == "code":
            custom_params["jsCode"] = "// Transform your data here\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    processed: true\n  }\n}));"
        
        action_node = create_node(action_key, node_name, position, custom_params)
        nodes.append(action_node)
        
        # Create connection
        connections[prev_node_name] = {
            "main": [[{"node": node_name, "type": "main", "index": 0}]]
        }
        
        prev_node_name = node_name
        current_x += 200
    
    # Build workflow object
    workflow = {
        "name": requirements["name"],
        "nodes": nodes,
        "connections": connections,
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": None,
        "tags": []
    }
    
    return workflow


def validate_workflow(workflow: Dict) -> List[str]:
    """Validate workflow structure and return any issues."""
    issues = []
    
    # Check required fields
    if "name" not in workflow:
        issues.append("Missing workflow name")
    if "nodes" not in workflow or not workflow["nodes"]:
        issues.append("Workflow must have at least one node")
    if "connections" not in workflow:
        issues.append("Missing connections")
    
    # Check node uniqueness
    node_names = [n["name"] for n in workflow.get("nodes", [])]
    if len(node_names) != len(set(node_names)):
        issues.append("Duplicate node names found")
    
    # Check connection references
    for source, conn_data in workflow.get("connections", {}).items():
        if source not in node_names:
            issues.append(f"Connection references non-existent source: {source}")
        if "main" in conn_data:
            for branch in conn_data["main"]:
                for conn in branch:
                    if conn.get("node") not in node_names:
                        issues.append(f"Connection references non-existent target: {conn.get('node')}")
    
    return issues


def format_json_output(workflow: Dict) -> str:
    """Format workflow JSON with proper indentation."""
    return json.dumps(workflow, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate n8n workflow from prompt")
    parser.add_argument("--prompt", required=True, help="User prompt describing the workflow")
    parser.add_argument("--output", help="Output file path (optional, prints to stdout if not provided)")
    parser.add_argument("--validate", action="store_true", help="Validate the generated workflow")
    
    args = parser.parse_args()
    
    # Generate workflow
    workflow = generate_workflow(args.prompt)
    
    # Validate if requested
    if args.validate:
        issues = validate_workflow(workflow)
        if issues:
            print("Validation Issues:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            sys.exit(1)
    
    # Output
    json_output = format_json_output(workflow)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"Workflow saved to: {args.output}")
        print(f"Nodes: {len(workflow['nodes'])}")
        print(f"Trigger: {workflow['nodes'][0]['type']}")
    else:
        print(json_output)


if __name__ == "__main__":
    import sys
    main()
