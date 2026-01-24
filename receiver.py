import numpy as np
import matplotlib.pyplot as plt
import adi
from qam import closest_symb
from messages import symbols_to_messages

oversampling = 25
byte_per_control = 15
sample_rate = 5e6 # Hz
center_freq = 2.4e9 # Hz
sampling_margin = int(oversampling/5)
num_samps = 200000

sdr = adi.Pluto('ip:192.168.2.1')
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 70.0 # dB
print(int(center_freq))
sdr.rx_lo = int(center_freq)
sdr.lo_offset = 600
sdr.sample_rate = int(sample_rate)
sdr.rx_rf_bandwidth = int(sample_rate)
sdr.rx_buffer_size = num_samps

samples = sdr.rx()

noise_floor = 1000

i = 0

# If the reception start in the middle of a message, we must wait for the next one to be sure the message is complete.
while i < len(samples) and abs(samples[i]) > noise_floor:
    i += 1

# We iterate over all samples, minus the ones at the end that will result in an incomplete message.
while i < len(samples):
    if abs(samples[i]) > noise_floor:
        # We just went above the noise, it's a new message
        msg_bytes = []
        while i < len(samples) and abs(samples[i] > noise_floor):

            # We pick the mean signal around here, it should be 1 + 0j, we can use that to calculate the amplitude and phase shift.
            ref = np.mean(samples[i + sampling_margin: i + oversampling - sampling_margin])

            # We calculate how much the amplitude and phase must be corrected.
            ampl = abs(ref)
            angle = np.angle(ref * (1 + 0j).conjugate())

            i += 3 * oversampling // 4
            while closest_symb(samples[i] * np.exp(-1j * angle) / ampl) != closest_symb(-1 + 0j):
                i += 1

            i += oversampling

            if ampl < noise_floor:
                # It was just a quirck, not a message following our protocol.
                print("quirck 2")
                continue


            # print("amplitude:", ampl, ", angle:", angle)
            
            bytes_to_add = []
            quirck = False
            for j in range(byte_per_control):
                byte = 0
                for k in range(4):
                    # We then pick the real data and correct it the same way. Hopefully, the amplitude and the phase wouldn't shifted since the ref was calculated.
                    data = np.mean(samples[i + sampling_margin: i + oversampling - sampling_margin])
                    data = data * np.exp(-1j * angle)

                    i += oversampling

                    if abs(data) < noise_floor:
                        # It was just a quirck, not a message following our protocol.
                        quirck = True
                        print("quirck 1")
                        break
                    data /= ampl

                    byte <<= 2
                    byte |= closest_symb(data)

                bytes_to_add.append(byte)

            if not quirck:
                msg_bytes.extend(bytes_to_add)

            i += 1

        if len(msg_bytes) > 0:
            print(bytes(msg_bytes))

    i += 1


plt.plot(np.angle(samples))
plt.show()
