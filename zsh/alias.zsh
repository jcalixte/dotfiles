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
alias gitfiles='git log --pretty=format: --name-only --since="7 days ago" | sort | uniq'
alias lab="cd ~/lab"
alias labcli="cd ~/lab-cli"
alias jc="cd ~/jclab"
alias n="cd ~/jcnote/notes && code ~/jcnote/notes && gl"
alias podinstall="cd ios && bundle exec pod install && cd .."
alias resetiphone="sudo killall -9 com.apple.CoreSimulator.CoreSimulatorService"
alias tct="tiny-care-terminal"
alias sshpi="ssh pi@192.168.1.36"
alias chdot="~/.dotfiles && gl && code ."

# Vaquant
alias va="cd ~/jclab/vaquant"

# pnpm commands
alias p='pnpm'
alias pi='p i'

# side project aliases
alias jcln="cd ~/jclab/lite-note"
alias jcl="cd ~/jclab/loopycode"
alias jcb="cd ~/jclab/blog"

# BAM Project aliases
alias col="cd ~/lab/colas360"

# Weather
alias wtr='curl "wttr.in/Paris?lang=fr"'

# Python
alias python=python3
