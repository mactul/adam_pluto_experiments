import numpy as np
import adi
from qam import symb_to_qam8

oversampling = 50
sample_rate = 5e6 # Hz
center_freq = 1e9 # Hz

def symb_sample(oversampling: int, symb: complex):
    # We send 1+0j so the receiver can adjust the amplitude and the phase shift
    # Then we send the symbol
    # It should be possible to send multiple symbols for one reference, but this increase the probability that the phase shift mid-message.
    return np.concatenate([(1+0j) * np.ones(oversampling), symb * np.ones(oversampling)]) * 2**14



sdr = adi.Pluto("ip:192.168.3.1")
sdr.sample_rate = int(sample_rate)
sdr.tx_rf_bandwidth = int(sample_rate)
sdr.tx_lo = int(center_freq)
sdr.tx_hardwaregain_chan0 = -20 # Increase for longer distance communication, valid range is between -90 to 0 dB

while True:
    # I send the same symbol over and over again
    # Because python is slow (and the library, and the USB bus, etc...), I will send no signal between each symbol
    # This time sending nothing is mandatory for the receiver to synchronise itself with the 1+0j control
    sdr.tx(symb_sample(oversampling, symb_to_qam8(0b101)))
