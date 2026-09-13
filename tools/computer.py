import subprocess


ALLOWED_APPLICATIONS = {
    "Calculator",
    "Finder",
    "Safari",
    "Visual Studio Code",
}


def open_application(application: str):
    """Open an approved macOS application."""

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
            "message": f"{application} has been opened.",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Could not open {application}: {error}",
        }