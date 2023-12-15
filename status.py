import os
import time
import psutil
import platform
import botpy
from botpy import logging, BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message
from botpy.ext.cog_yaml import read
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

# 管理员身分组
admin_users_roles_id = ["2", "4", "5", "7"]



# python运行时间
start_time = time.time()


@Commands("服务器状态")
async def server_status(api: BotAPI, message: Message, params=None):
    if not (message.content.startswith("服务器状态") or message.content.startswith("<@!")):
        return True
    uid = message.author.id
    gid = message.guild_id
    # 获取用户身分组
    user_infor_data = await api.get_guild_member(guild_id=gid, user_id=uid)
    # 判断是否是管理员
    roles_data = user_infor_data["roles"]
    count = 0
    for i in admin_users_roles_id:
        if i in roles_data:
            count = count + 1
    if count == 0:
        return True
    _log.info(params)
    # 打印机器人信息
    user = await api.me()
    print(user)

    # 图片 API URL
    url = 'https://api.suyanw.cn/api/sjmv.php'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
    }

    response = requests.get(url, headers=headers, allow_redirects=True)

    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        try:
            network_img = Image.open(BytesIO(response.content))
        except IOError:
            print("无法打开图像")
    else:
        print(f"请求失败，状态码：{response.status_code}")

    # 对网络图片进行高斯模糊处理
    network_img = network_img.filter(ImageFilter.GaussianBlur(15))

    # 调整网络图片的大小（宽度600，高度自适应）
    base_width = 600
    w_percent = (base_width / float(network_img.size[0]))
    h_size = int((float(network_img.size[1]) * float(w_percent)))
    network_img = network_img.resize((base_width, h_size), Image.Resampling.LANCZOS)

    # 如果高度超过500，则裁剪图片
    if h_size > 490:
        # 裁剪图片以适应 600x490 的尺寸
        network_img = network_img.crop((0, 0, base_width, 490))

    # 创建图像
    # img = Image.new('RGB', (600, max(450, h_size)), color=(152, 251, 152))
    img = Image.new('RGB', (600, 490), color=(152, 251, 152))

    # 将网络图片绘制到创建的图像上
    img.paste(network_img, (0, 0))

    d = ImageDraw.Draw(img)

    # 设置字体
    font = ImageFont.truetype("font/font.ttf", 15)

    # 获取系统信息
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk_partitions = psutil.disk_partitions()
    net_io_start = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    net_io_end = psutil.net_io_counters(pernic=True)
    cpu_cores = psutil.cpu_count(logical=False)  # 物理核心数
    cpu_threads = psutil.cpu_count()  # 总线程数
    system_info = f"{platform.architecture()[0]}, {platform.platform()}"
    current_time = f" {time.strftime('%Y-%m-%d %H:%M:%S')}"
    python_version = f"{platform.python_version()}"
    python_runtime = format_time(time.time() - start_time)
    system_uptime = format_time(time.time() - psutil.boot_time())

    # 设置每行文字的高度
    line_height = 20

    # 计算从底部开始绘制文字的初始位置
    bottom = img.height - line_height

    orange_color = (255, 165, 0)  # 橘色
    black_color = (0, 0, 0)       # 黑色

    # 绘制系统信息
    fixed_text = "系统信息: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), system_info, font=font, fill=orange_color)
    bottom -= line_height

    # 绘制系统开机时间
    fixed_text = "系统开机时间: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), system_uptime, font=font, fill=orange_color)
    bottom -= line_height

    # 绘制 Python 运行时间
    fixed_text = "Bot在线时间: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), python_runtime, font=font, fill=orange_color)
    bottom -= line_height

    # 绘制当前时间
    fixed_text = "当前时间: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), current_time, font=font, fill=orange_color)
    bottom -= line_height

    # 绘制 Python 版本
    fixed_text = "Python 版本: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), python_version, font=font, fill=orange_color)
    bottom -= line_height

    # 绘制网络速度
    for nic in reversed(net_io_start):
        sent_speed = (net_io_end[nic].bytes_sent - net_io_start[nic].bytes_sent) / 1024
        recv_speed = (net_io_end[nic].bytes_recv - net_io_start[nic].bytes_recv) / 1024
        bottom -= line_height

        # 绘制网络接口名称（橘色）
        nic_text = f"{nic}"
        d.text((10, bottom), nic_text, font=font, fill=orange_color)
        text_width = d.textlength(nic_text, font=font)

        # 绘制“: 发送 ”（黑色）
        send_text = ": 发送 "
        d.text((10 + text_width, bottom), send_text, font=font, fill=black_color)
        text_width += d.textlength(send_text, font=font)

        # 绘制发送速度（橘色）
        sent_speed_text = f"{sent_speed:.2f} KB/s, "
        d.text((10 + text_width, bottom), sent_speed_text, font=font, fill=orange_color)
        text_width += d.textlength(sent_speed_text, font=font)

        # 绘制“接收 ”（黑色）
        recv_text = "接收 "
        d.text((10 + text_width, bottom), recv_text, font=font, fill=black_color)
        text_width += d.textlength(recv_text, font=font)

        # 绘制接收速度（橘色）
        recv_speed_text = f"{recv_speed:.2f} KB/s"
        d.text((10 + text_width, bottom), recv_speed_text, font=font, fill=orange_color)

    bottom -= line_height

    # 绘制磁盘分区信息
    for dp in reversed(disk_partitions):
        disk_usage = psutil.disk_usage(dp.mountpoint)
        bottom -= line_height
        # 绘制“分区：”和设备名称
        fixed_text = "分区："
        text_width = d.textlength(fixed_text, font=font)
        d.text((10, bottom), fixed_text, font=font, fill=black_color)
        device_text = f"{dp.device}"
        d.text((10 + text_width, bottom), device_text, font=font, fill=orange_color)
        text_width += d.textlength(device_text, font=font)
        # 绘制“ - ”分隔符
        separator_text = " - "
        d.text((10 + text_width, bottom), separator_text, font=font, fill=black_color)
        text_width += d.textlength(separator_text, font=font)
        # 绘制磁盘使用信息
        usage_text = f"{disk_usage.percent}% ({disk_usage.total / (1024**3):.2f}G)"
        d.text((10 + text_width, bottom), usage_text, font=font, fill=orange_color)

    bottom -= line_height

    # 绘制 CPU 和内存信息
    bottom -= line_height
    fixed_text = "内存使用率: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), f"{memory.percent}% (总计 {memory.total / (1024**3):.2f} GB)", font=font, fill=orange_color)
    bottom -= line_height
    fixed_text = "CPU 使用率: "
    text_width = d.textlength(fixed_text, font=font)
    d.text((10, bottom), fixed_text, font=font, fill=black_color)
    d.text((10 + text_width, bottom), f"{cpu_usage}% ({cpu_cores}核心, {cpu_threads}线程)", font=font, fill=orange_color)


    # 保存图像
    img.save('system_status.png')

    await message.reply(file_image="system_status.png")

