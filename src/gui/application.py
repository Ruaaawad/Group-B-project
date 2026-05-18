"""Tkinter GUI for The Travel Agent Record Management System."""

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
        self.root = root
        self.root.title("Travel Agent Record Manager")
        self.root.geometry("1320x780")
        self.root.minsize(1120, 680)

        self._apply_theme()

        # Data layer
        self.storage = JSONStorage(storage_path)
        self.manager = RecordManager(self.storage.load_records())

        self.forms: dict[str, dict[str, tk.Entry]] = {}
        self.trees: dict[str, ttk.Treeview] = {}
        self.search_vars: dict[str, dict[str, tk.StringVar]] = {}

        self._build_header()
        self._build_status_bar()
        self._build_layout()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.set_status("Ready")

    # ---------------------- THEME ----------------------

    def _apply_theme(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        self.primary_color = "#2563EB"
        self.primary_hover = "#1D4ED8"
        self.danger_color = "#DC2626"
        self.danger_hover = "#B91C1C"
        self.background_color = "#F3F6FB"
        self.card_color = "#FFFFFF"
        self.text_color = "#111827"
        self.muted_text = "#6B7280"
        self.table_header = "#EFF4FA"

        self.root.configure(bg=self.background_color)

        style.configure(
            "TFrame",
            background=self.background_color,
        )

        style.configure(
            "TNotebook",
            background=self.background_color,
            borderwidth=0,
            padding=6,
        )

        style.configure(
            "TNotebook.Tab",
            background="#E7ECF3",
            foreground=self.muted_text,
            padding=(20, 10),
            font=("Segoe UI", 10, "bold"),
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.card_color),
                ("active", "#DBEAFE"),
            ],
            foreground=[
                ("selected", self.primary_color),
                ("active", self.primary_color),
            ],
        )

        style.configure(
            "TLabelFrame",
            background=self.card_color,
            foreground=self.text_color,
            padding=14,
        )

        style.configure(
            "TLabelFrame.Label",
            background=self.card_color,
            foreground=self.text_color,
            font=("Segoe UI", 11, "bold"),
        )

        style.configure(
            "TLabel",
            background=self.card_color,
            foreground=self.text_color,
            font=("Segoe UI", 10),
        )

        style.configure(
            "HeaderTitle.TLabel",
            background=self.primary_color,
            foreground="white",
            font=("Segoe UI", 18, "bold"),
        )

        style.configure(
            "HeaderSubtitle.TLabel",
            background=self.primary_color,
            foreground="#DBEAFE",
            font=("Segoe UI", 10),
        )

        style.configure(
            "TEntry",
            font=("Segoe UI", 10),
            padding=7,
            fieldbackground="#FFFFFF",
        )

        style.configure(
            "TCombobox",
            font=("Segoe UI", 10),
            padding=6,
            fieldbackground="#FFFFFF",
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
            background="#E5E7EB",
            foreground=self.text_color,
        )

        style.map(
            "TButton",
            background=[
                ("active", "#D1D5DB"),
                ("pressed", "#CBD5E1"),
            ],
            foreground=[
                ("active", self.text_color),
                ("pressed", self.text_color),
            ],
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
            background=self.primary_color,
            foreground="white",
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", self.primary_hover),
                ("pressed", "#1E40AF"),
            ],
            foreground=[
                ("active", "white"),
                ("pressed", "white"),
            ],
        )

        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
            background=self.danger_color,
            foreground="white",
        )

        style.map(
            "Danger.TButton",
            background=[
                ("active", self.danger_hover),
                ("pressed", "#991B1B"),
            ],
            foreground=[
                ("active", "white"),
                ("pressed", "white"),
            ],
        )

        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=32,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.text_color,
            borderwidth=1,
            relief="solid",
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#DDE7F3",
            foreground=self.text_color,
            padding=9,
            relief="raised",
            borderwidth=1,
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#BFDBFE"),
            ],
            foreground=[
                ("selected", "#111827"),
            ],
        )

        style.configure(
            "Status.TLabel",
            background="#0F172A",
            foreground="#F8FAFC",
            font=("Segoe UI", 10),
        )

    # ---------------------- HEADER ----------------------

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=self.primary_color, height=82)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = ttk.Label(
            header,
            text="Travel Agent Record Manager",
            style="HeaderTitle.TLabel",
        )
        title.pack(anchor="w", padx=24, pady=(14, 0))

        subtitle = ttk.Label(
            header,
            text="Manage client, airline, and flight records",
            style="HeaderSubtitle.TLabel",
        )
        subtitle.pack(anchor="w", padx=26, pady=(3, 0))

    # ---------------------- STATUS BAR ----------------------

    def _build_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            style="Status.TLabel",
            anchor="w",
            padding=(12, 8),
        )
        status_bar.pack(fill="x", side="bottom")

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    # ---------------------- MAIN LAYOUT ----------------------

    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=22, pady=(18, 16))

        for record_type in RECORD_TYPES:
            tab = ttk.Frame(notebook, padding=18)
            notebook.add(tab, text=f"  {DISPLAY_NAMES[record_type]}  ")
            self._build_tab(tab, record_type)
            self.refresh_tree(record_type)

    # ---------------------- TAB LAYOUT ----------------------

    def _build_tab(self, parent: ttk.Frame, record_type: str) -> None:
        parent.columnconfigure(0, weight=0, minsize=330)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        # ---------------- FORM SECTION ----------------
        form_frame = ttk.LabelFrame(
            parent,
            text=f"{DISPLAY_NAMES[record_type]} Details",
            padding=14,
        )
        form_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 14))
        form_frame.configure(width=330)

        entries: dict[str, tk.Entry] = {}
        editable_fields = [
            field for field, _ in FIELD_LABELS[record_type] if field != "Type"
        ]

        for row, field_name in enumerate(editable_fields):
            label = next(
                label
                for field, label in FIELD_LABELS[record_type]
                if field == field_name
            )

            ttk.Label(form_frame, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                pady=6,
            )

            entry = ttk.Entry(form_frame, width=24)
            entry.grid(row=row, column=1, sticky="ew", pady=5)
            entries[field_name] = entry

            if field_name == "ID":
                entry.configure(state="readonly")

        form_frame.columnconfigure(1, weight=1)
        self.forms[record_type] = entries

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(
            row=len(editable_fields),
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(16, 0),
        )

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(
            button_frame,
            text="+ Create",
            style="Primary.TButton",
            command=lambda rt=record_type: self.create_record(rt),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=4)

        ttk.Button(
            button_frame,
            text="Update",
            command=lambda rt=record_type: self.update_record(rt),
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=4)

        ttk.Button(
            button_frame,
            text="Delete",
            style="Danger.TButton",
            command=lambda rt=record_type: self.delete_record(rt),
        ).grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=4)

        ttk.Button(
            button_frame,
            text="Clear",
            command=lambda rt=record_type: self.clear_form(rt),
        ).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=4)

        # ---------------- SEARCH + TABLE SECTION ----------------
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        search_frame = ttk.LabelFrame(right_frame, text="Search Records", padding=12)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        search_term = tk.StringVar()
        field_var = tk.StringVar(value="All Fields")
        self.search_vars[record_type] = {
            "term": search_term,
            "field": field_var,
        }

        ttk.Label(search_frame, text="Search Term").grid(
            row=0,
            column=0,
            sticky="w",
        )

        ttk.Entry(
            search_frame,
            textvariable=search_term,
            width=30,
        ).grid(row=0, column=1, padx=6, sticky="ew")

        field_options = ["All Fields"] + [
            field for field, _ in FIELD_LABELS[record_type] if field != "Type"
        ]

        ttk.Label(search_frame, text="Field").grid(
            row=0,
            column=2,
            sticky="w",
        )

        ttk.Combobox(
            search_frame,
            textvariable=field_var,
            values=field_options,
            width=18,
            state="readonly",
        ).grid(row=0, column=3, padx=6)

        ttk.Button(
            search_frame,
            text="Search",
            style="Primary.TButton",
            command=lambda rt=record_type: self.search_records(rt),
        ).grid(row=0, column=4, padx=4)

        ttk.Button(
            search_frame,
            text="Show All",
            command=lambda rt=record_type: self.refresh_tree(rt),
        ).grid(row=0, column=5, padx=4)

        search_frame.columnconfigure(1, weight=1)

        # Table
        columns = self._get_display_columns(record_type)
        tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=18)
        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.tag_configure("oddrow", background="#EEF4FB")

        column_widths = {
            "ID": 70,
            "Type": 90,
            "Name": 180,
            "Full Address": 360,
            "City": 140,
            "State": 120,
            "Zip Code": 110,
            "Country": 140,
            "Phone Number": 150,
            "Company Name": 220,
            "Client_ID": 100,
            "Airline_ID": 100,
            "Date": 130,
            "Start City": 150,
            "End City": 150,
        }

        center_aligned_columns = {
            "ID",
            "Type",
            "Client_ID",
            "Airline_ID",
            "Date",
            "Zip Code",
        }

        for field in columns:
            width = column_widths.get(field, 155)
            anchor = "center" if field in center_aligned_columns else "w"

            tree.heading(field, text=field)
            tree.column(
                field,
                width=width,
                minwidth=width,
                anchor=anchor,
                stretch=False,
            )

        vertical_scrollbar = ttk.Scrollbar(
            right_frame,
            orient="vertical",
            command=tree.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            right_frame,
            orient="horizontal",
            command=tree.xview,
        )

        tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        tree.grid(row=1, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=1, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=2, column=0, sticky="ew")

        tree.bind(
            "<<TreeviewSelect>>",
            lambda event, rt=record_type: self.populate_selected_record(rt),
        )

        self.trees[record_type] = tree
    # ---------------------- FORM HELPERS ----------------------

    def _set_entry_value(
        self,
        entry: tk.Entry,
        value: object,
        readonly: bool = False,
    ) -> None:
        if readonly:
            entry.configure(state="normal")

        entry.delete(0, tk.END)
        entry.insert(0, "" if value is None else str(value))

        if readonly:
            entry.configure(state="readonly")

    def _collect_form_data(self, record_type: str) -> tuple[str, dict[str, str]]:
        entries = self.forms[record_type]
        record_id = entries["ID"].get().strip()

        payload = {
            field_name: widget.get().strip()
            for field_name, widget in entries.items()
            if field_name != "ID"
        }

        return record_id, payload

    def clear_form(self, record_type: str) -> None:
        for field_name, entry in self.forms[record_type].items():
            self._set_entry_value(entry, "", readonly=(field_name == "ID"))

        self.set_status("Form cleared.")

    # ---------------------- CRUD OPERATIONS ----------------------

    def create_record(self, record_type: str) -> None:
        _, payload = self._collect_form_data(record_type)

        try:
            self.manager.create_record(record_type, payload)
        except ValidationError as error:
            messagebox.showerror("Validation Error", str(error))
            return

        self.refresh_tree(record_type)
        self.clear_form(record_type)
        self.set_status("Record created successfully.")
        messagebox.showinfo("Success", f"{DISPLAY_NAMES[record_type]} record created.")

    def update_record(self, record_type: str) -> None:
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
        self.set_status("Record updated successfully.")
        messagebox.showinfo("Success", f"{DISPLAY_NAMES[record_type]} record updated.")

    def delete_record(self, record_type: str) -> None:
        record_id, _ = self._collect_form_data(record_type)

        if not record_id:
            messagebox.showerror("Missing ID", "Select a record before deleting it.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this record?",
        ):
            return

        try:
            self.manager.delete_record(record_type, int(record_id))
        except (ValidationError, ValueError) as error:
            messagebox.showerror("Delete Error", str(error))
            return

        self.refresh_tree(record_type)
        self.clear_form(record_type)
        self.set_status("Record deleted successfully.")
        messagebox.showinfo("Success", f"{DISPLAY_NAMES[record_type]} record deleted.")

    # ---------------------- SEARCH + TABLE ----------------------

    def search_records(self, record_type: str) -> None:
        search_term = self.search_vars[record_type]["term"].get()
        field_name = self.search_vars[record_type]["field"].get()
        selected_field = None if field_name == "All Fields" else field_name

        results = self.manager.search_records(record_type, search_term, selected_field)
        self.refresh_tree(record_type, results)
        self.set_status(f"Showing {len(results)} search result(s).")

    def _get_display_columns(self, record_type: str) -> list[str]:
        if DISPLAY_NAMES[record_type] == "Client":
            return [
                "ID",
                "Type",
                "Name",
                "Full Address",
                "City",
                "State",
                "Zip Code",
                "Country",
                "Phone Number",
            ]

        return [field for field, _ in FIELD_LABELS[record_type]]

    def _get_display_values(self, record_type: str, record: dict) -> list[object]:
        if DISPLAY_NAMES[record_type] == "Client":
            full_address = ", ".join(
                address_part
                for address_part in [
                    record.get("Address Line 1", ""),
                    record.get("Address Line 2", ""),
                    record.get("Address Line 3", ""),
                ]
                if str(address_part).strip()
            )

            return [
                record.get("ID", ""),
                record.get("Type", ""),
                record.get("Name", ""),
                full_address,
                record.get("City", ""),
                record.get("State", ""),
                record.get("Zip Code", ""),
                record.get("Country", ""),
                record.get("Phone Number", ""),
            ]

        columns = [field for field, _ in FIELD_LABELS[record_type]]
        return [record.get(column, "") for column in columns]

    def refresh_tree(
        self,
        record_type: str,
        records: list[dict] | None = None,
    ) -> None:
        tree = self.trees[record_type]
        tree.delete(*tree.get_children())

        source = records if records is not None else self.manager.get_records(record_type)

        for index, record in enumerate(source):
            values = self._get_display_values(record_type, record)
            row_tag = "evenrow" if index % 2 == 0 else "oddrow"
            tree.insert("", tk.END, values=values, tags=(row_tag,))

        self.set_status(f"Showing {len(source)} record(s).")

    # ---------------------- RECORD POPULATION ----------------------

    def populate_selected_record(self, record_type: str) -> None:
        tree = self.trees[record_type]
        selection = tree.selection()

        if not selection:
            return

        item = tree.item(selection[0])
        values = item.get("values", [])

        if not values:
            return

        selected_id = str(values[0])
        matching_record = None

        for record in self.manager.get_records(record_type):
            if str(record.get("ID", "")) == selected_id:
                matching_record = record
                break

        if matching_record is None:
            return

        for field_name, _ in FIELD_LABELS[record_type]:
            if field_name == "Type":
                continue

            entry = self.forms[record_type][field_name]
            self._set_entry_value(
                entry,
                matching_record.get(field_name, ""),
                readonly=(field_name == "ID"),
            )

        self.set_status("Record loaded into form.")

    # ---------------------- EXIT ----------------------

    def on_close(self) -> None:
        self.storage.save_records(self.manager.get_records())
        self.set_status("Saving data...")
        self.root.destroy()


def launch_app() -> None:
    root = tk.Tk()
    storage_path = Path(__file__).resolve().parents[1] / "data" / "records.json"
    RecordManagementApp(root, storage_path)
    root.mainloop()
