# Travel Agent Record Management System

This project is a Python desktop application for a specialist travel agent. It
manages client, airline, and flight records through a Tkinter graphical user
interface.

The system allows users to create, update, delete, search for, and display
records. Records are stored internally as a list of dictionaries and persisted to
JSON when the application closes. When the application starts, previously saved
records are loaded automatically.

## Backend Functionality

The backend supports the following operations:

- Create new client, airline, and flight records
- Update existing records
- Delete records safely
- Search and retrieve records
- Validate input before storing records
- Save and reload records using JSON storage

Flight records are linked to existing client and airline records. A flight can
only be created if the referenced client and airline already exist in the
system.

## Record Types

### Client Record

- ID
- Type
- Name
- Address Line 1
- Address Line 2
- Address Line 3
- City
- State
- Zip Code
- Country
- Phone Number

### Airline Record

- ID
- Type
- Company Name

### Flight Record

- ID
- Type
- Client_ID
- Airline_ID
- Date
- Start City
- End City

## Project Structure

- `app.py` - GUI entry point
- `src/main.py` - package entry point
- `src/gui/application.py` - Tkinter application interface
- `src/record/manager.py` - backend CRUD operations
- `src/record/validation.py` - validation rules for record input
- `src/record/storage.py` - JSON file persistence
- `src/conf/constants.py` - shared constants and field definitions
- `src/data/records.json` - application record data
- `tests/` - unit tests

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Python requirements:

```bash
pip install -r requirements.txt
```

The application uses Tkinter. On Linux/WSL, Tkinter may need to be installed as
a system package:

```bash
sudo apt install python3-tk
```

## Run

```bash
python3 -B app.py
```

The package entry point can also be used:

```bash
python3 -B -m src.main
```

## Test

```bash
python3 -B -m unittest discover -s tests -v
```
