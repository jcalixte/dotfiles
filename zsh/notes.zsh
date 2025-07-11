#!/usr/bin/env zsh

# Fleeting Notes Shortcuts
# ------------------------

# Fixed notes directory path
NOTES_DIR="$HOME/jcnote/notes"
INBOX_DIR="$NOTES_DIR/_inbox"

# Create a new fleeting note for today
# Format: YYYY-MM-DD.md with title DD/MM/YYYY
function new-note() {
  local date_filename=$(date +"%Y-%m-%d")
  local date_title=$(date +"%d/%m/%Y")
  local latest_note="${INBOX_DIR}/${date_filename}.md"

  # Create _inbox directory if it doesn't exist
  mkdir -p "${INBOX_DIR}"

  # Check if the file already exists
  if [[ ! -f "${latest_note}" ]]; then
    # Create the note with proper title if it doesn't exist
    echo "# ${date_title}\n" > "${latest_note}"
    echo "Created new fleeting note: ${latest_note}"
  else
    echo "Opening existing note: ${latest_note}"
  fi

  $EDITOR -n "${NOTES_DIR}"
  $EDITOR "${latest_note}"
}

# Open the oldest fleeting note in _inbox directory
function open-oldest-note() {
  # Check if _inbox exists and has markdown files
  if [[ ! -d "${INBOX_DIR}" || -z "$(ls -A ${INBOX_DIR}/*.md 2>/dev/null)" ]]; then
    echo "No fleeting notes found in ${INBOX_DIR}/"
    return 1
  fi

  # Find the first file alphabetically (oldest by YYYY-MM-DD naming)
  local oldest_note=$(ls -1 ${INBOX_DIR}/*.md | sort | head -n 1)

  echo "Opening oldest note: ${oldest_note}"
  $EDITOR -n "${NOTES_DIR}"
  $EDITOR "${oldest_note}"
}

# Git quick commit and push with timestamp
function git-commit-timestamp() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  git add .

  if git diff --cached --exit-code > /dev/null; then
    return 0
  fi
  
  git commit -m "${timestamp}"
  git push
  echo "✨ Changes pushed: ${timestamp}"
}

function git-commit-timestamp-watch() {
  while true; do
    git-commit-timestamp
    sleep 120
  done
}

# Create aliases for easier access
alias nn="new-note"
alias on="open-oldest-note"
alias gct="git-commit-timestamp"
alias gctw="git-commit-timestamp-watch"
