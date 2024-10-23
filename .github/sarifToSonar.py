import json
import os
import re

# Define custom classifications for rule IDs or keywords in messages
CLASSIFICATION_RULES = {
    "vulnerability": ["encryption", "KMS", "IAM", "unauthorized", "vulnerability", "rotation", "security"],
    "misconfiguration": ["misconfiguration", "multi-az", "protection", "enabled", "logging", "backup", "monitoring"],
    "bug": ["error", "failure", "incorrect", "invalid", "unexpected"]
}

# Regular expression pattern to extract the resource type from help.text or message.text
RESOURCE_PATTERN = re.compile(r"Resource:\s*module\.[a-zA-Z0-9_]+\.(aws_[a-zA-Z0-9_]+)")

def classify_issue(message):
    """Classify issues based on keywords found in the message."""
    category = "CODE_SMELL"  # Default to Code Smell
    
    # Apply classification rules based on keywords in the message
    for keyword in CLASSIFICATION_RULES["vulnerability"]:
        if keyword.lower() in message.lower():
            return "VULNERABILITY"
    for keyword in CLASSIFICATION_RULES["misconfiguration"]:
        if keyword.lower() in message.lower():
            return "VULNERABILITY"
    for keyword in CLASSIFICATION_RULES["bug"]:
        if keyword.lower() in message.lower():
            return "BUG"
    
    return category

def get_impacted_resource(help_text):
    """Extract the impacted resource type from the help text using a regex pattern."""
    match = RESOURCE_PATTERN.search(help_text)
    if match:
        return match.group(1)  # Return the matched resource type
    return "unknown_resource"  # Default if no resource type is found

def convert_to_sonar_format(sarif_file):
    with open(sarif_file, 'r') as f:
        sarif_data = json.load(f)

    sonar_issues = []

    for run in sarif_data.get("runs", []):
        # Extract tool name from SARIF file
        engine_id = run.get("tool", {}).get("driver", {}).get("name", "unknown_tool")
        
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "")
            message = result.get("message", {}).get("text", "")
            help_text = run["tool"]["driver"]["rules"][result.get("ruleIndex", 0)].get("help", {}).get("text", "")

            # Classify the issue based on the message or rule_id
            issue_type = classify_issue(message)

            # Get impacted resource type based on the help text using the pattern
            impacted_resource = get_impacted_resource(help_text)

            for location in result.get("locations", []):
                severity = result.get("level", "WARNING").upper()
                if severity not in ["INFO", "MINOR", "MAJOR", "CRITICAL", "BLOCKER"]:
                    severity = "MAJOR"  # Default to MAJOR if an invalid severity is found

                # Add tags for tool and impacted resource
                tags = [engine_id, impacted_resource]

                issue_data = {
                    "engineId": engine_id,
                    "ruleId": rule_id,
                    "severity": severity,
                    "type": issue_type,  # This is the Bug, Vulnerability, or Code Smell classification
                    "primaryLocation": {
                        "message": message,
                        "filePath": location.get("physicalLocation", {}).get("artifactLocation", {}).get("uri", ""),
                        "textRange": {
                            "startLine": location.get("physicalLocation", {}).get("region", {}).get("startLine", 1),
                            "endLine": location.get("physicalLocation", {}).get("region", {}).get("endLine", 1)
                        }
                    },
                    "tags": tags  # Add tool and resource tags
                }
                sonar_issues.append(issue_data)

    return sonar_issues

def analyze_all_sarif_files_in_current_directory(output_file):
    all_issues = {
        "issues": []
    }

    # Get the current directory where the script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Iterate over all .sarif files in the current directory
    for file in os.listdir(current_directory):
        if file.endswith(".sarif"):
            file_path = os.path.join(current_directory, file)
            print(f"Processing {file_path}")
            issues = convert_to_sonar_format(file_path)
            all_issues["issues"].extend(issues)

    # Write all issues to the final output file
    with open(output_file, 'w') as f:
        json.dump(all_issues, f, indent=2)

# Convert all SARIF files in the current directory to SonarQube-compatible format and combine into one output file
analyze_all_sarif_files_in_current_directory('all.json')