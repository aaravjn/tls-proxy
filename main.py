from scapy.all import sniff, send, IP, TCP
import time

INTERFACE = "enp0s3"

def forward_packet(packet):
    try:
        if IP in packet:
            if TCP in packet:
                print(f"[TCP] Ignoring packet to {packet[IP].dst} from {packet[IP].src}")
                return
            
            print(f"[Forwarding] Packet to {packet[IP].dst} from {packet[IP].src}")
            
            # Create new IP packet with same content but direct it to gateway
            new_packet = IP(
                src=packet[IP].src,
                dst=packet[IP].dst,
                ttl=packet[IP].ttl
            )
            
            # Copy the payload (everything after IP header)
            new_packet.payload = packet[IP].payload
            
            # Send using send() (L3) instead of sendp() (L2)
            send(new_packet, verbose=1)
            
    except Exception as e:
        print(f"Error forwarding packet: {e}")
    
    time.sleep(1)

def packet_listener():
    print(f"Listening for packets on interface {INTERFACE}...")
    sniff(iface=INTERFACE, prn=forward_packet, store=0)

if __name__ == "__main__":
    try:
        packet_listener()
    except KeyboardInterrupt:
        print("\nExiting...")