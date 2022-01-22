set nocompatible              " be iMproved, required
filetype off                  " required

source ~/.dotfiles/vim/plugin.vimrc

set runtimepath^=~/.vim/bundle/ctrlp.vim
packloadall
syntax on
colorscheme lucius
LuciusBlack
set tabstop=2 shiftwidth=2 expandtab
set backspace=indent,eol,start
set number relativenumber

source ~/.dotfiles/vim/map.vimrc

let g:ctrlp_custom_ignore = 'node_modules\|DS_Store\|git'

