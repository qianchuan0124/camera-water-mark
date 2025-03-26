import os
import shutil
import subprocess
import platform
import argparse
from pathlib import Path

def adjust_dirs(app_name, data_dirs, remove_dirs):
    # 定义资源文件夹的路径
    print("开始整理资源文件夹....")
    current_path = os.path.join(os.getcwd(), 'dist', app_name, '_internal')
    target_path = os.path.join(os.getcwd(), 'dist', app_name)
    print(os.getcwd())
    
    print("开始迁移数据....")
    for dir in data_dirs:
      dir_path = os.path.join(current_path, dir)
      target_dir_path = os.path.join(target_path, dir)
      if os.path.exists(target_dir_path):
        shutil.rmtree(target_dir_path)

      if os.path.exists(dir_path):
        shutil.move(dir_path, target_dir_path)
      else:
        os.makedirs(target_dir_path, exist_ok=True)

    print("开始删除数据....")
    for dir in remove_dirs:
      dir_path = os.path.join(current_path, dir)
      if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def run_inno_setup(iss_file_path, iscc_path=None):
    """
    使用 Inno Setup 编译器编译 Inno Setup 脚本文件 (.iss)。

    参数:
    iss_file_path (str or Path): Inno Setup 脚本文件的路径。
    iscc_path (str or Path, optional): iscc.exe 的路径。如果未提供，则假设 iscc.exe 在 PATH 中。
    """
    iss_file_path = Path(iss_file_path)
    
    if not iss_file_path.is_file():
        raise FileNotFoundError(f"指定的 Inno Setup 脚本文件不存在: {iss_file_path}")
    
    if iscc_path is None:
        iscc_path = r"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"  # 假设 iscc.exe 在 PATH 中
    else:
        iscc_path = Path(iscc_path)
        if not iscc_path.is_file():
            raise FileNotFoundError(f"iscc.exe 文件不存在: {iscc_path}")
    
    try:
        process = subprocess.Popen(
            [str(iscc_path), str(iss_file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        exit_code = process.wait()
        if exit_code != 0:
            print(f"编译失败，退出代码: {exit_code}")
            raise subprocess.CalledProcessError(exit_code, [str(iscc_path), str(iss_file_path)])
        else:
            print("Inno Setup 编译成功")
    except subprocess.CalledProcessError as e:
        print(f"编译失败: {e}")
        raise

def open_folder(folder_path):
    if platform.system() == 'Windows':
        subprocess.Popen(f'explorer "{folder_path}"', creationflags=subprocess.CREATE_NO_WINDOW)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.Popen(['open', folder_path], creationflags=subprocess.CREATE_NO_WINDOW)
    elif platform.system() == 'Linux':
        subprocess.Popen(['xdg-open', folder_path], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        print("未支持的操作系统")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="编译 Inno Setup 脚本并调整目录")
    
    parser.add_argument("app_name", type=str, help="应用程序名称")
    parser.add_argument("data_dirs", nargs='+', help="要迁移的数据目录列表")
    parser.add_argument("remove_dirs", nargs='+', help="要删除的数据目录列表")
    parser.add_argument("--iscc_path", type=str, default=None, help="iscc.exe 的路径 (可选)")
    
    args = parser.parse_args()
    
    # 调整目录
    adjust_dirs(args.app_name, args.data_dirs, args.remove_dirs)
    
    # 运行 Inno Setup 编译器
    run_inno_setup(".\\InnoScript.iss", args.iscc_path)
    
    # 打开输出文件夹
    open_folder(".")

