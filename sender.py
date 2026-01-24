import numpy as np
import adi
from qam import symb_to_qpsk
from messages import message_to_symbols

oversampling = 25
byte_per_control = 15
sample_rate = 5e6 # Hz
center_freq = 2.4e9 # Hz

def send_message(sdr: adi.Pluto, message: bytes, oversampling: int, byte_per_control: int):
    buf = []
    for i in range(0, len(message), byte_per_control):
        qpsk = np.array([[symb_to_qpsk((b >> 6) & 0b11), symb_to_qpsk((b >> 4) & 0b11), symb_to_qpsk((b >> 2) & 0b11), symb_to_qpsk(b & 0b11)] for b in message[i:i+byte_per_control]]).flatten()
        msg = np.repeat([1+0j, -1+0j, *qpsk], oversampling)
        if (4 * byte_per_control+1) * oversampling > msg.shape[0]:
            msg = np.concatenate([msg, symb_to_qpsk(0b00) * np.ones((4 * byte_per_control+1) * oversampling - msg.shape[0])])
        buf.append(msg)

    sdr.tx(np.concatenate(buf) * 2**14)



sdr = adi.Pluto("ip:192.168.3.1")
sdr.sample_rate = int(sample_rate)
sdr.tx_rf_bandwidth = int(sample_rate)
sdr.tx_lo = int(center_freq)
sdr.tx_hardwaregain_chan0 = -10 # Increase for longer distance communication, valid range is between -90 to 0 dB

while True:
    # I send the same symbol over and over again
    # Because python is slow (and the library, and the USB bus, etc...), I will send no signal between each symbol
    # This time sending nothing is mandatory for the receiver to synchronise itself with the 1+0j control
    send_message(sdr, "Hello world ! Comment allez vous ? ca va tres bien et vous ?".encode(), oversampling, byte_per_control)
