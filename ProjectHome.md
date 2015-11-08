Torrent bot is an MSN bot written in jython that allows you to remotely manage your torrents via commands sent to the bot.  Torrent bot connects to a locally running transmission (http://www.transmissionbt.com/) daemon client and communicates with it over its JSON-RPC API.

Currently tested against Transmission 1.75 on OSX and 1.75 on Ubuntu 9.04.

See the wiki for a more detailed overview of the project as well as detailed usage guide.

I have also created a google group for this project, so feel free to use it to discuss anything related to torrent-bot.

# News #
**September 19, 2009**:  I've had a couple of reports that torrent-bot isn't working against the newer version of transmission. I'm running transmission 1.75, built from source, on my Ubuntu 9.04 machine and I'm able to issue all the commands and get the appropriate responses in return from torrent-bot.  I'm using sun java, version 1.5, and running the transmission-daemon executable.  I have also tested torrent-bot against transmission 1.75 on OSX and it is working successfully as well.
If you are having issues there are a couple things I can suggest.  One check the version of java you are using.  Like I mentioned above, I'm using sun java 1.5.  Two, check your settings.json file.  This is found under ~/.config/transmission.  Make sure the following properties are set like this:


**"rpc-authentication-required": 0,
> "rpc-enabled": 1,
> "rpc-password": "",
> "rpc-port": 9091,
> "rpc-username": "",
> "rpc-whitelist": "127.0.0.1",
> "rpc-whitelist-enabled": 0,**



The one thing that you change to be different here is rpc-whitelist-enabled.  If you set it to 1, make sure the relevant IPs are in the rpc-whitelist.

Again, if you are still running into problems, add to the existing bug entry, or post on the mailing list.


**July 28, 2009**: A couple of people have contacted me mentioning that they can't get torrent-bot to work.  It seems to be a problem with the communication between torrent-bot and transmission.  I'm looking at it right now, and am trying to reproduce the problem.  If anyone else runs into any issues, let me know via a bug report or post on the mailing list.

**June 4, 2009**:  I have checked in a fix to svn and uploaded a new zip of the project.  In case anyone was wondering, the issue was that the newer Transmission builds were requiring a session id in the header of the RPC request, so I now add this header and torrent-bot works again.

**May 23, 2009**:  Hello Everyone.  I have gotten a report from a user, and tested it myself, it doesn't appear torrent-bot is working with versions greater than 1.5.  I believe its a problem with either the JSON encoding of the requests, or something deeper in the 3rd party transmission library I am using.  I am digging into the problem now and will post a new version as soon as possible.

**March 26, 2009**: Version 1.0.1 Torrent Bot now automatically accepts all incoming friend requests.  This means you don't have to login as your bot account and add yourself.