from CommandHandler import CommandHandler
from FwUpload import FwUpload
from OTACommands import OTACommands
from ble_communication import BLECommunicator  # Replace SerialCommunicator

def main():
    # Create BLE communicator instead of serial
    ble_comm = BLECommunicator(
        device_name="BMS_LE",
        service_uuid="d98cb893-05d5-445e-93a4-40a000030000",
        command_char_uuid="d98cb893-05d5-445e-93a4-40c000030001",
        response_char_uuid="d98cb893-05d5-445e-93a4-40c000030002"
    )
    
    command_handler = CommandHandler(ble_comm)
    fw_upload = FwUpload(command_handler)
    
    print("Starting BLE OTA Application...")
    
    try:
        # Connect to BLE device
        if command_handler.connect():
            print("✅ Connected to BLE device")
            
            # Get chip ID
            chip_id = command_handler.get_chip_id()
            print(f"Chip ID: 0x{chip_id:04X}" if chip_id else "Failed to get chip ID")
            
            # Update active firmware
            active_fw_update = fw_upload.update_active_firmware()     
            if active_fw_update:
                print("Active firmware updated")
            else:
                print("Active firmware not updated")  
            
            # Get Application version  
            app_version = command_handler.get_app_version()
            print(f"App Version: 0x{app_version:04X}" if app_version else "Failed to get application version")
            
            # OTA initialization and firmware upload can be done here
            # init_ota = fw_upload.init_OTA(OTACommands.CM4)
            # firmware_uploaded = fw_upload.full_update_workflow()
            
        else:
            print("❌ Failed to connect to BLE device")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        command_handler.disconnect()
        print("Application completed")

if __name__ == "__main__":
    main()
    