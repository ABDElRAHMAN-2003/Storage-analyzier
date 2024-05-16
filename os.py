import os
import psutil
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas as pd

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
    except FileNotFoundError:
        size = 0
        print(f"Error: File '{file_path}' not found.")
    return size

def get_directory_size(directory):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += get_file_size(file_path)
    return total_size

def get_disk_usage(path):
    total, used, free = 0, 0, 0
    try:
        usage = psutil.disk_usage(path)
        total = usage.total
        used = usage.used
        free = usage.free
    except FileNotFoundError:
        print("Error: Path not found.")
    return total, used, free

def analyze_storage():
    path = filedialog.askdirectory()
    if path:
        total, used, free = get_disk_usage(path)
        total_files_size = get_directory_size(path)

        # Get the size of the directory itself
        directory_size = total

        # Get a list of files and their access times
        files_access_times = []
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                access_time = os.path.getatime(file_path)
                files_access_times.append((file_path, access_time))

        # Sort files by access time
        files_access_times.sort(key=lambda x: x[1])

        # Get the oldest accessed files
        oldest_files = [file for file, _ in files_access_times[:5]]  # Change 5 to the desired number of recommendations

        # Display the oldest accessed files as archiving recommendations
        result_text.set(
            f"Path: {path}\n"
            f"Total space of the selected directory: {total / (1024**3):.2f} GB\n"
            f"Used space of the selected directory: {used / (1024**3):.2f} GB\n"
            f"Free space of the selected directory: {free / (1024**3):.2f} GB\n"
            f"Total size of files within the directory: {total_files_size / (1024**3):.2f} GB\n"
            f"Size of the directory itself: {directory_size / (1024**3):.2f} GB\n\n"
            "Oldest accessed files to consider archiving:\n\n" + "\n".join(oldest_files)
        )

        # Create a pie chart
        labels = ['Usage Of The Selected File', 'Selected']
        sizes = [total_files_size, directory_size]  # Total files size vs. other space in directory
        colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)  # explode 1st slice

        plt.figure(figsize=(12, 6))

        # Plot pie chart
        plt.subplot(1, 2, 1)
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Directory Usage Relative to Itself')
        plt.show()

        # Export data to CSV
        export_to_csv(path, total, used, free, total_files_size, directory_size)

def export_to_csv(directory, total, used, free, total_files_size, directory_size):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    csv_path = os.path.join(desktop_path, "storage_analysis.csv")

    data = {
        "Path": [directory],
        "Total space (GB)": [total / (1024**3)],
        "Used space (GB)": [used / (1024**3)],
        "Free space (GB)": [free / (1024**3)],
        "Total files size (GB)": [total_files_size / (1024**3)],
        "Directory size (GB)": [directory_size / (1024**3)]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

# Create the main application window
root = tk.Tk()
root.title("Storage Analyzer")

# Create a label to display the result
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify=tk.LEFT)
result_label.pack(padx=10, pady=10)

# Create a button to trigger storage analysis
analyze_button = tk.Button(root, text="Select Directory", command=analyze_storage)
analyze_button.pack(padx=10, pady=5)

# Run the application
root.mainloop()
