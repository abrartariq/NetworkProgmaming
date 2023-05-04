'''This module takes Url and return requested data'''

import logging
import socket
import sys
import ssl

# Global Tokens for easy parsing of bytes
double_cr = bytes("\r\n\r\n", 'utf-8')
carriage_r_bytes = bytes("\r\n", 'utf-8')
content_len_bytes = bytes("\r\nContent-Length: ", 'utf-8')
transfer_type = bytes("\r\nTransfer-Encoding:", 'utf-8')


def get_hostnameport(url):
    '''Extracts host_name, host_ip, obj_address and port from url'''

    host_name = ""
    host_ip = ""
    obj_address = ""
    port = 80

    hostnameport = url.split("/")[2]

    try:
        if ":" not in hostnameport:
            if "http://" in url:
                host_name = hostnameport
                host_ip = socket.gethostbyname(host_name)
                obj_address = url.split(host_name)[1]

            else:
                host_name = url.split("/")[2]
                host_ip = socket.gethostbyname(host_name)
                obj_address = url.split(host_name)[1]
                port = 443
        else:
            if "http://" in hostnameport:
                host_name = hostnameport.split(":")[0]
                host_ip = socket.gethostbyname(host_name)
                obj_address = url.split(hostnameport)[1]
                port = int(hostnameport.split(":")[1])

            else:
                host_name = hostnameport.split(":")[0]
                host_ip = socket.gethostbyname(host_name)
                obj_address = url.split(hostnameport)[1]
                port = int(hostnameport.split(":")[1])

        if obj_address == "":
            obj_address = "/"

    except socket.gaierror:
        return "", "", "", 0

    return host_name, host_ip, obj_address, port


def make_req(host_name, obj_address):
    '''Returns Req header for specific object'''

    close_connection = "Connection: close"+"\r\n\r\n"
    host_entry = "Host:"+host_name+"\r\n"
    request = "GET "+obj_address+" HTTP/1.1\r\n"+host_entry+close_connection
    return request.encode()


def code_moved(data):
    '''Response Code 301 Handler'''

    start_index = data.find(bytes("\r\nLocation: ", 'utf-8'))
    end_index = data[start_index+2:].find(carriage_r_bytes)
    n_url = str(data[start_index+2+10:start_index+end_index+2], 'utf-8')
    resp_data = retrieve_url(n_url)
    return resp_data


def code_ok(sock, data):
    '''Response Code 200 Handler'''

    resp_data = b''
    cl_index_s = data.find(content_len_bytes)
    resp_type = data.find(transfer_type)
    if resp_type != -1:
        resp_data = get_chunked_data(sock, data)
    else:
        resp_data = get_content_data(sock, data, cl_index_s)

    return resp_data


def get_chunked_data(sock, data):
    '''Response Code 200 For Chunked Data'''

    while True:
        buf = sock.recv(1024)
        if not buf:
            break
        data += buf

    resp_data = b''
    start_index = data.find(double_cr)+4
    chunked_data = data[start_index:]
    start_index = 0
    end_index = chunked_data.find(carriage_r_bytes)
    counter = 0
    while end_index != -1:
        counter += 1
        chucklength_bytes = str(chunked_data[start_index:end_index], 'utf-8')
        chucklength_int = int(chucklength_bytes, 16)
        single_chunk = chunked_data[end_index+2:end_index+2+chucklength_int]
        resp_data += single_chunk
        start_index = end_index+2+chucklength_int+2
        chunked_data = chunked_data[start_index:]
        end_index = chunked_data.find(carriage_r_bytes)
        start_index = 0

    return resp_data


def get_content_data(sock, data, cl_index_s):
    '''Response Code 200 For non Chunked Data'''

    local_data = data
    cl_index_e = local_data[cl_index_s+18:].find(carriage_r_bytes)
    ncl_index_s = cl_index_s+18
    ncl_index_e = cl_index_s+18+cl_index_e
    content_length = int(str(local_data[ncl_index_s:ncl_index_e], 'utf-8'))
    content_recieved = local_data[local_data.find(double_cr) + 4:]
    recieved_length = len(content_recieved)

    while recieved_length < (content_length - 1024):
        buf = sock.recv(1024)
        content_recieved += buf
        recieved_length += len(buf)

    content_recieved += sock.recv(content_length - recieved_length)
    return content_recieved


def http_get_data(sock, request):
    '''Main Response handles'''

    sock.send(request)
    data = sock.recv(4096)
    resp_code = str(data[9:12], 'utf-8')

    if resp_code == "301":
        data = code_moved(data)
    elif resp_code == "200":
        data = code_ok(sock, data)
    else:
        data = None

    return data


def retrieve_url(url):
    '''Main Function of this module'''
    resp_data = b''
    host_name, host_ip, obj_address, port = get_hostnameport(url)
    if port == 0:
        return None
    request_header = make_req(host_name, obj_address)

    try:
        if port == 443:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock = context.wrap_socket(sock, server_hostname=host_name)
                sock.connect((host_ip, port))
                resp_data = http_get_data(sock, request_header)

        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host_ip, port))
                resp_data = http_get_data(sock, request_header)

        return resp_data

    except RuntimeError as excp:
        print(excp)
        return None


if __name__ == "__main__":
    var = sys.argv[1]
    sys.stdout.buffer.write(retrieve_url(var))  # pylint: disable=no-member
