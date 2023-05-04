"""
Where solution code to HW5 should be written.  No other files should
be modified.
"""

import socket
import io
import time
import typing
import struct
import homework5
import homework5.logging


P_FIN = 0
P_ACK = 1
P_NEXT = 2


def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """

    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)

    rtt_lst = [1, 0.25]
    rtt_timeout = 2
    end_counter = 0

    packet_idx = 0

    logger = homework5.logging.get_logger("hw5-sender")
    chunk_size = homework5.MAX_PACKET
    packet_size = 1394

    last_acked = -1
    win_size = 20

    packet_lst = make_packet_list(data,packet_size)
    total_packets = len(packet_lst)

    while True:
        try:

            if packet_idx >= total_packets:
                sock.settimeout(rtt_timeout)
                end_counter += 1
                if end_counter < 3:
                    packet = struct.pack('HHH', packet_idx,0, P_FIN)
                    sock.send(packet)
                    sock.recv(6)
                break

            if win_size > (total_packets - packet_idx):
                win_size = total_packets - packet_idx

            start_time = time.time()

            for val in range(packet_idx,packet_idx+win_size):
                start = packet_lst[val][1]
                end = packet_lst[val][1] + packet_lst[val][2]
                chunk = data[start:end]
                packet = struct.pack('HHH', packet_lst[val][0], packet_lst[val][2], P_NEXT)+chunk
                sock.send(packet)

            temp_idx = 0
            sock.settimeout(rtt_timeout)
            ack_resp = sock.recv(6)
            rec_idx,_ , _ = struct.unpack('HHH', ack_resp)
            if last_acked +1 == rec_idx:
                temp_idx = 1
                last_acked +=1
                packet_idx +=1

            sample_rtt = time.time() - start_time


            while temp_idx < win_size:
                ack_resp = sock.recv(6)
                rec_idx,_ , _ = struct.unpack('HHH', ack_resp)
                if last_acked+1 == rec_idx:
                    temp_idx+=1
                    last_acked+=1
                    packet_idx +=1
                else:
                    if rec_idx >= last_acked+2:
                        raise socket.timeout


            rtt_result = calculate_rtt(sample_rtt, rtt_lst[0], rtt_lst[1])
            rtt_lst[0] = rtt_result[0]
            rtt_lst[1] = rtt_result[1]
            rtt_timeout = rtt_result[2]

            logger.info("Pausing for %f seconds", round(rtt_timeout, 2))

        except socket.timeout:
            if temp_idx == 0:
                rtt_timeout = rtt_timeout * 2
            else:
                rtt_result = calculate_rtt(sample_rtt, rtt_lst[0], rtt_lst[1])
                rtt_lst[0] = rtt_result[0]
                rtt_lst[1] = rtt_result[1]
                rtt_timeout = rtt_result[2]                






def calculate_rtt(sample_rtt, estimated_rtt, dev_rtt):
    '''
    For Calculating RTT
    '''
    n_estimated_rtt = (0.875 * estimated_rtt) + (0.125 * sample_rtt)
    n_dev_rtt = (0.75 * dev_rtt) + (0.25 * abs(sample_rtt - n_estimated_rtt))
    result_rtt = n_estimated_rtt + 4*n_dev_rtt

    return n_estimated_rtt, n_dev_rtt, result_rtt


def make_packet_list(data,break_th):
    total_packets = len(data)
    total_cycles = int(total_packets/break_th)
    tuple_lst = []
    for idx in range(0,total_cycles):
        start = idx*break_th
        tuple_lst.append( (idx,start,break_th) ) 

    final_packet = total_packets%break_th
    if final_packet > 0:
        tuple_lst.append((total_cycles,total_cycles*break_th,final_packet))
    
    print(tuple_lst[-1][2],final_packet)
    return tuple_lst



def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.

    Return:
        The number of bytes written to the destination.
    """
    logger = homework5.logging.get_logger("hw5-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    num_bytes = 0
    last_seq = -1
    proper_acked = -1
    seq_set = set()
    seq_list = [None] * 32000


    while True:
        data = sock.recv(homework5.MAX_PACKET)
        seq_num, pack_size, send_flag = struct.unpack('HHH', data[:6])
        twin_packet = (seq_num in seq_set)


        if not check_packet(data[6:],pack_size):
            continue


        if twin_packet and send_flag == P_NEXT:
            send_ack(sock, seq_num)

        elif send_flag == P_NEXT:
            chunk = data[6:]
            last_seq = seq_num
            send_ack(sock, last_seq)

            logger.info("Received %d bytes", len(chunk))
            seq_list[seq_num] = chunk
            seq_set.add(seq_num)
            num_bytes += len(chunk)


        elif send_flag == P_FIN:
            send_ack(sock, seq_num)
            break
        else:
            print("RECVER : => ", "WTF HAPPENED")
            print(seq_num,pack_size,send_flags)
            break

    f_count = 0
    while seq_list[f_count] != None:
        dest.write(seq_list[f_count])
        dest.flush()
        if seq_list[f_count+1] == None and seq_list[f_count+2] != None:
            print("RECVER : => ","Fck lol Fck lol")

        f_count += 1

    return num_bytes


def getlatestacked(seq_list,proper_acked):
    if proper_acked == -1:
        proper_acked = 0
    for idx,val in enumerate( seq_list[proper_acked:]):
        if val == None:
            proper_acked = idx
            break
    if proper_acked != 0:
        return proper_acked-1
    else:
        return 0

def send_ack(sock, seq_number):
    '''
    For Sending ACKs
    '''
    packet = struct.pack('HHH', seq_number, 32000, P_ACK)
    sock.send(packet)


def check_packet(data,d_size):
    if d_size != len(data):
        return False
    else:
        return True
