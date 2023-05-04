"""
resolve.py: a recursive resolver built using dnspython
"""
import argparse
import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype

IM_CACHE = {}

TLD_CACHE = {}

LOOKUP_CACHE = {}

FORMATS = (("CNAME", "{alias} is an alias for {name}"),
           ("A", "{name} has address {address}"),
           ("AAAA", "{name} has IPv6 address {address}"),
           ("MX", "{name} mail is handled by {preference} {exchange}"))

# current as of 19 October 2020
ROOT_SERVERS = ("198.41.0.4",
                "199.9.14.201",
                "192.33.4.12",
                "199.7.91.13",
                "192.203.230.10",
                "192.5.5.241",
                "192.112.36.4",
                "198.97.190.53",
                "192.36.148.17",
                "192.58.128.30",
                "193.0.14.129",
                "199.7.83.42",
                "202.12.27.33")

ROOT_TABLE = list(map((lambda x: ("X", x)), ROOT_SERVERS))


def collect_results(name: str) -> dict:
    """
    This function parses final answers into the proper data structure that
    print_results requires. The main work is done within the `lookup` function.
    """
    full_response = {}
    target_name = dns.name.from_text(name)
    # lookup CNAME
    response = lookup(target_name, dns.rdatatype.CNAME)
    cnames = []
    for answers in response.answer:
        for answer in answers:
            cnames.append({"name": answer, "alias": name})
    # lookup A
    response = lookup(target_name, dns.rdatatype.A)
    arecords = []
    for answers in response.answer:
        a_name = answers.name
        for answer in answers:
            if answer.rdtype == 1:  # A record
                arecords.append({"name": a_name, "address": str(answer)})
    # lookup AAAA
    response = lookup(target_name, dns.rdatatype.AAAA)
    aaaarecords = []
    for answers in response.answer:
        aaaa_name = answers.name
        for answer in answers:
            if answer.rdtype == 28:  # AAAA record
                aaaarecords.append({"name": aaaa_name, "address": str(answer)})
    # lookup MX
    response = lookup(target_name, dns.rdatatype.MX)
    mxrecords = []
    for answers in response.answer:
        mx_name = answers.name
        for answer in answers:
            if answer.rdtype == 15:  # MX record
                mxrecords.append({"name": mx_name,
                                  "preference": answer.preference,
                                  "exchange": str(answer.exchange)})

    full_response["CNAME"] = cnames
    full_response["A"] = arecords
    full_response["AAAA"] = aaaarecords
    full_response["MX"] = mxrecords

    # print("RES => ",full_response)
    return full_response


def lookup(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata) -> dns.message.Message:
    """
    This function uses a recursive resolver to find the relevant answer to the
    query.

    TODO: replace this implementation with one which asks the root servers
    and recurses to find the proper answer.
    """
    global LOOKUP_CACHE
    global ROOT_TABLE

    if (target_name, qtype) in LOOKUP_CACHE:
        return LOOKUP_CACHE[(target_name, qtype)]
    else:
        response, ip_found, _, _ = lookup_help(target_name, qtype, ROOT_TABLE)
        LOOKUP_CACHE[(target_name, qtype)] = response
        return response


def lookup_help(target_name, qtype, ip_table):
    ip_found = False
    response = None
    end_found = False
    for idx, (name, server) in enumerate(ip_table):

        try:
            response = query_sender(target_name, qtype, server, ip_table)
        except Exception as e:
            continue

        temp_answer = response.answer
        temp_authority = response.authority
        temp_additional = response.additional

        if len(temp_answer) == 0:
            if len(temp_additional) != 0:
                new_table = make_table(response)
                if len(new_table) != 0:
                    lookupresult = lookup_help(target_name, qtype, new_table)
                    response = lookupresult[0]
                    ip_found = lookupresult[1]
                    end_found = lookupresult[2]
                    table = lookupresult[3]
                    if ip_found:
                        return response, ip_found, end_found, table
                    elif end_found:
                        return response, False, True, None
            elif check_SOA(response):
                return response, False, True, None
            else:
                authority_table = make_authority_table(response)
                if len(authority_table) > 0:
                    server_table = glued_case(authority_table)
                    return lookup_help(target_name, qtype, server_table)
                else:
                    return response, False, True, None
        else:
            for val in response.answer:
                temp_val = val.to_text()
                temp_list = temp_val.split("\n")
                for n_val in temp_list:
                    n_temp_val = n_val.split(" ")
                    if n_temp_val[-2] == 'CNAME':
                        if qtype == dns.rdatatype.CNAME:
                            return response, True, False, None
                        else:
                            global ROOT_TABLE
                            n_lookup = n_temp_val[-1]
                            resp = lookup_help(n_lookup, qtype, ROOT_TABLE)
                            return resp
                    else:
                        return response, True, False, ip_table

    empty_query = dns.message.make_query(target_name, qtype)
    empty_resp = dns.message.make_response(empty_query)

    return empty_resp, False, False, None


