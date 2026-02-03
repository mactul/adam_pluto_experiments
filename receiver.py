import numpy as np
import matplotlib.pyplot as plt
import adi
from qam import closest_symb

oversampling = 25
byte_per_control = 2
sample_rate = 5e6 # Hz
center_freq = 2.4835e9 # Hz
sampling_margin = int(oversampling/5)
num_samps = 200000

sdr = adi.Pluto('ip:192.168.2.1')
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 70.0 # dB
print(int(center_freq))
sdr.rx_lo = int(center_freq)
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
        estimated_angle = None
        while i < len(samples) and len(msg_bytes) < 20:
            a = i
            # We pick the mean signal around here, it should be 0 + 1j, we can use that to calculate the phase shift.
            ref = np.mean(samples[i + sampling_margin: i + oversampling - sampling_margin])

            i += oversampling
            if estimated_angle is not None and closest_symb(ref * np.exp(-1j * estimated_angle)) != closest_symb(1j):
                # The phase shifted too much, don't trust this ref.
                i += oversampling
                angle = estimated_angle
            else:
                # We calculate how much the phase must be corrected.
                angle = np.angle(ref * (0 + 1j).conjugate())

                # We resynchronize the time by searching the moment we go from 1j to -1j
                j = i - oversampling // 4
                while j < i + oversampling // 4 and np.angle(samples[j] * np.exp(-1j * angle)) > 0:
                    j += 1
                if j < i + oversampling // 4 and closest_symb(np.mean(samples[j + sampling_margin: j + oversampling - sampling_margin]) * np.exp(-1j * angle)) == closest_symb(-1j):
                    # The time synchronization is good
                    i = j + oversampling
                else:
                    # The time synchronization is corrupted, use latest synchro
                    i += oversampling

            estimated_angle = angle

            # if ampl < noise_floor:
            #     # It was just a quirck, not a message following our protocol.
            #     print("quirck 2")
            #     continue
            #

            # print("amplitude:", ampl, ", angle:", angle)

            for j in range(byte_per_control):
                byte = 0
                for k in range(4):
                    # We then pick the real data and correct it the same way. Hopefully, the amplitude and the phase wouldn't shifted since the ref was calculated.
                    data = np.mean(samples[i + sampling_margin: i + oversampling - sampling_margin])
                    data = data * np.exp(-1j * angle)

                    i += oversampling


                    byte <<= 2
                    byte |= closest_symb(data)

                msg_bytes.append(byte)

            i += 1

        print(bytes(msg_bytes))

    i += 1


plt.plot(np.angle(samples))
plt.show()
