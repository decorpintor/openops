# OpenOps

Independent Endpoint and Cloud Operations Platform.

OpenOps is an open-source-inspired Remote Monitoring and
Management platform for Windows and Linux endpoints.

## Features

- Endpoint inventory and registration
- Windows and Linux monitoring
- CPU, memory, and disk monitoring
- Security event detection
- Patch compliance reporting
- Automated remediation
- Infrastructure monitoring

## Technology Stack

- Python
- FastAPI
- React
- PostgreSQL
- Docker
- Kubernetes
- Ansible
- Terraform
- Prometheus
- Grafana
- GitHub Actions

## Development

Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Start the API:

    uvicorn backend.app.main:app --reload

Run tests:

    python -m pytest backend/tests -v

API documentation:

    http://localhost:8000/docs

## Project Status

Milestone 1: Initial repository and API foundation.

## License

MIT
