#!/usr/bin/env bash
# Claude Code statusLine command — mirrors the nanotech Oh My Zsh theme
# PROMPT='%F{green}%2c%F{blue} [%f '
# RPROMPT='$(git_prompt_info) %F{blue}] %F{green}%D{%L:%M} %F{yellow}%D{%p}%f'

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')

# Replicate %2c: last 2 path components
short_path=$(echo "$cwd" | awk -F'/' '{
  n = NF
  if (n >= 2) print $(n-1) "/" $n
  else print $n
}')

# Git branch + dirty flag (skip optional locks)
git_branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    dirty=""
    if ! git -C "$cwd" diff --quiet 2>/dev/null || ! git -C "$cwd" diff --cached --quiet 2>/dev/null; then
      dirty=" *"
    fi
    git_branch="${branch}${dirty}"
  fi
fi

# Time: hour:minute am/pm  (mirrors %D{%L:%M} %D{%p})
time_hm=$(date +"%l:%M" | tr -d ' ')
time_ampm=$(date +"%p" | tr '[:upper:]' '[:lower:]')

# Token usage percentage
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# --- Build left section (plain text, no ANSI, for width measurement) ---
if [ -n "$git_branch" ]; then
  left_plain="${short_path} [ ${git_branch} ] ${time_hm} ${time_ampm}"
else
  left_plain="${short_path} [  ] ${time_hm} ${time_ampm}"
fi

# --- Build left section with ANSI colors ---
# green=32, blue=34, yellow=33, reset=0
if [ -n "$git_branch" ]; then
  left_colored=$(printf '\033[32m%s\033[34m [\033[0m \033[33m%s\033[34m ]\033[0m \033[32m%s \033[33m%s\033[0m' \
    "$short_path" "$git_branch" "$time_hm" "$time_ampm")
else
  left_colored=$(printf '\033[32m%s\033[34m [ ]\033[0m \033[32m%s \033[33m%s\033[0m' \
    "$short_path" "$time_hm" "$time_ampm")
fi

# --- Build right section: progress bar + percentage ---
if [ -n "$used_pct" ]; then
  bar_width=10
  # Round to nearest integer
  pct_int=$(printf '%.0f' "$used_pct")
  filled=$(( pct_int * bar_width / 100 ))
  empty=$(( bar_width - filled ))

  # Color: green <= 60%, yellow <= 85%, red > 85%
  if [ "$pct_int" -le 60 ]; then
    bar_color='\033[32m'   # green
  elif [ "$pct_int" -le 85 ]; then
    bar_color='\033[33m'   # yellow
  else
    bar_color='\033[31m'   # red
  fi

  bar_filled=$(printf "%${filled}s" | tr ' ' '█')
  bar_empty=$(printf "%${empty}s"  | tr ' ' '░')

  right_plain=" ${pct_int}% [${bar_filled}${bar_empty}]"
  right_colored=$(printf ' \033[35m%s%%\033[0m \033[34m[\033[0m%s%s\033[34m]\033[0m' \
    "$pct_int" \
    "$(printf "${bar_color}%s\033[0m" "$bar_filled")" \
    "$(printf '\033[2m%s\033[0m' "$bar_empty")")
else
  right_plain=""
  right_colored=""
fi

# --- Right-align: pad between left and right sections ---
# Claude Code runs this with stdout piped and no controlling tty, so COLUMNS is
# unset and `tput cols` always reports 80. Read the pane size off the parent
# claude process's tty so the bar tracks splits and resizes.
term_width="${COLUMNS:-}"
if [ -z "$term_width" ]; then
  ancestor=$PPID
  for _ in 1 2 3; do
    [ -z "$ancestor" ] || [ "$ancestor" = "0" ] || [ "$ancestor" = "1" ] && break
    tty_name=$(ps -o tty= -p "$ancestor" 2>/dev/null | tr -d ' ')
    if [ -n "$tty_name" ] && [ "$tty_name" != "??" ]; then
      term_width=$(stty -f "/dev/$tty_name" size 2>/dev/null | awk '{print $2}')
      break
    fi
    ancestor=$(ps -o ppid= -p "$ancestor" 2>/dev/null | tr -d ' ')
  done
fi
case "$term_width" in ''|*[!0-9]*) term_width=80 ;; esac
left_len=${#left_plain}
right_len=${#right_plain}
pad=$(( term_width - left_len - right_len ))
[ "$pad" -lt 1 ] && pad=1
padding=$(printf "%${pad}s" "")

printf '%s%s%s' "$left_colored" "$padding" "$right_colored"
