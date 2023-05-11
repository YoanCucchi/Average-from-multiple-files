import tkinter as tk
from tkinter import filedialog
import csv
import os
import numpy as np
from pathlib import Path

def check_columns(filenames):
	# Read the first file and record the number of columns.
	with open(filenames[0], 'r') as f:
		data = f.readlines()
	num_columns = len(data[0].strip().split(';')) - 1

	# Check if all other files have the same number of columns.
	for filename in filenames[1:]:
		with open(filename, 'r') as f:
			data = f.readlines()
		if len(data[0].strip().split(';')) - 1 != num_columns:
			print(f'Error: the file *{Path(filename).name}* does not have the same number of columns as 'f'*{Path(filenames[0]).name}*')
			return False
	return True

def read_data(filename):
	# Read the data from the file and return it as a tuple (zones, values).
	with open(filename, 'r') as f:
		data = f.readlines()

	zones = data[0].strip().split(';')[1:]
	values = []
	for row in data[1:]:
		values.append(row.strip().split(';')[1:])
	values = np.array(values, dtype=float)

	return zones, values

def write_csv(output_filename, zones, values, filename):
	# Write the zones and values to a CSV file.
	with open(output_filename, 'a', newline='') as f:
		writer = csv.writer(f, delimiter=';')
		name_to_copy = [f"{Path(filename).parent.parent.name} ~ {Path(filename).parent.name} ~ {Path(filename).stem}"]
		print(name_to_copy)
		writer.writerow(name_to_copy + zones)
		for i, row in enumerate(zones):
			writer.writerow([row] + list(values[i]))
		writer.writerow([])

def process_files(filenames):
	# Process each file in the list of files.
	if not check_columns(filenames):
		return
	matrices = []
	print('Choose the output file name:')
	input_name = input()
	desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
	# Create the absolute path to the output file
	output_filename = os.path.join(desktop_path, input_name + '.csv')
	print(output_filename)
	for filename in filenames:
		zones, values = read_data(filename)
		# Replace values close to 1 by 0.999999 to avoid division by zero
		tolerance = 1e-6
		values[np.isclose(values, 1, atol=tolerance)] = 0.99

		# Apply the Arctanh function to all values
		values = np.arctanh(values)

		# Replace values resulting from arctanh(0.99) by 1
		values[np.isclose(values, 2.64665)] = 1

		# Save to CSV
		write_csv(output_filename, zones, values, filename)
		print(f'{filename} has been successfully processed.')

		# Add the processed matrix to the list of matrices
		matrices.append(values)

	# Calculate the average of the processed matrices
	average = np.average(matrices, axis=0)

	# Add the average to the end of the output file
	with open(output_filename, 'a', newline='') as f:
		writer = csv.writer(f, delimiter=';')
		writer.writerow(['Average'] + zones)
		for i, row in enumerate(zones):
			writer.writerow([row] + list(average[i]))
		writer.writerow([])

# Manage file selection
root = tk.Tk()
root.withdraw()

file_paths = []
while True:
	new_files = filedialog.askopenfilenames(
	title='Select files to process',
	filetypes=[('Text files', '*.txt')],
	)
	if not new_files: # The user canceled the selection
		break
	file_paths.extend(new_files)

if file_paths:
	process_files(file_paths)
else:
	print('No file selected.')