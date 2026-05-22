import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import os

# ==========================================
# CONFIGURATION
# ==========================================
# Voice: AvaNeural is a natural young adult female voice
VOICE = os.getenv("SUSTAINAI_TTS_VOICE", "en-US-AvaNeural")
RATE = os.getenv("SUSTAINAI_TTS_RATE", "+2%")   # Speed of speech (e.g., +10% for faster, -10% for slower)
PITCH = os.getenv("SUSTAINAI_TTS_PITCH", "+0Hz") # Neutral pitch for a natural adult tone
OUTPUT_FILE = "response.mp3"

# ==========================================
# TEXT-TO-SPEECH (TTS) SECTION
# ==========================================
async def _generate_audio(text):
    """Internal async function to create the mp3 file using Edge TTS"""
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(OUTPUT_FILE)

def play_audio():
    """Plays the generated mp3 file and cleans up"""
    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    pygame.mixer.quit() 
    try:
        os.remove(OUTPUT_FILE) # Clean up the file after playing
    except OSError:
        pass

def speak(text):
    """Main function to convert text to speech and play it"""
    print(f"AI: {text}")
    asyncio.run(_generate_audio(text))
    play_audio()

# ==========================================
# SPEECH-TO-TEXT (STT) SECTION
# ==========================================
def listen():
    """Listens to microphone and returns recognized text"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\nListening... (Speak now)")
        # Adjust for background noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return None

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        print("AI: I didn't quite catch that.")
        return None
    except sr.RequestError:
        print("AI: System Error: Could not connect to the speech service.")
        return None

