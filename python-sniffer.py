#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import socket
import struct
import ctypes
import os

raw_socket = None
ifr = None


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


def parse_ARP(unpacked):
    print "-"*20+"ARP协议"+"-"*20
    print "源MAC地址:\t", ":".join([str(hex(i)).lstrip("0x") for i in unpacked[:6]])
    print "目的MAC地址:\t", ":".join([str(hex(i)).lstrip("0x") for i in unpacked[6:12]])
    print "\n\n"


def parse_IP(pkt):
    IP_protocol = {6: "TCP", 1: "ICMP", 17: "UDP",
                   2: "IGMP", 8: "EGP", 89: "OSPF", 41: "IPV6"}
    ip_header = pkt[14:34]  # 提取IP协议头，不包含option和padding字段。
    # ！标示转换网络字节序，前12字节为版本、头部长度、服务类型、总长度、标志等其他选项，后面的两个四字节依次为源IP地址和目的IP地址。
    ip_data = struct.unpack("!BBH4sBBH4s4s", ip_header)
    # (ip版本+首部长度，服务类型，总长度，0000,ttl,协议，检验和，源ip，目的ip)
    print "-"*20+"IP协议"+"-"*20
    print "源IP :\t\t" + socket.inet_ntoa(ip_data[7])
    print "目的IP :\t" + socket.inet_ntoa(ip_data[8])
    ip_version = ip_data[0] >> 4
    ip_header_length = (ip_data[0] & 0xf)*4
    ip_next_protocol = ip_data[5]

    if ip_version == 4:
        if ip_next_protocol == 6:
            parse_TCP(pkt, ip_header_length)
        if ip_next_protocol == 1:
            parse_ICMP(pkt, ip_header_length)
        if ip_next_protocol == 17:
            parse_UDP(pkt, ip_header_length)


def parse_TCP(pkt, ip_header_length):
    print "-"*20+"TCP协议"+"-"*20
    tcp_header = pkt[14+ip_header_length:14+ip_header_length+20]
    tcp_data = struct.unpack("!HH8sHH4s", tcp_header)

    source_port = tcp_data[0]
    destination_port = tcp_data[1]
    tcp_header_length = tcp_data[3] >> 12
    print "源端口:", source_port
    print "目的端口:", destination_port
    if tcp_header_length == 5 and (source_port == 80 or destination_port == 80):
        parse_HTTP(pkt)
    print "\n\n"


def parse_UDP(pkt, ip_header_length):
    print "-"*20+"UDP协议"+"-"*20
    udp_header = pkt[14+ip_header_length:14+ip_header_length+8]
    udp_data = struct.unpack("!HH4s", udp_header)

    source_port = udp_data[0]
    destination_port = udp_data[1]
    print "源端口:", source_port
    print "目的端口:", destination_port
    print "\n\n"


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
    print "-"*20+"ICMP协议"+"-"*20
    print "数据包类型:",
    if not icmp_dict.has_key(icmp_type):
        print "未知类型"
    else:
        print icmp_dict[icmp_type]
    print "\n\n"


def parse_HTTP(pkt):
    http_data = pkt[54:-4]
    print '-'*20+"HTTP"+'-'*20
    # print http_data


def get_raw_socket():
    global raw_socket
    global ifr
    if os.name == 'posix':
        import fcntl  # posix-only
        raw_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW,
                                   socket.htons(FLAGS.ETH_P_ALL))
        ifr = ifreq()
        ifr.ifr_ifrn = 'eth0'  # 此处注意，这里写死了网卡名称，需要根据实际情况修改或者传入
        fcntl.ioctl(raw_socket, FLAGS.SIOCGIFFLAGS, ifr)  # 获取标记字段的名称
        ifr.ifr_flags |= FLAGS.IFF_PROMISC  # 添加混杂模式的值
        fcntl.ioctl(raw_socket, FLAGS.SIOCSIFFLAGS, ifr)  # 更新
    else:
        # 创建socket
        raw_socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        HOST = socket.gethostbyname(socket.gethostname())
        raw_socketraw_socketraw_socketraw_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        raw_socketraw_socketraw_socket.bind((HOST, 0))
        raw_socketraw_socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        raw_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)


def exit():
    global raw_socket
    global ifr
    if os.name == 'posix':
        import fcntl
        ifr.ifr_flags ^= FLAGS.IFF_PROMISC
        fcntl.ioctl(raw_socket, FLAGS.SIOCSIFFLAGS, ifr)
    else:
        raw_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


def main():
    global raw_socket
    get_raw_socket()
    while True:
        pkt = raw_socket.recvfrom(65535)[0]
        eth_header = pkt[0:14]  # 提取以太网帧头

        # 6字节目的mac地址，6字节源mac地址，2字节协议类型
        unpacked = struct.unpack("!6B6BH", eth_header)
        eth_protocol = unpacked[12]

        # if int(eth_protocol) == 0x806:  # arp
        #     parse_ARP(unpacked)
        #     continue

        if int(eth_protocol) == 0x800:  # ip
            parse_IP(pkt)
            continue


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        exit()
