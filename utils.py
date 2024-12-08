import winsound

def play_success_sound():
    """Play a success sound sequence."""
    winsound.Beep(1000, 200)
    winsound.Beep(1500, 200)
    winsound.Beep(2000, 300)

def play_fail_sound():
    """Play a failure sound sequence."""
    winsound.Beep(500, 300)
    winsound.Beep(400, 300)
    winsound.Beep(300, 300)
