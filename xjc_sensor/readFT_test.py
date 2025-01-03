from pymodbus.client import ModbusSerialClient
import struct
import time

# 配置Modbus连接参数
SERIAL_PORT = '/dev/ttyUSB0'  # 根据实际的串口设置，如 COM3 或 /dev/ttyUSB0
BAUDRATE = 115200
PARITY = 'N'
STOPBITS = 1
BYTESIZE = 8
SLAVE_ID = 0x01  # 传感器的Modbus站号

# 数据回传指令（例如 1000Hz 数据回传）
REQUEST_COMMAND = [0x01, 0x10, 0x9A, 0x00, 0x02, 0x00, 0xEB, 0x6B]  # 替换为实际的指令

# 创建Modbus客户端
client = ModbusSerialClient(
    method='rtu',
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=1
)


# 解析六维力传感器数据的函数
def parse_force_data(data):
    """
    根据协议解析返回的力和力矩数据。
    """
    if len(data) < 14:
        print("收到的数据长度不足，无法解析")
        return

    # 提取并转换数据
    fx = struct.unpack('>h', bytes(data[0:2]))[0] / 100.0
    fy = struct.unpack('>h', bytes(data[2:4]))[0] / 100.0
    fz = struct.unpack('>h', bytes(data[4:6]))[0] / 100.0
    mx = struct.unpack('>h', bytes(data[6:8]))[0] / 1000.0
    my = struct.unpack('>h', bytes(data[8:10]))[0] / 1000.0
    mz = struct.unpack('>h', bytes(data[10:12]))[0] / 1000.0

    print(f"Fx: {fx} N, Fy: {fy} N, Fz: {fz} N")
    print(f"Mx: {mx} Nm, My: {my} Nm, Mz: {mz} Nm")


# 主函数
def main():
    if not client.connect():
        print("无法连接到Modbus设备")
        return

    try:
        # 发送指令开启数据回传
        client.write_registers(0x100, REQUEST_COMMAND, unit=SLAVE_ID)
        print("已发送数据回传指令，等待数据...")

        while True:
            # 接收传感器的数据帧（14字节：Fx, Fy, Fz, Mx, My, Mz + CRC）
            result = client.read_holding_registers(0x100, 14, unit=SLAVE_ID)

            if result.isError():
                print("读取数据时发生错误")
            else:
                # 解析数据
                parse_force_data(result.registers)

            time.sleep(1)  # 每秒读取一次

    except KeyboardInterrupt:
        print("程序终止")

    finally:
        # 停止数据回传
        stop_command = [0xFF] * 8  # 停止指令
        client.write_registers(0x100, stop_command, unit=SLAVE_ID)
        client.close()
        print("已停止数据回传并断开连接")


if __name__ == '__main__':
    main()
