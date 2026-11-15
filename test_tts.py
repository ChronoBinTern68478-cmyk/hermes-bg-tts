import torch
import soundfile as sf
import sys

sys.path.append("./BgTTS-38M-V2")

from tokenizer import TTSTokenizer
from codec import CodecV6
from model import load_for_inference
from inference import generate

print("Зареждане на модела...")
model = load_for_inference("./BgTTS-38M-V2")
tokenizer = TTSTokenizer()
codec = CodecV6()

print("Извличане на глас от примерния файл...")
sample_path = "./BgTTS-38M-V2/samples/sample_male_bg3.wav" 

with torch.no_grad():
    # Извикваме encode директно с пътя до файла
    encoded_result = codec.encode(sample_path)
    
    # Принтираме ключовете, за да видим как се казва ембедингът (за всеки случай)
    print(f"Ключове в резултата: {encoded_result.keys()}")
    
    # Извличаме ембединга (най-вероятно се казва 'embedding', 'global_embedding' или 'speaker_emb')
    if 'embedding' in encoded_result:
        speaker_emb = encoded_result['embedding']
    elif 'global_embedding' in encoded_result:
        speaker_emb = encoded_result['global_embedding']
    elif 'speaker_emb' in encoded_result:
        speaker_emb = encoded_result['speaker_emb']
    else:
        # Ако не намерим точно това име, взимаме първата стойност от речника
        speaker_emb = list(encoded_result.values())[0]

print("Генериране на аудио...")
text = "Здравейте! Това е първият ми тест на български гласов модел с истински глас."
generated_tokens = generate(
    model=model,
    tokenizer=tokenizer,
    text=text,
    speaker_emb=speaker_emb,
    max_new_tokens=500,
    temperature=0.8,
    top_k=50,
    top_p=0.9,
    rep_penalty=1.2,
    device="cpu"
)

print("Декодиране на токените в реален звук...")
# Добавяме speaker_emb като втори аргумент
audio_numpy = codec.tokens_to_wav(generated_tokens, speaker_emb)

# Уверяваме се, че е Numpy масив и е плосък
if hasattr(audio_numpy, 'cpu'):
    audio_numpy = audio_numpy.cpu().numpy()
audio_numpy = audio_numpy.squeeze().astype('float32')

print("Записване на файла...")
sf.write("output.wav", audio_numpy, 24000)
print("Готово! Чуйте файла output.wav")