import yt_dlp
import os
import sys
import time
from datetime import datetime
import subprocess
import json



class Yt_Dlp_Update:
    def __init__(self, auto_update=True, check_interval_days=7):
        """
        初始化下载器
        
        Args:
            auto_update: 是否自动更新 yt_dlp
            check_interval_days: 检查更新的间隔天数
        """
        if auto_update:
            self._check_and_update_ytdlp(check_interval_days)
        
        self.proxy_url = None
        self.cookies_file = None
        self.last_update_time = 0
        self.max_retry_attempts = 3
        self.current_retry = 0
    
    def _check_and_update_ytdlp(self, check_interval_days=7):
        """
        检查并自动更新 yt_dlp（带实时进度显示）
        
        Args:
            check_interval_days: 检查更新的间隔天数，避免频繁检查
        """
        update_check_file = ".ytdlp_last_check"
        current_time = time.time()
        
        try:
            # 检查上次更新时间
            if os.path.exists(update_check_file):
                with open(update_check_file, 'r') as f:
                    data = json.load(f)
                    last_check = data.get('last_check', 0)
                    
                # 如果距离上次检查未超过设定天数，跳过检查
                if (current_time - last_check) < (check_interval_days * 86400):
                    print(f"yt_dlp 最近已检查过更新 (版本: {yt_dlp.version.__version__})")
                    return
            
            print("=" * 50)
            print("正在检查 yt_dlp 更新...")
            current_version = yt_dlp.version.__version__
            print(f"当前版本: {current_version}")
            print("=" * 50)
            
            # 使用 Popen 实时显示输出
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--progress-bar", "on"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            # 实时读取并显示输出
            output_lines = []
            for line in process.stdout:
                line = line.rstrip()
                if line:  # 只显示非空行
                    print(line)
                    output_lines.append(line)
            
            # 等待进程结束
            process.wait(timeout=120)
            
            # 保存检查时间
            with open(update_check_file, 'w') as f:
                json.dump({'last_check': current_time}, f)
            
            print("=" * 50)
            
            # 判断更新结果
            full_output = '\n'.join(output_lines)
            
            if process.returncode == 0:
                if "Successfully installed" in full_output:
                    print("✓ yt_dlp 已更新到最新版本")
                    # 提取新版本号
                    for line in output_lines:
                        if "Successfully installed yt-dlp" in line:
                            print(f"  {line.strip()}")
                    print("\n⚠ 建议重启程序以使用新版本")
                elif "Requirement already satisfied" in full_output:
                    print("✓ yt_dlp 已是最新版本，无需更新")
                else:
                    print("✓ 更新检查完成")
            else:
                print(f"⚠ 更新时遇到问题 (返回码: {process.returncode})")
            
            print("=" * 50)
                
        except subprocess.TimeoutExpired:
            print("⚠ 更新检查超时（超过120秒），继续使用当前版本")
            if 'process' in locals():
                process.kill()
        except Exception as e:
            print(f"⚠ 检查更新时出错: {str(e)}")
            import traceback
            traceback.print_exc()            



class YouTubeDownloader:
    def __init__(self):
        self.proxy_url = None
        self.cookies_file = None
        self.last_update_time = 0  # 限制进度刷新频率
        self.max_retry_attempts = 3  # 最大重试次数
        self.current_retry = 0

    def detect_proxy(self):
        """检测系统代理设置（Windows）"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"
            )
            proxy_enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
            if proxy_enabled:
                proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
                if proxy_server:
                    self.proxy_url = f"http://{proxy_server}"
                    print(f"检测到代理设置: {self.proxy_url}")
            winreg.CloseKey(key)
        except Exception as e:
            print(f"代理检测失败: {e}")

    def create_manual_cookies_file(self):
        """创建手动cookies文件模板"""
        current_dir = os.getcwd()
        cookies_file_path = os.path.join(current_dir, "youtube_cookies.txt")

        cookies_content = """# 使用 Get cookies.txt LOCALLY 插件导出cookies：
