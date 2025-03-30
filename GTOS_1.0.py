import os
import sys
import shutil
import stat
import subprocess
import datetime
import time
import traceback
from typing import List, Dict, Any
import logging
import random
import calendar
import hashlib
import mimetypes
import tempfile
import textwrap
import ctypes  # 新增导入

try:
    import readline
except ImportError:
    import pyreadline3 as readline

class FileSystem:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def _full_path(self, path: str) -> str:
        return os.path.join(self.root_dir, path.lstrip('/'))

    def list_dir(self, path: str) -> List[str]:
        full_path = self._full_path(path)
        return os.listdir(full_path)

    def change_dir(self, path: str) -> bool:
        full_path = self._full_path(path)
        if os.path.isdir(full_path):
            os.chdir(full_path)
            return True
        return False

    def make_dir(self, path: str) -> bool:
        full_path = self._full_path(path)
        try:
            os.makedirs(full_path, exist_ok=True)
            return True
        except OSError as e:
            logging.error(f"无法创建目录 '{path}': {e}")
            return False

    def remove_file(self, path: str) -> bool:
        full_path = self._full_path(path)
        try:
            os.remove(full_path)
            return True
        except OSError as e:
            logging.error(f"无法删除文件 '{path}': {e}")
            return False

    def copy_file(self, src: str, dst: str) -> bool:
        src_path = self._full_path(src)
        dst_path = self._full_path(dst)
        try:
            shutil.copy2(src_path, dst_path)
            return True
        except OSError as e:
            logging.error(f"无法复制文件 '{src}' 到 '{dst}': {e}")
            return False

    def move_file(self, src: str, dst: str) -> bool:
        src_path = self._full_path(src)
        dst_path = self._full_path(dst)
        try:
            shutil.move(src_path, dst_path)
            return True
        except OSError as e:
            logging.error(f"无法移动文件 '{src}' 到 '{dst}': {e}")
            return False

    def create_file(self, path: str) -> bool:
        full_path = self._full_path(path)
        try:
            with open(full_path, 'w') as f:
                pass
            return True
        except OSError as e:
            logging.error(f"无法创建文件 '{path}': {e}")
            return False

    def read_file(self, path: str) -> str:
        full_path = self._full_path(path)
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except OSError as e:
            logging.error(f"无法读取文件 '{path}': {e}")
            return ""

    def write_file(self, path: str, content: str) -> bool:
        full_path = self._full_path(path)
        try:
            with open(full_path, 'w') as f:
                f.write(content)
            return True
        except OSError as e:
            logging.error(f"无法写入文件 '{path}': {e}")
            return False

    def remove_dir(self, path: str) -> bool:
        full_path = self._full_path(path)
        try:
            shutil.rmtree(full_path)
            return True
        except OSError as e:
            logging.error(f"无法删除目录 '{path}': {e}")
            return False

    def create_symlink(self, target: str, link_name: str) -> bool:
        target_path = self._full_path(target)
        link_path = self._full_path(link_name)
        try:
            os.symlink(target_path, link_path)
            return True
        except OSError as e:
            logging.error(f"无法创建符号链接 '{link_name}' 指向 '{target}': {e}")
            return False

    def change_mode(self, path: str, mode: int) -> bool:
        full_path = self._full_path(path)
        try:
            os.chmod(full_path, mode)
            return True
        except OSError as e:
            logging.error(f"无法更改文件 '{path}' 的模式: {e}")
            return False

    def change_owner(self, path: str, uid: int, gid: int) -> bool:
        full_path = self._full_path(path)
        try:
            os.chown(full_path, uid, gid)
            return True
        except OSError as e:
            logging.error(f"无法更改文件 '{path}' 的所有者: {e}")
            return False

    def disk_free(self) -> str:
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"无法获取磁盘使用信息: {e}")
            return ""

    def disk_usage(self, path: str) -> str:
        full_path = self._full_path(path)
        try:
            result = subprocess.run(['du', '-sh', full_path], capture_output=True, text=True, check=True)
            return result.stdout.split('\t')[0]
        except subprocess.CalledProcessError as e:
            logging.error(f"无法获取磁盘使用信息: {e}")
            return ""

    def find_files(self, path: str, pattern: str) -> List[str]:
        full_path = self._full_path(path)
        try:
            result = subprocess.run(['find', full_path, '-name', pattern], capture_output=True, text=True, check=True)
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(f"无法找到文件: {e}")
            return []

    def grep_files(self, pattern: str, files: List[str]) -> List[str]:
        try:
            result = subprocess.run(['grep', '-nH', pattern] + files, capture_output=True, text=True, check=True)
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(f"未找到匹配项: {e}")
            return []

