import pandas as pd
import json

def json_to_csv(json_file, csv_file):
    # List to store JSON objects
    data_list = []

    # Read JSON file line by line
    with open(json_file, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                # Load each line as a JSON object
                data = json.loads(line)
                data_list.append(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {str(e)}")

    # Convert to DataFrame
    df = pd.DataFrame(data_list)

    # Write to CSV
    df.to_csv(csv_file, index=False)

# Example usage
json_file_path = 'yelp_dataset/yelp_academic_dataset_review.json'
csv_file_path = 'test/output_file.csv'

json_to_csv(json_file_path, csv_file_path)