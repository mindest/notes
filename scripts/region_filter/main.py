import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import yaml
import os
from process_regions import filter_regions_by_short_name

class RegionFilterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Region Filter")
        self.geometry("800x600")

        self.data = None
        self.input_file_path = ""

        # Top frame for file selection
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.file_label = tk.Label(top_frame, text="Input File:")
        self.file_label.pack(side=tk.LEFT)

        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(top_frame, textvariable=self.file_path_var, state='readonly', width=80)
        self.file_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.browse_button = tk.Button(top_frame, text="Browse...", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Frame for region input
        region_frame = tk.Frame(self)
        region_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(region_frame, text="Regions (comma-separated):").pack(side=tk.LEFT)
        self.region_entry = tk.Entry(region_frame, width=50)
        self.region_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.region_entry.bind('<Return>', lambda event: self.filter_and_display())

        self.filter_button = tk.Button(region_frame, text="Filter", command=self.filter_and_display)
        self.filter_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = tk.Button(region_frame, text="Copy Output Text", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        # ScrolledText for output
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_default_file()

    def load_default_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_file = os.path.join(script_dir, 'release_regions.yaml')
        if os.path.exists(default_file):
            self.load_file(default_file)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a YAML file",
            filetypes=(("YAML files", "*.yaml *.yml"), ("All files", "*.*"))
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
            self.input_file_path = file_path
            self.file_path_var.set(self.input_file_path)
            self.status_var.set(f"Loaded: {os.path.basename(self.input_file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load or parse file: {e}")
            self.status_var.set("Error loading file.")

    def filter_and_display(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data loaded. Please select a file first.")
            return

        regions_str = self.region_entry.get()
        if not regions_str:
            messagebox.showwarning("Warning", "Please enter region short names.")
            return

        regions_to_keep = [region.strip() for region in regions_str.split(',')]

        filtered_data = filter_regions_by_short_name(self.data, regions_to_keep)

        self.output_text.delete(1.0, tk.END)
        if filtered_data:
            try:
                yaml_output = yaml.dump(filtered_data, sort_keys=False, indent=2)
                clean_output = yaml_output.rstrip() + '\n'
                self.output_text.insert(tk.END, clean_output)
                self.status_var.set(f"Filtered by: {regions_str}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate YAML output: {e}")
                self.status_var.set("Error generating output.")
        else:
            self.output_text.insert(tk.END, "# No matching regions found.")
            self.status_var.set(f"No results for: {regions_str}")
    def copy_to_clipboard(self):
        text_to_copy = self.output_text.get(1.0, tk.END)
        # Ensure there is exactly one trailing newline
        content_to_copy = text_to_copy.rstrip() + '\n'
        if content_to_copy.strip(): # Check if there's more than just whitespace
            self.clipboard_clear()
            self.clipboard_append(content_to_copy)
            self.status_var.set("Output copied to clipboard.")
        else:
            self.status_var.set("Nothing to copy.")

if __name__ == "__main__":
    app = RegionFilterApp()
    app.mainloop()
