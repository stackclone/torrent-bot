

__author__    = "Nathan Stehr (nstehr@gmail.com)"
__version__   = "$Revision: 1.0 $"
__date__      = "$Date: 2009/03/23 $"
__license__   = "GPL2"


#Torrent bot is a jython script that connects to the transmission (http://www.transmissionbt.com/) bit torrent client via RPC and lets users communicate with their transmission client via commands sent over the MSN network

#Makes use of:
# the simplejson(http://code.google.com/p/simplejson/)
# slightly modified version of: transmission client (http://lesion.noblogs.org/post/2008/09/12/python-binding-to-transmission-1.33-bittorrent-client-jsonrpc)
# java messenger library (http://jml.blathersource.org/)

import sys
from time import sleep
import os
#setup the path, i.e add the 3rd party stuff I need
current_path= os.getcwd()
sys.path.append(os.path.join(current_path,'simplejson-1.9.2/simplejson'))
sys.path.append(os.path.join(current_path,'python-transmission/python-transmission'))
sys.path.append(os.path.join(current_path,'jml-1.0b3-full.jar'))

from transmissionClient import TransmissionClient
from net.sf.jml import MsnMessenger
from net.sf.jml import MsnUserStatus
from net.sf.jml.impl import MsnMessengerFactory
from net.sf.jml import MsnSwitchboard
from net.sf.jml.event import MsnAdapter
from net.sf.jml.message import MsnControlMessage
from net.sf.jml.message import MsnDatacastMessage
from net.sf.jml.message import MsnInstantMessage
import urllib
from net.sf.jml import MsnFileTransfer
import bot_config

