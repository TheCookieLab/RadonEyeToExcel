import pandas as pd
from datetime import datetime, timedelta
import re
import tkinter as tk
from tkinter import filedialog
import openpyxl
from openpyxl.utils import get_column_letter
import os

# Create a file selection UI
root = tk.Tk()
root.withdraw()
input_file = filedialog.askopenfilename(title="Select RadonEye log file", filetypes=[("Text files", "*.txt")])

# Create a directory selection UI for output
output_dir = filedialog.askdirectory(title="Select Output Directory")

# Extract the end date and time from the file name
end_datetime_str = re.search(r'_([0-9]{8} [0-9]{6})', input_file).group(1)
end_datetime = datetime.strptime(end_datetime_str, '%Y%m%d %H%M%S')

# Read the input file
with open(input_file, 'r') as file:
    lines = file.readlines()

# Extract the Data No (number of readings) and the unit from the header
unit = ""
for line in lines:
    if line.startswith("Data No:"):
        num_readings = int(line.split(":")[1].strip())
    elif line.startswith("Unit:"):
        unit = line.split(":")[1].strip()

# Calculate the start date and time based on the end date and number of readings
start_datetime = end_datetime - timedelta(hours=(num_readings - 1))

# Extract the radon readings from the file
readings = []
for line in lines:
    match = re.match(r'\d+\)\s+(\d+\.\d+)', line)
    if match:
        readings.append(float(match.group(1)))

# Generate date/time stamps for each reading
date_times = [start_datetime + timedelta(hours=i) for i in range(len(readings))]

# Create a DataFrame with Date/Time and Radon Level columns
df = pd.DataFrame({
    'Date/Time': [dt.strftime('%m/%d/%Y %H:%M:%S') for dt in date_times],
    f'Radon Level ({unit})': readings
})

# Format start and end date/time for the output file name
start_datetime_str = start_datetime.strftime('%m.%d.%Y %H-%M-%S')
end_datetime_str = end_datetime.strftime('%m.%d.%Y %H-%M-%S')
output_file = os.path.join(output_dir, f'RadonEye Readings {start_datetime_str} to {end_datetime_str}.xlsx')

# Output the DataFrame to an Excel file using openpyxl
df.to_excel(output_file, index=False, engine='openpyxl')

# Adjust column widths in the Excel file
wb = openpyxl.load_workbook(output_file)
sheet = wb.active
for col in sheet.columns:
    max_length = 0
    column = col[0].column_letter  # Get the column letter
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = (max_length + 2)
    sheet.column_dimensions[column].width = adjusted_width

wb.save(output_file)

print(f"Excel file '{output_file}' has been created successfully.")
