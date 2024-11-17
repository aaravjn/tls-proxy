from netfilterqueue import NetfilterQueue # type: ignore
from scapy.all import IP

def packet_callback(pkt):
    # Get the packet (as Scapy packet)
    packet = IP(pkt.get_payload())

    # Print packet information (source IP, destination IP, etc.)
    print(f"Packet from {packet.src} to {packet.dst}")

    # You can also modify the packet here (if needed)
    # For example, drop the packet
    # pkt.drop()

    # Accept the packet (send it forward)
    pkt.accept()

def main():
    # Initialize the NetfilterQueue
    nfqueue = NetfilterQueue()

    # Bind the NetfilterQueue to queue number 0 (as set in iptables)
    nfqueue.bind(0, packet_callback)

    try:
        print("Starting packet interception...")
        nfqueue.run()
    except KeyboardInterrupt:
        print("Exiting...")
        nfqueue.unbind()

if __name__ == "__main__":
    main()
