/*
	Rename this to fat_structs.h

	Canvas does not like it when I post .h files.
*/

typedef struct 
{
  int8_t      jump_to_bootstrap[3];
  int8_t      oem_id[8];
  uint16_t    bytes_per_sector;
  uint8_t     sectors_per_cluster;
  uint16_t    reserved_sectors;
  uint8_t     fat_copies;
  uint16_t    root_dir_entries;
  uint16_t    total_sectors;
  uint8_t     media_descriptor_type;
  uint16_t    sectors_per_fat;
  uint16_t    sectors_per_track;
  uint16_t    heads;
  uint32_t    hidden_sectors;
  uint32_t    total_sectors2;
  uint8_t     drive_index;
  uint8_t     _stuff;
  uint8_t     signature;
  uint32_t    id;
  int8_t      label[11];
  int8_t      type[8];
  uint8_t     _more_stuff[448];
  uint16_t    sig;
} __attribute__ ((packed)) boot_t;

typedef struct
{
    int8_t      filename[8];
    int8_t      extension[3];
    int8_t      attributes;
    int8_t      _reserved[10];
    uint16_t    update_time;
    uint16_t    update_date;
    uint16_t    starting_cluster;
    uint32_t    file_size;
} __attribute__ ((packed)) dir_entry_t;

typedef struct
{
	uint8_t		seconds:5;
	uint8_t		minutes:6;
	uint8_t		hours:5;
} timestamp_t;
