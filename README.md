# plugin_test_mock

Test Jambu

通过模拟设备来对Jambu进行压力测试和稳定性测试.

测试方法:

通过种子(时间\次数)\随机数来生成数据
device: interval, value range
 
配置方式:json文件
{
    "device_id":"home/1/0",
    "device_addr:":"1",
    "device_port:":"0",
    "device_type":"testint",
    "interval": 10,
    "base_value":10,
    "step":1,
    "random_value": 10
}

每个周期循环次数为:1000/interval 然后休息0.5s

取值为: base_value + random(random_value) * step

