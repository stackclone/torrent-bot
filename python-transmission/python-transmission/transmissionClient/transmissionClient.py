#!/usr/bin/env python

##  need more specifications on rpc protocol implemented by transmission-daemon?
##  consider reading http://trac.transmissionbt.com/browser/trunk/doc/rpc-spec.txt
##

__author__    = "lesion (lesion@autistici.org)"
__version__   = "$Revision: 0.1 $"
__date__      = "$Date: 2008/09/10 $"
__license__   = "GPL2"

"""
transmissionClient.py
"""

from simplejson import dumps, loads
from urllib import urlopen
import sys


class TransmissionClientFailure(Exception): pass

class TransmissionClient(object):
  
  rpcUrl = None

  def __init__( self, rpcUrl='http://localhost:9091/transmission/rpc' ):
    """ try to do a stupid call to transmission via rpc """

    try:
      self.rpcUrl = rpcUrl
      #[Nathan Stehr March 7, 2009] comment this out, in transmission 1.5 connecting to the base rpc url just hangs
      #urlopen( rpcUrl ).read()

    except Exception, e:
      raise TransmissionClientFailure, \
            "Make sure your transmission-daemon is running  %s" % e



  def _rpc( self, method, params=[] ):
    """ generic rpc call to transmission """

    postdata = dumps({ 'method': method, 
                       'arguments': params, 
                       'id': 'jsonrpc'})

    try:
      response = loads( urlopen( self.rpcUrl , postdata).read() )
    except Exception, e:
      raise TransmissionClientFailure, \
            "Make sure your transmission-daemon is running  %s" % e

    return response



  def sessionStats( self ):
    return self._rpc( 'session-stats' )


  def torrentGet( self, torrentIds='', fields=[ 'id', 'name']):
    return self._rpc( 'torrent-get', { 'ids': torrentIds, 'fields': fields } ) 

  def torrentAdd( self, torrentFile, downloadDir='.' ):
    return self._rpc( 'torrent-add', { 'filename': torrentFile, 
                                      'download-dir': downloadDir } )


  def torrentRemove( self, torrents=None ):
    return self._rpc( 'torrent-remove', { 'ids': torrents } )


  def sessionSet( self, key, value ):
    return self._rpc( 'session-set', { key: value } )

  
  def sessionGet( self ):
    return self._rpc( 'session-get' )




