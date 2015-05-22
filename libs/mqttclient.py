#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
mqttclient类
"""

import json
import logging
import threading
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTT_ERR_SUCCESS

logger = logging.getLogger('plugin')


class MQTTClient(object):
    def __init__(self, mqtt_config, network_name):
        self.channel = None
        self.mqtt_config = mqtt_config
        self.server_addr = mqtt_config.get("server")
        self.server_port = mqtt_config.get("port")
        self.client_id = mqtt_config.get("client_id")
        self.gateway_topic = mqtt_config.get("gateway_topic")
        self.thread = None
        self.network_name = network_name

        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, rc):
            logger.info("Connected with result code " + str(rc))
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("%s/#" % self.network_name)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            logger.info("收到数据消息" + msg.topic + " " + str(msg.payload))
            # 消息只包含device_cmd，为json字符串
            try:
                cmd_msg = json.loads(msg.payload)
            except Exception, e:
                logger.error("消息内容错误，%r" % msg.payload)
                return

            if "device_id" not in cmd_msg \
                    or "device_addr" not in cmd_msg\
                    or "device_port" not in cmd_msg\
                    or "device_type" not in cmd_msg:
                logger.error("消息格式错误。")
                return

            if cmd_msg["device_id"] != msg.topic:
                logger.error("device_id（%s）和topic(%s)不一致." % (cmd_msg["device_id"], msg.topic))
                return

            # 输出命令内容
            logger.info("收到的命令为:%r" % cmd_msg)

            return

        self.mqtt_client = mqtt.Client(client_id=self.client_id)
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message

    def connect(self):
        try:
            result_code = self.mqtt_client.connect(host=self.server_addr, port=self.server_port, keepalive=60)
            if result_code == MQTT_ERR_SUCCESS:
                return True
            else:
                return False
        except Exception, e:
            logger.error("MQTT链接失败，错误内容:%r" % e)
            return False

    def publish_data(self, device_data_msg):
        """
        发布数据
        :param device_msg:
        :return:
        """
        if self.mqtt_client is None:
            # 该情况可能发生在插件启动时，channel已启动，但mqtt还未connect
            logger.debug("mqtt对象未初始化")
        else:
            try:
                self.mqtt_client.reconnect()
                result_code, local_mid = self.mqtt_client.publish(topic=self.gateway_topic, payload=json.dumps(device_data_msg))
                logger.info("向Topic(%s)发布消息：%r,结果码:%d, mid:%d" %
                            (self.gateway_topic,
                             device_data_msg,
                             result_code,
                             local_mid))
                if result_code != MQTT_ERR_SUCCESS:
                    return False
            except Exception,e :
                logger.error("MQTT链接失败，错误内容:%r" % e)
                self.mqtt_client.reconnect()
                return False

    def run(self):
        try:
            self.mqtt_client.loop_forever()
        except Exception, e:
            logger.error("MQTT链接失败，错误内容:%r" % e)
            self.mqtt_client.disconnect()

    def start(self):
        if self.thread is not None:
            # 如果进程非空，则等待退出
            self.thread.join(1)
        # 启动一个新的线程来运行
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def isAlive(self):
        if self.thread is not None:
            return self.thread.isAlive()
        else:
            return False