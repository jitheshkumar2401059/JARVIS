import subprocess


ALLOWED_APPLICATIONS = {
    "Calculator",
    "Finder",
    "Safari",
    "Visual Studio Code",
    "Google Chrome",
    "Notes",
    "Preview",
    "TextEdit",
    "Music",
    "System Settings",
    "ChatGPT",
    "Claude",
    "Antigravity",
    "Ollama",
    "WhatsApp",
    "Photos",
}
APPLICATION_ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "vs code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "chat gpt": "ChatGPT Classic",
    "chatgpt": "ChatGPT Classic",
    "chatgpt classic": "ChatGPT Classic",
    "claude": "Claude",
    "antigravity": "Antigravity",
    "ollama": "Ollama",
    "whatsapp": "WhatsApp",
    "photos": "Photos",
    "calculator": "Calculator",
    "finder": "Finder",
    "safari": "Safari",
    "notes": "Notes",
    "preview": "Preview",
    "textedit": "TextEdit",
    "music": "Music",
    "system settings": "System Settings",
    "settings": "System Settings",
}


def open_application(application: str):
    """Open an approved macOS application."""

    requested_application = application.strip().lower()

    if requested_application in APPLICATION_ALIASES:
        application = APPLICATION_ALIASES[requested_application]

    if application not in ALLOWED_APPLICATIONS:
        return {
            "success": False,
            "message": f"{application} is not an approved application.",
        }

    try:
        subprocess.run(
            ["open", "-a", application],
            check=True,
        )

        return {
            "success": True,
            "application": application,
            "message": f"{application} has been opened.",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not open {application}: {error}",
        }
def close_application(application: str):
    """Close an approved macOS application."""

    requested_application = application.strip().lower()

    if requested_application in APPLICATION_ALIASES:
        application = APPLICATION_ALIASES[requested_application]

    if application not in ALLOWED_APPLICATIONS:
        return {
            "success": False,
            "message": f"{application} is not an approved application.",
        }

    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "{application}" to quit',
            ],
            check=True,
        )

        return {
            "success": True,
            "application": application,
            "message": f"{application} has been closed.",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not close {application}: {error}",
        }
def is_application_running(application: str):
    """Check whether an approved macOS application is running."""

    requested_application = application.strip().lower()

    if requested_application in APPLICATION_ALIASES:
        application = APPLICATION_ALIASES[requested_application]

    if application not in ALLOWED_APPLICATIONS:
        return {
            "success": False,
            "message": f"{application} is not an approved application.",
        }

    try:
        result = subprocess.run(
            ["pgrep", "-x", application],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return {
                "success": True,
                "running": True,
                "application": application,
                "message": f"{application} is currently running.",
            }

        return {
            "success": True,
            "running": False,
            "application": application,
            "message": f"{application} is not currently running.",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not check {application}: {error}",
        }
def restart_application(application: str):
    """Restart an approved macOS application."""

    requested_application = application.strip().lower()

    if requested_application in APPLICATION_ALIASES:
        application = APPLICATION_ALIASES[requested_application]

    if application not in ALLOWED_APPLICATIONS:
        return {
            "success": False,
            "message": f"{application} is not an approved application.",
        }
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "{application}" to quit',
            ],
            check=True,
        )

        import time
        time.sleep(2)

        subprocess.run(
            ["open", "-a", application],
            check=True,
        )

        return {
            "success": True,
            "application": application,
            "message": f"{application} has been restarted.",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not restart {application}: {error}",
        }
def focus_application(application: str):
    """Bring an approved macOS application to the front."""

    requested_application = application.strip().lower()

    if requested_application in APPLICATION_ALIASES:
        application = APPLICATION_ALIASES[requested_application]

    if application not in ALLOWED_APPLICATIONS:
        return {
            "success": False,
            "message": f"{application} is not an approved application.",
        }
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "{application}" to activate',
            ],
            check=True,
        )

        return {
            "success": True,
            "application": application,
            "message": f"{application} is now in front.",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not focus {application}: {error}",
        }
def list_approved_applications():
    """Return the applications approved for JARVIS control."""
    return {
        "success": True,
        "applications": sorted(ALLOWED_APPLICATIONS),
        "message": (
            "These applications are approved for computer control: "
            + ", ".join(sorted(ALLOWED_APPLICATIONS))
        ),
    }