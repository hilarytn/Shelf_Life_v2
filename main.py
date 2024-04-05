from flask import Flask, render_template, request, redirect, jsonify
import os
import pandas as pd
import re
from collections import Counter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

application = app

def get_score_counts(filtered_dict):
    # Initialize counters for different score categories
    score_counts = Counter()

    # Iterate through each entry in the filtered dictionary
    for entry in filtered_dict:
        # Increment the counter based on the 'Final Score' value
        #print(entry)
        score_counts[entry['Final Score']] += 1

    # Calculate total number of samples
    total_samples = sum(score_counts.values())

    # Calculate percentages and add them to the Counter object
    for score, count in score_counts.items():
        percentage = (count / total_samples) * 100
        score_counts[score] = {'count': count, 'percentage': round(percentage, 2)}

    return score_counts

def parse_and_process_excel(file_path):
    try:
        # Specify the columns you want to select
        column_indices = [16, 18, 20, 32]  # 16- Date, 18-Item Number, 20-Item Number Description, 32-Final Score
        
        # Parse Excel file and select specific columns
        df = pd.read_excel(file_path, sheet_name=1, header=None, usecols=column_indices)

        # print("Original DataFrame:")
        # print(df)
        
        # Convert DataFrame to dictionary
        df_dict = df.iloc[1:].to_dict(orient='records')

        df_dict_with_keys = [{'Date': row[16], 'Item Number': row[18], 'Item Number Description': row[20], 'Final Score': row[32]} for row in df_dict]
        
        # print(df)  # Print DataFrame
        # print(df_dict_with_keys)  # Print DataFrame dictionary with keys

        filtered_dict = [entry for entry in df_dict_with_keys if entry['Date'].year == 2023]
        # print("Filtered dictionary:")
        # for entry in filtered_dict:
        #     print(entry)


        return filtered_dict
    except Exception as e:
        return {'error': str(e)}




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            # Parse and process the uploaded Excel file
            result = parse_and_process_excel(file_path)
            counts = get_score_counts(result)
            #print(counts)
            # Delete the uploaded file after processing
            os.remove(file_path)
            return render_template('dashboard.html', data=result, counts=counts)
        else:
            return jsonify({'error': 'No file provided'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)