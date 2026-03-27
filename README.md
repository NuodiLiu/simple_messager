# Simple Messager

A multi-user messaging application built to explore computer networking concepts, including socket programming, dual-protocol communication, and concurrent connection handling.

## What It Does

- **User authentication** — login with credentials, with temporary bans after repeated failed attempts
- **Private messaging (P2P)** — send direct messages to any active user
- **Group chat** — create/join named groups and broadcast messages to all members
- **P2P file transfer** — send files directly to another user over UDP
- **Active user listing** — view currently connected users along with their addresses

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Control channel | TCP (`socket.SOCK_STREAM`) |
| Data/messaging channel | UDP (`socket.SOCK_DGRAM`) |
| Concurrency | `threading.Thread` (one thread per client) |
| Logging | `logging` + custom `LoggerService` |

## Design Patterns

**Command Pattern**  
Each client action (`/msgto`, `/groupmsg`, `/activeuser`, `/creategroup`, `/joingroup`, `/p2pvideo`, `/logout`) is encapsulated in its own class that extends a base `Command` class with an `execute()` method. `ClientThread` dynamically dispatches incoming requests to the appropriate command object.

**Thread-per-Client Model**  
The server spawns a dedicated `ClientThread` (extending `threading.Thread`) for every accepted TCP connection. Each client also runs a background `ClientUDPListener` daemon thread to receive asynchronous UDP messages without blocking the main command loop.

**Service Layer**  
`MessageService` abstracts TCP send/receive and UDP delivery. `LoggerService` provides thread-safe, centralised activity logging used across server components.

**Dual-Socket Architecture**  
Every client maintains two channels: a persistent TCP socket for commands/control, and an ephemeral UDP socket for receiving messages and file chunks asynchronously. The server stores each client's UDP port at login and uses it to deliver messages out-of-band.

## Project Structure

```
src/
├── server/
│   ├── Server.py              # TCP listener, shared state (active users, groups, bans)
│   ├── ClientThread.py        # Per-client handler + authentication
│   ├── commands/              # One class per supported command
│   ├── models/                # User and Group data models
│   └── services/              # MessageService, LoggerService
├── client1/
│   ├── Client.py              # CLI, login flow, command dispatch, UDP file sender
│   └── ClientUDPListener.py   # Daemon thread for incoming UDP messages/files
└── common/
    └── Constants.py           # Shared protocol constants and response codes
```

## Running the Application

**Start the server:**
```bash
python src/server/main.py <port>
```

**Start a client:**
```bash
python src/client1/main.py <server_host> <server_port> <client_udp_port>
```

User credentials are stored in `credentials.txt` (one `username password` pair per line).
