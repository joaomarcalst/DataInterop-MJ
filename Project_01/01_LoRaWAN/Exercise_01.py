import json
import binascii


# Normalize payload input to a hex string for consistent processing.
def normalize_payload(payload):
    if isinstance(payload, bytes):  # Handle byte strings directly
        payload = binascii.hexlify(payload).decode('utf-8')
    elif payload.startswith("0x"):  # Handle hex string with "0x" prefix
        payload = payload[2:]
    return payload

# Decode Payload
def parse_payload(payload):
    # Convert input to hex string format if necessary
    payload = normalize_payload(payload)

    # Validate payload length (should be 8 bytes or 16 hex characters)
    if len(payload) != 16:
        print("Error: Invalid payload length. Expected 8 bytes (16 hex characters).")
        return None

    # Decode each field
    status = "Occupied" if int(payload[0:2], 16) & 0b1 else "Free"
    battery_voltage = (25 + (int(payload[2:4], 16) & 0xF)) / 10
    temperature = (int(payload[4:6], 16) & 0x7F) - 32
    time_minutes = int(payload[8:10] + payload[6:8], 16)  # Little-endian
    event_count = int(payload[14:16] + payload[12:14] + payload[10:12], 16)  # Little-endian

    return {
        "Status": status,
        "Battery (V)": battery_voltage,
        "Temperature (°C)": temperature,
        "Time (minutes)": time_minutes,
        "Event Count": event_count
    }

# Format the output as CSV or JSON
def format_output(data, output_format):
    if output_format.lower() == "csv":
        csv_output = f"{data['Status']},{data['Battery (V)']},{data['Temperature (°C)']},{data['Time (minutes)']},{data['Event Count']}"
        print("\nCSV Output:")
        print(csv_output)
    elif output_format.lower() == "json":
        print("\nJSON Output:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("Error: Unsupported output format. Please choose 'csv' or 'json'.")

def main():
    # Accepts both hex strings and byte string inputs
    user_input = input("Enter payload: ").strip()
    
    # Check if input is a byte string
    if user_input.startswith("b\"") or user_input.startswith("b'"):
        # Convert byte string representation to actual bytes
        user_input = eval(user_input)  # Converts to actual bytes object
    
    # Parse the payload
    parsed_data = parse_payload(user_input)
    if parsed_data:
        # Prompt user for output format
        output_format = input("Choose output format (csv or json): ").strip()
        format_output(parsed_data, output_format)

if __name__ == "__main__":
    main()