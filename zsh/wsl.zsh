# Add deno completions to search path
if [[ ":$FPATH:" != *":/home/julien/.zsh/completions:"* ]]; then export FPATH="/home/julien/.zsh/completions:$FPATH"; fi

# fnm
export FNM_DIR="/home/julien/.fnm"
FNM_PATH="/home/julien/.fnm"
if [ -d "$FNM_PATH" ]; then
  export PATH="/home/julien/.fnm:$PATH"
  eval "`fnm env --use-on-cd --corepack-enabled --version-file-strategy=recursive`"
fi

export EDITOR="code"

# Erlang
export PATH=/home/julien/.cache/rebar3/bin:$PATH