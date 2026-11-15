import sys
import os

# 1. Създаваме фалшив модул 'agent.tts_provider', за да залъжем нашия плъгин
os.makedirs("agent", exist_ok=True)
with open("agent/__init__.py", "w") as f: pass
with open("agent/tts_provider.py", "w") as f:
    f.write("class TTSProvider:\n    pass\n")

# 2. Симулираме обекта 'ctx', който Hermes подава на register()
class FakeContext:
    def register_tts_provider(self, provider):
        print(f"✅ Плъгинът '{provider.name}' беше регистриран успешно!")
        print(f"   Display Name: {provider.display_name}")
        print(f"   Достъпен ли е моделът: {provider.is_available()}")

# 3. Импортираме нашия плъгин и извикваме register()
from hermes_plugin import register, BG_TTS_Provider

print("Симулиране на стартиране на Hermes...")
ctx = FakeContext()
register(ctx)

# 4. Тестваме директно метода synthesize (както би направил Hermes)
# ВАЖНО: Тук създаваме нов екземпляр, който ще си зареди модела нормално
print("\nИнициализиране на нов провайдър за тестване на синтез...")
provider = BG_TTS_Provider()

sys.path.append(os.getcwd())

print("\nТестване на synthesize...")
text = "Здравей, Хермес! Това е тест на плъгина."
# Подаваме името на файла, което Hermes по принцип изисква
output_file = provider.synthesize(text, output_path="ignored.wav")
print(f"✅ Генериран файл: {output_file}")