# 1. 在浏览器中安装 "Get cookies.txt LOCALLY" 插件
# 2. 访问 https://www.youtube.com 并确保已登录
# 3. 点击插件图标，导出cookies
# 4. 将导出的cookies.txt放到此文件位置
# 
# 提示：每当遇到bot检测时，需要重新导出最新的cookies！

# Netscape HTTP Cookie File
# This is a generated file! Do not edit.
"""
        with open(cookies_file_path, "w", encoding="utf-8") as f:
            f.write(cookies_content)

        print(f"已创建cookies模板文件: {cookies_file_path}")
        return cookies_file_path

    def check_cookies_file_age(self):
        """检查cookies文件的修改时间"""
        if not self.cookies_file or not os.path.exists(self.cookies_file):
            return False, "cookies文件不存在"
        
        file_mtime = os.path.getmtime(self.cookies_file)
        current_time = time.time()
        age_minutes = (current_time - file_mtime) / 60
        
        if age_minutes > 5:  # 如果cookies文件超过5分钟没更新
            return False, f"cookies文件已过期 ({age_minutes:.1f}分钟前创建)"
        return True, f"cookies文件较新 ({age_minutes:.1f}分钟前创建)"

    def is_bot_detection_error(self, error):
        """检查是否为bot检测错误"""
        error_str = str(error).lower()
        bot_keywords = [
            "sign in to confirm you're not a bot",
            "confirm you're not a bot",
            "bot",
            "cookies-from-browser",
            "authentication"
        ]
        return any(keyword in error_str for keyword in bot_keywords)

    def prompt_cookie_update(self):
        """提示用户更新cookies"""
        print("\n" + "="*60)
        print("🤖 检测到YouTube Bot验证问题！")
        print("="*60)
        
        # 检查cookies文件状态
        if self.cookies_file:
            is_fresh, status_msg = self.check_cookies_file_age()
            print(f"📁 Cookies状态: {status_msg}")
        
        print("\n📝 请按以下步骤更新cookies:")
        print("1. 打开浏览器，确保已登录YouTube")
        print("2. 使用 'Get cookies.txt LOCALLY' 插件导出cookies")
        print("3. 将新的cookies.txt替换当前文件")
        print(f"4. Cookies文件位置: {self.cookies_file}")
        
        print("\n⏰ 当前时间:", datetime.now().strftime("%H:%M:%S"))
        
        while True:
            choice = input("\n请选择操作:\n[1] 已更新cookies，继续下载\n[2] 跳过此视频\n[3] 退出程序\n请选择 (1/2/3): ").strip()
            
            if choice == "1":
                # 验证cookies文件是否真的被更新了
                if self.cookies_file and os.path.exists(self.cookies_file):
                    is_fresh, status_msg = self.check_cookies_file_age()
                    if is_fresh:
                        print("✅ 检测到cookies已更新，继续下载...")
                        return "continue"
                    else:
                        print(f"⚠️  {status_msg}")
                        print("请确保已用最新的cookies替换文件！")
                        continue
                else:
                    print("❌ 未找到cookies文件！")
                    continue
                    
            elif choice == "2":
                return "skip"
            elif choice == "3":
                return "exit"
            else:
                print("请输入有效选择 (1/2/3)")

    def custom_progress(self, d):
        """自定义进度显示，防止刷屏"""
        if d['status'] == 'downloading':
            now = time.time()
            if now - self.last_update_time >= 0.5:  # 每0.5秒刷新一次
                percent = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                print(f"\r下载进度: {percent} | 速度: {speed} | 剩余时间: {eta}   ",
                      end='', flush=True)
                self.last_update_time = now
        elif d['status'] == 'finished':
            print("\n下载完成，正在合并文件...")

    def get_download_options(self, url, use_cookies=False):
        """下载配置优化"""
        base_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'merge_output_format': 'mp4',
            'retries': 10,
            'fragment_retries': 10,
            'concurrent_fragment_downloads': 10,
            'http_chunk_size': 1024 * 1024 * 10,
            'nopart': True,
            'buffer_size': 1024 * 1024 * 10,
            'progress_hooks': [self.custom_progress],
            'continuedl': True,
            'quiet': False,  # 显示详细信息以便调试
        }

        if self.proxy_url:
            base_opts['proxy'] = self.proxy_url

        if use_cookies and self.cookies_file and os.path.exists(self.cookies_file):
            base_opts['cookiefile'] = self.cookies_file

        base_opts['http_headers'] = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }

        return base_opts

    def try_download_with_cookies(self, url):
        """尝试用cookies下载，带重试机制"""
        cookies_file_path = os.path.join(os.getcwd(), "youtube_cookies.txt")
        
        # 初始化cookies文件
        if not os.path.exists(cookies_file_path):
            self.create_manual_cookies_file()
            print("\n📁 首次运行，请按提示设置cookies...")
            input("请填写 cookies.txt 后按 Enter 继续...")

        self.cookies_file = cookies_file_path
        
        while self.current_retry < self.max_retry_attempts:
            try:
                print(f"\n🎬 开始下载尝试 #{self.current_retry + 1}")
                opts = self.get_download_options(url, True)
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    # 先提取信息
                    info = ydl.extract_info(url, download=False)
                    print(f"\n📺 视频标题: {info.get('title', 'Unknown')}")
                    print(f"⏱️  时长: {info.get('duration_string', 'Unknown')}")
                    
                    # 开始下载
                    ydl.download([url])
                    
                print("\n✅ 下载完成！")
                return True
                
            except Exception as e:
                self.current_retry += 1
                print(f"\n❌ 下载失败 (尝试 {self.current_retry}/{self.max_retry_attempts})")
                
                if self.is_bot_detection_error(e):
                    print("🤖 检测到Bot验证问题")
                    
                    if self.current_retry < self.max_retry_attempts:
                        action = self.prompt_cookie_update()
                        
                        if action == "continue":
                            print("🔄 重新尝试下载...")
                            continue
                        elif action == "skip":
                            print("⏭️  跳过当前视频")
                            return False
                        elif action == "exit":
                            print("👋 程序退出")
                            sys.exit(0)
                    else:
                        print(f"❌ 已达到最大重试次数 ({self.max_retry_attempts})")
                        return False
                else:
                    print(f"❌ 其他错误: {str(e)}")
                    if self.current_retry >= self.max_retry_attempts:
                        print(f"❌ 已达到最大重试次数 ({self.max_retry_attempts})")
                        return False
                    else:
                        print("⏳ 等待3秒后重试...")
                        time.sleep(3)
                        
        return False

    def download_video(self, url):
        """下载主入口"""
        print(f"\n🎯 目标视频: {url}")
        self.detect_proxy()
        
        # 重置重试计数器
        self.current_retry = 0
        
        success = self.try_download_with_cookies(url)
        if not success:
            print("❌ 视频下载失败")
        
        return success


def main():
    print("YouTube视频下载器 v4.0 (智能Cookie重试版)")
    print("=" * 50)

    print("       yt-dlp 检查更新中..........")
    print("-" * 20)
    # 方式3: 自定义检查间隔（每3天检查一次）
    downloader = Yt_Dlp_Update(check_interval_days=1)

    while True:
        url = input("\n请输入YouTube视频URL (输入'q'退出): ").strip()
        
        if url.lower() == 'q':
            print("👋 程序退出")
            break
            
        if not url:
            print("⚠️  未输入URL，请重新输入")
            continue
            
        if "youtube.com" not in url and "youtu.be" not in url:
            print("⚠️  请输入有效的YouTube URL")
            continue

        downloader = YouTubeDownloader()
        success = downloader.download_video(url)
        
        if success:
            print("\n🎉 任务完成！")
        else:
            print("\n😔 任务失败，请检查URL或网络连接")
        
        print("\n" + "="*50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序发生未预期错误: {e}")
        input("按 Enter 键退出...")
