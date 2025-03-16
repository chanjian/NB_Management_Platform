import requests
from django.http import HttpResponse


def get_os_and_browser(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

    # 提取操作系统
    if 'windows' in user_agent:
        os = 'Windows'
    elif 'macintosh' in user_agent or 'mac os' in user_agent:
        os = 'macOS'
    elif 'linux' in user_agent:
        os = 'Linux'
    elif 'android' in user_agent:
        os = 'Android'
    elif 'iphone' in user_agent or 'ipad' in user_agent:
        os = 'iOS'
    else:
        os = 'Unknown'

    # 提取浏览器
    if 'chrome' in user_agent and 'edg' not in user_agent:  # 排除 Microsoft Edge（基于 Chromium）
        browser = 'Chrome'
    elif 'firefox' in user_agent:
        browser = 'Firefox'
    elif 'safari' in user_agent and 'chrome' not in user_agent:  # 排除 Chrome（Safari 的 User-Agent 中也包含 Safari）
        browser = 'Safari'
    elif 'edge' in user_agent:
        browser = 'Edge'
    elif 'opera' in user_agent or 'opr' in user_agent:
        browser = 'Opera'
    elif 'msie' in user_agent or 'trident' in user_agent:  # 兼容旧版 IE
        browser = 'Internet Explorer'
    else:
        browser = 'Unknown'

    return os, browser


from user_agents import parse


def get_device_info(request):
    user_agent_string = request.META.get('HTTP_USER_AGENT', 'Unknown')
    user_agent = parse(user_agent_string)

    device_info = {
        'browser': user_agent.browser.family,  # 浏览器类型
        'browser_version': user_agent.browser.version_string,  # 浏览器版本
        'os': user_agent.os.family,  # 操作系统
        'os_version': user_agent.os.version_string,  # 操作系统版本
        'device': user_agent.device.family,  # 设备类型（如 iPhone, iPad）
        'is_mobile': user_agent.is_mobile,  # 是否是移动设备
        'is_tablet': user_agent.is_tablet,  # 是否是平板设备
        'is_pc': user_agent.is_pc,  # 是否是桌面设备
        'is_bot': user_agent.is_bot,  # 是否是爬虫
    }
    return device_info

def get_client_ip(request):
    # 尝试从 HTTP_X_FORWARDED_FOR 获取 IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # HTTP_X_FORWARDED_FOR 可能包含多个 IP，第一个是用户的真实 IP
        ip = x_forwarded_for.split(',')[0]
    else:
        # 直接从 REMOTE_ADDR 获取 IP
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location_by_ip(ip):
    # 使用 IP-API 获取地理位置信息
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return {
                'country': data.get('country'),
                'region': data.get('regionName'),
                'city': data.get('city'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'isp': data.get('isp'),
            }
    return None

def ip(request):
    # user_ip = get_client_ip(request)
    # print("User IP:", user_ip)
    # os, browser = get_os_and_browser(request)
    # print(os,browser)
    # device_info = get_device_info(request)
    # print("Device Info:", device_info)
    user_ip = get_client_ip(request)
    location = get_location_by_ip(user_ip)

    if location:
        response = f"""
            <h1>User Information</h1>
            <p><strong>IP Address:</strong> {user_ip}</p>
            <p><strong>Country:</strong> {location['country']}</p>
            <p><strong>Region:</strong> {location['region']}</p>
            <p><strong>City:</strong> {location['city']}</p>
            <p><strong>Latitude:</strong> {location['latitude']}</p>
            <p><strong>Longitude:</strong> {location['longitude']}</p>
            <p><strong>ISP:</strong> {location['isp']}</p>
            """
    else:
        response = "Unable to determine location."

    return HttpResponse(response)