@Commands("重启")
async def restart(api, message, params=None):
    if not (message.content.startswith("重启") or message.content.startswith("<@!")):
        return True
    uid = message.author.id
    gid = message.guild_id
    # 获取用户身分组
    user_infor_data = await api.get_guild_member(guild_id=gid, user_id=uid)
    # 判断是否是管理员
    roles_data = user_infor_data["roles"]
    count = 0
    for i in admin_users_roles_id:
        if i in roles_data:
            count = count + 1
    if count == 0:
        return True
    # 发送重启确认消息
    await message.reply(content="正在重启...")
    # 使用绝对路径重启脚本
    python_path = "/usr/bin/python3"  # 修改为您的 Python 解释器的绝对路径
    script_path = "状态.py"  # 修改为您的脚本的绝对路径
    os.execv(python_path, [python_path, script_path])




class MyClient(botpy.Client):
    async def handle_message(self, message: Message):
        # 获取机器人信息
        # user = await self.api.me()
        # print(user)
        # 注册指令handler
        handlers = [
            server_status,
            restart,
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return
            
    async def on_at_message_create(self, message: Message):
        await self.handle_message(message)

    async def on_message_create(self, message: Message):
        # 检查消息是否包含@机器人，如果是，则跳过处理
        if "<@!" in message.content:
            return
        await self.handle_message(message)

def format_time(seconds):
    days, seconds = divmod(int(seconds), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}天 {hours}小时 {minutes}分钟 {seconds}秒"



if __name__ == "__main__":
    intents = botpy.Intents(public_guild_messages=True, guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=config["appid"], token=config["token"])
