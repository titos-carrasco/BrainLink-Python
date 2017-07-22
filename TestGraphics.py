#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
#import matplotlib
#matplotlib.use('TkAgg')
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
        rawWave16Bit = [0]*npts

        fig = plt.figure( figsize=(8, 6) )
        plt.show( block=False )

        plt.subplot( 2, 2, 1 )
        plt.ylim( 0, 101 )
        plt.grid( True )
        plt.title( "Attention ESense" )
        liAtt, = plt.plot( attentionESense, "r.-"  )

        plt.subplot( 2, 2, 2 )
        plt.ylim( 0, 101 )
        plt.grid( True )
        plt.title( "Meditation ESense" )
        liMed, = plt.plot( meditationESense, "b.-" )

        plt.subplot( 2, 2, 3 )
        plt.grid( True )
        plt.title( "Raw Wave 16Bit" )
        liRaw, = plt.plot( rawWave16Bit, "b.-" )

        while( True ):
            try:
                attentionESense.pop( 0 )
                meditationESense.pop( 0 )
                rawWave16Bit.pop( 0 )

                bl.fillBrainLinkData( bld )
                #sprint( bld.poorSignalQuality, bld.attentionESense, bld.meditationESense, bld.delta, bld.theta )
                attentionESense.append( bld.attentionESense );
                meditationESense.append( bld.meditationESense );
                rawWave16Bit.append( bld.rawWave16Bit );

                liAtt.set_ydata( attentionESense )
                liMed.set_ydata( meditationESense )
                liRaw.set_ydata( rawWave16Bit )
                liRaw.axes.relim()
                liRaw.axes.autoscale_view()

                fig.canvas.draw()
                time.sleep( 0 )

            except Exception as e:
                print( e )
                break
        bl.disconnect()

if( __name__ == "__main__" ):
    main()
