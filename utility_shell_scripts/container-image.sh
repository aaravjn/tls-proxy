```
#!/bin/bash

# Function to get the IP address, subnet, and gateway of the selected network interface
get_network_info() {
  local interface=$1
  
  # Check if the interface exists
  if ! ip link show "$interface" &>/dev/null; then
    echo "Error: Interface $interface does not exist."
    exit 1
  fi

  # Get the IP address and subnet (CIDR) of the selected interface
  ip_addr=$(ip addr show "$interface" | grep "inet " | awk '{print $2}')
  if [ -z "$ip_addr" ]; then
    echo "Error: Unable to find IP address for interface $interface."
    exit 1
  fi
  
  # Extract the IP address and subnet
  ip_address=$(echo "$ip_addr" | cut -d'/' -f1)
  subnet_mask=$(echo "$ip_addr" | cut -d'/' -f2)
  
  # Calculate the network address (simplified)
  subnet="${ip_address%.*}.0"
  
  # Get the default gateway
  gateway=$(ip route show default | grep "default" | awk '{print $3}')
  if [ -z "$gateway" ]; then
    echo "Error: Unable to find default gateway."
    exit 1
  fi
  
  echo "$subnet" "$gateway"
}

# Prompt the user to select the interface
echo "Available network interfaces:"
interfaces=$(ip -o link show | awk -F': ' '{print $2}')
if [ -z "$interfaces" ]; then
  echo "Error: No network interfaces found."
  exit 1
fi

# Display interfaces with numbers for selection
counter=1
for interface in $interfaces; do
  echo "$counter) $interface"
  ((counter++))
done

# Prompt for the interface selection by number
read -p "Select the interface by number: " interface_number

# Validate the user input
if ! [[ "$interface_number" =~ ^[0-9]+$ ]] || [ "$interface_number" -le 0 ] || [ "$interface_number" -gt "$counter" ]; then
  echo "Error: Invalid interface selection."
  exit 1
fi

# Get the selected interface from the list
selected_interface=$(echo "$interfaces" | cut -d' ' -f"$interface_number")
echo "You selected: $selected_interface"

# Get network info (subnet and gateway) for the selected interface
network_info=$(get_network_info "$selected_interface")
subnet=$(echo "$network_info" | awk '{print $1}')
gateway=$(echo "$network_info" | awk '{print $2}')

# Check if subnet and gateway were successfully retrieved
if [ -z "$subnet" ] || [ -z "$gateway" ]; then
  echo "Error: Could not determine subnet or gateway."
  exit 1
fi

# Generate the docker-compose.yml file
cat <<EOF > docker-compose.yml
version: '3.9'

services:
  monitor:
    image: alpine:latest   # Replace this with your actual monitoring tool image
    container_name: network_monitor
    command: sh -c "apk add --no-cache dhclient tcpdump && dhclient eth0 && tail -f /dev/null"
    networks:
      my_macvlan:
        ipv4_address: 0.0.0.0   # Placeholder — DHCP will assign the real IP.

networks:
  my_macvlan:
    driver: macvlan
    driver_opts:
      parent: $selected_interface               # Selected network interface
    ipam:
      config:
        - subnet: "$subnet/24"
          gateway: "$gateway"
EOF

# Check if the compose file was generated successfully
if [ $? -ne 0 ]; then
  echo "Error: Failed to generate docker-compose.yml file."
  exit 1
fi

echo "docker-compose.yml file generated successfully!"

# Automatically start the docker-compose setup
echo "Starting docker-compose..."

# Run docker-compose and check if it succeeds
docker-compose up -d
if [ $? -eq 0 ]; then
  echo "The container is now running!"
else
  echo "Error: There was an issue starting the container. Please check your Docker setup."
  exit 1
fi

# Check if the container is running
container_status=$(docker ps -q -f name=network_monitor)
if [ -z "$container_status" ]; then
  echo "Error: The container did not start successfully."
  exit 1
fi

echo "Container 'network_monitor' is running successfully."
```