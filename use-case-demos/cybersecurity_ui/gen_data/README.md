1. Download CVE JSON data
```bash
wget https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2021.json.zip
unzip nvdcve-2.0-2021.json.zip -d cve_json
```

2. Convert CVE JSON to CSV
```bash
python3 cve_json_to_csv.py
```

2. Generate other CSV files
```bash
python3 gen_data.py
```

4. Copy cve.csv to csv_data Directory
```bash
cp cve.csv ./csv_data/

```