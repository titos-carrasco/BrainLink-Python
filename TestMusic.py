#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import mido
import time

from rcr.mindwave.MindWave import *

def main():
    # requiere instalar rtmidi: $ pip install python-rtmidi
    mido.set_backend( 'mido.backends.rtmidi/UNIX_JACK' )
    #mido.set_backend( 'mido.backends.rtmidi/LINUX_ALSA' )
    #mido.set_backend( 'mido.backends.portmidi' )
    midiOut = mido.open_output( 'MindWave', virtual = True, autoreset = True  )

    mw = MindWave( "/dev/ttyUSB0", 1000, 0x0000 )
    if( mw.connect() ):
        mwd = MindWaveData()
        while( True ):
            mw.fillMindWaveData( mwd )
            print(  mwd.poorSignalQuality, mwd.attentionESense, mwd.meditationESense )
            nota1 = mwd.attentionESense
            nota2 = mwd.meditationESense

            msg = mido.Message( 'note_on', channel = 0, note = nota1, velocity = 16 )
            midiOut.send( msg )
            msg = mido.Message( 'note_on', channel = 1, note = nota2, velocity = 16 )
            midiOut.send( msg )
            time.sleep( (mwd.rawWave16Bit & 0x0F )/100 )
            msg = mido.Message( 'note_off', channel = 0, note = nota1, velocity = 16 )
            midiOut.send( msg )
            msg = mido.Message( 'note_off', channel = 1, note = nota2, velocity = 16 )
            midiOut.send( msg )

            time.sleep( 0.01 )
        mw.disconnect()

if( __name__ == "__main__" ):
    main()
