# Constants for error codes
class OTACommands:
    
   # Command definitions
    CMD_INIT_NEW_FIRMWARE_IMAGE = 0x00   #OTA initialize, erase sectors
    CMD_UPLOAD_FIRMWARE_CHUNK = 0x01
    
    CMD_GET_VERSION_BOOTLOADER      = 0x02
    CMD_GET_VERSION_APPLICATION_CM7 = 0x03
    CMD_GET_VERSION_APPLICATION_CM4 = 0x04
    
    CMD_GET_CHIP_ID                 = 0x05
    CMD_GO_TO_LOCATION              = 0x06
    
    CMD_ERASE_FLASH_SECTORS       = 0x09
    
    CMD_READ_PROTECT              = 0x07
    CMD_READ_UNPROTECT            = 0x08
    CMD_WRITE_PROTECT             = 0x0A
    CMD_WRITE_UNPROTECT           = 0x0B
    
    CMD_CRC_ACTIVE                = 0x0C
    CMD_CRC_INACTIVE              = 0x0D
    
    CMD_VERIFY_FIRMWARE_ACTIVE    = 0x0E
    CMD_VERIFY_FIRMWARE_INACTIVE  = 0x0F
    #configurations commands
    CMD_CONFIG_READ               = 0x10
    CMD_CONFIG_WRITE              = 0x11
    CMD_CONFIG_UPDATE             = 0x12
    
    CMD_COPY_FIRMWARE_AT_ACTIVE_LOCTION_CM7 = 0x15
    CMD_COPY_FIRMWARE_AT_ACTIVE_LOCTION_CM4 = 0x16
    
    
    # Response status codes
    RESPONSE_ACK  = 0x40
    RESPONSE_NACK = 0x41
    RESPONSE_BUSY = 0x42
    
    CM7 = 0x01
    CM4 = 0x02

    