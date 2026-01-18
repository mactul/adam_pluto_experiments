import numpy as np
import matplotlib.pyplot as plt
import adi
from qam import closest_symb
from messages import symbols_to_messages

oversampling = 50
sample_rate = 5e6 # Hz
center_freq = 2.4e9 # Hz
sampling_margin = int(oversampling/5)
num_samps = 600000

sdr = adi.Pluto('ip:192.168.2.1')
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 70.0 # dB
print(int(center_freq))
sdr.rx_lo = int(center_freq)
sdr.sample_rate = int(sample_rate)
sdr.rx_rf_bandwidth = int(sample_rate)
sdr.rx_buffer_size = num_samps

samples = sdr.rx()

noise_floor = 1500

i = 0

# If the reception start in the middle of a message, we must wait for the next one to be sure the message is complete.
while i < len(samples) - 2 * oversampling and abs(samples[i]) > noise_floor:
    i += 1

symbols = []
# We iterate over all samples, minus the ones at the end that will result in an incomplete message.
while i < len(samples) - 2 * oversampling:
    if abs(samples[i]) > noise_floor:
        # We just went above the noise, it's a new message

        # We pick the mean signal around here, it should be 1 + 0j, we can use that to calculate the amplitude and phase shift.
        ref = np.mean(samples[i + sampling_margin: i + oversampling - sampling_margin])

        # We calculate how much the amplitude and phase must be corrected.
        ampl = abs(ref)
        angle = np.angle(ref * (1 + 0j).conjugate())

        i += oversampling

        if ampl < noise_floor:
            # It was just a quirck, not a message following our protocol.
            continue

        # print("amplitude:", ampl, ", angle:", angle)

        # We then pick the real data and correct it the same way. Hopefully, the amplitude and the phase wouldn't shifted since the ref was calculated.
        data = np.mean(samples[i + sampling_margin: i + oversampling - sampling_margin])
        data = data * np.exp(-1j * angle)

        i += oversampling

        if abs(data) < noise_floor:
            # It was just a quirck, not a message following our protocol.
            continue

        data /= ampl

        symbols.append(closest_symb(data))

    i += 1

print(symbols_to_messages(symbols))

plt.plot(np.abs(samples))

plt.show()
