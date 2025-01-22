import requests as re
import urllib.parse as prs
import subprocess
import os
from winotify import Notification, audio

def nvidia_driver_version() -> float | None:
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)        
        if result.stderr:
            print(f"Error: {result.stderr}")
            return None
        driver_version = result.stdout.strip()
        return float(driver_version)

    except FileNotFoundError:
        print("nvidia-smi command not found. Ensure NVIDIA drivers are installed.")
        return None

def latest_driver_version(**kwargs) -> None:
    required_driver_name = "GeForce Game Ready Driver"
    current_card_series = "GeForce RTX 20 Series"

    payload = {
        "func": "DriverManualLookup",
        "psid": "107",                  # Product series ID
        "pfid": "902",                  # Product family ID
        "osID": "57",                   # Operating system ID
        "languageCode": "1033",         # Language code (English)
        "isWHQL": "0",                  # WHQL certified (0 for no, 1 for yes)
        "beta": "null",                 # Beta drivers (null if not specified)
        "dltype": "-1",                 # Download type (-1 for any)
        "dch": "1",                     # Driver type (DCH or standard)
        "upCRD": "null",                # Current release driver (null if not specified)
        "qnf": "0",                     # Quick fix (0 for no, 1 for yes)
        "ctk": "null",                  # Token (null if not specified)
        "sort1": "1",                   # Sort by preference (1 for date)
        "numberOfResults": "20"         # Maximum search depth of 5 results
    }
    #payload.update(kwargs)

    URL = "https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php"

    response = re.get(URL, params=payload)
    json_object = response.json()
    if response.status_code == 200: 

        current_driver_version = nvidia_driver_version()
        drivers = json_object["IDS"]

        if current_driver_version is not None:
            for driver in drivers :
                driver_name = prs.unquote(driver["downloadInfo"]["Name"])
                driver_version = float(driver["downloadInfo"]["Version"])

                series_compatible = False
                for series in driver["downloadInfo"]["series"] :
                    if prs.unquote(series["seriesname"]) == current_card_series :
                        series_compatible = True
                        break
                    
                if driver_name == required_driver_name and driver_version > current_driver_version and series_compatible: 
                    icon_path = os.path.join(os.path.dirname(__file__), 'nvidia-icon.png')
                    toast = Notification(
                        app_id= f'Nvidia driver {driver_version} is now available',
                        title=" ",
                        msg=" ",
                        duration="long",
                        icon=icon_path
                    )
                    download_url = driver["downloadInfo"]["DownloadURL"]
                    toast.add_actions(label="download", launch=download_url)
                    toast.set_audio(audio.SMS, loop=False)
                    toast.show()
                    break
    

latest_driver_version()