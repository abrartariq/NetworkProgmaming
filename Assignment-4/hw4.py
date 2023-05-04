"""
Where solution code to HW4 should be written.  No other files should
be modified.
"""

import socket
import io
import time
# import typing
import struct
import homework4
import homework4.logging

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
    # rtt_lst = [Estimated,Dev,RTT]
    rtt_lst = [1, .25]
    rtt_timeout = 1
    end_counter = 0

    logger = homework4.logging.get_logger("hw4-sender")
    total_packets = len(data)
    data_offset = 0

    while True:
        try:
            sock.settimeout(rtt_timeout)
            if data_offset >= total_packets:
                end_counter += 1
                if end_counter < 3:
                    packet = struct.pack('Ih', data_offset, P_FIN)
                    sock.send(packet)
                    sock.recv(6)
                break

            chunk = data[data_offset:data_offset+1394]
            packet = struct.pack('Ih', data_offset+1394, P_NEXT)+chunk

            start_time = time.time()

            sock.send(packet)
            ack_resp = sock.recv(6)

            sample_rtt = time.time() - start_time
            rtt_result = calculate_rtt(sample_rtt, rtt_lst[0], rtt_lst[1])

            rtt_lst[0] = rtt_result[0]
            rtt_lst[1] = rtt_result[1]
            rtt_timeout = rtt_result[2]

            data_offset, _ = struct.unpack('Ih', ack_resp)

            logger.info("Pausing for %f seconds", round(rtt_timeout, 2))

        except socket.timeout:
            rtt_timeout = rtt_timeout * 2
            continue


def calculate_rtt(sample_rtt, estimated_rtt, dev_rtt):
    '''
    For Calculating RTT
    '''
    n_estimated_rtt = (0.875 * estimated_rtt) + (0.125 * sample_rtt)
    n_dev_rtt = (0.75 * dev_rtt) + (0.25 * abs(sample_rtt - n_estimated_rtt))
    result_rtt = n_estimated_rtt + 4*n_dev_rtt

    return n_estimated_rtt, n_dev_rtt, result_rtt


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
    logger = homework4.logging.get_logger("hw4-receiver")
    num_bytes = 0
    last_seq = 0
    chunk_size = 1394

    while True:
        data = sock.recv(homework4.MAX_PACKET)
        seq_num, send_flag = struct.unpack('Ih', data[:6])
        twin_packet = last_seq == seq_num
        if last_seq > num_bytes and twin_packet and send_flag == P_NEXT:
            chunk = data[6:]
            b_index = num_bytes % chunk_size

            if len(chunk) > b_index:
                chunk = data[6+b_index:]
            else:
                continue

            last_seq = seq_num
            send_ack(sock, num_bytes+len(chunk))
            logger.info("Received %d bytes", len(chunk))
            dest.write(chunk)
            num_bytes += len(chunk)
            dest.flush()

        elif twin_packet and send_flag == P_NEXT:
            send_ack(sock, seq_num)

        elif seq_num > last_seq and send_flag == P_NEXT:
            b_index = num_bytes % chunk_size
            chunk = data[6+b_index:]

            if not chunk:
                continue

            last_seq = seq_num
            send_ack(sock, num_bytes+len(chunk))
            logger.info("Received %d bytes", len(chunk))
            dest.write(chunk)
            num_bytes += len(chunk)
            dest.flush()

        elif send_flag == P_FIN:
            send_ack(sock, seq_num)
            break

        else:
            break

    return num_bytes


def send_ack(sock, seq_number):
    '''
    For Sending ACKs
    '''
    packet = struct.pack('Ih', seq_number, P_ACK)
    sock.send(packet)
