import os
import sys
import subprocess
import shutil

def print_step(step, text):
    print(f"\n[{step}/5] {text}")

def run_command(command, error_msg):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError:
        print(f"❌ ГРЕШКА: {error_msg}")
        sys.exit(1)

def install_dependencies():
    print_step(1, "Инсталиране на PyTorch (CPU версия)...")
    # Проверка дали pip съществува
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pip_cmd = f"{sys.executable} -m pip"
    except subprocess.CalledProcessError:
        print("   - 'pip' не е намерен. Опит за инсталиране с 'ensurepip'...")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        pip_cmd = f"{sys.executable} -m pip"

    run_command(
        f"{pip_cmd} install torch torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "Неуспешна инсталация на PyTorch."
    )
    run_command(
        f"{sys.executable} -m pip install transformers sentencepiece protobuf soundfile numpy",
        "Неуспешна инсталация на основните библиотеки."
    )
    
    print_step(3, "Инсталиране на MioCodec от GitHub...")
    run_command(
        f"{sys.executable} -m pip install git+https://github.com/Aratako/MioCodec.git",
        "Неуспешна инсталация на MioCodec. Уверете се, че имате инсталиран 'git' в системата."
    )
"""
def install_dependencies():
    print_step(1, "Инсталиране на PyTorch (CPU версия)...")
    # Инсталираме само CPU версията, за да не сваляме излишни гигабайти
    run_command(
        f"{sys.executable} -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "Неуспешна инсталация на PyTorch."
    )

    print_step(2, "Инсталиране на останалите библиотеки...")
    run_command(
        f"{sys.executable} -m pip install transformers sentencepiece protobuf soundfile numpy",
        "Неуспешна инсталация на основните библиотеки."
    )
    
    print_step(3, "Инсталиране на MioCodec от GitHub...")
    run_command(
        f"{sys.executable} -m pip install git+https://github.com/Aratako/MioCodec.git",
        "Неуспешна инсталация на MioCodec. Уверете се, че имате инсталиран 'git' в системата."
    )
    """
def download_and_patch_model():
    print_step(4, "Изтегляне и подготовка на модела BgTTS-38M-V2...")
    model_dir = "./BgTTS-38M-V2"
    
    # Изтегляне
    if not os.path.exists(model_dir):
        try:
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id='beleata74/BgTTS-38M-V2', local_dir=model_dir)
            print("   - Моделът е изтеглен успешно.")
        except ImportError:
            print("   - Липсва 'huggingface_hub'. Инсталиране...")
            run_command(f"{sys.executable} -m pip install huggingface_hub", "Грешка при инсталиране на huggingface_hub")
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id='beleata74/BgTTS-38M-V2', local_dir=model_dir)
    else:
        print("   - Моделът вече е изтеглен. Пропускаме.")

    # Преименуване на checkpoint
    inf_path = os.path.join(model_dir, "checkpoint_inference.pt")
    ckpt_path = os.path.join(model_dir, "checkpoint.pt")
    if os.path.exists(inf_path) and not os.path.exists(ckpt_path):
        os.rename(inf_path, ckpt_path)
        print("   - Файлът с тегла е преименуван на checkpoint.pt.")

    # Патчване на CUDA -> CPU
    print("   - Коригиране на кода за работа без видео карта (CPU)...")
    patched_count = 0
    for root, dirs, files in os.walk(model_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                # Заменяме всички срещания на cuda с cpu
                content = content.replace('device="cuda"', 'device="cpu"')
                content = content.replace("device='cuda'", "device='cpu'")
                content = content.replace('torch.device("cuda")', 'torch.device("cpu")')
                content = content.replace('map_location=device', 'map_location="cpu"')
                content = content.replace('.cuda()', '.cpu()')
                content = content.replace('device = "cuda"', 'device = "cpu"')
                content = content.replace('device = torch.device("cuda")', 'device = torch.device("cpu")')
                
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    patched_count += 1
    
    if patched_count > 0:
        print(f"   - Успешно коригирани {patched_count} файла за работа на CPU.")

def setup_hermes_plugin():
    print_step(5, "Инсталиране на плъгина в Hermes Agent...")
    # Пътят, където Hermes търси плъгини (в Docker контейнера това е /root/.hermes)
    hermes_plugins_dir = "/root/.hermes/plugins/tts"
    target_dir = os.path.join(hermes_plugins_dir, "bg-tts")
    
    os.makedirs(hermes_plugins_dir, exist_ok=True)
    
    if os.path.exists(target_dir):
        print("   - Премахване на стара версия на плъгина...")
        shutil.rmtree(target_dir)
        
    print(f"   - Копиране на плъгина в {target_dir}...")
    shutil.copytree("./hermes_plugin", target_dir)
    print("   - Плъгинът е инсталиран успешно.")

def main():
    print("🚀 Стартиране на пълния инсталатор за Български TTS (BgTTS-38M-V2)")
    print("Това може да отнеме няколко минути...")
    
    install_dependencies()
    download_and_patch_model()
    setup_hermes_plugin()
    
    print("\n✅ ВСИЧКО Е ГОТОВО!")
    print("Моля, рестартирайте контейнера на Hermes (docker restart hermes-agent), за да активирате плъгина.")

if __name__ == "__main__":
    main()