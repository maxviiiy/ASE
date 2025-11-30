Quick prototype for the TP-ISIA master/slave project.

Files:
- `scheduler.py` - Master scheduler (listens on 127.0.0.1:7000)
- `slave_server.py` - Slave file server (default ports 6001, 6002)
- `client.py` - Simple client that talks to scheduler then to slave
- `files/` - sample text files served by slaves

Basic run steps (PowerShell):

1) Start slave(s) in separate terminals:

```powershell
python .\slave_server.py --port 6001 --files files
python .\slave_server.py --port 6002 --files files
```

2) Start scheduler:

```powershell
python .\scheduler.py
```

3) Run a client (in new terminal):

```powershell
python .\client.py
```

Notes:
- This is a minimal prototype for demonstration and testing. It uses a very simple text protocol.
- The `ROUTING_TABLE` in `scheduler.py` is hard-coded to map `data-01.txt` to port 6001 and `data-02.txt` to port 6002. Adjust as needed.
- `history.txt` is created and appended by the scheduler.
