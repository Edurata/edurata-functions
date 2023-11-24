import time
import os

def sleep(ms):
    time.sleep(ms / 1000.0)

def handler(inputs):
    print("Test inner logs")
    _sleep_time = inputs.get("sleepTime", 1000)
    _sleep_time = int(_sleep_time) if isinstance(_sleep_time, str) else _sleep_time
    _file_path = inputs.get("file", "testFile.txt")

    sleep(_sleep_time)

    if "file" in inputs:
        with open(inputs["file"], "r+") as file:
            file_data = file.read()
            file.write(file_data + " Hey there again!")
    else:
        with open(_file_path, "w") as file:
            file.write("Hey there!")

    print("Test error inner logs")

    return {
        "sleepTime": _sleep_time + 1000,
        "file": _file_path,
    }