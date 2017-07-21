#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import time
import random

from rcr.brainlink.BrainLink import *

def main():
    bl = BrainLink( "/dev/rfcomm4" )
    if( bl.connect() ):
        bld = BrainLinkData()

        npts = 30
        attentionESense = [0]*npts
        meditationESense = [0]*npts

        fig = plt.figure( figsize=(8, 6) )
        plt.show( block=False )

        plt.subplot( 211 )
        plt.ylim( 0, 101 )
        plt.grid( True )
        plt.title( "Attention ESense" )
        liAtt, = plt.plot( attentionESense, "ro-", label="Attetion ESense"  )

        plt.subplot( 212 )
        plt.ylim( 0, 101 )
        plt.grid( True )
        plt.title( "Meditation ESense" )
        plt.show( block=False )
        liMed, = plt.plot( meditationESense, "bo", label="Attetion ESense"  )

        while( True ):
            try:
                attentionESense.pop( 0 )
                meditationESense.pop( 0 )

                bl.fillBrainLinkData( bld )
                #print( bld.poorSignalQuality, bld.attentionESense, bld.meditationESense, bld.delta, bld.theta )
                attentionESense.append( bld.attentionESense );
                meditationESense.append( bld.meditationESense );

                liAtt.set_ydata( attentionESense )
                liMed.set_ydata( meditationESense )
                fig.canvas.draw()
                time.sleep( 0.001 )

            except Exception as e:
                print( e )
                break
        bl.disconnect()

if( __name__ == "__main__" ):
    main()
