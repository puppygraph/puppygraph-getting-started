import argparse
import os

import pandas as pd

"""
Script to convert CSV file(s) to Parquet format.

Usage:
    python your_script.py <csv_file_or_folder> <output_folder>

    Example:
    python your_script.py parts_lorem.csv ./parquet_output
    python your_script.py ./csv_folder ./parquet_output

    This will convert the specified CSV file or all CSV files in the specified folder 
    to Parquet format and save them in the provided output folder.

Dependencies:
    - pandas
    - pyarrow

Install dependencies:
    pip install pandas pyarrow
"""


def csv_to_parquet(csv_file, output_folder):
  # Read the CSV file
  df = pd.read_csv(csv_file)

  # Generate the Parquet file name and save it in the output folder
  parquet_file = os.path.join(output_folder, os.path.basename(csv_file).replace('.csv', '.parquet'))

  # Convert the CSV to Parquet
  df.to_parquet(parquet_file, engine='pyarrow', index=False)

  print(f"CSV file {csv_file} has been successfully converted to Parquet. Output file: {parquet_file}")


def process_folder(folder_path, output_folder):
  # Loop through all files in the directory
  for file_name in os.listdir(folder_path):
    # Check if the file is a CSV file
    if file_name.endswith(".csv"):
      csv_file_path = os.path.join(folder_path, file_name)
      csv_to_parquet(csv_file_path, output_folder)


if __name__ == "__main__":
  # Set up argument parsing
  parser = argparse.ArgumentParser(description="Convert CSV file(s) to Parquet format.")
  parser.add_argument("csv_file_or_folder", help="The path to the CSV file or folder to convert.")
  parser.add_argument("output_folder", help="The folder where the Parquet files will be saved.")

  # Parse the command-line arguments
  args = parser.parse_args()

  # Check if the output folder exists, if not, create it
  if not os.path.exists(args.output_folder):
    os.makedirs(args.output_folder)

  # Check if the input is a file or a folder
  if os.path.isfile(args.csv_file_or_folder):
    # If it's a file, convert the single CSV file
    csv_to_parquet(args.csv_file_or_folder, args.output_folder)
  elif os.path.isdir(args.csv_file_or_folder):
    # If it's a folder, process all CSV files in the folder
    process_folder(args.csv_file_or_folder, args.output_folder)
  else:
    print(f"The path {args.csv_file_or_folder} is neither a file nor a directory.")
