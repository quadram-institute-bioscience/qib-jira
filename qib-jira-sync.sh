# File sync script
# Syncs two files every hour

SOURCE_FILE="/data/software/qib-jira/qib-jira.db"
DEST_FILE="/qib/research-groups/CoreBioInfo/tickets/qib-jira.db"

# Log file for tracking sync operations
LOG_FILE="/var/log/file-sync.log"

# Function to log messages with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    log_message "ERROR: Source file $SOURCE_FILE does not exist"
    exit 1
fi

# Create destination directory if it doesn't exist
DEST_DIR=$(dirname "$DEST_FILE")
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
    log_message "Created destination directory: $DEST_DIR"
fi

# Perform the sync
if cp "$SOURCE_FILE" "$DEST_FILE"; then
    log_message "Successfully synced $SOURCE_FILE to $DEST_FILE"

    # Optional: Set permissions if needed
    # chmod 644 "$DEST_FILE"

    # Optional: Change ownership if needed
    # chown user:group "$DEST_FILE"

else
    log_message "ERROR: Failed to sync $SOURCE_FILE to $DEST_FILE"
    exit 1
fi