class Console:
    def __init__(self, file_system: FileSystem):
        self.file_system = file_system
        self.current_dir = '/'
        self.commands: Dict[str, Any] = {
            'about': self.about,
            'alias': self.alias,
            'cal': self.cal,
            'cat': self.cat,
            'cd': self.cd,
            'chmod': self.chmod,
            'chown': self.chown,
            'clear': self.clear,
            'cp': self.cp,
            'date': self.date,
            'df': self.df,
            'du': self.du,
            'echo': self.echo,
            'env': self.env,
            'export': self.export,
            'find': self.find,
            'grep': self.grep,
            'head': self.head,
            'help': self.help,
            'history': self.history,
            'kill': self.kill,
            'ln': self.ln,
            'ls': self.ls,
            'man': self.man,
            'mkdir': self.mkdir,
            'mv': self.mv,
            'ps': self.ps,
            'pwd': self.pwd,
            'rm': self.rm,
            'rmdir': self.rmdir,
            'sleep': self.sleep,
            'sort': self.sort,
            'top': self.top,
            'touch': self.touch,
            'uname': self.uname,
            'unalias': self.unalias,
            'uniq': self.uniq,
            'uptime': self.uptime,
            'wc': self.wc,
            'whereis': self.whereis,
            'which': self.which,
            'whoami': self.whoami,
            'tail': self.tail,
            'cut': self.cut,
            'paste': self.paste,
            'tr': self.tr,
            'sed': self.sed,
            'awk': self.awk,
            'printf': self.printf,
            'test': self.test,
            'expr': self.expr,
            'bc': self.bc,
            'time': self.time,
            'watch': self.watch,
            'yes': self.yes,
            'seq': self.seq,
            'shuf': self.shuf,
            'nl': self.nl,
            'fold': self.fold,
            'expand': self.expand,
            'unexpand': self.unexpand,
            'join': self.join,
            'comm': self.comm,
            'diff': self.diff,
            'patch': self.patch,
            'cmp': self.cmp,
            'sum': self.sum,
            'cksum': self.cksum,
            'md5sum': self.md5sum,
            'sha1sum': self.sha1sum,
            'sha256sum': self.sha256sum,
            'factor': self.factor,
            'numfmt': self.numfmt,
            'od': self.od,
            'hexdump': self.hexdump,
            'strings': self.strings,
            'file': self.file,
            'mime': self.mime,
            'stat': self.stat,
            'mktemp': self.mktemp,
            'realpath': self.realpath,
            'dirname': self.dirname,
            'basename': self.basename,
            'pathchk': self.pathchk,
            'readlink': self.readlink,
            'link': self.link,
            'unlink': self.unlink,
            'truncate': self.truncate,
            'split': self.split,
            'csplit': self.csplit,
            'fmt': self.fmt,
            'pr': self.pr,
            'ul': self.ul,
            'col': self.col,
            'colrm': self.colrm,
            'column': self.column,
            'rev': self.rev,
            'tac': self.tac,
            'tsort': self.tsort
        }
        self.setup_autocomplete()
        self.setup_logging()
        self.command_history = []
        self.aliases: Dict[str, str] = {}
        self.environment: Dict[str, str] = {}
        
        # 设置窗口标题
        self.set_window_title("GTOS 1.0")

    def setup_autocomplete(self):
        commands = list(self.commands.keys())
        completer = self.create_completer(commands)
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    def create_completer(self, commands: List[str]):
        def custom_completer(text: str, state: int):
            options = [cmd for cmd in commands if cmd.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None
        return custom_completer

    def setup_logging(self):
        if not os.path.exists('gtos.log'):
            with open('gtos.log', 'w') as f:
                pass
        logging.basicConfig(
            filename='gtos.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.info("GTOS 启动")

    def run(self):
        try:
            self.display_boot_screen()
            os.system('cls' if os.name == 'nt' else 'clear')
            while True:
                try:
                    command = input(f"{self.current_dir}$ ").strip()
                    if command.lower() == 'exit':
                        break
                    self.command_history.append(command)
                    self.execute_command(command)
                except Exception as e:
                    error_message = f"发生错误：{e}"
                    print(error_message)
                    logging.error(error_message, exc_info=True)
        except KeyboardInterrupt:
            print("\n程序已被用户中断。")
            logging.info("程序被用户中断")
        except Exception as e:
            error_message = f"发生未知错误：{e}"
            print(error_message)
            logging.error(error_message, exc_info=True)
        finally:
            logging.info("GTOS 关闭")

    def display_boot_screen(self):
        boot_messages = [
            "Initializing GTOS...",
            "Loading kernel modules...",
            "Starting system services...",
            "Checking file system integrity...",
            "Mounting file systems...",
            "Setting up network interfaces...",
            "Starting user interface...",
            "GTOS 1.0 - Developed by G.E. Studios"
        ]
        
        for message in boot_messages:
            print(message)
            time.sleep(0.5)
        print("\n")

    def execute_command(self, command: str):
        try:
            parts = command.split()
            if not parts:
                return

            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in self.aliases:
                command = self.aliases[cmd] + ' ' + ' '.join(args)
                return self.execute_command(command)

            if cmd in self.commands:
                self.commands[cmd](args)
            else:
                print(f"未找到命令 '{cmd}'")
        except Exception as e:
            error_message = f"执行命令 '{command}' 时发生错误：{e}"
            print(error_message)
            logging.error(error_message, exc_info=True)

    def ls(self, args: List[str]):
        files = self.file_system.list_dir(self.current_dir)
        for file in files:
            print(file)

    def cd(self, args: List[str]):
        if args:
            if self.file_system.change_dir(os.path.join(self.current_dir, args[0])):
                self.current_dir = os.path.join(self.current_dir, args[0])
            else:
                print("未找到目录")
        else:
            print("用法：cd <目录>")

    def mkdir(self, args: List[str]):
        if args:
            if self.file_system.make_dir(os.path.join(self.current_dir, args[0])):
                print(f"目录 '{args[0]}' 已创建")
            else:
                print(f"无法创建目录 '{args[0]}'")
        else:
            print("用法：mkdir <目录>")

    def rm(self, args: List[str]):
        if args:
            if self.file_system.remove_file(os.path.join(self.current_dir, args[0])):
                print(f"文件 '{args[0]}' 已删除")
            else:
                print(f"文件 '{args[0]}' 未找到或无法删除")
        else:
            print("用法：rm <文件>")

    def cp(self, args: List[str]):
        if len(args) == 2:
            if self.file_system.copy_file(os.path.join(self.current_dir, args[0]), os.path.join(self.current_dir, args[1])):
                print(f"文件 '{args[0]}' 已复制到 '{args[1]}'")
            else:
                print(f"无法将文件 '{args[0]}' 复制到 '{args[1]}'")
        else:
            print("用法：cp <源文件> <目标文件>")

    def mv(self, args: List[str]):
        if len(args) == 2:
            if self.file_system.move_file(os.path.join(self.current_dir, args[0]), os.path.join(self.current_dir, args[1])):
                print(f"文件 '{args[0]}' 已移动到 '{args[1]}'")
            else:
                print(f"无法将文件 '{args[0]}' 移动到 '{args[1]}'")
        else:
            print("用法：mv <源文件> <目标文件>")

    def touch(self, args: List[str]):
        if args:
            if self.file_system.create_file(os.path.join(self.current_dir, args[0])):
                print(f"文件 '{args[0]}' 已创建")
            else:
                print(f"无法创建文件 '{args[0]}'")
        else:
            print("用法：touch <文件>")

    def cat(self, args: List[str]):
        if args:
            content = self.file_system.read_file(os.path.join(self.current_dir, args[0]))
            if content:
                print(content)
            else:
                print(f"文件 '{args[0]}' 未找到或无法读取")
        else:
            print("用法：cat <文件>")

    def echo(self, args: List[str]):
        if args:
            content = ' '.join(args)
            if self.file_system.write_file(os.path.join(self.current_dir, 'output.txt'), content):
                print(f"内容已写入 'output.txt'")
            else:
                print("无法写入文件")
        else:
            print("用法：echo <内容>")

    def pwd(self, args: List[str]):
        print(self.current_dir)

    def rmdir(self, args: List[str]):
        if args:
            if self.file_system.remove_dir(os.path.join(self.current_dir, args[0])):
                print(f"目录 '{args[0]}' 已删除")
            else:
                print(f"无法删除目录 '{args[0]}'")
        else:
            print("用法：rmdir <目录>")

    def ln(self, args: List[str]):
        if len(args) == 2:
            if self.file_system.create_symlink(os.path.join(self.current_dir, args[0]), os.path.join(self.current_dir, args[1])):
                print(f"符号链接 '{args[1]}' 已创建，指向 '{args[0]}'")
            else:
                print(f"无法创建符号链接 '{args[1]}'")
        else:
            print("用法：ln <目标> <链接名>")

    def chmod(self, args: List[str]):
        if len(args) == 2:
            try:
                mode = int(args[0], 8)
                if self.file_system.change_mode(os.path.join(self.current_dir, args[1]), mode):
                    print(f"文件 '{args[1]}' 的模式已更改为 {oct(mode)}")
                else:
                    print(f"无法更改文件 '{args[1]}' 的模式")
            except ValueError:
                print("无效的模式。请使用八进制表示法（例如，755）")
        else:
            print("用法：chmod <模式> <文件>")

    def chown(self, args: List[str]):
        if len(args) == 3:
            try:
                uid = int(args[0])
                gid = int(args[1])
                if self.file_system.change_owner(os.path.join(self.current_dir, args[2]), uid, gid):
                    print(f"文件 '{args[2]}' 的所有者已更改为 UID {uid}，GID {gid}")
                else:
                    print(f"无法更改文件 '{args[2]}' 的所有者")
            except ValueError:
                print("无效的 UID 或 GID。请使用数字值")
        else:
            print("用法：chown <uid> <gid> <文件>")

    def df(self, args: List[str]):
        print(self.file_system.disk_free())

    def du(self, args: List[str]):
        if args:
            print(self.file_system.disk_usage(os.path.join(self.current_dir, args[0])))
        else:
            print("用法：du <路径>")

    def find(self, args: List[str]):
        if len(args) == 2:
            results = self.file_system.find_files(self.current_dir, args[1])
            for result in results:
                print(result)
        else:
            print("用法：find <路径> <模式>")

    def grep(self, args: List[str]):
        if len(args) >= 2:
            files = [os.path.join(self.current_dir, f) for f in args[1:]]
            results = self.file_system.grep_files(args[0], files)
            for result in results:
                print(result)
        else:
            print("用法：grep <模式> <文件1> [<文件2> ...]")

    def date(self, args: List[str]):
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def whoami(self, args: List[str]):
        print(os.getlogin())

    def help(self, args: List[str]):
        help_text = {
            'about': "显示关于GTOS的信息",
            'alias': "创建命令别名",
            'awk': "模式扫描和处理语言",
            'basename': "返回文件路径的基本名称",
            'bc': "基本计算器语言",
            'cal': "显示日历",
            'cat': "显示文件内容",
            'cd': "更改当前工作目录",
            'chmod': "更改文件模式",
            'chown': "更改文件所有者",
            'cksum': "计算文件的校验和",
            'clear': "清除屏幕上的输出",
            'cmp': "比较文件的字节",
            'col': "过滤控制字符",
            'colrm': "删除列",
            'column': "格式化表格输出",
            'comm': "比较两个排序文件",
            'cp': "复制文件",
            'csplit': "根据模式分割文件",
            'cut': "从文件中提取指定列",
            'date': "显示或设置系统日期和时间",
            'df': "显示磁盘空间使用情况",
            'diff': "比较文件差异",
            'dirname': "返回文件路径的目录部分",
            'du': "显示目录或文件的磁盘使用情况",
            'echo': "输出文本到标准输出",
            'env': "显示环境变量",
            'expand': "将制表符转换为空格",
            'expr': "计算表达式",
            'factor': "分解数字",
            'file': "确定文件类型",
            'find': "在文件系统中查找文件",
            'fmt': "简单文本格式化",
            'fold': "限制行宽度",
            'grep': "在文件中搜索文本模式",
            'head': "显示文件的前几行",
            'hexdump': "以十六进制格式转储文件内容",
            'history': "显示命令历史记录",
            'join': "根据指定字段连接文件",
            'kill': "模拟终止进程",
            'link': "创建硬链接",
            'ln': "创建符号链接",
            'ls': "列出当前目录中的文件",
            'man': "显示命令手册",
            'md5sum': "计算文件的MD5校验和",
            'mime': "确定文件的MIME类型",
            'mkdir': "创建一个新目录",
            'mktemp': "创建临时文件或目录",
            'mv': "移动或重命名文件",
            'nl': "为文件添加行号",
            'numfmt': "格式化数字",
            'od': "转储文件内容",
            'paste': "合并文件",
            'patch': "应用补丁文件",
            'pathchk': "检查文件名是否有效",
            'pr': "格式化并打印文本文件",
            'printf': "格式化输出文本",
            'ps': "模拟显示当前运行的进程",
            'pwd': "显示当前工作目录",
            'readlink': "读取符号链接的内容",
            'realpath': "返回文件的绝对路径",
            'rev': "反转行",
            'rm': "删除一个文件",
            'rmdir': "删除一个空目录",
            'sed': "流编辑器",
            'seq': "生成序列",
            'sha1sum': "计算文件的SHA1校验和",
            'sha256sum': "计算文件的SHA256校验和",
            'shuf': "随机排列行",
            'sleep': "暂停执行一段时间",
            'sort': "对文件内容进行排序",
            'split': "分割文件",
            'stat': "显示文件或文件系统状态",
            'strings': "从文件中提取可打印字符串",
            'sum': "计算文件的校验和",
            'tac': "反向显示文件内容",
            'tail': "显示文件的最后几行",
            'test': "测试文件或字符串",
            'time': "测量命令执行时间",
            'top': "模拟显示系统资源使用情况",
            'touch': "创建空文件或更新文件时间",
            'tr': "转换或删除字符",
            'truncate': "截断文件或扩展文件",
            'tsort': "拓扑排序",
            'ul': "下划线文本",
            'unalias': "删除命令别名",
            'uname': "显示系统信息",
            'unexpand': "将空格转换为制表符",
            'uniq': "去除文件中的重复行",
            'unlink': "删除文件",
            'uptime': "显示系统运行时间",
            'watch': "周期性执行命令并显示输出",
            'wc': "统计文件的行数、单词数和字符数",
            'whereis': "查找命令的二进制文件、源代码和手册页的路径",
            'which': "查找命令的路径",
            'whoami': "显示当前用户的登录名",
            'yes': "输出字符串直到被中断"
        }
        if args:
            command = args[0].lower()
            if command in help_text:
                print(f"{command}: {help_text[command]}")
            else:
                print(f"未找到命令 '{command}' 的帮助信息")
        else:
            print("可用命令：")
            for cmd in sorted(help_text.keys()):
                print(f"  {cmd}: {help_text[cmd]}")

    def about(self, args: List[str]):
        print("GTOS 版本信息：1.0")
        print("开发者：G.E. Studios")

    def history(self, args: List[str]):
        if args:
            try:
                num = int(args[0])
                for i, cmd in enumerate(self.command_history[-num:], start=len(self.command_history) - num + 1):
                    print(f"{i}: {cmd}")
            except ValueError:
                print("用法：history [数量]")
        else:
            for i, cmd in enumerate(self.command_history, start=1):
                print(f"{i}: {cmd}")

    def clear(self, args: List[str]):
        os.system('cls' if os.name == 'nt' else 'clear')

    def man(self, args: List[str]):
        man_pages = {
            'about': "显示关于GTOS的信息。用法：about",
            'alias': "创建命令别名。用法：alias <别名> <命令>",
            'awk': "模式扫描和处理语言。用法：awk '<脚本>' <文件>",
            'basename': "返回文件路径的基本名称。用法：basename <文件>",
            'bc': "基本计算器语言。用法：bc <表达式>",
            'cal': "显示日历。用法：cal [年份]",
            'cat': "显示文件内容。用法：cat <文件>",
            'cd': "更改当前工作目录。用法：cd <目录>",
            'chmod': "更改文件模式。用法：chmod <模式> <文件>",
            'chown': "更改文件所有者。用法：chown <uid> <gid> <文件>",
            'cksum': "计算文件的校验和。用法：cksum <文件>",
            'clear': "清除屏幕上的输出。用法：clear",
            'cmp': "比较文件的字节。用法：cmp <文件1> <文件2>",
            'col': "过滤控制字符。用法：col <文件>",
            'colrm': "删除列。用法：colrm <文件> <开始列> <结束列>",
            'column': "格式化表格输出。用法：column <文件>",
            'comm': "比较两个排序文件。用法：comm <文件1> <文件2>",
            'cp': "复制文件。用法：cp <源文件> <目标文件>",
            'csplit': "根据模式分割文件。用法：csplit <文件> <模式> <前缀>",
            'cut': "从文件中提取指定列。用法：cut -f <字段号> <文件>",
            'date': "显示或设置系统日期和时间。用法：date",
            'df': "显示磁盘空间使用情况。用法：df",
            'diff': "比较文件差异。用法：diff <文件1> <文件2>",
            'dirname': "返回文件路径的目录部分。用法：dirname <文件>",
            'du': "显示目录或文件的磁盘使用情况。用法：du <路径>",
            'echo': "输出文本到标准输出。用法：echo <内容>",
            'env': "显示环境变量。用法：env",
            'expand': "将制表符转换为空格。用法：expand <文件>",
            'expr': "计算表达式。用法：expr <表达式>",
            'factor': "分解数字。用法：factor <数字>",
            'file': "确定文件类型。用法：file <文件>",
            'find': "在文件系统中查找文件。用法：find <路径> <模式>",
            'fmt': "简单文本格式化。用法：fmt <文件>",
            'fold': "限制行宽度。用法：fold <文件> <宽度>",
            'grep': "在文件中搜索文本模式。用法：grep <模式> <文件1> [<文件2> ...]",
            'head': "显示文件的前几行。用法：head <文件>",
            'hexdump': "以十六进制格式转储文件内容。用法：hexdump <文件>",
            'history': "显示命令历史记录。用法：history [数量]",
            'join': "根据指定字段连接文件。用法：join <文件1> <文件2> <字段号>",
            'kill': "模拟终止进程。用法：kill <进程ID>",
            'link': "创建硬链接。用法：link <源文件> <目标文件>",
            'ln': "创建符号链接。用法：ln <目标> <链接名>",
            'ls': "列出当前目录中的文件。用法：ls",
            'man': "显示命令手册。用法：man <命令>",
            'md5sum': "计算文件的MD5校验和。用法：md5sum <文件>",
            'mime': "确定文件的MIME类型。用法：mime <文件>",
            'mkdir': "创建一个新目录。用法：mkdir <目录>",
            'mktemp': "创建临时文件或目录。用法：mktemp <模板>",
            'mv': "移动或重命名文件。用法：mv <源文件> <目标文件>",
            'nl': "为文件添加行号。用法：nl <文件>",
            'numfmt': "格式化数字。用法：numfmt <格式字符串> <数字>",
            'od': "转储文件内容。用法：od <文件>",
            'paste': "合并文件。用法：paste <文件1> [<文件2> ...]",
            'patch': "应用补丁文件。用法：patch <文件> <补丁文件>",
            'pathchk': "检查文件名是否有效。用法：pathchk <文件>",
            'pr': "格式化并打印文本文件。用法：pr <文件>",
            'printf': "格式化输出文本。用法：printf <格式字符串> [值1] [值2] ...",
            'ps': "模拟显示当前运行的进程。用法：ps",
            'pwd': "显示当前工作目录。用法：pwd",
            'readlink': "读取符号链接的内容。用法：readlink <符号链接>",
            'realpath': "返回文件的绝对路径。用法：realpath <文件>",
            'rev': "反转行。用法：rev <文件>",
            'rm': "删除一个文件。用法：rm <文件>",
            'rmdir': "删除一个空目录。用法：rmdir <目录>",
            'sed': "流编辑器。用法：sed <模式> <替换> <文件>",
            'seq': "生成序列。用法：seq <结束值> 或 seq <开始值> <结束值> 或 seq <开始值> <增量> <结束值>",
            'sha1sum': "计算文件的SHA1校验和。用法：sha1sum <文件>",
            'sha256sum': "计算文件的SHA256校验和。用法：sha256sum <文件>",
            'shuf': "随机排列行。用法：shuf <文件>",
            'sleep': "暂停执行一段时间。用法：sleep <秒数>",
            'sort': "对文件内容进行排序。用法：sort <文件>",
            'split': "分割文件。用法：split <文件> <前缀>",
            'stat': "显示文件或文件系统状态。用法：stat <文件>",
            'strings': "从文件中提取可打印字符串。用法：strings <文件>",
            'sum': "计算文件的校验和。用法：sum <文件>",
            'tac': "反向显示文件内容。用法：tac <文件>",
            'tail': "显示文件的最后几行。用法：tail <文件>",
            'test': "测试文件或字符串。用法：test <操作数1> <操作符> <操作数2>",
            'time': "测量命令执行时间。用法：time <命令>",
            'top': "模拟显示系统资源使用情况。用法：top",
            'touch': "创建空文件或更新文件时间。用法：touch <文件>",
            'tr': "转换或删除字符。用法：tr <集合1> <集合2> <文件>",
            'truncate': "截断文件或扩展文件。用法：truncate <文件> <大小>",
            'tsort': "拓扑排序。用法：tsort <文件>",
            'ul': "下划线文本。用法：ul <文件>",
            'unalias': "删除命令别名。用法：unalias <别名>",
            'uname': "显示系统信息。用法：uname",
            'unexpand': "将空格转换为制表符。用法：unexpand <文件>",
            'uniq': "去除文件中的重复行。用法：uniq <文件>",
            'unlink': "删除文件。用法：unlink <文件>",
            'uptime': "显示系统运行时间。用法：uptime",
            'watch': "周期性执行命令并显示输出。用法：watch <命令>",
            'wc': "统计文件的行数、单词数和字符数。用法：wc <文件>",
            'whereis': "查找命令的二进制文件、源代码和手册页的路径。用法：whereis <命令>",
            'which': "查找命令的路径。用法：which <命令>",
            'whoami': "显示当前用户的登录名。用法：whoami",
            'yes': "输出字符串直到被中断。用法：yes <字符串>"
        }
        if args:
            command = args[0].lower()
            if command in man_pages:
                print(man_pages[command])
            else:
                print(f"未找到命令 '{command}' 的手册")
        else:
            print("用法：man <命令>")

    def alias(self, args: List[str]):
        if len(args) == 2:
            self.aliases[args[0]] = args[1]
            print(f"别名 '{args[0]}' 已设置为 '{args[1]}'")
        else:
            print("用法：alias <别名> <命令>")

    def unalias(self, args: List[str]):
        if args:
            if args[0] in self.aliases:
                del self.aliases[args[0]]
                print(f"别名 '{args[0]}' 已删除")
            else:
                print(f"未找到别名 '{args[0]}'")
        else:
            print("用法：unalias <别名>")

    def export(self, args: List[str]):
        if len(args) == 2:
            self.environment[args[0]] = args[1]
            print(f"环境变量 '{args[0]}' 已设置为 '{args[1]}'")
        else:
            print("用法：export <变量名> <值>")

    def env(self, args: List[str]):
        for key, value in self.environment.items():
            print(f"{key}={value}")

    def kill(self, args: List[str]):
        if args:
            try:
                pid = int(args[0])
                print(f"模拟终止进程 {pid}")
            except ValueError:
                print("用法：kill <进程ID>")
        else:
            print("用法：kill <进程ID>")

    def ps(self, args: List[str]):
        processes = [
            {"pid": 1, "name": "systemd", "status": "running"},
            {"pid": 2, "name": "kernel", "status": "running"},
            {"pid": 3, "name": "GTOS", "status": "running"}
        ]
        for process in processes:
            print(f"PID: {process['pid']}, Name: {process['name']}, Status: {process['status']}")

    def top(self, args: List[str]):
        print("模拟系统资源使用情况：")
        print(f"CPU使用率: {random.randint(1, 100)}%")
        print(f"内存使用率: {random.randint(1, 100)}%")
        print(f"磁盘使用率: {random.randint(1, 100)}%")

    def which(self, args: List[str]):
        if args:
            command = args[0]
            if command in self.commands:
                print(f"/usr/bin/{command}")
            else:
                print(f"未找到命令 '{command}'")
        else:
            print("用法：which <命令>")

    def whereis(self, args: List[str]):
        if args:
            command = args[0]
            if command in self.commands:
                print(f"{command}: /usr/bin/{command} /usr/src/{command} /usr/share/man/man1/{command}.1")
            else:
                print(f"未找到命令 '{command}'")
        else:
            print("用法：whereis <命令>")

    def cal(self, args: List[str]):
        if args:
            try:
                year = int(args[0])
                print(calendar.calendar(year))
            except ValueError:
                print("用法：cal [年份]")
        else:
            now = datetime.datetime.now()
            print(calendar.month(now.year, now.month))

    def sleep(self, args: List[str]):
        if args:
            try:
                seconds = float(args[0])
                time.sleep(seconds)
            except ValueError:
                print("用法：sleep <秒数>")
        else:
            print("用法：sleep <秒数>")

    def uname(self, args: List[str]):
        print("GTOS 1.0")

    def uptime(self, args: List[str]):
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(1000, 36000))
        uptime = datetime.datetime.now() - start_time
        print(f"系统已运行 {uptime.days} 天 {uptime.seconds // 3600} 小时 {uptime.seconds // 60 % 60} 分钟")

    def wc(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    lines = content.count('\n') + 1 if content else 0
                    words = len(content.split())
                    chars = len(content)
                    print(f"{lines} {words} {chars} {args[0]}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：wc <文件>")

    def sort(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = sorted(f.readlines())
                for line in lines:
                    print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：sort <文件>")

    def uniq(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                unique_lines = []
                for line in lines:
                    if line not in unique_lines:
                        unique_lines.append(line)
                        print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：uniq <文件>")

    def head(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                for line in lines[:10]:
                    print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：head <文件>")

    def tail(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                for line in lines[-10:]:
                    print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：tail <文件>")

    def cut(self, args: List[str]):
        if len(args) >= 2:
            file_path = os.path.join(self.current_dir, args[-1])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        fields = line.strip().split()
                        if args[0] == '-f':
                            field_index = int(args[1]) - 1
                            if field_index < len(fields):
                                print(fields[field_index])
                        else:
                            print("用法：cut -f <字段号> <文件>")
            except OSError as e:
                print(f"无法读取文件 '{args[-1]}': {e}")
        else:
            print("用法：cut -f <字段号> <文件>")

    def paste(self, args: List[str]):
        if args:
            files = [os.path.join(self.current_dir, f) for f in args]
            try:
                lines = [[] for _ in range(len(files))]
                for i, file_path in enumerate(files):
                    with open(file_path, 'r') as f:
                        lines[i] = f.readlines()
                max_lines = max(len(line_list) for line_list in lines)
                for i in range(max_lines):
                    row = []
                    for j, line_list in enumerate(lines):
                        if i < len(line_list):
                            row.append(line_list[i].strip())
                        else:
                            row.append('')
                    print('\t'.join(row))
            except OSError as e:
                print(f"无法读取文件：{e}")
        else:
            print("用法：paste <文件1> [<文件2> ...]")

    def tr(self, args: List[str]):
        if len(args) == 3:
            set1, set2, file_path = args
            try:
                with open(os.path.join(self.current_dir, file_path), 'r') as f:
                    content = f.read()
                trans_table = str.maketrans(set1, set2)
                print(content.translate(trans_table))
            except OSError as e:
                print(f"无法读取文件 '{file_path}': {e}")
        else:
            print("用法：tr <集合1> <集合2> <文件>")

    def sed(self, args: List[str]):
        if len(args) == 3:
            pattern, replacement, file_path = args
            try:
                with open(os.path.join(self.current_dir, file_path), 'r') as f:
                    content = f.read()
                new_content = content.replace(pattern, replacement)
                print(new_content)
            except OSError as e:
                print(f"无法读取文件 '{file_path}': {e}")
        else:
            print("用法：sed <模式> <替换> <文件>")

    def awk(self, args: List[str]):
        if len(args) >= 2:
            script, file_path = args[0], os.path.join(self.current_dir, args[1])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        fields = line.strip().split()
                        if eval(script):
                            print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[1]}': {e}")
            except Exception as e:
                print(f"AWK 脚本执行错误：{e}")
        else:
            print("用法：awk '<脚本>' <文件>")

    def printf(self, args: List[str]):
        if args:
            format_string = args[0]
            values = args[1:]
            try:
                print(format_string % tuple(values))
            except Exception as e:
                print(f"格式化错误：{e}")
        else:
            print("用法：printf <格式字符串> [值1] [值2] ...")

    def test(self, args: List[str]):
        if len(args) == 3:
            op1, operator, op2 = args
            if operator == '-eq':
                print(int(op1) == int(op2))
            elif operator == '-ne':
                print(int(op1) != int(op2))
            elif operator == '-lt':
                print(int(op1) < int(op2))
            elif operator == '-le':
                print(int(op1) <= int(op2))
            elif operator == '-gt':
                print(int(op1) > int(op2))
            elif operator == '-ge':
                print(int(op1) >= int(op2))
            else:
                print("未支持的操作符")
        else:
            print("用法：test <操作数1> <操作符> <操作数2>")

    def expr(self, args: List[str]):
        if args:
            try:
                result = eval(' '.join(args))
                print(result)
            except Exception as e:
                print(f"表达式计算错误：{e}")
        else:
            print("用法：expr <表达式>")

    def bc(self, args: List[str]):
        if args:
            try:
                result = eval(' '.join(args))
                print(result)
            except Exception as e:
                print(f"计算错误：{e}")
        else:
            print("用法：bc <表达式>")

    def time(self, args: List[str]):
        if args:
            start_time = time.time()
            try:
                subprocess.run(args, check=True)
            except subprocess.CalledProcessError as e:
                print(f"命令执行错误：{e}")
            end_time = time.time()
            print(f"执行时间：{end_time - start_time:.2f} 秒")
        else:
            print("用法：time <命令>")

    def watch(self, args: List[str]):
        if args:
            try:
                while True:
                    subprocess.run(args, check=True)
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\nwatch 已被用户中断。")
            except subprocess.CalledProcessError as e:
                print(f"命令执行错误：{e}")
        else:
            print("用法：watch <命令>")

    def yes(self, args: List[str]):
        if args:
            while True:
                try:
                    print(args[0])
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nyes 已被用户中断。")
                    break
        else:
            print("用法：yes <字符串>")

    def seq(self, args: List[str]):
        if len(args) == 1:
            try:
                end = int(args[0])
                for i in range(1, end + 1):
                    print(i)
            except ValueError:
                print("用法：seq <结束值>")
        elif len(args) == 2:
            try:
                start, end = int(args[0]), int(args[1])
                for i in range(start, end + 1):
                    print(i)
            except ValueError:
                print("用法：seq <开始值> <结束值>")
        elif len(args) == 3:
            try:
                start, increment, end = int(args[0]), int(args[1]), int(args[2])
                for i in range(start, end + 1, increment):
                    print(i)
            except ValueError:
                print("用法：seq <开始值> <增量> <结束值>")
        else:
            print("用法：seq <结束值> 或 seq <开始值> <结束值> 或 seq <开始值> <增量> <结束值>")

    def shuf(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                random.shuffle(lines)
                for line in lines:
                    print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：shuf <文件>")

    def nl(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    for i, line in enumerate(f, start=1):
                        print(f"{i}\t{line.strip()}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：nl <文件>")

    def fold(self, args: List[str]):
        if len(args) == 2:
            file_path, width = args[0], int(args[1])
            try:
                with open(os.path.join(self.current_dir, file_path), 'r') as f:
                    for line in f:
                        while line:
                            print(line[:width])
                            line = line[width:]
            except OSError as e:
                print(f"无法读取文件 '{file_path}': {e}")
        else:
            print("用法：fold <文件> <宽度>")

    def expand(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        print(line.expandtabs())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：expand <文件>")

    def unexpand(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        print(line.replace('    ', '\t'))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：unexpand <文件>")

    def join(self, args: List[str]):
        if len(args) == 3:
            file1, file2, field = args[0], args[1], int(args[2])
            file1_path = os.path.join(self.current_dir, file1)
            file2_path = os.path.join(self.current_dir, file2)
            try:
                with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                    lines1 = [line.strip().split() for line in f1]
                    lines2 = [line.strip().split() for line in f2]
                    for line1 in lines1:
                        for line2 in lines2:
                            if line1[field - 1] == line2[field - 1]:
                                print(' '.join(line1 + line2[field:]))
            except OSError as e:
                print(f"无法读取文件：{e}")
        else:
            print("用法：join <文件1> <文件2> <字段号>")

    def comm(self, args: List[str]):
        if len(args) == 2:
            file1, file2 = args[0], args[1]
            file1_path = os.path.join(self.current_dir, file1)
            file2_path = os.path.join(self.current_dir, file2)
            try:
                with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                    lines1 = sorted(set(line.strip() for line in f1))
                    lines2 = sorted(set(line.strip() for line in f2))
                    i, j = 0, 0
                    while i < len(lines1) and j < len(lines2):
                        if lines1[i] < lines2[j]:
                            print(f"< {lines1[i]}")
                            i += 1
                        elif lines1[i] > lines2[j]:
                            print(f"> {lines2[j]}")
                            j += 1
                        else:
                            print(f"  {lines1[i]}")
                            i += 1
                            j += 1
                    while i < len(lines1):
                        print(f"< {lines1[i]}")
                        i += 1
                    while j < len(lines2):
                        print(f"> {lines2[j]}")
                        j += 1
            except OSError as e:
                print(f"无法读取文件：{e}")
        else:
            print("用法：comm <文件1> <文件2>")

    def diff(self, args: List[str]):
        if len(args) == 2:
            file1, file2 = args[0], args[1]
            file1_path = os.path.join(self.current_dir, file1)
            file2_path = os.path.join(self.current_dir, file2)
            try:
                with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                    lines1 = f1.readlines()
                    lines2 = f2.readlines()
                    for i, (line1, line2) in enumerate(zip(lines1, lines2), start=1):
                        if line1 != line2:
                            print(f"{i}c{i}")
                            print(f"< {line1.strip()}")
                            print(f"---")
                            print(f"> {line2.strip()}")
                    if len(lines1) > len(lines2):
                        for i in range(len(lines2) + 1, len(lines1) + 1):
                            print(f"{i}a{i}")
                            print(f"> {lines1[i - 1].strip()}")
                    elif len(lines2) > len(lines1):
                        for i in range(len(lines1) + 1, len(lines2) + 1):
                            print(f"{i}d{i}")
                            print(f"< {lines2[i - 1].strip()}")
            except OSError as e:
                print(f"无法读取文件：{e}")
        else:
            print("用法：diff <文件1> <文件2>")

    def patch(self, args: List[str]):
        if len(args) == 2:
            file_path, patch_path = args[0], args[1]
            file_full_path = os.path.join(self.current_dir, file_path)
            patch_full_path = os.path.join(self.current_dir, patch_path)
            try:
                with open(file_full_path, 'r') as f, open(patch_full_path, 'r') as p:
                    file_content = f.read()
                    patch_content = p.read()
                    new_content = file_content
                    for line in patch_content.splitlines():
                        if line.startswith('@@'):
                            continue
                        elif line.startswith('+'):
                            new_content += line[1:] + '\n'
                        elif line.startswith('-'):
                            new_content = new_content.replace(line[1:] + '\n', '')
                    with open(file_full_path, 'w') as f:
                        f.write(new_content)
                    print(f"已应用补丁到 '{file_path}'")
            except OSError as e:
                print(f"无法读取文件：{e}")
        else:
            print("用法：patch <文件> <补丁文件>")

    def cmp(self, args: List[str]):
        if len(args) == 2:
            file1, file2 = args[0], args[1]
            file1_path = os.path.join(self.current_dir, file1)
            file2_path = os.path.join(self.current_dir, file2)
            try:
                with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
                    byte1 = f1.read(1)
                    byte2 = f2.read(1)
                    i = 0
                    while byte1 and byte2:
                        i += 1
                        if byte1 != byte2:
                            print(f"文件 '{file1}' 和 '{file2}' 在第 {i} 个字节处不同")
                            return
                        byte1 = f1.read(1)
                        byte2 = f2.read(1)
                    if byte1 or byte2:
                        print(f"文件 '{file1}' 和 '{file2}' 长度不同")
                    else:
                        print(f"文件 '{file1}' 和 '{file2}' 相同")
            except OSError as e:
                print(f"无法读取文件：{e}")
        else:
            print("用法：cmp <文件1> <文件2>")

    def sum(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    checksum = 0
                    for byte in f.read():
                        checksum = (checksum + byte) & 0xFFFF
                    print(f"{checksum} {os.path.getsize(file_path)} {args[0]}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：sum <文件>")

    def cksum(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    crc = 0
                    for byte in f.read():
                        crc = (crc << 8) ^ crc32_table[(crc >> 24) ^ byte]
                    crc = crc & 0xFFFFFFFF
                    print(f"{crc} {os.path.getsize(file_path)} {args[0]}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：cksum <文件>")

    def md5sum(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    md5 = hashlib.md5()
                    for chunk in iter(lambda: f.read(4096), b''):
                        md5.update(chunk)
                    print(f"{md5.hexdigest()}  {args[0]}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：md5sum <文件>")

    def sha1sum(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    sha1 = hashlib.sha1()
                    for chunk in iter(lambda: f.read(4096), b''):
                        sha1.update(chunk)
                    print(f"{sha1.hexdigest()}  {args[0]}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：sha1sum <文件>")

    def sha256sum(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    sha256 = hashlib.sha256()
                    for chunk in iter(lambda: f.read(4096), b''):
                        sha256.update(chunk)
                    print(f"{sha256.hexdigest()}  {args[0]}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：sha256sum <文件>")

    def factor(self, args: List[str]):
        if args:
            try:
                number = int(args[0])
                factors = []
                for i in range(1, int(number**0.5) + 1):
                    if number % i == 0:
                        factors.append(i)
                        if i != number // i:
                            factors.append(number // i)
                print(f"{number}: {' '.join(map(str, sorted(factors)))}")
            except ValueError:
                print("用法：factor <数字>")
        else:
            print("用法：factor <数字>")

    def numfmt(self, args: List[str]):
        if len(args) == 2:
            format_string, number = args[0], args[1]
            try:
                print(format_string.format(float(number)))
            except ValueError:
                print("用法：numfmt <格式字符串> <数字>")
        else:
            print("用法：numfmt <格式字符串> <数字>")

    def od(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    for i in range(0, len(data), 16):
                        chunk = data[i:i+16]
                        hex_chunk = ' '.join(f'{byte:02x}' for byte in chunk)
                        ascii_chunk = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
                        print(f'{i:07o}: {hex_chunk:<48} {ascii_chunk}')
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：od <文件>")

    def hexdump(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    for i in range(0, len(data), 16):
                        chunk = data[i:i+16]
                        hex_chunk = ' '.join(f'{byte:02x}' for byte in chunk)
                        ascii_chunk = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
                        print(f'{i:08x}  {hex_chunk:<48}  |{ascii_chunk}|')
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：hexdump <文件>")

    def strings(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    current_string = b''
                    for byte in data:
                        if 32 <= byte <= 126:
                            current_string += bytes([byte])
                        else:
                            if len(current_string) >= 4:
                                print(current_string.decode('ascii', errors='ignore'))
                            current_string = b''
                    if len(current_string) >= 4:
                        print(current_string.decode('ascii', errors='ignore'))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：strings <文件>")

    def file(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'rb') as f:
                    data = f.read(1024)
                    if data.startswith(b'\x7fELF'):
                        print(f"{args[0]}: ELF 可执行文件")
                    elif data.startswith(b'MZ'):
                        print(f"{args[0]}: Windows 可执行文件")
                    elif data.startswith(b'\x89PNG'):
                        print(f"{args[0]}: PNG 图像文件")
                    elif data.startswith(b'\xff\xd8\xff'):
                        print(f"{args[0]}: JPEG 图像文件")
                    elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
                        print(f"{args[0]}: GIF 图像文件")
                    elif data.startswith(b'#!/bin/bash'):
                        print(f"{args[0]}: Bash 脚本")
                    else:
                        print(f"{args[0]}: 未知文件类型")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：file <文件>")

    def mime(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                mime_type = mimetypes.guess_type(file_path)[0]
                if mime_type:
                    print(f"{args[0]}: {mime_type}")
                else:
                    print(f"{args[0]}: 未知 MIME 类型")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：mime <文件>")

    def stat(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                stats = os.stat(file_path)
                print(f"文件: {args[0]}")
                print(f"大小: {stats.st_size} 字节")
                print(f"最后修改时间: {datetime.datetime.fromtimestamp(stats.st_mtime)}")
                print(f"最后访问时间: {datetime.datetime.fromtimestamp(stats.st_atime)}")
                print(f"创建时间: {datetime.datetime.fromtimestamp(stats.st_ctime)}")
                print(f"权限: {oct(stats.st_mode)[-3:]}")
                print(f"所有者: {stats.st_uid}")
                print(f"组: {stats.st_gid}")
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：stat <文件>")

    def mktemp(self, args: List[str]):
        if args:
            template = args[0]
            try:
                temp_file = tempfile.mkstemp(prefix=template)[1]
                print(f"临时文件创建成功: {temp_file}")
            except Exception as e:
                print(f"创建临时文件失败: {e}")
        else:
            print("用法：mktemp <模板>")

    def realpath(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                print(os.path.realpath(file_path))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：realpath <文件>")

    def dirname(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            print(os.path.dirname(file_path))
        else:
            print("用法：dirname <文件>")

    def basename(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            print(os.path.basename(file_path))
        else:
            print("用法：basename <文件>")

    def pathchk(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                os.path.normpath(file_path)
                print(f"文件名 '{args[0]}' 有效")
            except ValueError as e:
                print(f"文件名 '{args[0]}' 无效: {e}")
        else:
            print("用法：pathchk <文件>")

    def readlink(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                print(os.readlink(file_path))
            except OSError as e:
                print(f"无法读取符号链接 '{args[0]}': {e}")
        else:
            print("用法：readlink <符号链接>")

    def link(self, args: List[str]):
        if len(args) == 2:
            src, dst = args[0], args[1]
            src_path = os.path.join(self.current_dir, src)
            dst_path = os.path.join(self.current_dir, dst)
            try:
                os.link(src_path, dst_path)
                print(f"硬链接 '{dst}' 已创建，指向 '{src}'")
            except OSError as e:
                print(f"无法创建硬链接 '{dst}' 指向 '{src}': {e}")
        else:
            print("用法：link <源文件> <目标文件>")

    def unlink(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                os.unlink(file_path)
                print(f"文件 '{args[0]}' 已删除")
            except OSError as e:
                print(f"无法删除文件 '{args[0]}': {e}")
        else:
            print("用法：unlink <文件>")

    def truncate(self, args: List[str]):
        if len(args) == 2:
            file_path, size = args[0], int(args[1])
            file_full_path = os.path.join(self.current_dir, file_path)
            try:
                with open(file_full_path, 'r+') as f:
                    f.truncate(size)
                print(f"文件 '{file_path}' 已截断至 {size} 字节")
            except OSError as e:
                print(f"无法截断文件 '{file_path}': {e}")
        else:
            print("用法：truncate <文件> <大小>")

    def split(self, args: List[str]):
        if len(args) == 2:
            file_path, prefix = args[0], args[1]
            file_full_path = os.path.join(self.current_dir, file_path)
            try:
                with open(file_full_path, 'r') as f:
                    content = f.read()
                chunk_size = 1024  # 1KB
                for i, chunk in enumerate(range(0, len(content), chunk_size)):
                    with open(os.path.join(self.current_dir, f"{prefix}{i:03d}"), 'w') as out:
                        out.write(content[chunk:chunk + chunk_size])
                print(f"文件 '{file_path}' 已分割为 '{prefix}xxx' 文件")
            except OSError as e:
                print(f"无法读取文件 '{file_path}': {e}")
        else:
            print("用法：split <文件> <前缀>")

    def csplit(self, args: List[str]):
        if len(args) == 3:
            file_path, pattern, prefix = args[0], args[1], args[2]
            file_full_path = os.path.join(self.current_dir, file_path)
            try:
                with open(file_full_path, 'r') as f:
                    content = f.read()
                parts = content.split(pattern)
                for i, part in enumerate(parts):
                    with open(os.path.join(self.current_dir, f"{prefix}{i:03d}"), 'w') as out:
                        out.write(part)
                print(f"文件 '{file_path}' 已根据模式 '{pattern}' 分割为 '{prefix}xxx' 文件")
            except OSError as e:
                print(f"无法读取文件 '{file_path}': {e}")
        else:
            print("用法：csplit <文件> <模式> <前缀>")

    def fmt(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                print(textwrap.fill(content, width=70))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：fmt <文件>")

    def pr(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                print(f"文件: {args[0]}")
                print("-" * 72)
                print(content)
                print("-" * 72)
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：pr <文件>")

    def ul(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        print(line.replace('_', '\033[4m_\033[0m'))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：ul <文件>")

    def col(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        print(line.replace('\t', '    '))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：col <文件>")

    def colrm(self, args: List[str]):
        if len(args) == 3:
            file_path, start, end = args[0], int(args[1]), int(args[2])
            file_full_path = os.path.join(self.current_dir, file_path)
            try:
                with open(file_full_path, 'r') as f:
                    for line in f:
                        print(line[:start - 1] + line[end:])
            except OSError as e:
                print(f"无法读取文件 '{file_path}': {e}")
        else:
            print("用法：colrm <文件> <开始列> <结束列>")

    def column(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = [line.strip().split() for line in f]
                if lines:
                    max_widths = [max(len(row[i]) for row in lines) for i in range(len(lines[0]))]
                    for row in lines:
                        formatted_row = ' '.join(f"{cell:<{max_widths[i]}}" for i, cell in enumerate(row))
                        print(formatted_row)
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：column <文件>")

    def rev(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        print(line.strip()[::-1])
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：rev <文件>")

    def tac(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                for line in reversed(lines):
                    print(line.strip())
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：tac <文件>")

    def tsort(self, args: List[str]):
        if args:
            file_path = os.path.join(self.current_dir, args[0])
            try:
                with open(file_path, 'r') as f:
                    edges = [line.strip().split() for line in f]
                graph = {}
                for u, v in edges:
                    if u not in graph:
                        graph[u] = set()
                    if v not in graph:
                        graph[v] = set()
                    graph[u].add(v)
                result = []
                visited = set()
                def dfs(node):
                    if node in visited:
                        return
                    visited.add(node)
                    for neighbor in graph.get(node, set()):
                        dfs(neighbor)
                    result.append(node)
                for node in graph:
                    dfs(node)
                print(' '.join(reversed(result)))
            except OSError as e:
                print(f"无法读取文件 '{args[0]}': {e}")
        else:
            print("用法：tsort <文件>")

    def set_window_title(self, title: str):
        if os.name == 'nt':  # Windows
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif os.name == 'posix':  # Unix/Linux/Mac
            sys.stdout.write(f"\x1b]2;{title}\x07")
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        root_dir = os.path.abspath('.')
        fs = FileSystem(root_dir)
        console = Console(fs)
        console.run()
    except Exception as e:
        error_message = f"程序启动时发生错误：{e}"
        print(error_message)
        logging.error(error_message)
        traceback.print_exc()
        logging.error(traceback.format_exc()) 