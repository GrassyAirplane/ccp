#!/bin/sh

DB_PATH="/data/rewind.sqlite"
INIT_SQL="/init.sql"

echo "Checking if database exists at $DB_PATH..."

if [ ! -f "$DB_PATH" ]; then
    echo "Database does not exist. Creating new database..."
    sqlite3 "$DB_PATH" < "$INIT_SQL"
    echo "Database created successfully!"
else
    echo "Database already exists."
fi

echo "Database initialization complete."