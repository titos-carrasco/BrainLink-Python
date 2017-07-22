#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import threading
import serial
import time

class BrainLinkData:
    def __init__( self ):
        self.poorSignalQuality = 200         # byte      (0 <=> 200) 0=OK; 200=sensor sin contacto con la piel
        self.attentionESense = 0             # byte      (1 <=> 100) 0=no confiable
        self.meditationESense = 0            # byte      (1 <=> 100) 0=no confiable
        self.blinkStrength = 0               # byte      (1 <=> 255)
        self.rawWave16Bit = 0                # int16     (-32768 <=> 32767)
        self.delta = 0                       # uint32    (0 <=> 16777215)
        self.theta = 0                       # uint32    (0 <=> 16777215)
        self.lowAlpha = 0                    # uint32    (0 <=> 16777215)
        self.highAlpha = 0                   # uint32    (0 <=> 16777215)
        self.lowBeta = 0                     # uint32    (0 <=> 16777215)
        self.highBeta = 0                    # uint32    (0 <=> 16777215)
        self.lowGamma = 0                    # uint32    (0 <=> 16777215)
        self.midGamma = 0                    # uint32    (0 <=> 16777215)

class BrainLink():
    def __init__( self, port ):
        self.port = port
        self.mutex = threading.Lock()
        self.connected = False
        self.bld = None
        self.conn = None
        self.tRunning = False
        self.tParser = None
        self.queue = None
        self.bytesLeidos = 0
        self.bytesPerdidos = 0
        self.paquetesProcesados = 0
        self.paquetesPerdidos = 0

    def connect( self ):
        if( self.connected ):
            print( "BrainLink Connect(): Ya se encuentra conectado a", self.port )
            return True

        self.bld = BrainLinkData()
        self.conn = None
        self.tRunning = False
        self.tParser = None
        self.queue = bytearray()
        self.bytesLeidos = 0
        self.bytesPerdidos = 0
        self.paquetesProcesados = 0
        self.paquetesPerdidos = 0

        # conecta a la puerta
        print( "MindSet Connect(): Intentando conectar a", self.port, " ...", end='' )
        try:
            self.conn = serial.Serial( self.port, baudrate=57600, bytesize=8,
                                       parity='N', stopbits=1, timeout=0.1 )
            self.conn.flushInput()
            self.conn.flushOutput()
            self.connected = True
        except Exception as e:
            self.conn = None
            print( e )
            return False
        print( "OK" )

        # levantamos la tarea de apoyo
        print( "BrainLink Connect(): Levantando tarea de lectura de datos ...", end='' )
        self.tParser = threading.Thread( target=self._TParser, args=(), name="_TParser" )
        self.tParser.start()
        while ( not self.tRunning ):
            time.sleep( 0 )
        print( "OK" )

        return True

    def disconnect( self ):
        if( self.connected ):
            print( "BrainLink Disconnect(): Deteniendo Tarea ...", end='' )
            self.tRunning = False
            self.tParser.join()
            self.tParser = None
            self.queue = bytearray()
            print( "OK" )

            # Disconnect
            print( "BrainLink Disconnect(): Cerrando puerta ...", end='' )
            try:
                self.conn.close()
            except Exception as e:
                print( e )
            self.connected = False
            self.conn = None

            print( "OK" )
            print( "Bytes Leidos   :", self.bytesLeidos )
            print( "Bytes Perdidos :", self.bytesPerdidos )
            print( "Paquetes Procesados :", self.paquetesProcesados)
            print( "Paquetes Perdidos :", self.paquetesPerdidos )
            print( threading.enumerate() )

    def isConnected( self ):
        return self.connected

    def fillBrainLinkData( self, bld ):
        self.mutex.acquire()
        bld.poorSignalQuality = self.bld.poorSignalQuality
        bld.attentionESense = self.bld.attentionESense
        bld.meditationESense = self.bld.meditationESense
        bld.blinkStrength = self.bld.blinkStrength
        bld.rawWave16Bit = self.bld.rawWave16Bit
        bld.delta = self.bld.delta
        bld.theta = self.bld.theta
        bld.lowAlpha = self.bld.lowAlpha
        bld.highAlpha = self.bld.highAlpha
        bld.lowBeta = self.bld.lowBeta
        bld.highBeta = self.bld.highBeta
        bld.lowGamma = self.bld.lowGamma
        bld.midGamma = self.bld.midGamma
        self.mutex.release()

    # privadas
    def _TParser( self, *args ):
        self.conn.flushInput()
        estado = 0
        plength = 0
        idx = 0
        payload = None
        self.tRunning = True
        while( self.tRunning ):
            # lee en bloques
            try:
                if( self.conn.in_waiting > 0 ):
                    data = self.conn.read( self.conn.in_waiting )
                    if( type( data ) == str ):
                        self.queue = self.queue + bytearray( data )
                    else:
                        self.queue = self.queue + data
                    self.bytesLeidos = self.bytesLeidos + len( data )
                    if( len( self.queue ) > 512 ):
                        print( "Advertencia, bytes pendientes", len( self.queue ) )
            except Exception as e:
                print( e )

            # debe haber leido algo
            if( len( self.queue ) == 0 ):
                time.sleep( 0 )
                continue

            # trabajamos con un automata
            b = self.queue.pop( 0 )

            # 0xAA 0xAA 0xAA*
            if( estado == 0 and b == 0xAA ):
                estado = 1
            elif( estado == 1 and b == 0xAA ):
                estado = 2
            elif( estado == 2 and b == 0xAA ):
                pass

            # seguido del numero de bytes de data
            elif( estado == 2 and b > 0 and b < 0xAA ):
                plength = b
                payload = bytearray( plength )
                idx = 0
                estado = 3

            # seguido de la data
            elif( estado == 3 ):
                payload[idx] = b
                idx = idx + 1
                if( idx == plength ):
                    estado = 4

            # finalmente el checksum
            elif( estado == 4 ):
                suma = 0
                for i in range( plength ):
                    suma = suma + payload[i]
                suma = ( ~( suma & 0xff ) ) & 0xff
                if( b != suma ):
                    self.bytesPerdidos = self.bytesPerdidos + 1 + plength + 1
                    self.paquetesPerdidos = self.paquetesPerdidos + 1
                    print( "_TParser(): ErrCheckSum" )
                else:
                    self.paquetesProcesados = self.paquetesProcesados + 1
                    self._parsePayload( payload )
                estado = 0
            else:
                #print( "_TParser(): byte perdido" )
                self.bytesPerdidos = self.bytesPerdidos + 1
                estado = 0

    def _parsePayload( self, payload ):
        if( payload[0] == 0xd2 ):       # disconnected
            print( "_parsePayload(): ErrDisconnected" )
            return

        if( payload[0] == 0xd4 ):       # alive message in stand by mode
            print( "_parsePayload(): Alive Message" )
            return

        pos = 0
        self.mutex.acquire()
        while pos < len( payload ):
            exCodeLevel = 0
            while( payload[pos] == 0x55 ):
                exCodeLevel = exCodeLevel + 1
                pos = pos + 1
            code = payload[pos]
            pos = pos + 1
            if( code >= 0x80 ):
                vlength = payload[pos]
                pos = pos + 1
            else:
                vlength = 1

            data = bytearray( vlength )
            for i in range( vlength ):
                data[i] = payload[pos + i]
            pos = pos + vlength

            if( exCodeLevel == 0 ):
                if( code == 0x02 ):    # poor signal quality (0 to 255) 0=>OK; 200 => no skin contact
                    self.bld.poorSignalQuality = data[0]
                elif( code == 0x04 ):  # attention eSense (0 to 100) 40-60 => neutral, 0 => result is unreliable
                    self.bld.attentionESense = data[0]
                elif( code == 0x05 ):  # meditation eSense (0 to 100) 40-60 => neutral, 0 => result is unreliable
                    self.bld.meditationESense = data[0]
                elif( code == 0x16 ):  # blink strength (1 to 255)
                    self.bld.blinkStrength = data[0]
                elif( code == 0x80 ):  # raw wave value (-32768 to 32767) - big endian
                    n = ( data[0]<<8 ) + data[1]
                    if( n >= 32768 ):
                        n = n - 65536
                    self.bld.rawWave16Bit = n
                elif( code == 0x83 ):  # asic eeg power struct (8, 3 bytes unsigned int big indian)
                    self.bld.delta     = ( data[0]<<16 ) + ( data[1]<<8 ) + data[2]
                    self.bld.theta     = ( data[3]<<16 ) + ( data[4]<<8 ) + data[5]
                    self.bld.lowAlpha  = ( data[6]<<16 ) + ( data[7]<<8 ) + data[8]
                    self.bld.highAlpha = ( data[9]<<16 ) + ( data[10]<<8 ) + data[11]
                    self.bld.lowBeta   = ( data[12]<<16 ) + ( data[13]<<8 ) + data[14]
                    self.bld.highBeta  = ( data[15]<<16 ) + ( data[16]<<8 ) + data[17]
                    self.bld.lowGamma  = ( data[18]<<16 ) + ( data[19]<<8 ) + data[20]
                    self.bld.midGamma  = ( data[21]<<16 ) + ( data[22]<<8 ) + data[23]
                # elif( code == 0x01 ):  # code battery - battery low (0x00)
                # elif( code == 0x03 ):  # heart rate (0 to 255)
                # elif( code == 0x06 ):  # 8bit raw wave value (0 to 255)
                # elif( code == 0x07 ):  # raw marker section start (0)
                # elif( code == 0x81 ):  # eeg power struct (legacy float)
                # elif( code == 0x86 ):  # rrinterval (0 to 65535)
                else:
                    print( "_parsePayload(): ExCodeLevel - %02x, Code: %02x, Data: [%s]" % ( exCodeLevel, code, ''.join(format(x, '02X') for x in data) ) )
            else:
                print( "_parsePayload(): ExCodeLevel - %02x, Code: %02x, Data: [%s]" % ( exCodeLevel, code, ''.join(format(x, '02X') for x in data) ) )
        self.mutex.release()
        return None
