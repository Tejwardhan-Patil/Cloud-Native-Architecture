#!/bin/bash

# Configurations
BACKUP_DIR="/var/backups/db"
DB_NAME="production_db"
TIMESTAMP=$(date +"%Y%m%d%H%M")
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-backup-$TIMESTAMP.sql.gz"
RETENTION_DAYS=7
S3_BUCKET="s3://db-backups-production"
LOG_FILE="/var/log/db_backup.log"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Log function
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Backup the database
log "Starting backup for database $DB_NAME"
if mysqldump -u root -p'password' "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    log "Backup successful: $BACKUP_FILE"
else
    log "Backup failed for $DB_NAME"
    exit 1
fi

# Upload backup to S3
log "Uploading backup to S3: $S3_BUCKET"
if aws s3 cp "$BACKUP_FILE" "$S3_BUCKET"; then
    log "Backup uploaded to S3 successfully: $BACKUP_FILE"
else
    log "Failed to upload backup to S3"
    exit 1
fi

# Remove old backups
log "Removing backups older than $RETENTION_DAYS days"
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -name "*.gz" -exec rm {} \;
log "Old backups removed"

# Verify S3 backup integrity
log "Verifying backup integrity on S3"
REMOTE_FILE_SIZE=$(aws s3 ls "$S3_BUCKET/$DB_NAME-backup-$TIMESTAMP.sql.gz" | awk '{print $3}')
LOCAL_FILE_SIZE=$(stat -c %s "$BACKUP_FILE")

if [ "$REMOTE_FILE_SIZE" -eq "$LOCAL_FILE_SIZE" ]; then
    log "Backup integrity verified successfully"
else
    log "Backup integrity verification failed"
fi

log "Backup process completed"