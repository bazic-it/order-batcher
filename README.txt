README FOR ORDER BATCHER PROGRAM

Program structure:
The executable needs to be in the same directory with the 'assets' folder and 'batch_outputs'. The 'assets' folder needs to contain 'config.json' and 'icon' folder. The 'icon' folder needs to have 'icon.ico' file.

Two master files are needed to run this program:
1. UOM master data -> Excel file (.xlsx)
Columns format: Ecommerce SKU, SAP Item Number, Qty of the UOM

2. Inventory master data -> Excel file (.xlsx)
Columns format: #, Item No., Item Description, Avail. Qty

Configurations:
1. assets_base_directory -> string
Description: The absolute path of the directory which the master files are in.
Example: "S:/ECOM-CC-WHS/master_files"

2. uom_master_filename -> string
Description: The filename of the UOM master data.
Example: "uom_input.xlsx"

3. inventory_master_filename -> string
Description: The filename of the inventory master data.
Example: "Available Qty Whse 01 + Price Levels.xlsx"

4. logs_filename -> string
Description: The filename of the master log file.
Example: "logs.txt"

5. local_logs_filepath -> string
Description: The filename of the local log file.
Example: "./assets/local_logs.txt"

6. input_file_location -> string
Description: The relative path of the directory from the user's home directory, which the input file is in.
Example: "Downloads" (this will result in /home/<user>/Downloads)

7. output_file_location -> string
Description: The relative path of the output directory from the directory where the executable is in.
Example: "./batch_outputs/"

To make an executable:
- on the terminal with virtual environment activated, run pyinstaller main.py --onefile --noconsole --icon="./assets/icon/icon.ico"