def query_sender(target_name, qtype, authority_server, ip_table):
    global ROOT_TABLE
    global TLD_CACHE
    global IM_CACHE

    if ip_table == ROOT_TABLE:
        domain = get_GTLD(target_name)
        if (domain, qtype, authority_server) in TLD_CACHE:
            response = TLD_CACHE[(domain, qtype, authority_server)]
            return response
        else:
            outbound_query = dns.message.make_query(target_name, qtype)
            response = dns.query.udp(outbound_query, authority_server, 3)
            TLD_CACHE[(domain, qtype, authority_server)] = response
            return response
    else:
        if (target_name, qtype, authority_server) in IM_CACHE:
            response = IM_CACHE[(target_name, qtype, authority_server)]
            return response
        else:
            outbound_query = dns.message.make_query(target_name, qtype)
            response = dns.query.udp(outbound_query, authority_server, 3)
            IM_CACHE[(target_name, qtype, authority_server)] = response
            return response


def glued_case(authority_table):
    authority_list = []
    global ROOT_TABLE
    for (val_0, val_1) in authority_table:
        qtype = dns.rdatatype.A
        response, ip_found, _, ip_table = lookup_help(val_1, qtype, ROOT_TABLE)
        if ip_found:
            ip_dict = extract_dict(ip_table, True)
            authority_dict = extract_dict(authority_table, False)
            if check_similarity(authority_dict, ip_dict):
                return ip_table
            else:
                authority_list.append((val_1, get_answer(response)))

    return authority_list


def dict_to_table(mydict):
    result_table = []
    for val in mydict:
        result_table.append((val, mydict[val]))
    return result_table


def get_answer(response):
    for val in response.answer:
        temp_val = val.to_text()
        temp_list = temp_val.split("\n")
        for n_val in temp_list:
            n_temp_val = n_val.split(" ")
            return n_temp_val[-1]


def extract_dict(authority_table, flag):
    result_dict = {}
    if flag:
        for (val_0, val_1) in authority_table:
            result_dict[val_0] = val_1
    else:
        for (val_0, val_1) in authority_table:
            result_dict[val_1] = val_0

    return result_dict


def check_similarity(authority_dict, ip_dict):
    dict_size = len(authority_dict)
    counter = 0
    for val in authority_dict.keys():
        if val in ip_dict:
            counter += 1
    if counter >= dict_size/2:
        return True
    else:
        return False


def make_authority_table(response):
    authority_table = []
    for val in response.authority:
        temp_val = val.to_text()
        temp_list = temp_val.split("\n")
        for n_val in temp_list:
            n_temp_val = n_val.split(" ")
            if n_temp_val[-2] == 'NS':
                authority_table.append((0, n_temp_val[-1]))
    return authority_table


def check_SOA(response):
    for val in response.authority:
        temp_val = val.to_text()
        temp_list = temp_val.split("\n")
        for n_val in temp_list:
            n_temp_val = n_val.split(" ")
            if n_temp_val[3] == 'SOA':
                return True
    return False


def make_table(response):
    name_ip_table = []
    authority_set = set([])
    for val in response.authority:
        temp_val = val.to_text()
        temp_list = temp_val.split("\n")
        for n_val in temp_list:
            n_temp_val = n_val.split(" ")
            if n_temp_val[-2] == 'NS':
                authority_set.add(n_temp_val[-1])

    for idx, val in enumerate(response.additional):
        temp_list = (val.to_text()).split(" ")
        if temp_list[-2] == 'A' and temp_list[0] in authority_set:
            temp_tup = (temp_list[0], temp_list[-1])
            name_ip_table.append(temp_tup)

    return name_ip_table


def get_GTLD(target_name):
    url = str(target_name)
    if url[-1] == '.':
        url = url[:-1]
    index = -1
    while url[index] != '.':
        index = index - 1
    return url[index:]


def print_response(qtype, response):
    print("TYPE ==> ", qtype)
    print(len(response))
    for val in response:
        print(val)


def print_results(results: dict) -> None:
    """
    take the results of a `lookup` and print them to the screen like the host
    program would.
    """

    for rtype, fmt_str in FORMATS:
        for result in results.get(rtype, []):
            print(fmt_str.format(**result))


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    program_args = argument_parser.parse_args()
    for a_domain_name in program_args.name:
        print_results(collect_results(a_domain_name))


if __name__ == "__main__":
    main()
