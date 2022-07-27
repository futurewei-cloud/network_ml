from datetime import datetime as dt

class Packet:
    PROTO_TCP = 6
    PROTO_UDP = 17

    def __init__(self, time, ip_src, ip_dst, ip_proto, data_len, src_port=None, dst_port=None):
        self.time = time
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.proto = ip_proto
        self.data_len = data_len
        self.src_port = src_port
        self.dst_port = dst_port
    @classmethod
    def IP_Packet(self, time, ip_src, ip_dst, ip_proto, ip_len):
        return Packet(time, ip_src, ip_dst, ip_proto, ip_len)
    @classmethod
    def TCP_Packet(self, time, ip_src, ip_dst, tcp_len, src_port, dst_port):
        return Packet(time, ip_src, ip_dst, Packet.PROTO_TCP, tcp_len, src_port, dst_port)
    @classmethod
    def UDP_Packet(self, time, ip_src, ip_dst, udp_len, src_port, dst_port):
        return Packet(time, ip_src, ip_dst, Packet.PROTO_UDP, udp_len, src_port, dst_port)
    @classmethod
    def from_line(self, line, parser):
        parsed = parser(line)
        if parsed == None: return None #Error in the parser

        if parsed['ip_proto'] == Packet.PROTO_TCP:
            return Packet.TCP_Packet(
                time = parsed['time'],
                ip_src = parsed['ip_src'],
                ip_dst = parsed['ip_dst'],
                tcp_len = parsed['data_len'],
                src_port = parsed['src_port'],
                dst_port = parsed['dst_port']
            )
        elif parsed['ip_proto'] == Packet.PROTO_UDP:
            return Packet.UDP_Packet(
                time = parsed['time'],
                ip_src = parsed['ip_src'],
                ip_dst = parsed['ip_dst'],
                udp_len = parsed['data_len'],
                src_port = parsed['src_port'],
                dst_port = parsed['dst_port']
            )
        else:
            return Packet.IP_Packet(
                time = parsed['time'],
                ip_src = parsed['ip_src'],
                ip_dst = parsed['ip_dst'],
                ip_proto = parsed['ip_proto'],
                ip_len = parsed['data_len']
            )

    def __str__(self):
        if self.proto == Packet.PROTO_TCP or self.proto == Packet.PROTO_UDP:
            return '{} : {}:{} --> {}:{}   (datasize:{},protocol:{})'.format(
                self.time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.ip_src, self.src_port,
                self.ip_dst, self.dst_port,
                self.data_len, 'TCP' if self.proto == Packet.PROTO_TCP else 'UDP'
            )
        else : return '{} : {} --> {}   (datasize:{},protocol:{})'.format(
            self.time.strftime('%Y-%m-%d %H:%M:%S.%f'),
            self.ip_src, self.ip_dst,
            self.data_len, self.proto
        )
    def get_host(self, who = 'src'):
        if self.proto == Packet.PROTO_TCP or self.proto == Packet.PROTO_UDP:
            return '{}:{}'.format(*([self.ip_src, self.src_port] if (who == 'src') else [self.ip_dst, self.dst_port]))
        return '{}:'.format(self.ip_src if who == 'src' else self.ip_dst)

    @staticmethod
    def csv_header():
        return 'time,proto,data_len,ip_src,ip_dst,src_port,dst_port\n'
    def as_csv_line(self):
        return '{},{},{},{},{},{},{}\n'.format(
            dt.timestamp(self.time), self.proto, self.data_len,
            self.ip_src, self.ip_dst,
            self.src_port, self.dst_port
        )



    @staticmethod
    def from_csv_line(line):
        return Packet.from_line(line, Packet.default_parser)


    @staticmethod
    def default_parser(line):
        p_data = line.split('\n')[0].split(',')
        #e.g.10.0.4.89,bulk
        #after：['10.0.4.89', 'bulk']
        parsed = {}

        try:
            parsed['time'] = dt.fromtimestamp(float(p_data[0]))
            #时间戳转换成字符串日期时间fromtimestamp
            parsed['ip_proto'] = int(p_data[1])
            parsed['data_len'] = int(p_data[2])
            parsed['ip_src'], parsed['ip_dst'] = p_data[3:5]
            parsed['src_port'], parsed['dst_port'] = p_data[5:7]
        except: return None

        return parsed
