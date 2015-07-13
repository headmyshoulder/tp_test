#! /usr/bin/python

""" Manage.py """
 
__date__ = "2015-07-13"
__author__ = "Karsten Ahnert"
__email__ = "karsten.ahnert@gmx.de"

import sys
import argparse
import logging
import os
import time

thirdPartyDir = os.path.abspath( os.path.dirname( __file__ ) )
installDir = os.path.join( thirdPartyDir , "Install" )
includeDir = os.path.join( installDir , "include" )

logCmd = False
numOfThreads = 1

class Timer:
    def __init__( self ):
        self.start = time.time()
    def seconds( self ):
        now = time.time()
        return now - self.start
    
class CmdException( Exception ):
    def __init__( self , cmd ):
        self.cmd = cmd
    def __str__( self ):
        return self.cmd

def cmd( str ):
    if logCmd:
        logging.info( str )
    if os.system( str ) != 0:
        raise CmdException( str )
    
   
def listToString( ll ):
    str = ""
    first = True
    for l in ll:
        if first: first = False
        else: str += " "
        str += l
    return str


class BuilderDummy:
    def build( self ):
        pass
    def clean( self ):
        pass


class AmbossBuilder:
    dir = "Amboss"
    def build( self ):
        logging.info( "Copying headers into " + os.path.join( installDir , "include" ) + "." )
        cmd( "cp -rf include/Amboss " + includeDir )
    def clean( self ):
        logging.info( "Nothing to do." )
    
class BoostBuilder:
    dir = "boost"
    def build( self ):
        pass
    def clean( self ):
        pass
    
class ZeroMqBuilder:
    dir = "zeromq"
    def build( self ):
        logging.info( "Configuring zeromq." )
        cmd( './configure --prefix="' + installDir + '"' )
        logging.info( "Building and installing zeromq." )
        cmd( 'make install -j ' + str( numOfThreads ) )
        logging.info( "Copying zmq.hpp to " + includeDir )
        cmd( 'cp include/zmq.hpp ' + includeDir )
    def clean( self ):
        cmd( "git clean -d -f" )


class CppCmsBuilder:
    dir = "cppcms"
    def build( self ):
        pass
    def clean( self ):
        pass
    




builders = {}
builders[ "amboss" ] = AmbossBuilder()
builders[ "boost" ] = BoostBuilder()
builders[ "zeromq" ] = ZeroMqBuilder()
builders[ "cppcms" ] = CppCmsBuilder()

libraryList = builders.keys()


def parseCmd( argv ):
    parser = argparse.ArgumentParser( description = "Application description" )
    parser.add_argument( "-l" , "--logfiles" , help="Logiles" , default="logs/log.log" , type=str )
    parser.add_argument( "--clean" , help="Cleanup" , action='store_true' )
    parser.add_argument( "--distclean" , help="Clean installion" , action='store_true' )
    parser.add_argument( "--logcmd" , help="Log build commands." , action='store_true' )
    parser.add_argument( "-j" , help="Number of threads" , type=int , default=4 )
    parser.add_argument( "libs" , help="Libraries to build. Possible libraries are " + listToString( libraryList ) , nargs='*' )
    args = parser.parse_args( argv[1:] )
    return args

def initLogging( args ):
    formatString = '[%(levelname)s][%(asctime)s] : %(message)s'
    logLevel = logging.INFO
    logging.basicConfig( format=formatString , level=logLevel , datefmt='%Y-%m-%d %I:%M:%S')
    

def main( argv ):
    
    global logCmd
    global numOfThreads
    
    args = parseCmd( argv )
    initLogging( args )
    
    librariesToBuild = libraryList
    if args.libs is not None:
        librariesToBuild = args.libs
    logging.info( "Build libraries " + listToString( librariesToBuild ) )
    
    if args.distclean:
        logging.info( "Cleaning up installation. Removing all files from " + installDir )
        os.system( "rm -rf " + os.path.join( installDir , "*" ) )

    logCmd = args.logcmd
    if logCmd: logging.info( "Logging of all commands is enabled." )
    else: logging.info( "Logging of all commands is disabled." )
    numOfThreads = args.j
    logging.info( "Using " + str( numOfThreads ) + " threads." )
        
    logging.info( "Preparing install directory." )
    os.system( "mkdir -p " + includeDir )
        
    for lib in librariesToBuild:
        if not lib in builders:
            logging.error( lib + " is not in registered." )
            continue
        builder = builders[ lib ]
        os.chdir( os.path.join( thirdPartyDir , builder.dir ) )
        timer = Timer()
        if not args.clean:
            logging.info( "Starting build of " + lib + "." )
            try:
                builder.build()
            except CmdException as e:
                logging.error( "Error while building " + lib + ". The command was \n" + e.cmd + "\nThe current directory was \n" + os.getcwd() )
            logging.info( "Finished build in " + str( timer.seconds() ) + " seconds." )    
        else:
            logging.info( "Starting clean up of " + lib + "." )
            try:
                builder.clean()
            except CmdException as e:
                logging.error( "Error while cleaning " + lib + ". The command was \n " + e.cmd + "\nThe current directory was \n" + os.getcwd()  )
            logging.info( "Finished clean up in " + str( timer.seconds() ) + " seconds." )
        
    

if __name__ == "__main__" :
    main( sys.argv )


