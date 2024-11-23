# fnm
export FNM_DIR="/home/julien/.fnm"
FNM_PATH="/home/julien/.fnm"
if [ -d "$FNM_PATH" ]; then
  export PATH="/home/julien/.fnm:$PATH"
  eval "`fnm env --use-on-cd --corepack-enabled`"
fi
