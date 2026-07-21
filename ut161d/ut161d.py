import binascii
import logging
import decimal
import usb.core
import usb.util
import string
import time
from time import sleep

from ut61eplus import UT61EPLUS

log = logging.getLogger(__name__)

class UT161D(UT61EPLUS):
    #class UT161D:
    UT161D_VID = 0x1a86
    UT161D_PID = 0xe429

    def __init__(self):
        #VID = 0x1a86
        #PID = 0xe429

        """
        print("UT161D.__init__")
        #self.
        dev = usb.core.find(idVendor=self.UT161D_VID, idProduct=self.UT161D_PID)
        #if self.dev is None:
        if dev is None:
            print("Device not found. Is it connected?")
            exit(1)
        print("USB device is found.")

        # Try unplug kernel-driver
        try:
            #if self.dev.is_kernel_driver_active(0):
            if dev.is_kernel_driver_active(0):
                print("Unplug kernel-driver.")
                #self.dev.deatch_kernel_driver(0)
                dev.deatch_kernel_driver(0)
        except Exception as e:
            print("Kernel-driver can't unplug:",e)

        # Set configuration
        #self.
        dev.set_configuration()
        #cfg = self.dev.get_active_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]

        # Find IN-endpoint
        self.ep_in = usb.util.find_descriptor(intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

        # Find OUT-endpoint
        self.ep_out = usb.util.find_descriptor( intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

        print(f"IN endpoint: {hex(self.ep_in.bEndpointAddress)}")
        print(f"OUT endpoint: {hex(self.ep_out.bEndpointAddress)}")
        """


        log.debug("Etsin laitetta...")

        self.dev = usb.core.find(idVendor=self.UT161D_VID, idProduct=self.UT161D_PID)
        if self.dev is None:
            print("Device not found. Is it connected?")
            exit(1)
        log.debug("USB device is found.")

        # Yritä irrottaa kernel-ajuri
        try:
            if self.dev.is_kernel_driver_active(0):
                print("Unplug kernel-driver.")
                self.dev.detach_kernel_driver(0)
        except Exception as e:
            print("Kernel-ajuria ei voitu irrottaa:", e)

        # Aseta konfiguraatio
        self.dev.set_configuration()

        cfg = self.dev.get_active_configuration()
        intf = cfg[(0, 0)]

        # Etsi IN-endpoint
        self.ep_in = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )

        # Etsi OUT-endpoint
        self.ep_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )
        log.debug('IN endpoint: %02x',self.ep_in.bEndpointAddress)
        log.debug('OUT endpoint: %02x',self.ep_out.bEndpointAddress)
        #self._write(self._SEQUENCE_GET_NAME)
        #self._write(self._SEQUENCE_SEND_DATA)

    def _write(self, b: bytes):
        buf = []
        buf.append(len(b))
        buf += b
        while len(buf)<64:
            buf.append(0)
        #print(len(buf))
        #for d in buf:
        #    print(hex(d),end=" ")
        #exit()
        self.writebuf=buf
        self.dev.write(self.ep_out.bEndpointAddress,buf) # Toivottavasti toimii. On lisätty 20260720
        #try:
        #    self.dev.read(self.ep_in.bEndpointAddress, self.ep_in.wMaxPacketSize,timeout=1000)
        #except:
        #    pass

    def _readResponse(self) -> bytes:
        self.readData=[]
        state=0
        buf:bytes = None
        index:int = None
        sum:int = 0

        toomanyTimeOuts=0
        #print("TULI VARMUUDELLA")
        while True:
            try:
                x = self.dev.read(self.ep_in.bEndpointAddress, self.ep_in.wMaxPacketSize,timeout=1000)
                #print("read meni onnistuneesti läpi!!!",x)
                toomanyTimeOuts=0

                #for d in x:
                #    print(hex(d),end=" ")
                #print()
                #for c in x:
                #    print(chr(c),end="'")
                #print()
                #print("\n\n\n")
                #exit()
                self.readData=x
                #return True
                b:int
                for b in x[1:]:
                    #print(hex(b))
                    if state < 3 or index +2 < len(buf): # sum all bytes except last 2
                        sum += b
                    if state == 0 and b == 0xAB:
                        state = 1
                    elif state == 1 and b == 0xcd:
                        state = 2
                    elif state == 2:
                        buf = bytearray(b)
                        index = 0
                        state = 3
                    elif state == 3:
                        buf[index] = b
                        index += 1
                        if index == len(buf):
                            recevied_sum = (buf[-2] << 8) + buf[-1]
                            log.debug('calculated sum=%04x expected sum=%04x',sum,recevied_sum)
                            if sum != recevied_sum:
                                log.warning('checksum mismatch')
                                #print("Tarkistussumma heittää")
                                # exit()
                                return None
                            #print("Lukeminen onnistui !!!")
                            return buf[:-2] # drop last 2 bytes at end with checksum
                    else:
                        log.warning('unexpected byte %02x in state %i',b,state)
                        exit(1)
            except usb.core.USBTimeoutError:
                toomanyTimeOuts+=1
                log.debug("%i, Ei data (timeout), yritän uudelleen...",toomanyTimeOuts)
                if toomanyTimeOuts==10:
                    print("Yritetty riittävästi, joten lopetamme ohjelman suorituksen.")
                    exit()
                return False
                #self.dev.write(self.ep_out.bEndpointAddress,self.writebuf)
            pass

    def getName(self):
        #self._write(self._SEQUENCE_SEND_DATA)
        #print("write meni\n")
        #self._write(self._SEQUENCE_GET_NAME)
        #name=self._readResponse()
        #self._write(self._SEQUENCE_GET_NAME)
        #name=self._readResponse()


        name=False
        while name==False:
            #self._write(self._SEQUENCE_SEND_DATA)
            self._write(self._SEQUENCE_GET_NAME)
            name = self._readResponse()
            if name!=False:
                if name[0]<32 or name[0]>ord('z'):
                    #print("Failas")
                    name=False
        #print("read meni\n")
        #print(self.readData,"\n")
        #print()
        #print("TULI VARMUUDELLA TÄNNE!!!!")
        #print(name.decode('ASCII'))
        #exit()

        return name.decode('ASCII')







