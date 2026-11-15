import os
from datetime import datetime  

# Опитваме се да заредим истинския базов клас на Hermes
try:
    from hermes.plugins import TTSProvider
except ImportError:
    # Ако Hermes не е инсталиран, използваме тестов клас
    class TTSProvider:
        def __init__(self, config=None):
            self.config = config

from bg_tts import BulgarianTTS

class BG_TTS_Provider(TTSProvider):
    def __init__(self, config=None):
        super().__init__(config)
        
        # Настройки по подразбиране
        self.model_path = config.get("model_path", "./BgTTS-38M-V2") if config else "./BgTTS-38M-V2"
        self.voice_sample_path = config.get("voice_sample", "./BgTTS-38M-V2/samples/sample_male_bg3.wav") if config else "./BgTTS-38M-V2/samples/sample_male_bg3.wav"
        self.output_dir = config.get("output_dir", "./tts_outputs") if config else "./tts_outputs"
        
        # Създаваме папка за изходите, ако не съществува
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("Инициализиране на Български TTS плъгин...")
        self.engine = BulgarianTTS(model_path=self.model_path)

    def synthesize(self, text: str, **kwargs) -> str:
        """
        Извиква се от Hermes. Връща пътя до генерирания аудио файл.
        """
        # Генерираме името на файла като: audio_20261115080700.wav
        time_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"audio_{time_str}.wav"
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Генерираме аудиото
        self.engine.generate_audio(
            text=text,
            reference_wav_path=self.voice_sample_path,
            output_wav_path=output_path
        )
        
        return output_path

def get_provider(config=None):
    return BG_TTS_Provider(config)