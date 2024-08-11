#!/bin/bash

# Function to initialize the in-memory database
initialize_db() {
  echo "Initializing in-memory SQLite database..."

  # Define the path for the temporary SQLite database file
  export DB_FILE=$(mktemp)

  # Write the schema to initialize the database
  cat <<EOF | sqlite3 $DB_FILE
CREATE TABLE Recipe (
    id INTEGER PRIMARY KEY,
    title TEXT,
    sunday BOOLEAN,
    monday BOOLEAN,
    tuesday BOOLEAN,
    wednesday BOOLEAN,
    thursday BOOLEAN,
    friday BOOLEAN,
    saturday BOOLEAN
);

CREATE TABLE Ingredient (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER,
    name TEXT,
    quantity TEXT,
    optional BOOLEAN,
    FOREIGN KEY (recipe_id) REFERENCES Recipe(id)
);
EOF

  echo "Database initialized at $DB_FILE."

  # Export the database file path to make it accessible to the Python script
  export DB_FILE

  # Keep the script running to keep the database alive
  echo "Press [CTRL+C] to stop..."
  while :; do sleep 1; done
}

# On script termination, clean up
cleanup() {
  echo "Cleaning up..."
  if [[ -n "$DB_FILE" && -f "$DB_FILE" ]]; then
    rm "$DB_FILE"
    echo "Database file $DB_FILE deleted."
  fi
  echo "Done."
}

# Trap the exit signal to run cleanup
trap cleanup EXIT

# Initialize the database and keep the script running
initialize_db

