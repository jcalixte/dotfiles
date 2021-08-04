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
alias lab="cd ~/lab"
alias labcli="cd ~/lab-cli"
alias jc="cd ~/jclab"
alias note="cd ~/jcnote"
alias notes="cd ~/jcnote/notes && code ~/jcnote/notes && gl"
alias podinstall="cd ios && bundle exec pod install && cd .."
alias deployand="bundle exec fastlane android deploy --env=staging"
alias deployios="bundle exec fastlane ios deploy --env=staging"
alias emulatepixel="~/Library/Android/sdk/emulator/emulator -avd Pixel_3_XL_API_29"
alias emulatenexus="~/Library/Android/sdk/emulator/emulator -avd Nexus_5_API_28"
alias resetiphone="sudo killall -9 com.apple.CoreSimulator.CoreSimulatorService"
alias tct="tiny-care-terminal"
alias liveandroid="scrcpy"
alias sshpi="ssh pi@192.168.1.36"
alias ide="tmux split-window -h -p 30 && tmux split-window -v -p 66"
alias chdot="code ~/.dotfiles"

# yarn commands
alias ys="yarn serve"

# side project aliases
alias bp="cd ~/jclab/bons-programmeurs"
alias jcln="cd ~/jclab/lite-note"

# Dotnet Core aliases
alias efdbreset="rm -rf Migrations && dotnet ef database drop --force && dotnet ef migrations add Initial && dotnet ef database update"

# BAM Project aliases
alias col-mob="cd ~/lab/chantier360/apps/front/mobile"
alias col-scripts="cd ~/lab/chantier360/apps/scripts"
alias col-ser="cd ~/lab/chantier360/apps/server"
alias col-doc="cd ~/lab/chantier360/apps/docs"

# Weather
alias wtr='curl "wttr.in/Paris?lang=fr"'
