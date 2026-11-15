import torch
import soundfile as sf
import sys
import re

from replacements import BG_TTS_REPLACEMENTS

sys.path.append("./BgTTS-38M-V2")

from tokenizer import TTSTokenizer
from codec import CodecV6
from model import load_for_inference
from inference import generate

class BulgarianTTS:
    def __init__(self, model_path="./BgTTS-38M-V2"):
        print("Зареждане на модела...")
        self.model = load_for_inference(model_path)
        self.tokenizer = TTSTokenizer()
        self.codec = CodecV6()
        self.replacements = BG_TTS_REPLACEMENTS 

        # Дефинираме правилата за транслитерация (първо комбинациите от 2-3 букви, после единичните)
        self.translit_map = {
            'sh': 'ш', 'ch': 'ч', 'th': 'т', 'ph': 'ф', 'zh': 'ж', 'kh': 'х',
            'ya': 'я', 'yu': 'ю', 'yo': 'йо', 'ye': 'е', 'ay': 'ей', 'ey': 'ей',
            'a': 'а', 'b': 'б', 'c': 'к', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г',
            'h': 'х', 'i': 'и', 'j': 'дж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
            'o': 'о', 'p': 'п', 'q': 'к', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
            'v': 'в', 'w': 'у', 'x': 'кс', 'y': 'й', 'z': 'з'
        }

    def _transliterate_word(self, match):
        """Взима латинска дума и я превръща в кирилица"""
        word = match.group(0)
        word_lower = word.lower()
        result = ""
        i = 0
        while i < len(word_lower):
            # Проверяваме за комбинация от 2 букви
            if i + 1 < len(word_lower) and word_lower[i:i+2] in self.translit_map:
                result += self.translit_map[word_lower[i:i+2]]
                i += 2
            # Ако няма комбинация, взимаме 1 буква
            elif word_lower[i] in self.translit_map:
                result += self.translit_map[word_lower[i]]
                i += 1
            else:
                result += word_lower[i]
                i += 1
        
        # Запазваме главната буква, ако оригиналът е започвал с главна
        if word[0].isupper():
            result = result.capitalize()
        return result

    def _fix_latin_words(self, text):
        # 1. Първо прилагаме изключенията (акроними) от речника
        processed_text = text
        for latin, cyrillic in self.replacements.items():
            processed_text = re.sub(latin, cyrillic, processed_text, flags=re.IGNORECASE)
        
        # 2. После транслитерираме всички останали латински думи
        # Намираме всички думи, състоящи се от латински букви, и ги подаваме на функцията
        processed_text = re.sub(r'[A-Za-z]+', self._transliterate_word, processed_text)
        
        return processed_text

    def generate_audio(self, text, reference_wav_path, output_wav_path):
        text = self._fix_latin_words(text)
        print(f"Текст за генериране: {text}")

        print("Извличане на глас...")
        with torch.no_grad():
            encoded_result = self.codec.encode(reference_wav_path)
            speaker_emb = encoded_result['global_embedding']

        print("Генериране на реч...")
        generated_tokens = generate(
            model=self.model,
            tokenizer=self.tokenizer,
            text=text,
            speaker_emb=speaker_emb,
            max_new_tokens=500,
            temperature=0.8,
            top_k=50,
            top_p=0.9,
            rep_penalty=1.2,
            device="cpu"
        )

        print("Записване...")
        audio_numpy = self.codec.tokens_to_wav(generated_tokens, speaker_emb)
        
        if hasattr(audio_numpy, 'cpu'):
            audio_numpy = audio_numpy.cpu().numpy()
        audio_numpy = audio_numpy.squeeze().astype('float32')
        
        sf.write(output_wav_path, audio_numpy, 24000)
        print(f"Готово! Записано в {output_wav_path}")

# Тест
if __name__ == "__main__":
    tts = BulgarianTTS()
    # Тестваме с думи, които не са в речника
    tts.generate_audio(
        text="Здравейте! Аз съм Hermes Agent. Работя с software и използвам ChatGPT за coding.",
        reference_wav_path="./BgTTS-38M-V2/samples/sample_male_bg3.wav",
        output_wav_path="test_output.wav"
    )