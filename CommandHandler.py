import struct
import zlib
import time
import asyncio
from typing import Union, Optional, Tuple, Dict
from CRC32 import CRC32
from OTACommands import OTACommands
from ble_communication import BLECommunicator  # Replace SerialCommunicator

class CommandHandler:
    # Constants
    SOP = 0x23  # Start of packet marker (2 bytes)
    EOP = 0x0D  # End of packet marker (2 bytes)
    
    def __init__(self, ble_comm: BLECommunicator):  # Changed parameter type
        self.ble = ble_comm  # Changed from self.serial
        self._current_sequence = 0
        self._response_buffer = bytearray()
        self.crc = CRC32()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def _async_send_command_and_wait_response(self, command: int, data: bytes = b'', 
                                                   packet_sequence: int = 0x0000,
                                                   timeout: float = 10.0, retries: int = 3) -> Tuple[bool, Optional[Dict]]:
        """Async version of send_command_and_wait_response"""
        for attempt in range(retries):
            packet = self.build_command_packet(command, data, packet_sequence)
            print(f"Command Packet (hex): {packet.hex().upper()}")
            
            if not await self.ble.write_data(packet):
                continue
            
            ct = time.time()
            print(f"Time: {time.ctime(ct)}")
            
            # Wait for response
            response_data = await self.ble.read_response(timeout)
            if response_data:
                response = self.parse_response(response_data)
                if response:
                    return True, response
            
            await asyncio.sleep(0.1)
        
        return False, None

    def send_command_and_wait_response(self, command: int, data: bytes = b'', 
                                      packet_sequence: int = 0x0000,
                                      timeout: float = 10.0, retries: int = 3) -> Tuple[bool, Optional[Dict]]:
        """Synchronous wrapper for async method"""
        return self.loop.run_until_complete(
            self._async_send_command_and_wait_response(
                command, data, packet_sequence, timeout, retries
            )
        )

    # ... (keep all other methods the same - build_command_packet, parse_command, etc.)
    
    # Update any UART-specific code to use BLE
    def write_data(self, data):
        """Write data using BLE"""
        return self.loop.run_until_complete(self.ble.write_data(data))
    
    def connect(self):
        """Connect to BLE device"""
        return self.loop.run_until_complete(self.ble.connect())
    
    def disconnect(self):
        """Disconnect from BLE device"""
        return self.loop.run_until_complete(self.ble.disconnect())
    
    def is_connected(self):
        """Check connection status"""
        return self.ble.is_connected()