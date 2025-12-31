export FNM_DIR="/Users/julien/.fnm"
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# Added by Antigravity
export PATH="/Users/julien/.antigravity/antigravity/bin:$PATH"

export EDITOR="code"

# Homebrew
if command -v /opt/homebrew/bin/brew > /dev/null 2>&1;
  then eval "$(/opt/homebrew/bin/brew shellenv)";
fi

# Aliases
alias chgho="nvim ~/.config/ghostty/config"

# From https://raw.githubusercontent.com/dreamsofautonomy/zen-omp/main/zen.toml
eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/zen.toml)"

# Initialize zsh completions (added by deno install script)
autoload -Uz compinit
compinit
. "/Users/julien/.deno/env"

# fnm
export PATH="$HOME/.fnm:$PATH"
eval "`fnm env --use-on-cd --corepack-enabled --version-file-strategy=recursive`"

# Images
splitimg() {
  # Default values
  input=""
  splits=2
  do_print=false
  do_preview=false

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      *.png|*.jpg|*.jpeg)
        input="$1"
        shift
        ;;
      --opti)
        do_optimisation=true
        shift
        ;;
      --split)
        splits="$2"
        shift 2
        ;;
      --print)
        do_print=true
        shift
        ;;
      --preview)
        do_preview=true
        shift
        ;;
      *)
        echo "Unknown option: $1"
        echo "Usage: splitimg <image.png> [--split N] [--print] [--preview]"
        return 1
        ;;
    esac
  done

  if [ -z "$input" ]; then
    echo "No input image provided."
    echo "Usage: splitimg <image.png> [--split N] [--print] [--preview]"
    return 1
  fi

  # Preview if requested
  if [ "$do_optimisation" = true ]; then
    optipng $input
  fi

  crop_width="$((100 / splits))"
  base="${input%.*}"
  output_pattern="${base}_split_%d.png"

  # Split using `magick`
  magick "$input" -crop "${crop_width}%x100%" +repage "$output_pattern"

  # Preview if requested
  if [ "$do_preview" = true ]; then
    open "${base}_split_"*.png
  fi

  # Print if requested then delete split files
  if [ "$do_print" = true ]; then
    echo "Merge splitted prints in a pdf and send to printer..."
    img2pdf \
      --pagesize A3 \
      --fit shrink \
      --border 0 \
      "${base}_split_"*.png \
    | lp -o media=A3 -o fit-to-page -o position=center -o sides=one-sided - && \
      rm "${base}_split_"*.png
  fi
}

alias printa3="lp -o media=A3 -o fit-to-page -o position=center -o sides=one-sided"
alias printa4="lp -o media=A4 -o fit-to-page -o position=center -o sides=one-sided"

# Suffix alias
alias -s html=open