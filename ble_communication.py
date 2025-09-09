import asyncio
import time
from typing import Optional, Callable
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

class BLECommunicator:
    def __init__(self, device_name="BMS_LE", 
                 service_uuid="d98cb893-05d5-445e-93a4-40a000030000",
                 command_char_uuid="d98cb893-05d5-445e-93a4-40c000030001",
                 response_char_uuid="d98cb893-05d5-445e-93a4-40c000030002"):
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.command_char_uuid = command_char_uuid
        self.response_char_uuid = response_char_uuid
        
        self.client = None
        self.connected = False
        self.command_char = None
        self.response_char = None
        self.response_callback = None
        self.response_queue = asyncio.Queue()
        self.response_event = asyncio.Event()
        self.current_response = None
        
    def _notification_handler(self, sender, data):
        """Handle incoming notifications from response characteristic"""
        if self.response_callback:
            self.response_callback(data)
        
        # Store response and notify waiting tasks
        self.current_response = data
        self.response_event.set()
        asyncio.create_task(self.response_queue.put(data))
    
    async def connect(self, timeout=30.0, max_retries=3):
        """Connect to BLE device"""
        for attempt in range(max_retries):
            try:
                print(f"🔍 Scanning for {self.device_name} (attempt {attempt + 1})...")
                
                # Scan for device
                devices = await BleakScanner.discover(timeout=10.0)
                target_device = None
                
                for device in devices:
                    if device.name and self.device_name.lower() in device.name.lower():
                        target_device = device
                        break
                
                if not target_device:
                    print(f"❌ Device {self.device_name} not found")
                    continue
                
                print(f"✅ Found device: {target_device.name} ({target_device.address})")
                
                # Connect to device
                self.client = BleakClient(target_device.address)
                await asyncio.wait_for(self.client.connect(), timeout=timeout)
                self.connected = self.client.is_connected
                
                if not self.connected:
                    continue
                
                print(f"✅ Connected to {self.device_name}")
                
                # Discover services and characteristics
                services = await self.client.get_services()
                
                for service in services:
                    service_uuid_clean = service.uuid.lower().replace('-', '')
                    target_service_uuid = self.service_uuid.lower().replace('-', '')
                    
                    if target_service_uuid in service_uuid_clean:
                        print(f"✅ Found OTA service: {service.uuid}")
                        
                        for char in service.characteristics:
                            char_uuid_clean = char.uuid.lower().replace('-', '')
                            
                            target_cmd_uuid = self.command_char_uuid.lower().replace('-', '')
                            target_resp_uuid = self.response_char_uuid.lower().replace('-', '')
                            
                            if target_cmd_uuid in char_uuid_clean:
                                self.command_char = char
                                print(f"   ✅ Command characteristic: {char.uuid}")
                                print(f"      Properties: {char.properties}")
                            
                            elif target_resp_uuid in char_uuid_clean:
                                self.response_char = char
                                print(f"   ✅ Response characteristic: {char.uuid}")
                                print(f"      Properties: {char.properties}")
                
                if not self.command_char or not self.response_char:
                    print("❌ Required characteristics not found")
                    await self.disconnect()
                    continue
                
                # Enable notifications
                if "notify" in self.response_char.properties:
                    await self.client.start_notify(self.response_char.uuid, self._notification_handler)
                    print("✅ Notifications enabled")
                
                return True
                
            except asyncio.TimeoutError:
                print("⏰ Connection timeout")
            except BleakError as e:
                print(f"❌ BLE error: {e}")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
            
            if attempt < max_retries - 1:
                print("🔄 Retrying...")
                await asyncio.sleep(2)
        
        return False
    
    async def write_data(self, data):
        """Write data to command characteristic"""
        if not self.connected or not self.command_char or not self.client:
            print("❌ Not connected or command characteristic not available")
            return False
        
        try:
            # Clear previous response
            self.current_response = None
            self.response_event.clear()
            
            # Write data
            await self.client.write_gatt_char(self.command_char.uuid, data)
            print(f"📤 Sent {len(data)} bytes: {data.hex().upper()}")
            return True
            
        except Exception as e:
            print(f"❌ Write error: {e}")
            return False
    
    async def read_response(self, timeout=10.0):
        """Wait for response with timeout"""
        if not self.connected:
            return None
        
        try:
            # Wait for response with timeout
            await asyncio.wait_for(self.response_event.wait(), timeout=timeout)
            return self.current_response
            
        except asyncio.TimeoutError:
            print("⏰ Response timeout")
            return None
        except Exception as e:
            print(f"❌ Read error: {e}")
            return None
    
    async def disconnect(self):
        """Disconnect from device"""
        if self.client:
            try:
                # Stop notifications
                if self.response_char:
                    await self.client.stop_notify(self.response_char.uuid)
                
                await self.client.disconnect()
                self.connected = False
                print("✅ Disconnected from device")
            except Exception as e:
                print(f"❌ Disconnect error: {e}")
            finally:
                self.client = None
                self.command_char = None
                self.response_char = None
    
    def set_response_callback(self, callback: Callable):
        """Set callback for response notifications"""
        self.response_callback = callback
    
    def is_connected(self):
        """Check if connected"""
        return self.connected and self.client and self.client.is_connected
    