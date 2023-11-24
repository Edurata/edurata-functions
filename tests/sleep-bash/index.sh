#!/bin/bash

# Function to simulate sleep in milliseconds
sleep_ms() {
    sleep $(( $1 / 1000 ))
}

# Main handler function
handler() {
    echo "Test inner logs"
    sleep_time=${1:-1000}
    file_path=${2:-"testFile.txt"}

    # Sleep for the specified time
    sleep_ms $sleep_time

    # Check if file path is provided and write to the file
    if [ -n "$2" ]; then
        if [ -f "$file_path" ]; then
            echo " Hey there again!" >> "$file_path"
        else
            echo " Hey there!" > "$file_path"
        fi
    else
        echo " Hey there!" > "$file_path"
    fi

    echo "Test error inner logs"
    sleep_time=$(( sleep_time + 1000 ))
    echo "Sleep time: $sleep_time, File: $file_path"
}