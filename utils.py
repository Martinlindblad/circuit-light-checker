import numpy as np
import pygame
import threading

# Initialize pygame mixer
pygame.mixer.init()

def generate_beep(frequency, duration, sample_rate=44100):
    """Generate a beep sound as a Pygame Sound object."""
    t = np.linspace(0, duration / 1000, int(sample_rate * (duration / 1000)), endpoint=False)
    wave = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    # Convert mono to stereo by duplicating the channel
    stereo_wave = np.stack((wave, wave), axis=-1)
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound

def play_sound_sequence(beep_sequence):
    """Play a sequence of beeps."""
    for frequency, duration in beep_sequence:
        beep = generate_beep(frequency, duration)
        beep.play()
        pygame.time.wait(duration)  # Wait for the current beep to finish

def play_success_sound():
    """Play a success sound sequence."""
    beep_sequence = [
        (1000, 200),
        (1500, 200),
        (2000, 300),
    ]
    threading.Thread(target=play_sound_sequence, args=(beep_sequence,), daemon=True).start()

def play_fail_sound():
    """Play a failure sound sequence."""
    beep_sequence = [
        (500, 300),
        (400, 300),
        (300, 300),
    ]
    threading.Thread(target=play_sound_sequence, args=(beep_sequence,), daemon=True).start()