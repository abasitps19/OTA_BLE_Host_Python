import os
from typing import Optional, Tuple, Dict
from CRC32 import CRC32
from OTACommands import OTACommands

class FwUpload:
    CHUNK_SIZE = 192  # Fixed chunk size of 200 bytes
    MINIMUM_NO_OF_DATA_CHUNKS = 10  # minimum number of chunks
    DEFAULT_FW_PATH = r"D:\fw\appcm4.bin"  # Raw string for Windows path

    def __init__(self, command_handler, file_path: str = None):
        self.command_handler = command_handler
        self.firmware_data = b''
        self.total_chunks = 0
        self.file_crc = 0
        self.target_core = 0
        self.file_path = file_path if file_path else self.DEFAULT_FW_PATH
        self.crc = CRC32()        

    def load_firmware_file(self) -> bool:
        try:
            if not os.path.exists(self.file_path):
                print(f"Firmware file not found at {self.file_path}")
                return False

            with open(self.file_path, 'rb') as f:
                self.firmware_data = f.read()

            file_size = len(self.firmware_data)
            self.total_chunks = (file_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            print(f"Loaded firmware: {file_size} bytes, {self.total_chunks} chunks")
            return True
            
        except Exception as e:
            print(f"Error loading firmware: {str(e)}")
            return False
    #-Updated ota intialize packet with payload (CRC(4 bytes) + (total_chunks +4))
    def calculate_file_crc(self) -> int:
        #Calculate CRC32 using CommandHandler's method
        if not self.firmware_data:
            return 0
            
        self.file_crc = self.crc.calculate_crc32(
            data=self.firmware_data,
            initial_crc=0xFFFFFFFF
        )
        print(f"Calculated CRC32: 0x{self.file_crc:08X}")
        return self.file_crc


    def full_update_workflow(self) -> bool:
        """
        Complete firmware update sequence:
        1. Load firmware file
        2. Calculate file metadata (CRC, size, chunks)
        3. Initialize OTA with device
        4. Upload all chunks sequentially
        5. Verify firmware with device
        """
        # Step 1: Load firmware file
        if not self.load_firmware_file():
            print("Error: Failed to load firmware file")
            return False

        # Step 2: Calculate file metadata
        self.calculate_file_crc()
        if not hasattr(self, 'file_crc') or not hasattr(self, 'total_chunks'):
            print("Error: File CRC or chunk calculation failed")
            return False

        print(f"Firmware Info - CRC: 0x{self.file_crc:08X}, "
            f"Size: {len(self.firmware_data)} bytes, "
            f"Chunks: {self.total_chunks}")

        # Step 3: Initialize OTA with device
        #if not self.init_OTA():
        #    print("Error: OTA initialization failed")
        #    return False

        # Step 4: Upload chunks
        if not self.upload_chunks(timeout=20,no_of_retries=1):
            print("Error: Firmware upload failed")
            return False

        # Step 5: Verify firmware
        print("verify firmware secondary location")
        if not self.verify_firmware():
            print("Error: Firmware verification failed")
            return False

        print("Firmware update completed successfully!")
        return True

    def init_OTA(self, core=OTACommands.CM4) -> bool:
        # Initialize with default values
        print("initializing OTA")
        file_crc = 0x00000000
        payload = b''
        # step1. get target core
        self.target_core = core 
        # Step 2: Load firmware file
        if not self.load_firmware_file():
            print("Error: Failed to load firmware file")
            return False
        else:
            print("firmware file loaded successfully")    
        
        # Step 3: Calculate file CRC
        file_crc = self.calculate_file_crc()
        if not file_crc:
            print(f"Error: Invalid file CRC {file_crc:08X}")
            return False
        else:
            print(f"firmware file crc calculated {self.file_crc:08X}")
                
        # Step 4: Validate chunk count
        if self.total_chunks < self.MINIMUM_NO_OF_DATA_CHUNKS:
            print(f"Error: Insufficient chunks ({self.total_chunks}) - minimum {self.MINIMUM_NO_OF_DATA_CHUNKS} required")
            return False
        # step 5: print information 
        print(f"OTA Init - Firmware Info -  Size: {len(self.firmware_data)} bytes, "
              f"CRC: 0x{self.file_crc:08X}, "
              f"Chunks: {self.total_chunks}, "
              f"Target_core:{self.target_core}")
        # Step 6: Prepare payload (firmware image size + CRC + chunk count+ target core)
        try:
            payload = (len(self.firmware_data).to_bytes(4, 'big')+file_crc.to_bytes(4, 'big') + self.total_chunks.to_bytes(4, 'big') + self.target_core.to_bytes(1,'big'))
            
        except Exception as e:
            print(f"Error creating payload: {e}")
            return False

        # Step 5: Send command and wait for response
        
        try:
            success, response = self.command_handler.send_command_and_wait_response(
                        command=OTACommands.CMD_INIT_NEW_FIRMWARE_IMAGE,
                        data=payload,timeout=120.0)
                
            if not success:
                print("Error: No response from device")
                return False
                    
            if response['packet_type'] == OTACommands.RESPONSE_ACK:
                print(f"OTA Init successful - CRC: {file_crc:08X}, Chunks: {self.total_chunks}")
                return True
            
            elif response['packet_type'] == OTACommands.RESPONSE_NACK:
                print("Error: Device rejected initialization (NACK)")
                return False
            else:
                print(f"Error: Unexpected response type {response['packet_type']:02X}")
                return False
                    
        except Exception as e:
            print(f"Error during OTA initialization: {e}")
            return False

    def upload_chunks(self, timeout: float = 20.0, no_of_retries: int = 3) -> bool:
        """
        Upload firmware in chunks to device
        Args:
            timeout: Timeout per chunk in seconds
        Returns:
            bool: True if all chunks were uploaded successfully
         """
        for chunk_idx in range(self.total_chunks):
            # Calculate chunk start/end positions
            start = chunk_idx * self.CHUNK_SIZE
            end = start + self.CHUNK_SIZE
            chunk = self.firmware_data[start:end]

            # Pad last chunk if needed
            if len(chunk) < self.CHUNK_SIZE and chunk_idx == self.total_chunks - 1:
                chunk += b'\xFF' * (self.CHUNK_SIZE - len(chunk))

            print(f"Uploading chunk {chunk_idx + 1}/{self.total_chunks} "
              f"(Size: {len(chunk)} bytes)")

            # Send chunk with retries
            success, response = self.command_handler.send_command_and_wait_response(
                command=OTACommands.CMD_UPLOAD_FIRMWARE_CHUNK,
                packet_sequence=chunk_idx,
                data=chunk,
                timeout=timeout,
                retries=no_of_retries
            )

            if not success:
                print(f"Error: Failed to upload chunk {chunk_idx}")
                return False

            if response.get('packet_type') != OTACommands.RESPONSE_ACK:
                print(f"Error: Device rejected chunk {chunk_idx}")
                return False

            # Optional: Progress indicator
            progress = (chunk_idx + 1) / self.total_chunks * 100
            print(f"Progress: {progress:.1f}%")
        # Send last chunck
        '''
        final_packet =  0xFF00
        print("uploading final packet")
        success, response = self.command_handler.send_command_and_wait_response(
                command=OTACommands.CMD_UPLOAD_FIRMWARE_CHUNK,
                packet_sequence=final_packet,
                data=chunk,
                timeout=timeout,
                retries=no_of_retries)    
        '''        

        return True

    def verify_firmware(self) -> bool:
        """
        Verify firmware CRC with device
        Returns:
            bool: True if device confirms firmware is valid
        """
        crc_bytes = self.file_crc.to_bytes(4, 'big')
    
        print("Verifying new firmware inactive...")
        success, response = self.command_handler.send_command_and_wait_response(
            command=OTACommands.CMD_VERIFY_FIRMWARE_INACTIVE,
            data=crc_bytes,
            timeout=120.0
        )
        if success and response.get('packet_type') == OTACommands.RESPONSE_ACK:
            print("New Firmware verification successful!")
            return True
        
        print("New Firmware verification failed")
        return False
    
    def verify_active_firmware(self) -> bool:
        crc_bytes = self.file_crc.to_bytes(4, 'big')
    
        print("Verifying new firmware inactive...")
        success, response = self.command_handler.send_command_and_wait_response(
            command=OTACommands.CMD_VERIFY_FIRMWARE_ACTIVE,
            data=crc_bytes,
            timeout=500.0
        )
        if success and response.get('packet_type') == OTACommands.RESPONSE_ACK:
            print("New Firmware verification successful!")
            return True
        
        print("New Firmware verification failed")
            
        return False
    
    def update_active_firmware(self, core_type: int = OTACommands.CMD_COPY_FIRMWARE_AT_ACTIVE_LOCTION_CM4) ->bool:
        print("updating active firmware...")
        crc_bytes = self.file_crc.to_bytes(4, 'big')
        success, response = self.command_handler.send_command_and_wait_response(
            command=core_type,
            packet_sequence=0,
            data=crc_bytes,
            timeout=60.0,
            
        )
        if success and response.get('packet_type') == OTACommands.RESPONSE_ACK:
            print("Active firmware updated successful!")
            return True
        else:
            print("Error in updadting Active firmware")
            return False
        return True
    
    def read_configuration(self) ->bool:
        success, response = self.command_handler.send_command_and_wait_response(
            command=OTACommands.CMD_CONFIG_READ,timeout=100)
        if success and response.get('packet_type') == OTACommands.RESPONSE_ACK:
            print("Configuration Read Successfully!")
            return True
        else:
            print("Error in configuration Read")
            return False
        return True

    def write_configuration(self) ->bool:
        success, response = self.command_handler.send_command_and_wait_response(
            command=OTACommands.CMD_CONFIG_WRITE,timeout=100)
        if success and response.get('packet_type') == OTACommands.RESPONSE_ACK:
            print("Configuration Write successfully!")
            return True
        else:
            print("Error in configuration write")
            return False
        return True

    def update_configuration(self) ->bool:
        success, response = self.command_handler.send_command_and_wait_response(
            command=OTACommands.CMD_CONFIG_UPDATE,timeout=100)
        if success and response.get('packet_type') == OTACommands.RESPONSE_ACK:
            print("Configuration updated successfully!")
            return True
        else:
            print("Error in configuration update")
            return False
        return True
