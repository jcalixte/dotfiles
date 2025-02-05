export FNM_DIR="/Users/julien/.fnm"
export JAVA_HOME="/Users/julien/Library/Java/JavaVirtualMachines/corretto-17.0.14/Contents/Home"

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
eval "`fnm env --use-on-cd --corepack-enabled`"
