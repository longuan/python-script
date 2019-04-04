# coding:utf-8

import socket
import struct
import ctypes
import fcntl  # posix-only
import threading


class PacketItem(object):
    def __init__(self, pkt):
        self.protocol_name = ""
        self.src_mac = ""
        self.dst_mac = ""
        self.src_ip = ""
        self.dst_ip = ""
        self.src_port = ""
        self.dst_port = ""
        self.parse_pkt(pkt)

    def parse_pkt(self, pkt):
        eth_header = pkt[0:14]  # 提取以太网帧头

        # 6字节目的mac地址，6字节源mac地址，2字节协议类型
        unpacked = struct.unpack("!6B6BH", eth_header)
        self.src_mac = ":".join(hex(i).lstrip("0x") for i in unpacked[:6])
        self.dst_mac = ":".join(hex(i).lstrip("0x") for i in unpacked[6:12])
        eth_protocol = unpacked[12]

        if int(eth_protocol) == 0x0806:  # arp
            self.protocol_name = "ARP"
            return

        if int(eth_protocol) == 0x0800:  # ip
            self.protocol_name = "IP"
            ip_datas = parse_IP(pkt)
            self.protocol_name = ip_datas[0]
            self.src_ip = ip_datas[1]
            self.dst_ip = ip_datas[2]
            if ip_datas[0] == "TCP":
                tcp_datas = parse_TCP(pkt, ip_datas[-1])
                self.src_port = tcp_datas[1]
                self.dst_port = tcp_datas[2]
            elif ip_datas[0] == "UDP":
                udp_datas = parse_UDP(pkt, ip_datas[-1])
                self.src_port = udp_datas[1]
                self.dst_port = udp_datas[2]
            elif ip_datas[0] == "ICMP":
                pass
            return

        if int(eth_protocol) == 0x814c:
            self.protocol_name = "SNMP"
            return

        if int(eth_protocol) == 0x86DD:
            self.protocol_name = "IPV6"
            return


class PacketContainer(object):
    def __init__(self):
        self.raw_socket = None
        self.ifr = None
        self.packets = []
        self.status = False
        self.s = None

    def get_raw_socket(self):
        self.raw_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW,
                                   socket.htons(FLAGS.ETH_P_ALL))
        self.ifr = ifreq()
        self.ifr.ifr_ifrn = b'ens33'  # 此处注意，这里写死了网卡名称，需要根据实际情况修改或者传入
        fcntl.ioctl(self.raw_socket, FLAGS.SIOCGIFFLAGS, self.ifr)  # 获取标记字段的名称
        self.ifr.ifr_flags |= FLAGS.IFF_PROMISC  # 添加混杂模式的值
        fcntl.ioctl(self.raw_socket, FLAGS.SIOCSIFFLAGS, self.ifr)  # 更新

    def recv_packets(self):
        while True:
            if self.status:
                pkt = self.raw_socket.recvfrom(65535)[0]
                self.packets.append(PacketItem(pkt))
            else:
                return

    def start_sniff(self):
        self.get_raw_socket()
        self.status = True
        self.s = threading.Thread(target=self.recv_packets)
        self.s.start()

    def stop_sniff(self):
        self.ifr.ifr_flags ^= FLAGS.IFF_PROMISC
        fcntl.ioctl(self.raw_socket, FLAGS.SIOCSIFFLAGS, self.ifr)
        self.status = False
        self.raw_socket.close()
        self.s.join()


class FLAGS(object):
    # linux/if_ether.h
    ETH_P_ALL = 0x0003  # 所有协议
    ETH_P_IP = 0x0800  # 只处理IP层
    # linux/if.h，混杂模式
    IFF_PROMISC = 0x100
    # linux/sockios.h
    SIOCGIFFLAGS = 0x8913
    SIOCSIFFLAGS = 0x8914


class ifreq(ctypes.Structure):
    _fields_ = [("ifr_ifrn", ctypes.c_char * 16),
                ("ifr_flags", ctypes.c_short)]


def parse_IP(pkt):
    IP_protocol = {6: "TCP", 1: "ICMP", 17: "UDP",
                   2: "IGMP", 8: "EGP", 89: "OSPF", 41: "IPV6"}
    ip_header = pkt[14:34]  # 提取IP协议头，不包含option和padding字段。
    # ！标示转换网络字节序，前12字节为版本、头部长度、服务类型、总长度、标志等其他选项，后面的两个四字节依次为源IP地址和目的IP地址。
    ip_data = struct.unpack("!BBH4sBBH4s4s", ip_header)
    # (ip版本+首部长度，服务类型，总长度，0000,ttl,协议，检验和，源ip，目的ip)
    src_ip = socket.inet_ntoa(ip_data[7])
    dst_ip = socket.inet_ntoa(ip_data[8])
    ip_version = ip_data[0] >> 4
    ip_header_length = (ip_data[0] & 0xf)*4
    next_protocol_name = IP_protocol[ip_data[5]]
    return (next_protocol_name,src_ip,dst_ip,ip_header_length)


def parse_TCP(pkt, ip_header_length):
    tcp_header = pkt[14+ip_header_length:14+ip_header_length+20]
    tcp_data = struct.unpack("!HH8sHH4s", tcp_header)

    src_port = tcp_data[0]
    dst_port = tcp_data[1]
    tcp_header_length = tcp_data[3] >> 12
    return ("",src_port,dst_port,tcp_header_length)


def parse_UDP(pkt, ip_header_length):
    udp_header = pkt[14+ip_header_length:14+ip_header_length+8]
    udp_data = struct.unpack("!HHHH", udp_header)

    src_port = udp_data[0]
    dst_port = udp_data[1]
    udp_data_length = udp_data[2]
    return ("",src_port,dst_port,udp_data_length)


def parse_ICMP(pkt, ip_header_length):
    """
    icmp_type 类型描述
    0 响应应答（ECHO-REPLY）
    3 不可到达
    4 源抑制
    5 重定向
    8 响应请求（ECHO-REQUEST）
    11 超时
    12 参数失灵
    13 时间戳请求
    14 时间戳应答
    15 信息请求（*已作废）
    16 信息应答（*已作废）
    17 地址掩码请求
    18 地址掩码应答
    """
    icmp_dict = {0: "回显应答(ping应答)", 3: "不可到达", 4: "源抑制",
                 5: "重定向", 8: "请求回显(ping请求)", 11: "超时"}
    icmp_header = pkt[14+ip_header_length:14+ip_header_length+4]
    icmp_data = struct.unpack("!BBH", icmp_header)
    icmp_type = icmp_data[0]
    icmp_code = icmp_data[1]

#
# def parse_HTTP(pkt):
#     http_data = pkt[54:-4]
#     print '-'*20+"HTTP"+'-'*20
#     # print http_data
#
#