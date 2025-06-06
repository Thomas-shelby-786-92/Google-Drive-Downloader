import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import gdown
import re
import os
import threading
from datetime import datetime

class GoogleDriveDownloader:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.download_history = []
        
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Google Drive Downloader")
        self.root.geometry("600x480")
        self.root.resizable(True, False)
        self.root.configure(bg='#f0f0f0')
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (480 // 2)
        self.root.geometry(f"600x480+{x}+{y}")
        
    def create_styles(self):
        """Create custom styles for ttk widgets."""
        style = ttk.Style()
        
        # Configure modern button style
        style.configure('Modern.TButton',
                       font=('Segoe UI', 10),
                       padding=(20, 10))
        
        # Configure header label style
        style.configure('Header.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       background='#f0f0f0')
        
        # Configure info label style
        style.configure('Info.TLabel',
                       font=('Segoe UI', 9),
                       background='#f0f0f0',
                       foreground='#666666')
        
    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Google Drive Downloader", 
                               style='Header.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Download files from Google Drive with ease",
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # URL Input Section
        url_frame = tk.LabelFrame(main_frame, text=" Google Drive URL ", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='#f0f0f0', fg='#333333',
                                 padx=15, pady=10)
        url_frame.pack(fill='x', pady=(0, 15))
        
        self.link_entry = tk.Entry(url_frame, font=('Segoe UI', 10),
                                  relief='solid', bd=1,
                                  bg='white', fg='#333333')
        self.link_entry.pack(fill='x', ipady=8)
        self.link_entry.bind('<KeyRelease>', self.validate_url)
        
        # URL validation label
        self.url_status_label = tk.Label(url_frame, text="", 
                                        font=('Segoe UI', 8),
                                        bg='#f0f0f0')
        self.url_status_label.pack(anchor='w', pady=(5, 0))
        
        # Output Location Section
        location_frame = tk.LabelFrame(main_frame, text=" Save Location ", 
                                      font=('Segoe UI', 10, 'bold'),
                                      bg='#f0f0f0', fg='#333333',
                                      padx=15, pady=10)
        location_frame.pack(fill='x', pady=(0, 15))
        
        location_input_frame = tk.Frame(location_frame, bg='#f0f0f0')
        location_input_frame.pack(fill='x')
        
        self.location_entry = tk.Entry(location_input_frame, font=('Segoe UI', 10),
                                      relief='solid', bd=1,
                                      bg='white', fg='#333333')
        self.location_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        self.browse_button = ttk.Button(location_input_frame, text="Browse",
                                       command=self.browse_location,
                                       style='Modern.TButton')
        self.browse_button.pack(side='right', padx=(10, 0))
        
        # Control Buttons
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.download_button = ttk.Button(button_frame, text="Start Download",
                                         command=self.download_file,
                                         style='Modern.TButton')
        self.download_button.pack(side='left')
        
        self.clear_button = ttk.Button(button_frame, text="Clear All",
                                      command=self.clear_fields,
                                      style='Modern.TButton')
        self.clear_button.pack(side='left', padx=(10, 0))
        
        self.history_button = ttk.Button(button_frame, text="View History",
                                        command=self.show_history,
                                        style='Modern.TButton')
        self.history_button.pack(side='right')
        
        # Progress Section
        progress_frame = tk.LabelFrame(main_frame, text=" Download Progress ", 
                                      font=('Segoe UI', 10, 'bold'),
                                      bg='#f0f0f0', fg='#333333',
                                      padx=15, pady=10)
        progress_frame.pack(fill='x', pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=500, 
                                           mode='determinate',
                                           style='TProgressbar')
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        # Status info frame
        status_info_frame = tk.Frame(progress_frame, bg='#f0f0f0')
        status_info_frame.pack(fill='x')
        
        self.status_label = tk.Label(status_info_frame, text="Ready to download",
                                    font=('Segoe UI', 10),
                                    bg='#f0f0f0', fg='#333333')
        self.status_label.pack(side='left')
        
        self.progress_text = tk.Label(status_info_frame, text="",
                                     font=('Segoe UI', 9),
                                     bg='#f0f0f0', fg='#666666')
        self.progress_text.pack(side='right')
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#f0f0f0')
        footer_frame.pack(fill='x', side='bottom')
        
        footer_label = ttk.Label(footer_frame, 
                                text="Tip: Ensure the Google Drive file is publicly accessible",
                                style='Info.TLabel')
        footer_label.pack()
        
    def validate_url(self, event=None):
        """Validate the Google Drive URL and show status."""
        url = self.link_entry.get().strip()
        if not url:
            self.url_status_label.config(text="", fg='#666666')
            return
            
        file_id = self.extract_file_id(url)
        if file_id:
            self.url_status_label.config(text="✓ Valid Google Drive URL", 
                                        fg='#28a745')
        else:
            self.url_status_label.config(text="✗ Invalid Google Drive URL", 
                                        fg='#dc3545')
    
    def extract_file_id(self, url):
        """Extract the file ID from a Google Drive URL."""
        patterns = [
            r'/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/file/d/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def update_progress(self, progress):
        """Update the progress bar and status label."""
        percentage = progress * 100
        self.progress_bar['value'] = percentage
        self.progress_text.config(text=f"{percentage:.1f}%")
        self.root.update_idletasks()
    
    def download_file(self):
        """Handle the download process in a separate thread."""
        url = self.link_entry.get().strip()
        output_path = self.location_entry.get().strip()
        
        if not url or not output_path:
            messagebox.showerror("Error", "Please provide a valid URL and output location.")
            return
        
        file_id = self.extract_file_id(url)
        if not file_id:
            messagebox.showerror("Error", "Invalid Google Drive URL.")
            return
        
        if os.path.exists(output_path):
            if not messagebox.askyesno("File Exists", 
                                      "File already exists. Do you want to overwrite it?"):
                return
        
        # Disable buttons during download
        self.download_button.config(state='disabled', text='Downloading...')
        self.browse_button.config(state='disabled')
        self.clear_button.config(state='disabled')
        
        def download_thread():
            try:
                self.status_label.config(text="Initializing download...", fg='#007bff')
                
                gdown.download(
                    f"https://drive.google.com/uc?id={file_id}",
                    output_path,
                    quiet=False,
                    use_cookies=False,
                    progress_callback=self.update_progress
                )
                
                # Add to history
                self.download_history.append({
                    'url': url,
                    'file': os.path.basename(output_path),
                    'path': output_path,
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                self.status_label.config(text="Download completed successfully!", fg='#28a745')
                self.progress_text.config(text="100%")
                messagebox.showinfo("Success", "File downloaded successfully!")
                
            except Exception as e:
                self.status_label.config(text=f"Download failed: {str(e)}", fg='#dc3545')
                self.progress_bar['value'] = 0
                self.progress_text.config(text="")
                messagebox.showerror("Error", f"Download failed: {str(e)}")
                
            finally:
                self.download_button.config(state='normal', text='Start Download')
                self.browse_button.config(state='normal')
                self.clear_button.config(state='normal')
        
        # Run download in a separate thread to keep GUI responsive
        threading.Thread(target=download_thread, daemon=True).start()
    
    def browse_location(self):
        """Open a file dialog to select the output location."""
        file_path = filedialog.asksaveasfilename(
            title="Save file as...",
            defaultextension=".mp4",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.wmv"),
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Document files", "*.pdf *.doc *.docx *.txt"),
                ("Archive files", "*.zip *.rar *.7z"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, file_path)
    
    def clear_fields(self):
        """Clear all input fields and reset progress."""
        self.link_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.progress_bar['value'] = 0
        self.progress_text.config(text="")
        self.status_label.config(text="Ready to download", fg='#333333')
        self.url_status_label.config(text="")
    
    def show_history(self):
        """Show download history in a new window."""
        if not self.download_history:
            messagebox.showinfo("History", "No download history available.")
            return
            
        history_window = tk.Toplevel(self.root)
        history_window.title("Download History")
        history_window.geometry("700x400")
        history_window.configure(bg='#f0f0f0')
        
        # Create treeview for history
        columns = ('File', 'Date/Time', 'Status')
        tree = ttk.Treeview(history_window, columns=columns, show='headings', height=15)
        
        # Define headings
        tree.heading('File', text='File Name')
        tree.heading('Date/Time', text='Downloaded At')
        tree.heading('Status', text='Status')
        
        # Configure column widths
        tree.column('File', width=300)
        tree.column('Date/Time', width=200)
        tree.column('Status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=20)
        
        # Populate history
        for item in self.download_history:
            tree.insert('', tk.END, values=(item['file'], item['time'], 'Completed'))

def main():
    root = tk.Tk()
    app = GoogleDriveDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
