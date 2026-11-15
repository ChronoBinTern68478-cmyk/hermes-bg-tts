import os
from datetime import datetime

# Опитваме се да заредим истинския базов клас на Hermes
try:
    from agent.tts_provider import TTSProvider
except ImportError:
    # Тестов клас за Codespace
    class TTSProvider:
        pass

from bg_tts import BulgarianTTS

class BG_TTS_Provider(TTSProvider):
    @property
    def name(self) -> str:
        return "bg-tts"  # Трябва да съвпада с tts.provider в config.yaml

    @property
    def display_name(self) -> str:
        return "Български TTS (BgTTS-38M-V2)"

    def is_available(self) -> bool:
        # Връща False, ако моделът липсва, за да не се показва в списъка
        return os.path.exists("./BgTTS-38M-V2")

    def __init__(self, config=None):
        super().__init__()
        self.model_path = config.get("model_path", "./BgTTS-38M-V2") if config else "./BgTTS-38M-V2"
        self.voice_sample_path = config.get("voice_sample", "./BgTTS-38M-V2/samples/sample_male_bg3.wav") if config else "./BgTTS-38M-V2/samples/sample_male_bg3.wav"
        self.output_dir = config.get("output_dir", "./tts_outputs") if config else "./tts_outputs"
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.engine = BulgarianTTS(model_path=self.model_path)

    def synthesize(self, text: str, output_path: str, *, voice=None, model=None, speed=None, format="wav", **extra) -> str:
        # Генерираме името на файла
        time_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"audio_{time_str}.wav"
        full_output_path = os.path.join(self.output_dir, filename)
        
        # Генерираме аудиото
        self.engine.generate_audio(
            text=text,
            reference_wav_path=self.voice_sample_path,
            output_wav_path=full_output_path
        )
        
        # Връщаме пътя, който Hermes очаква
        return full_output_path

def register(ctx):
    ctx.register_tts_provider(BG_TTS_Provider())