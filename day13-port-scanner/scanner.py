import socket
from concurrent.futures import ThreadPoolExecutor

# A socket is an endpoint for network communication — think of it as
# a "phone line" your code opens to try to talk to a specific
# IP address + port combination.
def scan_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    # connect_ex returns 0 if the connection succeeded (port is open),
    # or a nonzero error code if it failed (port closed/filtered) —
    # unlike connect(), it doesn't raise an exception, so it's cleaner
    # for scanning many ports without wrapping everything in try/except.
    result = sock.connect_ex((target, port))
    sock.close()
    if result == 0:
        return port
    return None

# Threading helps here because this is I/O-bound work — most of the
# time is spent WAITING on the network (the 1s timeout), not doing
# CPU work. While one thread waits, others can run. This is different
# from something CPU-bound like the grade calculator, where threads
# fight over the same CPU core and don't help (or need multiprocessing
# instead).
def scan_range(target, start, end):
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(lambda p: scan_port(target, p), range(start, end + 1))
        for result in results:
            if result is not None:
                open_ports.append(result)
    return sorted(open_ports)


if __name__ == "__main__":
    # Ethics rule: only scan hosts you own or have explicit permission
    # to scan. Scanning systems you don't own/control without
    # permission is illegal in most jurisdictions. This script only
    # ever targets 127.0.0.1 — your own machine — never anything else.
    target = "127.0.0.1"
    services = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL"}

    open_ports = scan_range(target, 1, 1024)

    if not open_ports:
        print("No open ports found in range 1-1024.")
    for port in open_ports:
        service = services.get(port, "Unknown")
        print(f"Port {port} open — {service}")