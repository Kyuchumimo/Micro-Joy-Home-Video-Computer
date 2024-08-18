import time

class WT588D:
    def __init__(self, rst, sda, scl=None, cs=None):
        self.rst = rst
        self.sda = sda
        self.scl = scl
        self.cs = cs

        self.rst.init(self.rst.OUT, value=1)
        self.sda.init(self.sda.OUT, value=0)

        if self.scl:
            self.scl.init(self.scl.OUT, value=1)
        if self.cs:
            self.cs.init(self.rst.OUT, value=1)

    def send_threelines(self, addr):
        self.rst.value(0)           # reset the IC
        time.sleep_ms(5)            # reset signal retain low level 5ms
        self.rst.value(1)
        time.sleep_ms(20)           # reset signal retain high level 20 ms

        self.cs.value(0)
        time.sleep_ms(5)            # select-chip signal retain low level 5ms

        for i in range(8):
            self.scl.value(0)
            if addr & 1:
                self.sda.value(1)
            else:
                self.sda.value(0)
            addr>>=1
            time.sleep_us(150)     # clock cycle300us
            self.scl.value(1)
            time.sleep_us(150)

        self.cs.value(1)

    def send_oneline(self, addr):
        self.rst.value(0)           # reset the IC
        time.sleep_ms(5)            # reset signal retain low level 5ms
        self.rst.value(1)
        time.sleep_ms(17)           # reset signal retain high level 17ms

        self.sda.value(0)
        time.sleep_ms(5)            # put data signal to low level 5ms

        for i in range(8):
            self.sda.value(1)
            if addr & 1:
                time.sleep_us(600)  # High level:Low level=600us:200us, stand for send data 1
                self.sda.value(0)
                time.sleep_us(200)
            else:
                time.sleep_us(200)  # High level:Low level=200us : 600us , stand for send data0
                self.sda.value(0)
                time.sleep_us(600)
            addr>>=1

        self.sda.value(1)
