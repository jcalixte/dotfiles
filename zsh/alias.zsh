alias c='code .'
alias v='vim .'
alias lsc='ls -lah | lolcat'
alias gbr="git branch --merged | grep -v "master" | xargs git branch -D"
alias chzsh="$EDITOR ~/.zshrc"
alias srczsh="source ~/.zshrc"
alias ide="tmux"
alias vim="nvim"

alias signal='gurk'

# git
alias lz="lazygit"
alias gcz="git cz"
alias gpf='git push --force-with-lease=$(git symbolic-ref --short HEAD):$(git rev-parse @{u})'
alias gcaf="gaa && git commit --amend --no-edit && gpf"
alias gpuo='git push --set-upstream origin $(git branch --show-current)'
alias gitfiles='git log --pretty=format: --name-only --since="7 days ago" | sort | uniq'
alias gw="watch -n 300 \"git pull && (git ls-files --modified --others --exclude-standard | grep . > /dev/null) && { git add . ; git commit -m 'autocommit' ; git push; }\""
alias gcgh='function _clone_github() {
    repo_url="https://github.com/$1.git"
    folder_name="${2:-$(basename "$1")}"
    git clone "$repo_url" "$folder_name" && cd "$folder_name"
}; _clone_github'

# folder shortcuts
alias lab="cd ~/lab"
alias labcli="cd ~/lab-cli"
alias jc="cd ~/jclab"
alias n="nvim ."
alias chdot="~/.dotfiles && gl & $EDITOR . &"

# Utils
alias podinstall="cd ios && bundle exec pod install && cd .."
alias tct="tiny-care-terminal"
alias sshpi="ssh pi@192.168.1.36"

# pnpm commands
alias p='pnpm'
alias pi='p i'
alias pc='p commit'
alias pu='p uninstall'
alias px="pnpx"

# Markdown
alias mdz="px mdzilla"

# yarn commands
alias y='yarn'

# Weather
alias wtr='curl "wttr.in/Paris?lang=fr"'

# Python
alias python=python3

# Kanata
alias resetkanata='sudo launchctl stop org.pqrs.service.daemon.Karabiner-Core-Service && sudo launchctl kickstart -k system/com.kanata'
alias rk=resetkanata

searchgit() {
  STRING_TO_SEARCH=$1
  shift;

  git log -S"$STRING_TO_SEARCH" --color=always \
      --format="%C(auto)%h%d %s %C(black)%C(bold)%cr" "$@" |
  fzf --ansi --reverse --tiebreak=index \
      --bind "ctrl-m:execute:
                (grep -o '[a-f0-9]\{7\}' | head -1 |
                xargs -I % sh -c 'git show --color=always % | less -R') << 'FZF-EOF'
                {}
                FZF-EOF
              "
}

alias sgit=searchgit

# Suffix alias
alias -s json=jless
alias -s md=bat
alias -s txt=bat
alias -s log=bat
alias -s css='$EDITOR'
alias -s vue='$EDITOR'
alias -s js='$EDITOR'
alias -s ts='$EDITOR'

function killport {
	echo '🚨 Killing all processes at port' $1
	lsof -ti tcp:$1 | xargs kill
}
