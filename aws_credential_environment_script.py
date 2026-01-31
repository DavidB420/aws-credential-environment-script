import json
import sys
import subprocess
import configparser
import os
from pathlib import Path

def runCmd(cmd: str, output=True):
    try:
        result = subprocess.run(cmd,shell=True,capture_output=output,text=True,check=True)
        return result.stdout.strip() if output else None
    except:
        print("An error occured when attempting to execute '" + cmd + "'")
        sys.exit(1)

def getProfile():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.aws/config"))
    profiles = [s.replace("profile ", "") for s in config.sections() if s.startswith("profile ")]
    return profiles[-1] if profiles else "default"

def main():
    #Get default profile name, create new profile if it doesnt exist
    profileName = getProfile()
    if profileName == "default":
        print("Configuring new AWS profile...")
        runCmd(f"aws configure sso",output=False)
        profileName = getProfile()
    print("Using default profile name " + profileName)

    #Get SSO sign on
    print("\nRunning AWS SSO sign-on...")
    runCmd(f"aws sso login --profile {profileName}",output=False)
    input("Press Enter to continue...")

    #Read data from json file
    print(f"\nReading credentials from profile {profileName}...")
    savedOutput = runCmd(f"aws configure export-credentials --profile {profileName}",output=True)
    print(f"Recovered JSON: {savedOutput}")
    jsonSavedOutput = json.loads(savedOutput)
    #saves to a .env at the current directory, change if needed
    envPath = Path(".env")
    with envPath.open("w") as f:
        f.write(f"AWS_ACCESS_KEY_ID={jsonSavedOutput['AccessKeyId']}\n")
        f.write(f"AWS_SECRET_ACCESS_KEY={jsonSavedOutput['SecretAccessKey']}\n")
        f.write(f"AWS_SESSION_TOKEN={jsonSavedOutput.get('SessionToken','')}\n")
        f.write(f"AWS_REGION={jsonSavedOutput.get('Region','') if jsonSavedOutput.get('Region','') else "ca-central-1"}\n")

    print("\nCompleted!")




main()