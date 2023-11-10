import os
import logging
import subprocess

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def convert_to_m4a(og_filepath: str) -> str:
    # if os.path.splitext(og_filepath)[1] == '.m4a':
    #     return og_filepath

    converted_filepath = os.path.splitext(og_filepath)[0] + ".m4a"
    command = ["ffmpeg", "-y", "-i", og_filepath, "-c:a", "aac", converted_filepath]
    subprocess.run(command, check=True)
    return converted_filepath


def get_audio_duration(filepath: str) -> float:
    result = subprocess.run(
        ["ffmpeg", "-i", filepath],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    for line in result.stdout.splitlines():
        if "Duration" in line:
            time = line.split(",")[0].split("Duration:")[1].strip()
            hours, minutes, seconds = map(float, time.split(":"))
            total_milliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000
            return total_milliseconds