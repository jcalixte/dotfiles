# If you come from bash you might have to change your $PATH.
export PATH="$HOME/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
export PATH="$HOME/.jenv/shims:$PATH"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home/"

# Homebrew
if command -v /opt/homebrew/bin/brew > /dev/null 2>&1;
  then eval "$(/opt/homebrew/bin/brew shellenv)";
fi

# fnm
export PATH="$HOME/.fnm:$PATH"
eval "`fnm env --use-on-cd`"
export FNM_DIR="/home/julien/.fnm" # need to be absolute, fix to have the same on Linux and MacOS

# ruby

if [ -x "$(command -v rbenv)" ]; then
  eval "$(rbenv init - zsh)"
fi

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="nanotech"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "cloud" "avit" "wezm" "amuse" "candy" "dogenpunk" "lambda" "nanotech" )

#enable color output
export CLICOLOR=1
export LSCOLORS=gx

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS=true

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
# plugins=(git git-flow tmux zsh-autosuggestions copyfile docker encode64 extract yarn-autocompletions fzf-yarn)
plugins=(
  git
  encode64
  extract
  zsh-autosuggestions
)

source $ZSH/oh-my-zsh.sh
# autoload -U promptinit; promptinit
# prompt pure

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"
export ANDROID_HOME=~/Library/Android/sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

source ~/.dotfiles/zsh/private.zsh

export FZF_COMPLETION_TRIGGER=','

source ~/.dotfiles/zsh/alias.zsh
source ~/.dotfiles/zsh/zprofile

# eval "$(starship init zsh)"

# tabtab source for yarn package
# uninstall by removing these lines or running `tabtab uninstall yarn`
# [[ -f /home/julien/.fnm/node-versions/v12.18.0/installation/lib/node_modules/yarn-completions/node_modules/tabtab/.completions/yarn.zsh ]] && . /home/julien/.fnm/node-versions/v12.18.0/installation/lib/node_modules/yarn-completions/node_modules/tabtab/.completions/yarn.zsh

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

export PNPM_HOME=~/pnpm
export PATH="$PNPM_HOME:$PATH"

# Add RVM to PATH for scripting. Make sure this is the last PATH variable change.
export PATH="$PATH:$HOME/.rvm/bin"

# tabtab source for packages
# uninstall by removing these lines
[[ -f ~/.config/tabtab/zsh/__tabtab.zsh ]] && . ~/.config/tabtab/zsh/__tabtab.zsh || true

if [[ -f "~/.docker/init-zsh.sh" ]]; then
  source ~/.docker/init-zsh.sh || true # Added by Docker Desktop
fi

if [[ -s " /opt/homebrew/opt/chruby/share/chruby/chruby.sh" ]]; then
  source /opt/homebrew/opt/chruby/share/chruby/chruby.sh
  source /opt/homebrew/opt/chruby/share/chruby/auto.sh
  chruby ruby-3.2.2
fi

# bun completions
[ -s "~/.bun/_bun" ] && source "~/.bun/_bun"
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# flashlight
export PATH="~/.flashlight/bin:$PATH"

# Zoxide
eval "$(zoxide init zsh)"

# Maestro
export PATH=$PATH:$HOME/.maestro/bin
