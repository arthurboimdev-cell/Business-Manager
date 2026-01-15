import pytest
import tkinter as tk

@pytest.fixture(scope="session")
def tk_root():
    """Create a single shared Tk root window for the entire test session."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass

@pytest.fixture(autouse=True)
def mock_messagebox(monkeypatch):
    """Prevent GUI popups during tests by mocking messagebox."""
    from tkinter import messagebox
    
    # Mock all common messagebox functions
    monkeypatch.setattr(messagebox, "showinfo", lambda *args, **kwargs: None)
    monkeypatch.setattr(messagebox, "showwarning", lambda *args, **kwargs: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: None)
    monkeypatch.setattr(messagebox, "askyesno", lambda *args, **kwargs: True)
    monkeypatch.setattr(messagebox, "askokcancel", lambda *args, **kwargs: True)
    monkeypatch.setattr(messagebox, "askretrycancel", lambda *args, **kwargs: False)

