#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time

from rcr.brainlink.BrainLink import *

def main():
    bl = BrainLink( "/dev/rfcomm4" )
    if( bl.connect() ):
        bld = BrainLinkData()
        t = time.time()
        while( time.time() - t < 20 ):
            bl.fillBrainLinkData( bld )
            print(  bld.poorSignalQuality,
                    bld.attentionESense,
                    bld.meditationESense,
                    bld.blinkStrength,
                    bld.rawWave16Bit,
                    bld.delta,
                    bld.theta,
                    bld.lowAlpha,
                    bld.highAlpha,
                    bld.lowBeta,
                    bld.highBeta,
                    bld.lowGamma,
                    bld.midGamma
            )
            time.sleep( 0 )
            #time.sleep( 20 )
        bl.disconnect()


if( __name__ == "__main__" ):
    main()
