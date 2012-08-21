#! /usr/bin/env python
#
# Example program using ircbot.py.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
          after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import os
import time
import subprocess
import re
channel = "#greyh@t"
nickname = "breakme"
#channel = "#Helpdesk"

class TestBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname, reconnection_interval=5)
        self.channel = channel


    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        a = e.arguments()[0].split(":", 1)
        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.do_command_pub(e, a[1].strip())
	return

    def on_dccmsg(self, c, e):
        c.privmsg("You said: " + e.arguments()[0])

    def on_dccchat(self, c, e):
        if len(e.arguments()) != 2:
            return
	args = e.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
	        port = int(args[3])
    	    except ValueError:
	        return
            self.dcc_connect(address, port)
    def do_command_pub(self, e, cmd):
        global channel
        nick = nm_to_n(e.source())
        c = self.connection
        time.sleep(1)
        c.privmsg(channel, nick+": I will only respond to commands in private")

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection
        global channel
    
        #if cmd == "disconnect":
        #    self.disconnect("But, I was so helpful...")
        #elif cmd == "restart":
        #   self.die()
        if cmd == "stats":
            for chname, chobj in self.channels.items():
                c.privmsg(nick, "--- Channel statistics ---")
                c.privmsg(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                c.privmsg(nick, "Users: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                c.privmsg(nick, "Opers: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                c.privmsg(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "hi" or cmd == "hello" or cmd == "hey":
	        time.sleep(1)
	        c.privmsg(nick, ": Hello")
        elif cmd == "ping":
            time.sleep(1)
            c.privmsg(nick, "pong")
        elif cmd == "pong":
            time.sleep(1)
            c.privmsg(nick, "ping")
        elif cmd == "add":
            time.sleep(1)
            c.privmsg(nick, "--- Creating system user "+nick+" ---")
            time.sleep(2)
            os.system('sudo /usr/sbin/useradd -mk /etc/skel_empty -g users -s /bin/bash $(echo '+nick+'|tr \'[A-Z]\' \'[a-z]\')')
            c.privmsg(nick, "--- Setting password to \"Password\" ---")
            time.sleep(2)
            os.system('sudo /usr/local/bin/resetpasswd $(echo '+nick+'|tr \'[A-Z]\' \'[a-z]\')')
            print ("USER CREATED FOR "+nick)
            c.privmsg(nick, "--- Copying files ---")
            c.privmsg(nick, "This may take some time, please be patient...")
    	    os.system('/usr/local/bin/chrootsetup $(echo '+nick+'|tr \'[A-Z]\' \'[a-z\')')
    	    print ("CREATED USER CHROOT ENV")
            c.privmsg(nick, "--- Finished creating system user ---")
            c.privmsg(nick, "--- Please change your password as soon as possible ---")
        elif cmd == "help":
            c.privmsg(nick, 'Why should I help you?')
    	    c.privmsg(nick, 'I know how to respond to many commands, but I will only tell you a couple to get you started')
    	    c.privmsg(nick, 'There is only one way to give me a command. type "/msg '+nickname+' command" or give me the command directly in the irc private message window')
    	    c.privmsg(nick, 'Here are some of the more useful commands: help, ping, disconnect')
    	    c.privmsg(nick, 'These may not be all of my commands, however, because this help prompt is not always updated after changes are made to my source code. Please notify the developer if you find any such commands.')
# Prevent subshells and text editors (will hang script)
        elif re.search(r'\bbash\b', cmd) or re.search(r'\bpico\b', cmd) or re.search(r'\btelnet\b', cmd) or re.search(r'\bssh\b', cmd) or re.search(r'\byes\b', cmd) or re.search(r'\bno\b', cmd) or re.search(r'\bex\b', cmd) or re.search(r'\bvi\b', cmd) or re.search(r'\bed\b', cmd) or re.search(r'\bsh\b', cmd) or re.search(r'\bcsh\b', cmd) or re.search(r'\bksh\b', cmd) or re.search(r'\bzsh\b', cmd) or re.search(r'\bvim\b', cmd) or re.search(r'\bemacs\b', cmd) or re.search(r'\bnano\b', cmd) or re.search(r'\bpython\b', cmd) or re.search(r'\bperl\b', cmd) or re.search(r'\bruby\b', cmd) or re.search(r'\beval\b', cmd):
            time.sleep(1)
            c.privmsg(nick, 'I\'m afraid that I can\'t allow you to use '+cmd+'. You will prevent me from accepting any more commands and I can\'t allow that to happen.')
    	elif re.search(r'\bsudo\b', cmd) or re.search(r'\bkill\b', cmd) or re.search(r'\bpkill\b', cmd) or re.search(r'\bkillall\b', cmd) or re.search(r'^passwd\b', cmd) or re.search(r'\bsu\b', cmd):
            time.sleep(1)
            c.privmsg(nick, "I'm afraid I can't let you do that "+nick)
# Prevent hang on commands expecting input
        elif re.search(r'\bcat\b', cmd) or re.search(r'\bnc\b', cmd) or re.search(r'\bhead\b', cmd) or re.search(r'\btail\b', cmd) or re.search(r'\bread\b', cmd):
            cmd2 = cmd.split()
            if not re.search(r'^'+cmd2[0]+'*\s+\w+', cmd):
                c.privmsg(nick, 'you must provide more than just '+cmd2[0])
            else:
                print nick+': '+cmd
                proc=subprocess.Popen(cmd+'|tr \'\\n\' \' \' 2>&1', shell=True, stdout=subprocess.PIPE, )
                output=proc.communicate()[0]
                if output == "" :
                    c.privmsg(nick, cmd+": Permission denied")
                else:
                    out_length = len(output)
                    #print (out_length) ## Enable for debuging
                    if out_length > 500:
                        c.privmsg(nick, "Error: Request too long")
                    else:
                        c.privmsg(nick, "Unknown command: " + output)
        else:
            print nick+': '+cmd
            proc=subprocess.Popen(cmd+'|tr \'\\n\' \' \' 2>&1', shell=True, stdout=subprocess.PIPE, )
            output=proc.communicate()[0]
            if output == "" or "setfactl" in cmd :
                c.privmsg(nick, cmd+": Permission denied")
            else:
                out_length = len(output)
                #print (out_length) ## Enable for debuging
                if out_length > 500:
                    c.privmsg(nick, "Error: Request too long")
                else:
                     c.privmsg(nick, "Unknown command: " + output)
    
def main():
    import sys
    server = "irc.freenode.net"
    #server = "192.168.56.102"
    port = 6667
    global channel
    global nickname
    bot = TestBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
