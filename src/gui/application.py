"""Tkinter GUI for the travel agent record management system."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from src.conf.constants import DISPLAY_NAMES, FIELD_LABELS, RECORD_TYPES
from src.record.manager import RecordManager
from src.record.storage import JSONStorage
from src.record.validation import ValidationError


class RecordManagementApp:
    """Desktop GUI application for CRUD operations on travel records."""

    def __init__(self, root: tk.Tk, storage_path: str | Path) -> None:
        """Create the main window and load any previously saved records."""
        self.root = root
        self.root.title("Travel Agent Record Manager")
        self.root.geometry("1200x700")

        self.storage = JSONStorage(storage_path)
        self.manager = RecordManager(self.storage.load_records())
        self.forms: dict[str, dict[str, tk.Entry]] = {}
        self.trees: dict[str, ttk.Treeview] = {}
        self.search_vars: dict[str, dict[str, tk.StringVar]] = {}

        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_layout(self) -> None:
        """Create one notebook tab for each supported record type."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        for record_type in RECORD_TYPES:
            tab = ttk.Frame(notebook, padding=12)
            notebook.add(tab, text=f"{DISPLAY_NAMES[record_type]} Records")
            self._build_tab(tab, record_type)
            self.refresh_tree(record_type)

    def _build_tab(self, parent: ttk.Frame, record_type: str) -> None:
        """Build the form, search controls, and table for one record type."""
        parent.columnconfigure(0, weight=0)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        form_frame = ttk.LabelFrame(parent, text=f"{DISPLAY_NAMES[record_type]} Details", padding=12)
        form_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        entries: dict[str, tk.Entry] = {}
        editable_fields = [field for field, _ in FIELD_LABELS[record_type] if field != "Type"]
        for row, field_name in enumerate(editable_fields):
            label = next(label for field, label in FIELD_LABELS[record_type] if field == field_name)
            ttk.Label(form_frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            entries[field_name] = entry
            if field_name == "ID":
                entry.configure(state="readonly")

        form_frame.columnconfigure(1, weight=1)
        self.forms[record_type] = entries

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(editable_fields), column=0, columnspan=2, pady=(12, 0), sticky="ew")

        ttk.Button(button_frame, text="Create", command=lambda rt=record_type: self.create_record(rt)).grid(
            row=0, column=0, padx=4
        )
        ttk.Button(button_frame, text="Update", command=lambda rt=record_type: self.update_record(rt)).grid(
            row=0, column=1, padx=4
        )
        ttk.Button(button_frame, text="Delete", command=lambda rt=record_type: self.delete_record(rt)).grid(
            row=0, column=2, padx=4
        )
        ttk.Button(button_frame, text="Clear", command=lambda rt=record_type: self.clear_form(rt)).grid(
            row=0, column=3, padx=4
        )

        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        search_frame = ttk.LabelFrame(right_frame, text="Search", padding=12)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        search_term = tk.StringVar()
        field_var = tk.StringVar(value="All Fields")
        self.search_vars[record_type] = {"term": search_term, "field": field_var}

        ttk.Label(search_frame, text="Search Term").grid(row=0, column=0, sticky="w")
        ttk.Entry(search_frame, textvariable=search_term, width=30).grid(row=0, column=1, padx=6, sticky="ew")

        field_options = ["All Fields"] + [field for field, _ in FIELD_LABELS[record_type] if field != "Type"]
        ttk.Label(search_frame, text="Field").grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            search_frame,
            textvariable=field_var,
            values=field_options,
            width=18,
            state="readonly",
        ).grid(row=0, column=3, padx=6, sticky="ew")

        ttk.Button(search_frame, text="Search", command=lambda rt=record_type: self.search_records(rt)).grid(
            row=0, column=4, padx=4
        )
        ttk.Button(search_frame, text="Show All", command=lambda rt=record_type: self.refresh_tree(rt)).grid(
            row=0, column=5, padx=4
        )
        search_frame.columnconfigure(1, weight=1)

        columns = [field for field, _ in FIELD_LABELS[record_type]]
        tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=18)
        for field in columns:
            tree.heading(field, text=field)
            tree.column(field, width=120, anchor="w")

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        tree.bind("<<TreeviewSelect>>", lambda event, rt=record_type: self.populate_selected_record(rt))

        self.trees[record_type] = tree

    def _set_entry_value(self, entry: tk.Entry, value: object, readonly: bool = False) -> None:
        """Update an entry widget while preserving its readonly state when needed."""
        if readonly:
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, "" if value is None else str(value))
        if readonly:
            entry.configure(state="readonly")

    def _collect_form_data(self, record_type: str) -> tuple[str, dict[str, str]]:
        """Read the current form values for the selected record type."""
        entries = self.forms[record_type]
        record_id = entries["ID"].get().strip()
        payload = {
            field_name: widget.get().strip()
            for field_name, widget in entries.items()
            if field_name not in {"ID"}
        }
        return record_id, payload

    def clear_form(self, record_type: str) -> None:
        """Clear all input fields in the selected record form."""
        for field_name, entry in self.forms[record_type].items():
            self._set_entry_value(entry, "", readonly=(field_name == "ID"))

    def create_record(self, record_type: str) -> None:
        """Create a new record from the current form input."""
        _, payload = self._collect_form_data(record_type)
        try:
            created = self.manager.create_record(record_type, payload)
        except ValidationError as error:
            messagebox.showerror("Validation Error", str(error))
            return

        self.refresh_tree(record_type)
        self.clear_form(record_type)
        self._set_entry_value(self.forms[record_type]["ID"], created["ID"], readonly=True)
        messagebox.showinfo("Success", f"{DISPLAY_NAMES[record_type]} record created.")

    def update_record(self, record_type: str) -> None:
        """Update the selected record using the current form input."""
        record_id, payload = self._collect_form_data(record_type)
        if not record_id:
            messagebox.showerror("Missing ID", "Select a record before updating it.")
            return

        try:
            self.manager.update_record(record_type, int(record_id), payload)
        except (ValidationError, ValueError) as error:
            messagebox.showerror("Update Error", str(error))
            return

        self.refresh_tree(record_type)
        messagebox.showinfo("Success", f"{DISPLAY_NAMES[record_type]} record updated.")

    def delete_record(self, record_type: str) -> None:
        """Delete the selected record from the current record type tab."""
        record_id, _ = self._collect_form_data(record_type)
        if not record_id:
            messagebox.showerror("Missing ID", "Select a record before deleting it.")
            return

        try:
            self.manager.delete_record(record_type, int(record_id))
        except (ValidationError, ValueError) as error:
            messagebox.showerror("Delete Error", str(error))
            return

        self.refresh_tree(record_type)
        self.clear_form(record_type)
        messagebox.showinfo("Success", f"{DISPLAY_NAMES[record_type]} record deleted.")

    def search_records(self, record_type: str) -> None:
        """Search records and refresh the table with matching results."""
        search_term = self.search_vars[record_type]["term"].get()
        field_name = self.search_vars[record_type]["field"].get()
        selected_field = None if field_name == "All Fields" else field_name
        results = self.manager.search_records(record_type, search_term, selected_field)
        self.refresh_tree(record_type, results)

    def refresh_tree(self, record_type: str, records: list[dict] | None = None) -> None:
        """Refresh the table display for one record type."""
        tree = self.trees[record_type]
        tree.delete(*tree.get_children())

        source = records if records is not None else self.manager.get_records(record_type)
        columns = [field for field, _ in FIELD_LABELS[record_type]]
        for record in source:
            tree.insert("", tk.END, values=[record.get(column, "") for column in columns])

    def populate_selected_record(self, record_type: str) -> None:
        """Load the selected table row back into the edit form."""
        tree = self.trees[record_type]
        selection = tree.selection()
        if not selection:
            return

        item = tree.item(selection[0])
        values = item.get("values", [])
        for index, (field_name, _) in enumerate(FIELD_LABELS[record_type]):
            if field_name == "Type":
                continue
            entry = self.forms[record_type][field_name]
            self._set_entry_value(entry, values[index], readonly=(field_name == "ID"))

    def on_close(self) -> None:
        """Save records to disk before the application window closes."""
        self.storage.save_records(self.manager.get_records())
        self.root.destroy()


def launch_app() -> None:
    """Start the GUI application."""
    root = tk.Tk()
    storage_path = Path(__file__).resolve().parents[1] / "data" / "records.json"
    RecordManagementApp(root, storage_path)
    root.mainloop()
