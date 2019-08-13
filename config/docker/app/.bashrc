# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

if [ -f ~/app/code/bin/activate ]; then
    source ~/app/code/bin/activate
fi

alias runner="/home/bitmex/api/console/runner"
