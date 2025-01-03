from pymodbus.client import ModbusSerialClient
import struct


class ModbusSensor:
    def __init__(self, serial_port='/dev/ttyUSB0', baudrate=115200, parity='N', stopbits=1, bytesize=8, slave_id=0x01):
        # 配置 Modbus 连接参数
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.slave_id = slave_id

        # 初始化 Modbus 客户端
        self.client = ModbusSerialClient(
            method='rtu',
            port=self.serial_port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=1
        )

        # 检查连接
        if not self.client.connect():
            print(f"无法连接到 Modbus 设备: {self.serial_port}")
            self.client = None

    def read_register(self, address, count=1):
        """读取 Modbus 寄存器数据"""
        if self.client is None:
            print("Modbus 客户端未初始化，无法读取数据")
            return None

        result = self.client.read_holding_registers(address, count, unit=self.slave_id)
        if result.isError():
            print(f"读取寄存器 {address} 错误: {result}")
            return None
        return result.registers

    def write_register(self, address, value):
        """写入 Modbus 寄存器数据"""
        if self.client is None:
            print("Modbus 客户端未初始化，无法写入数据")
            return False

        result = self.client.write_register(address, value, unit=self.slave_id)
        if result.isError():
            print(f"写入寄存器 {address} 错误: {result}")
            return False
        return True

    def close_connection(self):
        """关闭 Modbus 连接"""
        if self.client:
            self.client.close()

    def __del__(self):
        """析构函数，确保连接被正确关闭"""
        self.close_connection()


# 使用示例
if __name__ == "__main__":
    # 创建 Modbus 传感器实例
    sensor = ModbusSensor(serial_port='/dev/ttyUSB0', baudrate=115200, slave_id=0x01)

    # 读取寄存器数据
    data = sensor.read_register(0x00, count=2)
    if data:
        print(f"读取的寄存器数据: {data}")

    # 写入寄存器数据
    success = sensor.write_register(0x01, 100)
    if success:
        print("成功写入寄存器")

    # 确保连接关闭
    sensor.close_connection()
