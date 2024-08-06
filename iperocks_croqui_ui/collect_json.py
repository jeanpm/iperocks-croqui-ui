import json
import os
from collections import defaultdict


def load_json_files(root_folder):
    # Dictionary to store all routes, categorized by different properties
    consolidated_data = {
        "by_grade": defaultdict(list),
        "by_block": defaultdict(list),
        "by_sector": defaultdict(list),
    }

    # Walk through the directory to find JSON files
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".json"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    print(f"Reading JSON file {file_path}")
                    data = json.load(file)
                    # Extract routes
                    for route in data.get("routes", []):
                        # Add route to different categories
                        grade = route.get("grade")
                        block = route.get("block")
                        sector = route.get("sector")

                        if grade:
                            consolidated_data["by_grade"][grade].append(route)
                        if block:
                            consolidated_data["by_block"][block].append(route)
                        if sector:
                            consolidated_data["by_sector"][sector].append(route)

    return consolidated_data


def save_consolidated_data(consolidated_data, output_file):
    print(f"Saving JSON {output_file}")
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(consolidated_data, file, indent=4)


# Usage example
root_folder = "output"  # Replace with your folder containing JSON files
output_file = "output/consolidated_routes.json"

consolidated_data = load_json_files(root_folder)
save_consolidated_data(consolidated_data, output_file)

print(f"Consolidated data saved to {output_file}")
