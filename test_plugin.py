from hermes_plugin.bg_tts_provider import BG_TTS_Provider

print("Стартиране на теста на плъгина...")
# Симулираме, че Hermes зарежда плъгина
provider = BG_TTS_Provider()

# Текст, който агентът иска да каже
text_from_agent = "Тествам плъгина. Използвам API и TTS, за да говоря."

# Извикваме метода synthesize точно както би направил Hermes
# Обърнете внимание, че вече не подаваме път за запис, а само текста
output_file = provider.synthesize(text_from_agent)

print(f"Успех! Файлът е записан тук: {output_file}")