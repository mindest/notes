import subprocess
import json
import sys
import keyring
import argparse
import os

# This is the unique name for the service in your OS credential store.
SERVICE_NAME = "curl_gui_app"
# Define the config file path relative to this script's location
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "curl_gui_config.json")

def update_keys_and_config(resource_group):
    """
    Fetches all speech service accounts from a resource group, updates the
    local config file with their regions, and stores their keys securely.
    """
    print(f"Processing resource group: '{resource_group}'...")
    try:
        # 1. Get all speech accounts from Azure
        print("  - Querying Azure for speech service accounts...")
        accounts = _get_speech_accounts(resource_group)
        if not accounts:
            print("  - Status: No Speech service accounts found in this resource group.")
            return

        print(f"  - Found {len(accounts)} account(s).")

        # 2. Update the local JSON config file with the regions
        found_regions = sorted(list(set(acc['Location'] for acc in accounts)))
        _update_config_file(resource_group, found_regions)
        print(f"  - Successfully updated '{CONFIG_FILE}' with {len(found_regions)} region(s).")

        # 3. Fetch and store the key for each account in the keyring
        print("  - Storing API keys in secure keyring...")
        for account in accounts:
            account_name = account['Name']
            location = account['Location']

            keys_cmd = (
                f"az cognitiveservices account keys list -n {account_name} -g {resource_group} "
                f"--query \"{{key1:key1}}\" -o json"
            )
            keys_process = subprocess.run(keys_cmd, capture_output=True, text=True, shell=True, check=True)
            keys = json.loads(keys_process.stdout)
            key1 = keys.get('key1')

            if not key1:
                print(f"    - Warning: Could not retrieve key for '{account_name}'. Skipping.")
                continue

            keyring.set_password(SERVICE_NAME, location, key1)
            print(f"    - Stored key for region: '{location}'")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        _handle_azure_cli_error(e, resource_group)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def _update_config_file(resource_group, regions):
    """Helper to read, update, and write the JSON config file."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print(f"  - Warning: Could not parse existing '{CONFIG_FILE}'. A new one will be created.")

    if 'rg_region_map' not in config:
        config['rg_region_map'] = {}

    config['rg_region_map'][resource_group] = regions

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def _get_speech_accounts(resource_group):
    """Helper function to query Azure for speech accounts."""
    list_cmd = (
        f"az cognitiveservices account list --resource-group {resource_group} "
        f"--query \"[?kind=='SpeechServices'].{{Name:name, Location:location}}\" -o json"
    )
    process = subprocess.run(list_cmd, capture_output=True, text=True, shell=True, check=True)
    return json.loads(process.stdout)

def _handle_azure_cli_error(e, resource_group):
    """Helper function to print a standard error for Azure CLI failures."""
    print("\n--- Error ---", file=sys.stderr)
    print("Failed to execute Azure CLI command.", file=sys.stderr)
    print("Please ensure the Azure CLI is installed, you are logged in (`az login`),", file=sys.stderr)
    print(f"and the resource group '{resource_group}' is correct.", file=sys.stderr)
    print(f"Details: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Azure Speech keys, store them securely, and update the local region config file."
    )
    parser.add_argument("-g", "--resource-group", required=True, help="The Azure resource group to process.")
    args = parser.parse_args()

    if not keyring.get_keyring():
        print("Warning: No recommended backend found for 'keyring'. Keys may be stored in plaintext.", file=sys.stderr)

    update_keys_and_config(args.resource_group)
    print("\nProcess finished.")

if __name__ == "__main__":
    main()
