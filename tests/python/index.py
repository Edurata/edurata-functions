import time
import os

def sleep(ms):
    time.sleep(ms / 1000.0)

def handler(inputs):
    print("Test inner logs")
    _sleep_time = inputs.get("sleepTime", 1000)
    _sleep_time = int(_sleep_time) if isinstance(_sleep_time, str) else _sleep_time
    _file_path = inputs.get("infile", "testFile.txt")
    _random_file_path = os.environ.get("DEPLOYMENT_ID") + ".txt"
    _message = inputs.get("message", "Hello there!")
    # message
    print(_message)

    # sleep
    sleep(_sleep_time)

    # dummy file
    with open(_random_file_path, "w") as file:
        # Write content to the file
        file.write("Just a dummy file to test multiple files.\n")

    if "infile" in inputs:
        with open(inputs["infile"], "r+") as file:
            file_data = file.read()
            file.write(file_data + _message)
    else:
        with open(_file_path, "w") as file:
            file.write(_message)

    print("Test error inner logs")

    return {
        "sleepTime": _sleep_time + 1000,
        "outfile": _file_path,
        "randomfile": _random_file_path,
        "message": _message
    }