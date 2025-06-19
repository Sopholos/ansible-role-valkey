#!/usr/bin/env python3
"""Get Redis master IP. Used by ansible to update valkeydb hosts."""

import argparse
import socket

import common_redis as common


def get_current_master(db, srv1, srv2, srv3):
    """Get current master."""
    redis_conf = f'/opt/valkey/{db}/valkey.conf'

    with open(redis_conf, 'r') as conf:
        for line in conf.readlines():
            if 'requirepass' in line:
                password = line.split(' ')[1].rstrip()
            if 'port' == line.split(' ')[0]:
                sentinel_port = int(line.split(' ')[1]) - 20000

    redis_obj = common.Redis(False, verbose=False, timeout=1)

    # Query sentinel
    for host in [srv1, srv2, srv3]:
        master_ip = redis_obj.run_command(host, sentinel_port, password, 'SENTINEL GET-MASTER-ADDR-BY-NAME default')
        if master_ip:
            break

    if not master_ip:
        # Return the host of the first db, usually srv1.
        master_ip = srv1
    else:
        master_ip = master_ip[0].decode()

    print(master_ip)


def main():
    """Main."""
    parser = argparse.ArgumentParser(description='Get Redis master host')
    parser.add_argument('--db', '-d', help='redis db name', required=True)
    parser.add_argument('--srv1', '-s1', help='server1 address', required=True)
    parser.add_argument('--srv2', '-s2', help='server2 address', required=True)
    parser.add_argument('--srv3', '-s3', help='server3 address', required=True)    
    args = parser.parse_args()

    get_current_master(args.db, args.srv1, args.srv2, args.srv3)


if __name__ == '__main__':
    main()
