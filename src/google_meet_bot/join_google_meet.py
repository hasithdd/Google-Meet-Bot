# import required modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import tempfile
import asyncio
from dotenv import load_dotenv

from .record_audio import AudioRecorder
from .speech_to_text import SpeechToText


load_dotenv()


class JoinGoogleMeet:
    def __init__(self, enable_livekit: bool = False):
        self.mail_address = os.getenv('EMAIL_ID')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.enable_livekit = enable_livekit
        self.livekit_manager = None
        self.livekit_bridge = None
        
        # Initialize LiveKit if enabled
        if self.enable_livekit:
            try:
                from .livekit_agent import LiveKitAgentManager, GoogleMeetLiveKitBridge
                self.livekit_manager = LiveKitAgentManager()
                self.livekit_bridge = GoogleMeetLiveKitBridge(self.livekit_manager)
            except ImportError as e:
                print(f"Warning: LiveKit integration not available: {e}")
                self.enable_livekit = False
        
        # create chrome instance
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        self.driver = webdriver.Chrome(options=opt)

    def Glogin(self):
        # Login Page
        self.driver.get(
            'https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')

        # input Gmail
        self.driver.find_element(By.ID, "identifierId").send_keys(self.mail_address)
        self.driver.find_element(By.ID, "identifierNext").click()
        self.driver.implicitly_wait(10)

        # input Password
        self.driver.find_element(By.XPATH,
            '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.ID, "passwordNext").click()
        self.driver.implicitly_wait(10)
        # go to google home page
        self.driver.get('https://google.com/')
        self.driver.implicitly_wait(100)
        print("Gmail login activity: Done")

    def turnOffMicCam(self, meet_link):
        # Navigate to Google Meet URL
        self.driver.get(meet_link)
        # turn off Microphone
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="t2mBxb"][data-anchor-id="hw0c9"]').click()
        self.driver.implicitly_wait(3000)
        print("Turn of mic activity: Done")

        # turn off camera
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="bwqwSd"][data-anchor-id="psRWwc"]').click()
        self.driver.implicitly_wait(3000)
        print("Turn of camera activity: Done")

    def checkIfJoined(self):
        try:
            # Wait for the join button to appear
            join_button = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.uArJ5e.UQuaGc.Y5sE8d.uyXBBb.xKiqt'))
            )
            print("Meeting has been joined")
        except (TimeoutException, NoSuchElementException):
            print("Meeting has not been joined")

    def AskToJoin(self, audio_path, duration):
        # Ask to Join meet
        time.sleep(5)
        self.driver.implicitly_wait(2000)
        self.driver.find_element(By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]').click()
        print("Ask to join activity: Done")
        # checkIfJoined()
        # Ask to join and join now buttons have same xpaths
        
        if self.enable_livekit:
            print("Starting LiveKit agent mode...")
            self._start_livekit_agent(duration)
        else:
            AudioRecorder().get_audio(audio_path, duration)

    def _start_livekit_agent(self, duration):
        """Start LiveKit agent and bridge audio with Google Meet.
        
        Args:
            duration: Duration to run the agent (in seconds)
        """
        if not self.livekit_manager:
            print("LiveKit manager not initialized")
            return
        
        # Get LiveKit room name from environment or generate one
        room_name = os.getenv('LIVEKIT_ROOM_NAME', 'google-meet-session')
        
        print(f"Connecting to LiveKit room: {room_name}")
        
        # Run the agent in a background thread/process
        # For now, we'll use the CLI-based approach
        try:
            # Option 1: Run as a worker (recommended for production)
            print("To run the LiveKit agent, execute in a separate terminal:")
            print(f"  python -m google_meet_bot.livekit_worker --room {room_name}")
            print()
            print("Or use the programmatic approach (experimental)...")
            
            # Option 2: Programmatic approach (may need adjustment)
            # This would require running the agent in the background
            # For simplicity, we'll just print instructions
            print(f"LiveKit agent mode enabled. Keeping session alive for {duration} seconds...")
            time.sleep(duration)
            
        except Exception as e:
            print(f"Error running LiveKit agent: {e}")
            # Fallback to regular audio recording
            print("Falling back to regular audio recording...")
            audio_path = os.path.join(tempfile.mkdtemp(), "output.wav")
            AudioRecorder().get_audio(audio_path, duration)


def _main():
    DO_ANALYSIS = True
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "output.wav")
    # Get configuration from environment variables
    meet_link = os.getenv('MEET_LINK')
    duration = int(os.getenv('RECORDING_DURATION', 60))

    obj = JoinGoogleMeet()
    obj.Glogin()
    obj.turnOffMicCam(meet_link)
    obj.AskToJoin(audio_path, duration)
    if DO_ANALYSIS:
        SpeechToText().transcribe(audio_path)


