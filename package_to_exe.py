import subprocess
import os

def package_to_exe():
    try:
        # 使用 PyInstaller 打包 console_app.py 为 .exe 文件
        subprocess.run(["pyinstaller", "--onefile", "--name", "GTOS", "--version-file", "version_info.txt", "console_app.py"], check=True)
        
        # 创建 version_info.txt 文件
        with open("version_info.txt", "w") as f:
            f.write("""FileVersion=1.0.0.0
ProductVersion=1.0.0.0
FileDescription=GTOS 控制台模拟器
LegalCopyright=Copyright 2025 Guoge Studios
OriginalFilename=GTOS.exe
ProductName=GTOS
""")

        print("GTOS 已成功打包为 GTOS.exe，并包含了版权信息和版本号")
    except subprocess.CalledProcessError as e:
        print(f"打包过程中发生错误：{e}")

if __name__ == "__main__":
    package_to_exe()
