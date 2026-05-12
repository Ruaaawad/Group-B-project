# Travel Agent Record Management System

This project is a Python desktop application for managing client, airline, and flight records for a specialist travel agent. It uses a Tkinter graphical user interface, stores records as a list of dictionaries, and saves data to JSON when the application closes.

## Features

- Create, update, delete, search, and display client records
- Create, update, delete, search, and display airline records
- Create, update, delete, search, and display flight records
- Automatic record loading on startup if the JSON data file already exists
- Automatic data saving on close
- Unit tests for the validation, storage, and business-logic modules

## Project Structure

- `src/main.py` starts the GUI application
- `src/gui/application.py` provides the Tkinter interface
- `src/record/validation.py` validates and normalises input data
- `src/record/manager.py` handles CRUD logic and search behavior
- `src/record/storage.py` loads and saves records in JSON format
- `src/conf/constants.py` stores shared record metadata
- `tests/` contains unit tests

## Running the Application

```bash
python src/main.py
```

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

## Assumptions

- Flight records include an internal `ID` so they can be searched, updated, and deleted consistently through the GUI.
- Flight records can only be created when the referenced client and airline already exist.
- A client or airline cannot be deleted while linked flight records still exist.
