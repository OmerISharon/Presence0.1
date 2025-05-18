import json
from pathlib import Path


def find_profile_by_email(email: str) -> str:
    """
    Read Chrome's Local State file to deduce the profile folder associated with the given Gmail account.
    Looks for a matching 'user_name' in the 'info_cache' section.
    """
    user_data_dir = Path.home() / "AppData/Local/Google/Chrome Beta/User Data"
    local_state_path = user_data_dir / "Local State"

    if not local_state_path.exists():
        raise FileNotFoundError("Chrome 'Local State' file not found.")

    with local_state_path.open("r", encoding="utf-8") as f:
        local_state = json.load(f)

    profiles = local_state.get("profile", {}).get("info_cache", {})
    for profile_dir, info in profiles.items():
        if info.get("user_name", "").lower() == email.lower():
            return profile_dir  # e.g., "Profile 1"

    raise ValueError(f"No Chrome profile found for Gmail: {email}")

def main():
    EmailAddress = "notepadclips@gmail.com"
    Profile = find_profile_by_email(EmailAddress)
    print(Profile)
    

if __name__ == "__main__":
    main()