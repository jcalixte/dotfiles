# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
alias c='code .'
alias v='vim .'
alias lsc='ls -lah | lolcat'
alias gbr="git branch --merged | grep -v "master" | xargs git branch -D"
alias chzsh="code ~/.zshrc"
alias srczsh="source ~/.zshrc"
alias gcz="git cz"
alias gcaf="git commit --amend --no-edit && gpf"
alias gpuo='git push --set-upstream origin $(git branch --show-current)'
alias lab="cd ~/lab"
alias labcli="cd ~/lab-cli"
alias jc="cd ~/jclab"
alias note="cd ~/jcnote"
alias notes="cd ~/jcnote/notes && code ~/jcnote/notes && gl"
alias n="notes"
alias podinstall="cd ios && bundle exec pod install && cd .."
alias resetiphone="sudo killall -9 com.apple.CoreSimulator.CoreSimulatorService"
alias tct="tiny-care-terminal"
alias liveandroid="scrcpy"
alias sshpi="ssh pi@192.168.1.36"
alias ide="tmux split-window -h -p 30 && tmux split-window -v -p 66"
alias chdot="~/.dotfiles && gl && code ."

# Vaquant
alias va="cd ~/jclab/vaquant"

# pnpm commands
alias p='pnpm'
alias pi='p i'

# side project aliases
alias jcln="cd ~/jclab/lite-note"

# BAM Project aliases
alias col="cd ~/lab/colas360"
alias amob="cd ~/lab/colas360/apps/atelier360"
alias cmob="cd ~/lab/colas360/apps/chantier360"
alias ser="cd ~/lab/colas360/apps/server"
alias doc="cd ~/lab/colas360/docs"

# Weather
alias wtr='curl "wttr.in/Paris?lang=fr"'

# Python
alias python=python3
