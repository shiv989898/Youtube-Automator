import pyttsx3

def create_voiceover(text, filename="voiceover.mp3"):
    """
    Creates a voiceover from text using pyttsx3 and saves it as an MP3 file.
    """
    engine = pyttsx3.init()
    
    # You can adjust properties for a clearer voice
    voices = engine.getProperty('voices')
    # You might want to experiment with different voices available on your system
    # engine.setProperty('voice', voices[1].id) # Example: setting to the second available voice
    
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50) # Slow down the speech rate
    
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume + 0.25) # Increase the volume

    # pyttsx3's save_to_file can sometimes be problematic with mp3.
    # A common workaround is to save to wav and then convert, but we will try mp3 first.
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename
