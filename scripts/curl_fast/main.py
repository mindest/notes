import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import shlex
import os
import sys
import ctypes
from tkinter import font as tkfont
try:
    import keyring
except ImportError:
    keyring = None
try:
    import requests
except ImportError:
    requests = None
try:
    from pygments import lex
    from pygments.lexers import JsonLexer
    from pygments.token import Token
except ImportError:
    lex = None # Flag that pygments is not installed
    Token = None

class CurlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech-to-Text cURL Request Sender")
        self.geometry("800x1200")

        # --- Configuration ---
        self.config_file = os.path.join(os.path.dirname(__file__), "curl_gui_config.json")
        self.default_font = ("Fira Code", 10)
        self.SERVICE_NAME = "curl_gui_app"
        # This list provides the initial regions for the dropdown.
        # The keys will be fetched from the keyring store.
        self.regions = [] # Will be populated from keyring
        self.api_versions = ["2024-11-15", "2025-10-15"]
        self.locale_history = [] # For storing recent locale settings

        self.create_widgets()
        self.toggle_diarization_fields() # Set initial state for diarization fields
        self._toggle_custom_model_fields() # Set initial state for custom model fields
        self._toggle_api_version_fields() # Set initial state for enhanced mode based on API version
        self.load_config()
        self.update_key() # Set initial key
        self._check_keyring_backend()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Function Selection ---
        func_frame = ttk.LabelFrame(main_frame, text="Function")
        func_frame.pack(fill="x", pady=5)
        self.function_var = tk.StringVar(value="transcribe")
        self.function_menu = ttk.Combobox(func_frame, textvariable=self.function_var, values=["transcribe", "locales"], state="readonly")
        self.function_menu.pack(fill="x", padx=5, pady=5)
        self.function_menu.bind("<<ComboboxSelected>>", self._toggle_function_fields)

        # --- Request Configuration Frame ---
        config_frame = ttk.LabelFrame(main_frame, text="Request Configuration")
        config_frame.pack(fill="x", pady=5)
        config_frame.grid_columnconfigure(1, weight=1)

        # Region
        ttk.Label(config_frame, text="Endpoint Region:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.region_var = tk.StringVar()
        if self.regions:
            self.region_var.set(self.regions[0])
        self.region_menu = ttk.Combobox(config_frame, textvariable=self.region_var, values=self.regions, state="normal")
        self.region_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.region_menu.bind("<<ComboboxSelected>>", self.update_key)
        self.region_menu.bind("<Return>", self.update_key)

        # API Version
        ttk.Label(config_frame, text="API Version:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.api_version_var = tk.StringVar(value=self.api_versions[0])
        self.api_version_menu = ttk.Combobox(config_frame, textvariable=self.api_version_var, values=self.api_versions, state="readonly")
        self.api_version_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.api_version_menu.bind("<<ComboboxSelected>>", self._toggle_api_version_fields)

        # Subscription Key
        ttk.Label(config_frame, text="Subscription Key:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        key_frame = ttk.Frame(config_frame)
        key_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        key_frame.grid_columnconfigure(0, weight=1)
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=60)
        self.key_entry.grid(row=0, column=0, sticky="ew")
        self.save_key_button = ttk.Button(key_frame, text="Save Key", command=self.save_key_to_keyring)
        self.save_key_button.grid(row=0, column=1, padx=(5, 0))

        # Audio File
        ttk.Label(config_frame, text="Audio File:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.audio_file_var = tk.StringVar()
        self.audio_file_frame = ttk.Frame(config_frame)
        self.audio_file_frame.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.audio_file_frame.grid_columnconfigure(0, weight=1)
        self.audio_file_entry = ttk.Entry(self.audio_file_frame, textvariable=self.audio_file_var)
        self.audio_file_entry.grid(row=0, column=0, sticky="ew")
        self.browse_button = ttk.Button(self.audio_file_frame, text="Browse...", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=(5, 0))

        # --- Definition Frame ---
        self.definition_frame = ttk.LabelFrame(main_frame, text="Definition")
        self.definition_frame.pack(fill="x", pady=5)
        self.definition_frame.grid_columnconfigure(0, weight=1)
        self.definition_frame.grid_columnconfigure(1, weight=1)

        # --- Left Column ---
        left_col_frame = ttk.Frame(self.definition_frame)
        left_col_frame.grid(row=0, column=0, sticky="new")
        left_col_frame.grid_columnconfigure(1, weight=1)

        # Locales
        ttk.Label(left_col_frame, text="Locales:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.locale_var = tk.StringVar()
        self.locale_combobox = ttk.Combobox(left_col_frame, textvariable=self.locale_var)
        self.locale_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Diarization Enabled
        self.diarization_enabled_var = tk.BooleanVar(value=False)
        self.diarization_check = ttk.Checkbutton(left_col_frame, text="Enable Diarization", variable=self.diarization_enabled_var, command=self.toggle_diarization_fields)
        self.diarization_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Max Speakers
        self.max_speakers_label = ttk.Label(left_col_frame, text="Max Speakers:")
        self.max_speakers_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.max_speakers_var = tk.IntVar(value=2)
        self.max_speakers_spinbox = ttk.Spinbox(left_col_frame, from_=1, to=10, textvariable=self.max_speakers_var, width=10)
        self.max_speakers_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Channels
        ttk.Label(left_col_frame, text="Channels:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        channel_frame = ttk.Frame(left_col_frame)
        channel_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.channel_0_var = tk.BooleanVar(value=True) # Default to [0]
        self.channel_1_var = tk.BooleanVar(value=False)
        self.channel_0_check = ttk.Checkbutton(channel_frame, text="0", variable=self.channel_0_var)
        self.channel_0_check.pack(side="left")
        self.channel_1_check = ttk.Checkbutton(channel_frame, text="1", variable=self.channel_1_var)
        self.channel_1_check.pack(side="left", padx=(10, 0))

        # Custom Properties
        self.postprocessing_dump_var = tk.BooleanVar(value=False)
        self.postprocessing_dump_check = ttk.Checkbutton(
            left_col_frame,
            text="Enable DPP Data Dump",
            variable=self.postprocessing_dump_var
        )
        self.postprocessing_dump_check.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # --- Right Column ---
        right_col_frame = ttk.Frame(self.definition_frame)
        right_col_frame.grid(row=0, column=1, sticky="new")
        right_col_frame.grid_columnconfigure(0, weight=1) # Make the column expandable

        # Custom Model
        self.use_custom_model_var = tk.BooleanVar(value=False)
        self.use_custom_model_check = ttk.Checkbutton(
            right_col_frame,
            text="Use Custom Model",
            variable=self.use_custom_model_var,
            command=self._toggle_custom_model_fields
        )
        self.use_custom_model_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.custom_model_frame = ttk.Frame(right_col_frame)
        self.custom_model_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.custom_model_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(self.custom_model_frame, text="Model (JSON):").grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        self.custom_model_text = tk.Text(self.custom_model_frame, height=4, width=30, font=self.default_font)
        self.custom_model_text.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Enhanced Mode
        self.use_enhanced_mode_var = tk.BooleanVar(value=False)
        self.use_enhanced_mode_check = ttk.Checkbutton(
            right_col_frame,
            text="Enable Enhanced Mode",
            variable=self.use_enhanced_mode_var,
            command=self._toggle_enhanced_mode_fields
        )
        self.use_enhanced_mode_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.enhanced_mode_frame = ttk.Frame(right_col_frame)
        self.enhanced_mode_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.enhanced_mode_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(self.enhanced_mode_frame, text="Task:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.enhanced_mode_task_var = tk.StringVar(value="transcribe")
        self.enhanced_mode_task_menu = ttk.Combobox(
            self.enhanced_mode_frame,
            textvariable=self.enhanced_mode_task_var,
            values=["transcribe", "translate"],
            state="readonly"
        )
        self.enhanced_mode_task_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.enhanced_mode_frame, text="Prompt:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.enhanced_mode_prompt_var = tk.StringVar()
        self.enhanced_mode_prompt_entry = ttk.Entry(self.enhanced_mode_frame, textvariable=self.enhanced_mode_prompt_var)
        self.enhanced_mode_prompt_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- Action and Output ---
        self.send_button = ttk.Button(main_frame, text="Send Request", command=self.send_request)
        self.send_button.pack(pady=10)

        output_frame = ttk.LabelFrame(main_frame, text="Output")
        output_frame.pack(fill="both", expand=True, pady=5)
        self.output_font = tkfont.Font(family=self.default_font[0], size=self.default_font[1])
        self.output_text = tk.Text(output_frame, wrap="word", height=15, font=self.output_font)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)

        self._configure_highlighting_tags()
        self._create_menu()

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)

        view_menu.add_command(label="Increase Font Size", command=self.increase_font_size)
        view_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size)
        view_menu.add_separator()

        font_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Select Font", menu=font_menu)

        # Populate with common fixed-width fonts
        common_fonts = ["Courier New", "Consolas", "Lucida Console", "Monaco", "Menlo", "Fira Code"]
        for f in common_fonts:
            font_menu.add_command(label=f, command=lambda f=f: self.change_font(f))

    def _configure_highlighting_tags(self):
        if Token is None: # Pygments not installed
            return
        # Basic color scheme for JSON
        self.output_text.tag_configure(str(Token.Keyword), foreground='#0000ff')
        self.output_text.tag_configure(str(Token.Name.Tag), foreground='#008000') # Keys
        self.output_text.tag_configure(str(Token.Literal.String.Double), foreground='#a31515')
        self.output_text.tag_configure(str(Token.Literal.Number.Integer), foreground='#098658')
        self.output_text.tag_configure(str(Token.Literal.Number.Float), foreground='#098658')
        self.output_text.tag_configure(str(Token.Punctuation), foreground='#333333')

    def _highlight_json(self, json_string):
        if lex is None: # Pygments not installed
            self.output_text.insert(tk.END, json_string)
            return

        # Don't delete, just insert tokens at the end
        tokens = lex(json_string, JsonLexer())
        for token_type, token_value in tokens:
            self.output_text.insert(tk.END, token_value, (str(token_type),))
    def _set_widget_state_recursively(self, widget, state):
        """Recursively set the state of a widget and all its children."""
        try:
            # For Comboboxes, 'normal' makes them editable. If we are enabling
            # them, we should respect their intended 'readonly' state.
            if isinstance(widget, ttk.Combobox) and state == 'normal':
                # This assumes comboboxes are either 'readonly' or 'disabled'
                widget.configure(state='readonly')
            else:
                widget.configure(state=state)
        except tk.TclError:
            # This widget doesn't have a 'state' option (e.g., a Frame)
            pass
        for child in widget.winfo_children():
            self._set_widget_state_recursively(child, state)

    def _toggle_function_fields(self, event=None):
        selected_function = self.function_var.get()
        is_transcribe = selected_function == "transcribe"
        state = 'normal' if is_transcribe else 'disabled'

        # Recursively enable/disable all widgets in the relevant frames
        self._set_widget_state_recursively(self.audio_file_frame, state)
        self._set_widget_state_recursively(self.definition_frame, state)

        if is_transcribe:
            # If enabling, we need to re-apply the specific states of conditional fields
            self.toggle_diarization_fields()
            self._toggle_custom_model_fields()
            self._toggle_enhanced_mode_fields()

    def change_font(self, font_family):
        self.output_font.config(family=font_family)

    def increase_font_size(self):
        size = self.output_font.cget("size")
        self.output_font.config(size=size + 1)

    def decrease_font_size(self):
        size = self.output_font.cget("size")
        if size > 6:
            self.output_font.config(size=size - 1)

    def update_key(self, event=None):
        region = self.region_var.get()
        if keyring:
            try:
                key = keyring.get_password(self.SERVICE_NAME, region)
                if key:
                    self.key_var.set(key)
                else:
                    self.key_var.set("KEY NOT FOUND IN STORE")
            except Exception as e:
                self.key_var.set(f"Error reading from keyring: {e}")
        else:
            self.key_var.set("keyring library not installed")

    def save_key_to_keyring(self):
        if not keyring:
            messagebox.showerror("Keyring Error", "The 'keyring' library is not installed.\nPlease run 'pip install keyring'.")
            return

        region = self.region_var.get()
        key = self.key_var.get()

        if not region:
            messagebox.showerror("Error", "Please enter a region first.")
            return
        if not key or "KEY NOT FOUND" in key:
            messagebox.showerror("Error", "Please enter a valid key to save.")
            return

        try:
            keyring.set_password(self.SERVICE_NAME, region, key)
            messagebox.showinfo("Success", f"Successfully saved key for region: '{region}'")
            # Add the new region to the list if it's not already there
            if region not in self.region_menu['values']:
                self.region_menu['values'] = (*self.region_menu['values'], region)
        except Exception as e:
            messagebox.showerror("Keyring Error", f"Failed to save key for '{region}':\n{e}")

    def _check_keyring_backend(self):
        if keyring and not keyring.get_keyring():
            messagebox.showwarning(
                "Keyring Backend Warning",
                "No recommended backend found for the 'keyring' library.\n"
                "Your keys may be stored in a less secure, plaintext file.\n\n"
                "Please see the keyring documentation for installation instructions:\n"
                "https://keyring.readthedocs.io/en/latest/installation.html"
            )

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=(("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*"))
        )
        if filename:
            self.audio_file_var.set(filename)

    def toggle_diarization_fields(self):
        state = "normal" if self.diarization_enabled_var.get() else "disabled"
        self.max_speakers_label.config(state=state)
        self.max_speakers_spinbox.config(state=state)

    def _toggle_custom_model_fields(self):
        state = 'normal' if self.use_custom_model_var.get() else 'disabled'
        self._set_widget_state_recursively(self.custom_model_frame, state)

    def _toggle_enhanced_mode_fields(self):
        state = 'normal' if self.use_enhanced_mode_var.get() else 'disabled'
        self._set_widget_state_recursively(self.enhanced_mode_frame, state)

    def _toggle_api_version_fields(self, event=None):
        """Enable/disable Enhanced Mode based on the selected API version."""
        api_version = self.api_version_var.get()
        if api_version == "2024-11-15":
            # This version does not support enhanced mode
            self.use_enhanced_mode_check.config(state='disabled')
            self.use_enhanced_mode_var.set(False)
        else:
            # Assume future versions support it
            self.use_enhanced_mode_check.config(state='normal')
        # Update the fields based on the new state
        self._toggle_enhanced_mode_fields()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                # Populate regions from the map
                rg_map = config.get("rg_region_map", {})
                all_regions = set()
                for rg, regions in rg_map.items():
                    all_regions.update(regions)

                self.regions = sorted(list(all_regions))
                if self.regions:
                    self.region_menu['values'] = self.regions
                    self.region_var.set(self.regions[0])

                # Load locale history
                self.locale_history = config.get("locale_history", ["en-US, ja-JP", "en-US"])
                self.locale_combobox['values'] = self.locale_history
                if self.locale_history:
                    self.locale_var.set(self.locale_history[0])

                last_file = config.get("last_audio_file")
                if last_file and os.path.exists(last_file):
                    self.audio_file_var.set(last_file)

                font_family = config.get("font_family", self.default_font[0])
                font_size = config.get("font_size", self.default_font[1])
                self.output_font.config(family=font_family, size=font_size)

            except (json.JSONDecodeError, IOError):
                pass # Ignore errors in config file, start fresh

    def save_config(self):
        # Read existing config to preserve the region map
        config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass # Start fresh if config is broken

        # Update locale history
        current_locales = self.locale_var.get()
        if current_locales:
            # Remove from history if it exists, to move it to the top
            if current_locales in self.locale_history:
                self.locale_history.remove(current_locales)
            # Insert at the beginning
            self.locale_history.insert(0, current_locales)
            # Keep only the last 10 entries
            self.locale_history = self.locale_history[:10]
            # Immediately update the combobox in the GUI
            self.locale_combobox['values'] = self.locale_history

        # Update the values we manage
        config["last_audio_file"] = self.audio_file_var.get()
        config["font_family"] = self.output_font.cget("family")
        config["font_size"] = self.output_font.cget("size")
        config["locale_history"] = self.locale_history
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            # Don't crash if we can't write the config file
            pass

    def on_closing(self):
        self.save_config()
        self.destroy()

    def _convert_path_for_wsl(self, path):
        """Converts a Windows path to a WSL path if it looks like one."""
        if len(path) > 2 and path[1] == ':' and path[2] == '\\':
            drive = path[0].lower()
            rest = path[3:].replace('\\', '/')
            return f"/mnt/{drive}/{rest}"
        return path

    def send_request(self):
        self.save_config() # Save history and other settings immediately
        self.output_text.delete("1.0", tk.END)

        if requests is None:
            messagebox.showerror("Missing Library", "The 'requests' library is not installed.\nPlease run 'pip install requests' in your terminal.")
            self.output_text.insert(tk.END, "Error: 'requests' library not found.")
            return

        self.output_text.insert(tk.END, "Sending request...\n\n")
        self.update()

        selected_function = self.function_var.get()
        if selected_function == "transcribe":
            self._send_transcribe_request()
        elif selected_function == "locales":
            self._send_locales_request()

    def _send_locales_request(self):
        url = f"https://{self.region_var.get()}.api.cognitive.microsoft.com/speechtotext/transcriptions/locales?api-version={self.api_version_var.get()}"
        headers = {
            'Ocp-Apim-Subscription-Key': self.key_var.get()
        }

        try:
            # Mask key for printing
            masked_headers = headers.copy()
            if 'Ocp-Apim-Subscription-Key' in masked_headers:
                masked_headers['Ocp-Apim-Subscription-Key'] = '********'

            self.output_text.insert(tk.END, f"GET {url}\n")
            self.output_text.insert(tk.END, f"Request Headers: {json.dumps(masked_headers, indent=2)}\n\n")

            response = requests.get(url, headers=headers)
            self._process_and_display_response(response)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred while sending the request:\n{e}")
            self.output_text.insert(tk.END, f"\n\n--- Python Exception ---\n{e}")
        except Exception as e:
            messagebox.showerror("An Unexpected Error Occurred", str(e))
            self.output_text.insert(tk.END, f"\n\n--- Python Exception ---\n{e}")

    def _send_transcribe_request(self):
        audio_path = self.audio_file_var.get()
        if not audio_path or not os.path.exists(audio_path):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        # --- Build Definition JSON ---
        # Parse the comma-separated string of locales
        locales_str = self.locale_var.get()
        locales_list = [locale.strip() for locale in locales_str.split(',') if locale.strip()]

        definition = {
            "locales": locales_list,
            "diarization": {
                "enabled": self.diarization_enabled_var.get()
            }
        }
        if self.diarization_enabled_var.get():
            definition["diarization"]["maxSpeakers"] = self.max_speakers_var.get()

        # Add channels to the definition
        channels = []
        if self.channel_0_var.get():
            channels.append(0)
        if self.channel_1_var.get():
            channels.append(1)

        # Only add the key if channels are selected and the selection is not the default ([0])
        if channels and channels != [0]:
            definition["channels"] = channels

        # Handle custom properties
        custom_properties = {}
        if self.postprocessing_dump_var.get():
            custom_properties["isBatchDisplayPostprocessingDataDumpEnabled"] = "true"

        if custom_properties:
            definition["customProperties"] = custom_properties

        # Handle custom models
        if self.use_custom_model_var.get():
            model_json_str = self.custom_model_text.get("1.0", tk.END).strip()
            if model_json_str:
                try:
                    models = json.loads(model_json_str)
                    if isinstance(models, dict) and models:
                        definition["models"] = models
                    else:
                        raise json.JSONDecodeError("Input must be a non-empty JSON object.", model_json_str, 0)
                except json.JSONDecodeError as e:
                    messagebox.showerror("Invalid JSON", f"The custom model definition is not valid JSON:\n{e}")
                    return

        # Handle Enhanced Mode
        if self.use_enhanced_mode_var.get():
            enhanced_mode = {
                "enabled": True,
                "task": self.enhanced_mode_task_var.get()
            }
            prompt = self.enhanced_mode_prompt_var.get().strip()
            if prompt:
                enhanced_mode["prompt"] = [prompt]
            definition["enhancedMode"] = enhanced_mode

        # --- Build Request components ---
        url = f"https://{self.region_var.get()}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version={self.api_version_var.get()}"
        headers = {
            'Ocp-Apim-Subscription-Key': self.key_var.get()
        }

        data = {
            'definition': json.dumps(definition)
        }

        try:
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'audio': (os.path.basename(audio_path), audio_file, 'audio/mpeg')
                }

                # Mask key for printing
                masked_headers = headers.copy()
                if 'Ocp-Apim-Subscription-Key' in masked_headers:
                    masked_headers['Ocp-Apim-Subscription-Key'] = '********'

                self.output_text.insert(tk.END, f"POST {url}\n")
                self.output_text.insert(tk.END, f"Request Headers: {json.dumps(masked_headers, indent=2)}\n")
                self.output_text.insert(tk.END, f"Form Data: {json.dumps(data, indent=2)}\n\n")

                response = requests.post(url, headers=headers, data=data, files=files)
                self._process_and_display_response(response)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred while sending the request:\n{e}")
            self.output_text.insert(tk.END, f"\n\n--- Python Exception ---\n{e}")
        except IOError as e:
            messagebox.showerror("File Error", f"Could not open the audio file:\n{e}")
            self.output_text.insert(tk.END, f"\n\n--- Python Exception ---\n{e}")
        except Exception as e:
            messagebox.showerror("An Unexpected Error Occurred", str(e))
            self.output_text.insert(tk.END, f"\n\n--- Python Exception ---\n{e}")

    def _process_and_display_response(self, response):
        self.output_text.insert(tk.END, f"--- Response (Status: {response.status_code}) ---\n")

        # Print response headers
        self.output_text.insert(tk.END, "Response Headers:\n")
        formatted_headers = json.dumps(dict(response.headers), indent=2)
        self._highlight_json(formatted_headers)
        self.output_text.insert(tk.END, "\n\n")

        # Check if the response has content
        self.output_text.insert(tk.END, "Response Body:\n")
        if response.text:
            try:
                # Try to parse and pretty-print JSON
                parsed_json = response.json()
                formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                self._highlight_json(formatted_json)
            except json.JSONDecodeError:
                # If it's not JSON, just insert the raw text
                self.output_text.insert(tk.END, response.text)
        else:
            self.output_text.insert(tk.END, "[No content in response]")

        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)


if __name__ == "__main__":
    # Make the app DPI-aware on Windows
    if sys.platform == 'win32':
        try:
            # For Windows 8.1 and later
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            try:
                # For Windows Vista and later
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass # Not on a version of Windows that supports this

    app = CurlApp()
    app.mainloop()
