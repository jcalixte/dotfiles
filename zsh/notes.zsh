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
  
  # Try to push, if it fails try to pull and push again
  if ! git push; then
    echo "⚠️  Push failed, pulling changes first..."
    if git pull --no-edit; then
      echo "🔄 Pull successful, pushing again..."
      if git push; then
        echo "✨ Changes pushed after pull: ${timestamp}"
      else
        echo "❌ Push failed even after pull: ${timestamp}"
        return 1
      fi
    else
      echo "❌ Pull failed: ${timestamp}"
      return 1
    fi
  else
    echo "✨ Changes pushed: ${timestamp}"
  fi
}

function git-commit-timestamp-watch() {
  while true; do
    git-commit-timestamp
    sleep 200
  done
}

# Notes Tree Display
# ------------------

# Global associative array to track visited files (prevent infinite loops)
declare -A _notes_visited_files

# Extract the title from a markdown file (first # heading)
function _extract_markdown_title() {
  local file="$1"
  if [[ -f "$file" ]]; then
    # Get the first line that starts with # and extract the title
    local title=$(grep -m 1 '^#[[:space:]]' "$file" 2>/dev/null | sed 's/^#[[:space:]]*//')
    if [[ -n "$title" ]]; then
      echo "$title"
    else
      echo ""
    fi
  else
    echo ""
  fi
}

# Extract markdown links from a file, filtering only .md files
function _extract_markdown_links() {
  local file="$1"
  local base_dir="$(dirname "$file")"
  
  if [[ ! -f "$file" ]]; then
    return 1
  fi
  
  # Extract all markdown links, excluding YouTube links and external URLs
  grep -oE '\[[^]]*\]\([^)]*\.md[^)]*\)' "$file" 2>/dev/null | while read -r link; do    
    # Extract the URL part from [text](url)
    local url=$(echo "$link" | sed -n 's/.*\](\([^)]*\)).*/\1/p')
    
    # Skip external URLs (http/https)
    if [[ "$url" =~ ^https?:// ]]; then
      continue
    fi
    
    # Remove anchor (#section) if present
    url=$(echo "$url" | sed 's/#.*//')
    
    # Skip empty URLs
    if [[ -z "$url" ]]; then
      continue
    fi
    
    # Resolve relative path
    local resolved_path
    if [[ "$url" = /* ]]; then
      # Absolute path
      resolved_path="$url"
    else
      # Relative path - resolve it relative to the current file's directory
      resolved_path="$(cd "$base_dir" && realpath "$url" 2>/dev/null)"
    fi
    
    # Only output if the resolved path exists and is a .md file
    if [[ -n "$resolved_path" && -f "$resolved_path" && "$resolved_path" == *.md ]]; then
      echo "$resolved_path"
    fi
  done
}

# Recursive function to parse markdown tree
function _parse_markdown_tree() {
  local current_file="$1"
  local level="$2"
  local is_last="$3"
  local prefix="$4"
  
  # Get absolute path for tracking visited files
  local abs_path="$(realpath "$current_file" 2>/dev/null)"
  if [[ -z "$abs_path" ]]; then
    abs_path="$current_file"
  fi
  
  # Check if file exists
  if [[ ! -f "$current_file" ]]; then
    echo "${prefix}├── $(basename "$current_file") (🕳️)"
    return 1
  fi
  
  # Check if already visited (prevent infinite loops)
  if [[ -n "${_notes_visited_files[$abs_path]}" ]]; then
    local title=$(_extract_markdown_title "$current_file")
    local display_name="$(basename "$current_file")"
    if [[ -n "$title" ]]; then
      display_name="$display_name ($title)"
    fi
    echo "${prefix}├── $display_name (➰)"
    return 0
  fi
  
  # Mark as visited
  _notes_visited_files[$abs_path]=1
  
  # Extract title and display current file
  local title=$(_extract_markdown_title "$current_file")
  local display_name="$(basename "$current_file")"
  if [[ -n "$title" ]]; then
    display_name="$display_name | $title"
  fi
  
  # Choose tree character based on whether this is the last item
  local tree_char="├──"
  local next_prefix="$prefix│   "
  if [[ "$is_last" == "true" ]]; then
    tree_char="└──"
    next_prefix="$prefix    "
  fi
  
  echo "${prefix}${tree_char} $display_name"
  
  # Extract links from current file
  local links=()
  while IFS= read -r link; do
    links+=("$link")
  done < <(_extract_markdown_links "$current_file")
  
  # Process each link recursively
  local total_links=${#links[@]}
  local i=1
  for link in "${links[@]}"; do
    local is_last_link="false"
    if [[ $i -eq $total_links ]]; then
      is_last_link="true"
    fi
    
    _parse_markdown_tree "$link" $((level + 1)) "$is_last_link" "$next_prefix"
    ((i++))
  done
}

# Main function to display notes tree starting from README.md
function notes-tree() {
  local start_file="${NOTES_DIR}/README.md"
  
  # Check if README.md exists
  if [[ ! -f "$start_file" ]]; then
    echo "❌ Fichier README.md introuvable dans ${NOTES_DIR}/"
    return 1
  fi
  
  # Clear visited files tracking
  _notes_visited_files=()
  
  echo "📝 Arbre des notes markdown depuis README.md"
  echo ""
  
  # Start recursive parsing
  _parse_markdown_tree "$start_file" 0 "true" ""
  
  echo ""
  echo "✨ Arbre généré avec succès"

  # Clear visited files tracking
  _notes_visited_files=()
}

# Create aliases for easier access
alias nn="new-note"
alias on="open-oldest-note"
alias gct="git-commit-timestamp"
alias gctw="git-commit-timestamp-watch"
