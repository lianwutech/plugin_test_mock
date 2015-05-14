#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    modbus网络的串口数据采集插件
    1、device_id的组成方式为ip_port_slaveid
    2、设备类型为0，协议类型为modbus
    3、devices_info_dict需要持久化设备信息，启动时加载，变化时写入
    4、device_cmd内容：json字符串
"""

import time
import random

from setting import *
from libs.daemon import Daemon
from libs.plugin import *
from libs.mqttclient import MQTTClient

# 全局变量
devices_file_name = "devices.txt"

# 日志对象
logger = logging.getLogger('plugin')

# 配置信息
device_config_info = load_config(devices_file_name)


# 主函数
class PluginDaemon(Daemon):
    def _run(self):
        # 切换工作目录
        os.chdir(cur_file_dir())

        if "devices" not in device_config_info \
                or "network_name" not in device_config_info\
                or "mqtt" not in device_config_info\
                or "protocol_type" not in device_config_info:
            logger.fatal("配置文件配置项不全，启动失败。")
            return

        network_name = device_config_info["network_name"]
        devices_info = device_config_info["devices"]
        mqtt_config = device_config_info["mqtt"]
        protocol_type = device_config_info["protocol_type"]

        # 初始化mqttclient对象
        mqtt_client = MQTTClient(mqtt_config, network_name)
        result = mqtt_client.connect()
        if not result:
            logger.fatal("mqtt connect fail.")
            return

        while True:
            if not mqtt_client.isAlive():
                logger.info("mqtt进程停止，重新启动。")
                mqtt_client.start()

            # 发送数据
            for device_info in devices_info:
                for i in range(1, 1000/device_info["interval"]):
                    value = device_info["base_value"] + \
                            device_info["step"] * random.randint(0, device_info["random_value"])
                    device_data_msg = {
                        "device_id": device_info["device_id"],
                        "device_addr": device_info["device_addr"],
                        "device_port": device_info["device_port"],
                        "device_type": device_info["device_type"],
                        "protocol": protocol_type,
                        "data": "%d" % value
                    }
                    mqtt_client.publish_data(device_data_msg)

            logger.debug("周期处理结束")
            time.sleep(0.1)

# 主函数
def main(argv):
    pid_file_path = "/tmp/%s.pid" % plugin_name
    stdout_file_path = "/tmp/%s.stdout" % plugin_name
    stderr_file_path = "/tmp/%s.stderr" % plugin_name
    daemon = PluginDaemon(pid_file_path, stdout=stdout_file_path, stderr=stderr_file_path)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            logger.info("Unknown command")
            sys.exit(2)
        sys.exit(0)
    elif len(sys.argv) == 1:
        daemon.run()
    else:
        logger.info("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()