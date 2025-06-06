import tkinter as tk
from tkinter import filedialog, ttk
import gdown
import re
import os
import threading

def extract_file_id(url):
    """Extract the file ID from a Google Drive URL."""
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def update_progress(progress):
    """Update the progress bar and status label."""
    progress_bar['value'] = progress * 100
    status_label.config(text=f"Downloading: {progress * 100:.1f}%")
    root.update_idletasks()

def download_file():
    """Handle the download process in a separate thread."""
    url = link_entry.get().strip()
    output_path = location_entry.get().strip()
    
    if not url or not output_path:
        status_label.config(text="Error: Please provide a valid URL and output location.")
        return
    
    file_id = extract_file_id(url)
    if not file_id:
        status_label.config(text="Error: Invalid Google Drive URL.")
        return
    
    # Disable buttons during download
    download_button.config(state='disabled')
    browse_button.config(state='disabled')
    
    def download_thread():
        try:
            gdown.download(
                f"https://drive.google.com/uc?id={file_id}",
                output_path,
                quiet=False,
                use_cookies=False,
                progress_callback=update_progress
            )
            status_label.config(text="Download complete!")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")
        finally:
            download_button.config(state='normal')
            browse_button.config(state='normal')
    
    # Run download in a separate thread to keep GUI responsive
    threading.Thread(target=download_thread, daemon=True).start()

def browse_location():
    """Open a file dialog to select the output location."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".mp4",
        filetypes=[("Video files", "*.mp4 *.mkv *.avi"), ("All files", "*.*")]
    )
    if file_path:
        location_entry.delete(0, tk.END)
        location_entry.insert(0, file_path)

# Create the main GUI window
root = tk.Tk()
root.title("Google Drive Downloader")
root.geometry("500x250")
root.resizable(False, False)

# Link input
tk.Label(root, text="Google Drive Link:").pack(pady=10)
link_entry = tk.Entry(root, width=60)
link_entry.pack()

# Output location
tk.Label(root, text="Save to:").pack(pady=10)
location_entry = tk.Entry(root, width=60)
location_entry.pack()
browse_button = tk.Button(root, text="Browse", command=browse_location)
browse_button.pack(pady=5)

# Download button
download_button = tk.Button(root, text="Download", command=download_file)
download_button.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Status label
status_label = tk.Label(root, text="Ready to download")
status_label.pack(pady=10)

# Start the GUI
root.mainloop()