# Installation & Configuration

## Install

```bash
pip install -e .

# With dev/test dependencies
pip install -e ".[test,dev]"
```

## Database Connection

Set via environment variables or `.env` file:

```bash
# Option 1: Full URL
DB_URL=postgresql://user:password@host:5432/database

# Option 2: Individual parameters
DB_HOST=localhost
DB_PORT=5432
DB_NAME=egon-data
DB_USER=postgres
DB_PASSWORD=secret
```

## SSH Tunnel (optional)

For remote databases behind a firewall:

```bash
SSH_HOST=gateway.example.com
SSH_PORT=22                    # SSH port (default: 22)
SSH_USER=username
SSH_KEY_FILE=~/.ssh/id_rsa
SSH_LOCAL_PORT=59763           # Local port to forward
SSH_REMOTE_PORT=59763          # Remote database port
```

Use with `--with-tunnel` flag.

## Execution Settings

```bash
EGON_OUT_DIR=./validation_runs    # Output directory for validation results
EGON_LOG_LEVEL=INFO               # Log level (DEBUG, INFO, WARNING, ERROR)
EGON_LOG_DIR=logs                 # Directory for log files
EGON_ENVIRONMENT=development      # Set to "production" for JSON logging
```

Note: `max_workers` for parallel execution is configured via code (default: 6).