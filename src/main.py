"""
主程序入口模块。

简单的Hello World示例程序。
"""
import os
import winreg


def get_vpn_port():
    """
    检测当前系统 VPN/代理使用的端口。

    支持两种检测方式：
    1. 环境变量 (HTTP_PROXY/HTTPS_PROXY) - 适用于受限环境
    2. Windows 系统代理 (注册表) - 适用于 Clash、V2Ray 等

    Returns:
        int: 代理端口号，如 7890、10808、10809
        None: 未检测到代理设置
    """
    # 方法1: 检测环境变量（优先级更高，因为在受限环境中常用）
    for env_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        proxy_url = os.environ.get(env_var)
        if proxy_url:
            # 格式如 "http://127.0.0.1:10809"
            if ':' in proxy_url:
                try:
                    port = proxy_url.split(':')[-1].rstrip('/')
                    return int(port)
                except ValueError:
                    continue

    # 方法2: 检测 Windows 注册表系统代理设置
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        )

        proxy_enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]

        if proxy_enabled:
            proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
            winreg.CloseKey(key)

            # 提取端口号
            if ':' in proxy_server:
                # 处理多种格式
                # 格式1: "127.0.0.1:7890"
                # 格式2: "http=127.0.0.1:7890;https=127.0.0.1:7890"
                if ';' in proxy_server:
                    proxy_server = proxy_server.split(';')[0]
                if '=' in proxy_server:
                    proxy_server = proxy_server.split('=')[1]

                port = proxy_server.split(':')[-1]
                return int(port)

        winreg.CloseKey(key)
        return None

    except Exception as e:
        print(f"检测代理失败: {e}")
        return None


def main():
    """程序主函数，打印问候语。"""
    print("哈罗 world!")

    # 测试 VPN 端口检测
    port = get_vpn_port()
    if port:
        print(f"检测到 VPN 端口: {port}")
    else:
        print("未检测到 VPN 代理设置")


if __name__ == "__main__":
    main()
