"""Get updates on clipboard changes and log them."""

import logging
import re
from datetime import date, datetime, timedelta
from pathlib import Path

RE_UPPERCASE = re.compile(r"[A-Z]")
RE_LOWERCASE = re.compile(r"[a-z]")
RE_DIGIT = re.compile(r"\d")
RE_SPECIAL = re.compile(r"[^A-Za-z0-9]")


class ClipboardLogHandler(logging.Handler):
    """Custom logging handler to log clipboard changes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Start a new log file at the beginning of Sunday
        last_sunday = date.today() - timedelta(days=datetime.today().weekday() + 1)

        self.log_path = Path(f"clipboard_log_{last_sunday.strftime('%Y-%m-%d')}.md")

        day_header = f"# {date.today().strftime('%Y-%m-%d')}"
        has_header = False
        if self.log_path.exists():
            text = self.log_path.read_text()
            has_header = day_header in text

        with self.log_path.open("a") as out:    
            if not has_header:
                out.write(f"{day_header}\n\n")
            self.last_timestamp = datetime.now()
            out.write(f"{self.last_timestamp.strftime('\n## %H:%M (start)')}\n\n")

        self.last_entry = None

    def emit(self, record):
        log_entry = self.format(record)
        # Here you can implement the logic to save log_entry to a file or database
        # For example, you could write it to a file:

        if log_entry == self.last_entry:
            return
        self.last_entry = log_entry

        with self.log_path.open("a") as out:

            if self.last_timestamp + timedelta(minutes=15) < datetime.now():
                self.last_timestamp = datetime.now()
                out.write(f"\n{self.last_timestamp.strftime('\n## %H:%M')}\n\n")

            out.write(f"{log_entry}\n")


def filter_password(text: str) -> str:
    """Filter out passwords from the text.  E.g. Passw0rd!

    d4a5c93073a78f365d348f2532da463fa77c02b8 is a perfectly good password this method
    would not protect. Also passphrases are harder, could adopt using a particular word
    in all your passphrases.
    """
    if len(text.split()) > 1:
        # space or newline *in* text => not a password
        return text
    if all(
        (
            RE_UPPERCASE.search(text),
            RE_LOWERCASE.search(text),
            RE_DIGIT.search(text),
            RE_SPECIAL.search(text),
        )
    ):
        return "[PASSWORD?]"
    return text


def log_clipboard_change(text: str) -> None:
    """Log the clipboard change."""
    filtered_text = filter_password(text).replace("\r\n", "\n")
    logger.info(filtered_text)


# set logging level to INFO with timestamp with format "YYYY-MM-DD HH:MM:SS"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(ClipboardLogHandler())
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

if __name__ == "__main__":
    # Example usage
    log_clipboard_change("This is a test clipboard change.")
    log_clipboard_change("Passw0rd!")
