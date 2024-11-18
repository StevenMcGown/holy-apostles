0 12 * * * /usr/bin/python3 /path/to/your_script.py

# Start OBS and begin streaming immediately
obs --startstreaming --profile "YourProfileName"
# Stop OBS
pkill obs  # Linux/macOS
