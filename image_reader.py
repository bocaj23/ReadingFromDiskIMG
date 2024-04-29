import struct

class boot_t:
    def __init__(self, data):
        self.bytes_per_sector = struct.unpack('<H', data[11:13])[0]
        self.sectors_per_cluster = struct.unpack('<B', data[13:14])[0]
        self.reserved_sectors = struct.unpack('<H', data[14:16])[0]
        self.fat_copies = struct.unpack('<B', data[16:17])[0]
        self.root_dir_entries = struct.unpack('<H', data[17:19])[0]
        self.total_sectors = struct.unpack('<H', data[19:21])[0]
        self.sectors_per_fat = struct.unpack('<H', data[22:24])[0]
        self.root_dir_base = (self.reserved_sectors + (self.fat_copies * self.sectors_per_fat)) * self.bytes_per_sector


def readBootSector():
    with open('disk1.img', 'rb') as img:
        img.seek(0)
        boot_sector_data = img.read(512)
    return boot_t(boot_sector_data)

def readFAT(boot_sector):
    fat_start = boot_sector.reserved_sectors * boot_sector.bytes_per_sector
    fat_size = boot_sector.sectors_per_fat * boot_sector.bytes_per_sector
    with open('disk1.img', 'rb') as img:
        img.seek(fat_start)
        fat_data = img.read(fat_size)
    return fat_data

def compute_start_of_root_directory(boot_sector):
    return boot_sector.reserved_sectors + (boot_sector.fat_copies * boot_sector.sectors_per_fat) * boot_sector.bytes_per_sector

def getRootFiles(boot_sector):
    root_dir_start = boot_sector.root_dir_base
    root_dir_size = boot_sector.root_dir_entries * 32  # Each directory entry is 32 bytes
    files = []

    with open('disk1.img', 'rb') as img:
        img.seek(root_dir_start)
        root_dir_data = img.read(root_dir_size)

        for i in range(boot_sector.root_dir_entries):
            entry = root_dir_data[i * 32:(i + 1) * 32]
            # Check if the entry is used (not deleted files marked by 0xE5)
            if entry[0] == 0xE5:
                continue

            # Decode and process filename and extension separately
            filename = entry[:8].rstrip(b'\x00').decode('ascii', errors='ignore').strip()
            extension = entry[8:11].rstrip(b'\x00').decode('ascii', errors='ignore').strip()

            # Concatenate filename and extension correctly
            full_filename = f"{filename}.{extension}" if extension else filename
            
            # Append only if the filename is non-empty and not a placeholder
            if filename and not all(c == '\x00' or c == ' ' for c in filename):
                files.append(full_filename)

    return files

def main():
    boot_sector = readBootSector()
    fat_data = readFAT(boot_sector)
    files = getRootFiles(boot_sector)
    for file in files:
            print(file)

if __name__ == "__main__":
    main()