# Speech-to-Text cURL GUI

This application provides a graphical user interface (GUI) for sending transcription requests to the Azure Speech-to-Text API. It simplifies the process of constructing and sending `curl` requests by providing a user-friendly form.

## Prerequisites

Before running the application, you need to set up your environment and credentials.

### 1. Install Dependencies

Install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 2. Azure Login

You must be logged into your Azure account via the Azure CLI. Run the following command and follow the authentication process:

```bash
az login
```

### 3. Fetch and Store Subscription Keys

The application retrieves API keys from your system's secure credential store (Keyring).

1.  **Fetch Keys**: The `azure_key_fetcher.py` script (not provided here, but assumed to exist) is used to retrieve the subscription keys from your Azure account and store them.
2.  **Store in Keyring**: Once you have a key, run the main GUI.
    *   Select the appropriate **Endpoint Region** from the dropdown.
    *   Paste the corresponding subscription key into the **Subscription Key** field.
    *   Click the **Save Key** button. This will securely store the key in your system's keyring for that specific region.

The application will automatically load the correct key whenever you select a region.

## Main Usage

To run the application, execute the `main.py` script:

```bash
python main.py
```

### Sending a Transcription Request

1.  **Function**: Select "transcribe" from the function dropdown.
2.  **Endpoint Region**: Choose the Azure region for your Speech service. The subscription key will be automatically populated if it has been saved.
3.  **API Version**: Select the desired API version.
4.  **Audio File**: Click "Browse..." to select a local audio file (`.mp3`, `.wav`, etc.).
5.  **Definition**: Configure the transcription options as needed:
    *   **Locales**: Enter a comma-separated list of locales (e.g., `en-US,ja-JP`).
    *   **Enable Diarization**: Check to enable speaker separation and set the max number of speakers.
    *   **Channels**: Select the audio channels to process. Defaults to `[0]`.
    *   **Enable DPP Data Dump**: A custom property for enabling post-processing data dump.
    *   **Use Custom Model**: Check to provide a custom model endpoint in JSON format.
    *   **Enable Enhanced Mode**: Check to enable enhanced processing, select a task (`transcribe` or `translate`), and provide an optional prompt.
6.  **Send Request**: Click the **Send Request** button. The full API response, including headers and body, will be displayed in the output text area.

### Configuration File

The application creates a `curl_gui_config.json` file in the same directory to store your last-used audio file, locale history, and font settings.
