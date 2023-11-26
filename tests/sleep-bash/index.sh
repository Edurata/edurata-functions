#!/bin/bash

# Function to simulate sleep in milliseconds
sleep_ms() {
    sleep $(( $1 / 1000 ))
}

# Main handler function
handler() {
    local json_input=$1

    echo "Test inner logs"

    # Extract values using jq
    sleep_time=$(echo "$json_input" | jq -r '.sleepTime // 1000')
    file_path=$(echo "$json_input" | jq -r '.file // "testFile.txt"')

    # Sleep for the specified time
    sleep_ms $sleep_time

    # Check if file path is provided and write to the file
    if [ -n "$(echo "$json_input" | jq -r '.file')" ]; then
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
    echo "{\"sleepTime\":$sleep_time,\"file\":\"$file_path\"}" > $CMD_DIR/output.json
}
