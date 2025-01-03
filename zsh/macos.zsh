export FNM_DIR="/Users/julien/.fnm"

# Homebrew
if command -v /opt/homebrew/bin/brew > /dev/null 2>&1;
  then eval "$(/opt/homebrew/bin/brew shellenv)";
fi

# Aliases
alias chgho="nvim ~/.config/ghostty/config"

# source /Users/julien/.kepler/kntools/environment-setup-sdk.sh
# source /Users/julien/.kepler/kntools/sdk/0.10.4/environment-setup-sdk.sh

# From https://raw.githubusercontent.com/dreamsofautonomy/zen-omp/main/zen.toml
eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/zen.toml)"

# Initialize zsh completions (added by deno install script)
autoload -Uz compinit
compinit
. "/Users/julien/.deno/env"

# fnm
export PATH="$HOME/.fnm:$PATH"
eval "`fnm env --use-on-cd --corepack-enabled`"
