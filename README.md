

### Install Python on MAC OS
```bash
sudo xcode-select --switch path/to/Xcode.app
xcode-select --install
```

### Deploy Python scripts
```bash
cd /Users/stephaniefavre/Documents/UNIGE/Thèse/BD/Metadata/
git clone https://github.com/stephaniefavre/soussol-metadata.git
pyvenv soussol-metadata/
cd soussol-metadata/
source bin/activate
pip install -r requirements.txt
```

### Execute Script to create Metatada
Need to indicate the folder of RAW Excel Information
```Bash
cd /Users/stephaniefavre/Documents/UNIGE/Thèse/BD/Metadata/soussol-metadata/
source bin/activate
python metadata.py -f ../source-files/raw_metadata.xlsx
```

### Execute Script to Export metadata as XML Format
The XML files will be created in the current directory 
```Bash
cd /Users/stephaniefavre/Documents/UNIGE/Thèse/BD/Metadata/soussol-metadata/
source bin/activate
python export_xml_metadata.py
```