class MSNEventHandler(MsnAdapter):
    #overridden call back functions
    def instantMessageReceived(self, switchboard,message,contact):
        receivedText = message.getContent()
        #set the switchboard, so that we can send messages
        self.switchboard = switchboard
        
        #defines how we should handle the commands received from the other end
        self.handleInput(receivedText)
    
    #Apparently file transfer isn't working in the jml library....
    #file transfer is handled instead by passing the url in a message and then downloading in the bot code

    #def fileTransferRequestReceived(self,transfer):
    #    print "Transfer request received..."
    #    filename = transfer.getFile().getName()
    #    file = File('/Users/nate/dls'+filename)
    #    transfer.setFile(file)
    #    transfer.start()
        
    #def fileTransferFinished(self,transfer):
    #    print "File transfer done!!!"
        
    def loginCompleted(self,messenger):
        messenger.getOwner().setDisplayName(bot_config.screenname)
 

    #non overridden functions
    def sendMessage(self,message):
        self.switchboard.sendMessage(message)

    def handleInput(self,receivedMsg):
        
        client = TransmissionClient()
        command = receivedMsg.lower()
        output = ""
        if command == 'overview':
            results = client.sessionStats()
            arguments = results['arguments']
            sessionStats = arguments['session-stats']
            
            uploadSpeed = sessionStats['uploadSpeed']
            uploadSpeed = float(uploadSpeed)/1000
            uploadSpeed = str(uploadSpeed) + " kb/s"
            
            downloadSpeed = sessionStats['downloadSpeed']
            downloadSpeed = float(downloadSpeed)/1000
            downloadSpeed = str(downloadSpeed) + " kb/s"
            
            activeTorrents = str(sessionStats['activeTorrentCount'])
            pausedTorrents = str(sessionStats['pausedTorrentCount'])
            
            totalTorrents = str(sessionStats['torrentCount'])
        
            output = "Download Speed: "+downloadSpeed+"\n"
            output = output + "Upload Speed: "+uploadSpeed+"\n"
            output = output + "Number of Active Torrents: " + activeTorrents+"\n"
            output = output + "Number of Paused Torrents: " + pausedTorrents+"\n"
            output = output + "Total Number of Torrents: " + totalTorrents
            
        if command == 'all torrents':
            torrents = self.getTorrentList(client)
            if len(torrents) == 0:
                output = "No torrents in the system"
            for torrent in torrents:
                output = output+self.calculateTorrentMsg(torrent)
                
                
        if command.startswith("get torrent"):
            torrentName = command.split(":")[1].lower()
            torrents = self.getTorrentList(client)
            for torrent in torrents:
                name = torrent['name']
                if name.lower() == torrentName:
                    output = self.calculateTorrentMsg(torrent)
                    break
            if output == "":
               output = "Torrent not found"
               
        if command.startswith("download torrent"):
            command=command.replace(':','#',1)
            url = command.split("#")[1]
            filename = self.saveFile(url)
            results = client.torrentAdd(filename)
            success = results['result']
            output = "Addition of torrent was a "+success

        if command.startswith("delete torrent"):
            torrentName = command.split(":")[1].lower()
            torrents = self.getTorrentList(client)
            id = -1
            for torrent in torrents:
                name = torrent['name']
                if name.lower() == torrentName:
                    id = torrent['id']
                    break
            if id == -1:
                output = "Torrent not found"
            else:
                results = client.torrentRemove(id)
                success = results['result']
                output = "Deletion of torrent was a "+success

        if command.startswith("help"):
            output = "Commands \n"
            output = output+"overview --> Overview of torrent client current state \n"
            output = output+"all torrents --> Info on all torrents currently being downloaded or seeded \n"
            output = output+"get torrent:<torrent name> --> Info on the specified torrent \n"
            output = output+"download torrent:<url of torrent file> --> Downloads the specified torrent file and starts downloading it \n"
            output = output+"delete torrent:<torrent name> --> Removes the torrent, but does not delete the data \n"
                       
        #send the msg to the buddy        
        msnMessage = MsnInstantMessage()
        msnMessage.setContent(output)
        self.sendMessage(msnMessage)
                
    def getTorrentList(self,client):
        results  = client.torrentGet(fields=['name','id','totalSize','downloadedEver','rateDownload','rateUpload','files'])
        torrents = results['arguments']['torrents']
        return torrents

    def calculateTorrentMsg(self,torrent):
        name = torrent['name']
        totalSize = float(torrent['totalSize'])/1048576
        totalSize = round(totalSize,3)
        #downloaded = float(torrent['downloadedEver'])/1048576
        #downloaded = round(downloaded,3)
        #going to calculate current downloaded amount based on the files array.  The above method seems to be off when
        #the client has been stopped and restarted
        files = torrent['files']
        
        sum = 0
        for file in files:
            sum = sum+file['bytesCompleted']
        downloaded = float(sum) / 1048576
        downloaded = round(downloaded,3)
        downloadRate = float(torrent['rateDownload'])/1000
        downloadRate = round(downloadRate,3)
        uploadRate = float(torrent['rateUpload'])/1000
        uploadRate = round(uploadRate,3)
        percent = (downloaded/totalSize)*100
        percent = round(percent,3)
              

        torrentMsg = "Name: "+name+"\n"
        torrentMsg = torrentMsg + "Total Size: "+str(totalSize)+" MB \n"
        torrentMsg = torrentMsg + "Downloaded So Far: "+str(downloaded) +" MB \n"
        torrentMsg = torrentMsg + "Percent Completed: "+ str(percent)+" %\n"
        torrentMsg = torrentMsg + "Download Rate: " + str(downloadRate) + " kb/s \n"
        torrentMsg = torrentMsg + "Upload Rate: " + str(uploadRate) + " kb/s \n"
             

        remaining = totalSize-downloaded
        remaining = remaining * 1024 
        if remaining > 0:
            if downloadRate > 0:
                #time in seconds
                time = remaining/downloadRate
                time = uptime(time)
                torrentMsg = torrentMsg +"Time Remaining "+ time +"\n"
            else:
                torrentMsg = torrentMsg +"Time Remaining ? \n"
        else:
            torrentMsg = torrentMsg +"Download complete \n"
        output = torrentMsg+"-----\n"
        return output
    
    def saveFile(self,link):
        webFile = urllib.urlopen(link)
        localFile = open(link.split('/')[-1], 'wb')
        localFile.write(webFile.read())
        webFile.close()
        localFile.close()
        path = os.getcwd()+os.sep+localFile.name
        return path
    
        
class MSNMessenger:
    def initMessenger(self,messenger):
        print "Initializing...."
        listener = MSNEventHandler()
        messenger.addMessageListener(listener)
        messenger.addFileTransferListener(listener)
        messenger.addMessengerListener(listener)

    def connect(self,email,password):
        messenger = MsnMessengerFactory.createMsnMessenger(email,password)
        messenger.getOwner().setInitStatus(MsnUserStatus.ONLINE)
        self.initMessenger(messenger)
        messenger.login()
        
        
        
def start():
    messenger = MSNMessenger()
    messenger.connect(bot_config.username,bot_config.password)
    print "Connected"    
#uptime function from: http://thesmithfam.org/blog/2005/11/19/python-uptime-script/
def uptime(total_seconds):
     # Helper vars:
     MINUTE  = 60
     HOUR    = MINUTE * 60
     DAY     = HOUR * 24
     # Get the days, hours, etc:
     days    = int( total_seconds / DAY )
     hours   = int( ( total_seconds % DAY ) / HOUR )
     minutes = int( ( total_seconds % HOUR ) / MINUTE )
     seconds = int( total_seconds % MINUTE )
     # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
     string = ""
     if days> 0:
         string += str(days) + " " + (days == 1 and "day" or "days" ) + ", "
     if len(string)> 0 or hours> 0:
         string += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "
     if len(string)> 0 or minutes> 0:
         string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ", "
     string += str(seconds) + " " + (seconds == 1 and "second" or "seconds" )
     return string;


def main():
    start()
    while 1:
        sleep(10)


if __name__ == "__main__":
    main()
