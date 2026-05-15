# Travel Agent Record Management System

This project is a Python desktop application designed for a specialist travel agent. It manages three types of records: client records, airline records, and flight records.

The system allows the user to create, update, delete, search for, and display records through a graphical user interface. The backend stores record data internally as a list of dictionaries and saves the data to a JSON file when the application closes. When the application starts, previously saved records are loaded automatically.

## Backend Functionality

The backend supports the following operations:

- Create new client, airline, and flight records
- Update existing records
- Delete records safely
- Search and retrieve records
- Validate input before storing records
- Save and reload records using JSON storage

Flight records are linked to existing client and airline records. This means that a flight can only be created if the referenced client and airline already exist in the system.

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

- `src/main.py` starts the application
- `src/gui/application.py` contains the GUI logic
- `src/record/manager.py` contains the main backend CRUD operations
- `src/record/validation.py` contains validation rules for record input
- `src/record/storage.py` handles JSON file persistence
- `src/conf/constants.py` stores shared constants and field definitions
- `tests/test_manager.py` tests record management logic
- `tests/test_validation.py` tests validation behaviour
- `tests/test_storage.py` tests JSON storage behaviour

## Running the Application

```bash
python src/main.py

