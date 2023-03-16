import pyaudio
import struct
import math
import wave
import pyfiglet


ASCII_art_1 = pyfiglet.figlet_format("Decibel Meter")
print(ASCII_art_1)

# Set up audio stream
CHUNK = 30000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
stream_input = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Set up alarm noise
alarm_wave = wave.open('alarm.wav', 'rb')
alarm_data = alarm_wave.readframes(alarm_wave.getnframes())

# Function to calculate decibel level
def calculate_dB(data):
    """
    It takes a chunk of audio data, converts it to a list of 16-bit signed integers,
    squares each integer, sums the squares, divides by the number of samples, and
    then takes the log of the result
    
    :param data: the raw audio data
    :return: The decibel level of the audio.
    """
    count = len(data)/2
    format = '%dh'%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 1e-6
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return 10*math.log10( sum_squares / count ) + 110

# Set threshold
threshold = 83
print(f"Threshold at {threshold} \n")

stream_output = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=1024
)

# Start streaming audio and measuring decibel levels
try:
    while True:
        # Listen 
        data = stream_input.read(CHUNK,exception_on_overflow = False)
        decibel_level = calculate_dB(data)
        print(f"Decibel level: {int(decibel_level)} dB", end="\r")
        if decibel_level >= threshold:
            # Increase volume of system to 100% (on Mac)
            import platform
            if platform.system() == 'Darwin':
                from subprocess import call
                call(["osascript -e 'set volume output volume 100'"], shell=True)
            # Play alarm noise
            stream_output.write(alarm_data)

except KeyboardInterrupt:
    # Keyboard interruption : ctrl+c
    print("\nExiting program due to keyboard interrupt")

    print("Stop stream 2")
    stream_output.stop_stream()
    stream_output.close()

    print("Stop stream 1")
    stream_input.stop_stream()
    stream_input.close()

    print("Stop pyaudio")
    p.terminate()


