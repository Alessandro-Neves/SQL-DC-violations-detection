Benchmark DC violations detection.

Setup
<br>
Go to virtual env: 
```
    python -m venv env
    source env/bin/activate
```

Install dependencies:
```
    apt install build-essential libpq-dev python3-dev
    pip install -r requirements.txt
```

Configure `pipeline_config.py` file with the desired benchmarks.
<br>
Run:        `python pipeline.py`


To run with other datasets:
- Extract dataset at benchmark/testdatas or Download the dataset at: [DriveLink](https://drive.google.com/drive/folders/1Du8EmFlOPc4tTXXO8l15OQjahzH7edZ2?usp=sharing)
- Configure the dataset path in `options.py`

To run with other DBMSs: 
- Run `make start_databases`
- Configure `DBMSs` and `Benchmark_*` in `options.py`

To run with SQL Server:
```
    Linux ODBC install:
    ./databases/install_odbc.sh
```