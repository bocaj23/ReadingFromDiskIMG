import struct

#sector offsets gathered from BIOS parameter block wikipedia page (DOS 2.0)
#WORD is 2 bytes
#BYTE is 1 byte
#bytes per logical sector                                                     | 0x00B(11) WORD
#logical sectors per cluster                                                  | 0x00D(13) BYTE
#reserved logical sectors                                                     | 0x00E(14) WORD
#number of fats                                                               | 0x010(16) BYTE
#root directory entries                                                       | 0x011(17) WORD
#total logical sectors                                                        | 0x013(19) WORD
#media descriptor, not needed but still need to know location for other fields| 0x015(21) BYTE
#logical sectors per fat                                                      | 0x016(22) WORD
#there are a bunch of other fields in FAT12 for the boot sector but this is all we need
class boot_t:
    def __init__(self, data):
        self.bytesPerSector = struct.unpack('<H', data[11:13])[0]
        self.sectorsPerCluster = struct.unpack('<B', data[13:14])[0]
        self.reservedSectors = struct.unpack('<H', data[14:16])[0]
        self.fatCopies = struct.unpack('<B', data[16:17])[0]
        self.rootDirEntries = struct.unpack('<H', data[17:19])[0]
        self.totalSectors = struct.unpack('<H', data[19:21])[0]
        self.sectorsPerFat = struct.unpack('<H', data[22:24])[0]
        self.rootDirBase = (self.reservedSectors + (self.fatCopies * self.sectorsPerFat)) * self.bytesPerSector
        self.dataAreaStart = self.rootDirBase + (self.rootDirEntries * 32)

#FAT Directory Entry Format
#Bytes 0-11 are the filename+extension
#Bytes 12-21 are reserved
#Bytes 22-23 is the last modified date
#Bytes 24-25 is the last modified time
#Bytes 26-27 starting cluster number 
#Bytes 28-31 file size
class DirEntry:
    def __init__(self, data):
        self.filename = data[:8].rstrip(b'\x00').decode('ascii', errors='ignore')
        self.extension = data[8:11].rstrip(b'\x00').decode('ascii', errors='ignore')
        self.attributes = data[11]
        self.reserved = data[12:22]
        self.updateTime = struct.unpack('<H', data[22:24])[0]
        self.updateDate = struct.unpack('<H', data[24:26])[0]
        self.startCluster = struct.unpack('<H', data[26:28])[0]
        self.fileSize = struct.unpack('<I', data[28:32])[0]

def readBootSector():
    with open('disk1.img', 'rb') as img:
        img.seek(0)
        data = img.read(512)
    return boot_t(data)

def readFAT(boot):
    startFat = boot.reservedSectors * boot.bytesPerSector
    fatSize = boot.sectorsPerFat * boot.bytesPerSector
    with open('disk1.img', 'rb') as img:
        img.seek(startFat)
        fatData = img.read(fatSize)
    return fatData


def getRootFiles(boot):
    startRoot = boot.rootDirBase
    rootSize = boot.rootDirEntries * 32
    files = []

    with open('disk1.img', 'rb') as img:
        img.seek(startRoot)
        root_dir_data = img.read(rootSize)

        for i in range(boot.rootDirEntries):
            entry = root_dir_data[i * 32:(i + 1) * 32]

            #entry not being used is represented by the bit 0xE5
            if entry[0] == 0xE5:
                continue

            filename = entry[:8].rstrip(b'\x00').decode('ascii', errors='ignore').strip()
            extension = entry[8:11].rstrip(b'\x00').decode('ascii', errors='ignore').strip()
            fullFilename = f"{filename}.{extension}" if extension else filename
            
            #extra check to make sure filename is valid
            if filename and not all(c == '\x00' or c == ' ' for c in filename):
                files.append(fullFilename)

            if filename == "NETWORKS" and extension == "TXT":
                networkFileEntry = DirEntry(entry)

    return networkFileEntry

def readCluster(boot, img, clusterNum):
    clusterOffset = boot.dataAreaStart + (clusterNum - 2) * boot.sectorsPerCluster * boot.bytesPerSector
    img.seek(clusterOffset)
    return img.read(boot.sectorsPerCluster * boot.bytesPerSector)



def readFile(boot, img, fatData, startCluster):
    cluster = startCluster
    data = b''
    while cluster < 0xFF8:
        data += readCluster(boot, img, cluster)
        offset = cluster * 3 // 2
        if cluster % 2 == 0:
            nextCluster = struct.unpack('<H', fatData[offset:offset+2])[0] & 0x0FFF
        else:
            nextCluster = struct.unpack('<H', fatData[offset - 1:offset + 1])[0] >> 4
        if nextCluster >= 0xF88:
            break
        cluster = nextCluster
    return data

def main():
    boot = readBootSector()
    fatData = readFAT(boot)
    fileToOpen = getRootFiles(boot)
    if fileToOpen:
        with open('disk1.img', 'rb') as img:
            contents = readFile(boot, img, fatData, fileToOpen.startCluster)
            print(contents.decode('ascii', errors='ignore'))
    

if __name__ == "__main__":
    main()