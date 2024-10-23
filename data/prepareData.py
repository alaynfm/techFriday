import requests
import os
import zipfile
import pandas as pd
import json

# Set headers for GitHub API
def set_headers(github_token):
    return {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

# Step 1: Get the last successful workflow run
def get_last_successful_run(headers, repo_owner, repo_name, workflow_id):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/runs"
    params = {"status": "success", "per_page": 1}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        runs = response.json()["workflow_runs"]
        if runs:
            return runs[0]
    return None

# Step 2: Download artifacts for the run into the "data/downloads" folder
def download_artifacts(headers, run_id, repo_owner, repo_name, download_folder="data/downloads"):
    os.makedirs(download_folder, exist_ok=True)
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/artifacts"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        artifacts = response.json()["artifacts"]

        if artifacts:
            for artifact in artifacts:
                artifact_name = artifact["name"]
                download_url = artifact["archive_download_url"]
                download_artifact(headers, artifact_name, download_url, download_folder)

# Step 3: Download an individual artifact into the "data/downloads" folder
def download_artifact(headers, artifact_name, download_url, download_folder):
    response = requests.get(download_url, headers=headers)

    if response.status_code == 200:
        output_file = os.path.join(download_folder, f"{artifact_name}.zip")
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {artifact_name} to {output_file}")
    else:
        print(f"Error downloading artifact {artifact_name}")

# Step 4: Unzip files twice and move all .sarif files into the "data" folder
def unzip_twice_and_rename_files_to_data(zip_files, destination_folder="data"):
    os.makedirs(destination_folder, exist_ok=True)

    for zip_file in zip_files:
        if os.path.exists(zip_file):
            # Extract the base name from the zip file (e.g., "AWSGoat", "TerraGoat-AWS")
            base_name = os.path.basename(zip_file).replace(".zip.zip", "")
            
            # First unzip (extract the .zip.zip)
            first_unzip_folder = f"temp_unzip_{base_name}"
            os.makedirs(first_unzip_folder, exist_ok=True)
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(first_unzip_folder)

            # Find and unzip the inner .zip
            for inner_zip in os.listdir(first_unzip_folder):
                if inner_zip.endswith(".zip"):
                    inner_zip_path = os.path.join(first_unzip_folder, inner_zip)
                    with zipfile.ZipFile(inner_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(destination_folder)

                    # Rename the .sarif file dynamically based on the original zip file's base name
                    for file_name in zip_ref.namelist():
                        if file_name.endswith(".sarif"):
                            original_sarif_path = os.path.join(destination_folder, file_name)
                            if 'AWS' in zip_file:
                                new_sarif_name = f"{file_name.replace('.sarif', '')}-{base_name}-AWS.sarif"
                            elif 'Azure' in zip_file:
                                new_sarif_name = f"{file_name.replace('.sarif', '')}-{base_name}-Azure.sarif"
                            new_sarif_path = os.path.join(destination_folder, new_sarif_name)
                            os.rename(original_sarif_path, new_sarif_path)
                            print(f"Renamed {original_sarif_path} to {new_sarif_path}")

# Step 5: Load SARIF files into pandas DataFrames
def load_sarif_files_into_dataframes(sarif_folder):
    sarif_files = [f for f in os.listdir(sarif_folder) if f.endswith(".sarif")]

    dataframes = {}

    for sarif_file in sarif_files:
        sarif_file_path = os.path.join(sarif_folder, sarif_file)

        with open(sarif_file_path, 'r') as file:
            sarif_data = json.load(file)

        tool_name = sarif_data.get("runs", [])[0].get("tool", {}).get("driver", {}).get("name", "UnknownTool")

        if "AWS" in sarif_file:
            source = "AWS"
        elif "Azure" in sarif_file:
            source = "Azure"
        else:
            source = "Unknown"

        results = []
        for run in sarif_data.get("runs", []):
            for result in run.get("results", []):
                rule_id = result.get("ruleId", "N/A")
                message = result.get("message", {}).get("text", "N/A")
                level = result.get("level", "N/A")
                results.append({
                    "rule_id": rule_id,
                    "message": message,
                    "level": level,
                    "source": source
                })

        df = pd.DataFrame(results)

        if tool_name not in dataframes:
            dataframes[tool_name] = []

        dataframes[tool_name].append(df)

    for tool_name, dfs in dataframes.items():
        dataframes[tool_name] = pd.concat(dfs, ignore_index=True)

    return dataframes

# Main function to perform the entire process
def fetch_sarif_dataframes(github_token, repo_owner, repo_name, workflow_id):
    headers = set_headers(github_token)
    
    # Execute the steps to get SARIF files as DataFrames
    last_run = get_last_successful_run(headers, repo_owner, repo_name, workflow_id)
    if last_run:
        run_id = last_run["id"]
        download_artifacts(headers, run_id, repo_owner, repo_name)

    # Get the downloaded zip files automatically from the "data/downloads" folder
    download_folder = "data/downloads"
    zip_files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.endswith(".zip")]

    # After downloading, unzip and process the SARIF files into the "data" folder
    unzip_twice_and_rename_files_to_data(zip_files)

    # Load the SARIF files into pandas DataFrames
    sarif_folder = "data"
    sarif_dataframes_by_tool = load_sarif_files_into_dataframes(sarif_folder)

    # Return the DataFrames
    return sarif_dataframes_by_tool