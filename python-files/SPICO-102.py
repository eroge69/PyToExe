from __future__ import annotations

"""Enhanced Serial Control GUI

Highlights of this redesign
---------------------------
* Modern QMainWindow layout with menu, toolbar, status‑bar
* QSplitter + QTabWidget organization for clear, resizable panes
* Real‑time register view alongside a live terminal‑style log
* Quick command entry line + history
* Dynamic port list with refresh
* Logging to file
* Cleaner separation of worker thread / UI logic

This file can be run directly (Python 3.9+, PyQt6, pyserial)."""

import sys
import threading
import time
import queue
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import serial  # PySerial
from serial.serialutil import SerialException

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QListWidget,
    QMessageBox, QGroupBox, QGridLayout, QLineEdit, QSizePolicy, QSplitter,
    QTabWidget, QPlainTextEdit, QFileDialog, QStatusBar, QToolBar
)

# --------------------------- Constants -----------------------------------------
SERIAL_BAUD = 19200
SERIAL_BYTESIZE = serial.EIGHTBITS
SERIAL_PARITY = serial.PARITY_NONE
SERIAL_STOPBITS = serial.STOPBITS_ONE
POLL_INTERVAL_MS = 500
BIT_COUNT = 16
HEX_RE = re.compile(r"0x([0-9A-Fa-f]{1,4})")

REGISTER_ORDER = ["1004", "2004"]

# --------------------------- Module Data ---------------------------------------
@dataclass
class Module:
    name: str
    commands: Dict[str, List[str]]
    bits: Dict[str, List[int]] = field(default_factory=dict)

MODULES: List[Module] = [
    Module(
        name="DCLS",
        commands={"activate": [], "deactivate": []},
        bits={"1004": [3], "2004": [3]},
    ),
    Module(
        name="TIS",
        commands={"activate": ["w 0002 0x1B00"], "deactivate": []},
        bits={"1004": [4], "2004": [4]},
    ),
    Module(
        name="VOBCAC",
        commands={"activate": ["w 1002 0x0800"], "deactivate": ["w 1002 0x0000"]},
        bits={"1004": [11]},
    ),
    Module(
        name="EBRC1",
        commands={"activate": ["w 1002 0x0801"], "deactivate": ["w 1002 0x0800"]},
        bits={"1004": [0], "2004": [12]},
    ),
    Module(
        name="EBRC2",
        commands={"activate": ["w 2002 0x0100"], "deactivate": ["w 2002 0x0000"]},
        bits={"1004": [0], "2004": [12]},
    ),
    Module(
        name="PEC",
        commands={
            "activate": ["w 1002 0x0808", "w 2002 0x0800"],
            "deactivate": ["w 1002 0x0000", "w 2002 0x0000"],
        },
        bits={"2004": [14]},
    ),
    Module(
        name="DELC",
        commands={
            "activate": ["w 1002 0x0820", "w 2002 0x2000"],
            "deactivate": ["w 1002 0x0000", "w 2002 0x0000"],
        },
        bits={"1004": [7]},
    ),
    Module(
        name="DERC",
        commands={
            "activate": ["w 1002 0x0810", "w 2002 0x1000"],
            "deactivate": ["w 1002 0x0000", "w 2002 0x0000"],
        },
        bits={"2004": [7]},
    ),
    Module(
        name="AUC",
        commands={
            "activate": ["w 1002 0x0004", "w 2002 0x0010"],
            "deactivate": ["w 1002 0x0000", "w 2002 0x0000"],
        },
        bits={"2004": [10]},
    ),
    Module(
        name="FWDC",
        commands={"activate": ["w 1002 0x0900"], "deactivate": ["w 1002 0x0000"]},
        bits={"1004": [13]},
    ),
    Module(
        name="REVC",
        commands={
            "activate": ["w 1002 0x0800", "w 2002 0x0001"],
            "deactivate": ["w 1002 0x0000", "w 2002 0x0000"],
        },
        bits={"2004": [13]},
    ),
    Module(
        name="VOBCRPC",
        commands={"activate": ["w D001 0x0001"], "deactivate": ["w D001 0x0000"]},
        bits={"2004": [15]},
    ),
    Module(
        name="VOBCRC",
        commands={"activate": ["w 1002 0x2000"], "deactivate": ["w 1002 0x0000"]},
        bits={},
    ),
    Module(
        name="DARS",
        commands={"activate": [], "deactivate": []},
        bits={"1004": [9]},
    ),
]


# --------------------------- Serial Worker -------------------------------------
class SerialWorker(QObject):
    """Background thread handling serial I/O."""

    received = pyqtSignal(str)  # decoded line
    status = pyqtSignal(str)    # port‑level status messages

    def __init__(self, port_name: str):
        super().__init__()
        self._port_name = port_name
        self._running = threading.Event()
        self._tx_queue: "queue.Queue[str]" = queue.Queue()
        self._port: Optional[serial.Serial] = None

    # ---------------- Public API -----------------
    def start(self) -> bool:
        try:
            self._port = serial.Serial(
                self._port_name,
                baudrate=SERIAL_BAUD,
                bytesize=SERIAL_BYTESIZE,
                parity=SERIAL_PARITY,
                stopbits=SERIAL_STOPBITS,
                timeout=1.0,
                write_timeout=1.0,
            )
        except SerialException as exc:
            self.status.emit(f"Error opening port: {exc}")
            return False

        self._running.set()
        threading.Thread(target=self._rx_loop, daemon=True).start()
        threading.Thread(target=self._tx_loop, daemon=True).start()
        self.status.emit("CONNECTED")
        return True

    def stop(self):
        self._running.clear()
        if self._port and self._port.is_open:
            try:
                self._port.close()
            except SerialException:
                pass
        self.status.emit("DISCONNECTED")

    def send(self, line: str):
        if not self._running.is_set():
            self.status.emit("Port not open – cannot send")
            return
        self._tx_queue.put(line.strip() + "\r")

    # --------------- Internal loops -------------
    def _rx_loop(self):
        assert self._port is not None
        while self._running.is_set():
            try:
                raw = self._port.readline()
            except SerialException:
                self.status.emit("Serial read error – stopping")
                break
            if raw:
                try:
                    decoded = raw.decode(errors="replace").strip()
                except UnicodeDecodeError:
                    continue
                self.received.emit(decoded)
        self._running.clear()

    def _tx_loop(self):
        assert self._port is not None
        while self._running.is_set():
            try:
                line = self._tx_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                self._port.write(line.encode())
            except SerialException:
                self.status.emit("Serial write error – stopping")
                self._running.clear()
                break

# --------------------------- Main Window ---------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Serial Control")
        self.resize(1200, 700)

        self.worker: Optional[SerialWorker] = None
        self.register_values: Dict[str, int] = {reg: 0 for reg in REGISTER_ORDER}
        self.highlight_bits: Dict[str, List[int]] = {reg: [] for reg in REGISTER_ORDER}
        self._register_toggle = False  # alternating read flag

        # --- central UI components
        self._build_ui()

        # --- poll timer
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(POLL_INTERVAL_MS)
        self._poll_timer.timeout.connect(self._poll_cycle)

    # --------------------------------------------------------------------- UI --
    def _build_ui(self):
        self._create_actions()
        self._create_menubar_and_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # left side – quick actions & modules
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)

        # ---- Connection box
        conn_box = QGroupBox("Connection")
        cl = QHBoxLayout(conn_box)
        self.port_selector = QComboBox()
        self._refresh_ports()
        self.btn_refresh_ports = QPushButton("⟳")
        self.btn_refresh_ports.setFixedWidth(32)
        self.btn_refresh_ports.clicked.connect(self._refresh_ports)
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self._toggle_connection)
        cl.addWidget(QLabel("Port:"))
        cl.addWidget(self.port_selector)
        cl.addWidget(self.btn_refresh_ports)
        cl.addWidget(self.btn_connect)
        left_layout.addWidget(conn_box)

        # ---- Quick actions
        qa_box = QGroupBox("Quick Actions")
        qa_grid = QGridLayout(qa_box)
        btn_setup_env = QPushButton("1. Setup Environment")
        btn_setup_env.clicked.connect(self._do_setup_env)
        qa_grid.addWidget(btn_setup_env, 0, 0, 1, 2)
        # replicas
        rep_buttons = [
            ("2‑A. Setup Replica 1", 1),
            ("2‑B. Setup Replica 2", 2),
            ("2‑C. Setup Replica 3", 3),
        ]
        for col, (text, idx) in enumerate(rep_buttons):
            btn = QPushButton(text)
            btn.clicked.connect(lambda _=False, n=idx: self._do_setup_replica(n))
            qa_grid.addWidget(btn, 1, col)
        btn_enable_sys = QPushButton("3. Enable System")
        btn_enable_sys.clicked.connect(self._do_enable_system)
        qa_grid.addWidget(btn_enable_sys, 2, 0, 1, 2)
        left_layout.addWidget(qa_box)

        # ---- Modules
        mod_box = QGroupBox("Modules")
        ml = QVBoxLayout(mod_box)
        self.module_list = QListWidget()
        self.module_list.addItems([m.name for m in MODULES])
        ml.addWidget(self.module_list)
        btn_row = QHBoxLayout()
        btn_act = QPushButton("Activate")
        btn_deact = QPushButton("Deactivate")
        btn_act.clicked.connect(lambda: self._module_action("activate"))
        btn_deact.clicked.connect(lambda: self._module_action("deactivate"))
        btn_row.addWidget(btn_act)
        btn_row.addWidget(btn_deact)
        ml.addLayout(btn_row)
        left_layout.addWidget(mod_box)
        left_layout.addStretch()

        # right side – tabs
        right_tabs = QTabWidget()

        # ---- Registers tab
        reg_tab = QWidget()
        reg_layout = QVBoxLayout(reg_tab)
        self.table_regs = QTableWidget(len(REGISTER_ORDER), 2 + BIT_COUNT)
        self.table_regs.setHorizontalHeaderLabels(["Register", "Hex"] + [str(i) for i in range(BIT_COUNT - 1, -1, -1)])
        self.table_regs.verticalHeader().setVisible(False)
        for row, reg in enumerate(REGISTER_ORDER):
            self.table_regs.setItem(row, 0, QTableWidgetItem(reg))
            for col in range(2, 2 + BIT_COUNT):
                itm = QTableWidgetItem("0")
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_regs.setItem(row, col, itm)
        self.table_regs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        reg_layout.addWidget(self.table_regs)
        right_tabs.addTab(reg_tab, "Registers")

        # ---- Terminal tab
        term_tab = QWidget()
        term_layout = QVBoxLayout(term_tab)
        self.txt_terminal = QPlainTextEdit()
        self.txt_terminal.setReadOnly(True)
        term_layout.addWidget(self.txt_terminal)
        # command entry
        cmd_row = QHBoxLayout()
        self.line_cmd = QLineEdit()
        self.line_cmd.setPlaceholderText("Enter raw command and press ↵…")
        self.line_cmd.returnPressed.connect(self._send_manual_cmd)
        cmd_row.addWidget(self.line_cmd)
        term_layout.addLayout(cmd_row)
        right_tabs.addTab(term_tab, "Terminal")

        # --- assemble splitter
        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_tabs)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

    # ---------------------- Menus & Toolbar ---------------------------
    def _create_actions(self):
        self.act_save_log = QAction("Save Log…", self)
        self.act_save_log.triggered.connect(self._save_log)

        self.act_clear_log = QAction("Clear Log", self)
        self.act_clear_log.triggered.connect(lambda: self.txt_terminal.clear())

        self.act_exit = QAction("Exit", self)
        self.act_exit.triggered.connect(self.close)

    def _create_menubar_and_toolbar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.act_save_log)
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)

        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.act_clear_log)

        toolbar = QToolBar("Main", self)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.addAction(self.act_save_log)
        toolbar.addAction(self.act_clear_log)
        self.addToolBar(toolbar)

    # ---------------------- Port Handling ----------------------------
    def _refresh_ports(self):
        from serial.tools import list_ports
        current = self.port_selector.currentText()
        self.port_selector.clear()
        ports = [p.device for p in list_ports.comports()]
        self.port_selector.addItems(ports)
        if current in ports:
            self.port_selector.setCurrentText(current)

    def _toggle_connection(self):
        if self.worker:  # disconnect
            self._disconnect()
        else:  # connect
            port = self.port_selector.currentText().strip()
            if not port:
                QMessageBox.warning(self, "No port", "Select a port first")
                return
            self.worker = SerialWorker(port)
            self.worker.received.connect(self._on_serial_line)
            self.worker.status.connect(self._on_serial_status)
            if self.worker.start():
                self.btn_connect.setText("Disconnect")
                self._poll_timer.start()
            else:
                self.worker = None

    def _disconnect(self):
        self._poll_timer.stop()
        if self.worker:
            self.worker.stop()
        self.worker = None
        self.btn_connect.setText("Connect")
        self.status_bar.showMessage("Disconnected", 5000)

    # ---------------------- Serial handlers -------------------------
    def _on_serial_line(self, line: str):
        self.txt_terminal.appendPlainText(line)
        m = HEX_RE.search(line)
        if m:
            value = int(m.group(1), 16)
            reg = "1004" if not self._register_toggle else "2004"
            self._register_toggle = not self._register_toggle
            self.register_values[reg] = value
            self._refresh_table()

    def _on_serial_status(self, msg: str):
        self.status_bar.showMessage(msg, 5000)
        self.txt_terminal.appendPlainText(f"# {msg}")

    # ---------------------- Table refresh ---------------------------
    def _refresh_table(self):
        for row, reg in enumerate(REGISTER_ORDER):
            value = self.register_values[reg]
            self.table_regs.setItem(row, 1, QTableWidgetItem(f"0x{value:04X}"))
            for bit in range(BIT_COUNT):
                col = 2 + (BIT_COUNT - 1 - bit)
                bit_val = (value >> bit) & 1
                itm = self.table_regs.item(row, col)
                if itm is None:
                    itm = QTableWidgetItem("0")
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_regs.setItem(row, col, itm)
                itm.setText(str(bit_val))
                # highlight bits of interest
                if bit in self.highlight_bits.get(reg, []):
                    color = Qt.GlobalColor.yellow if bit_val else Qt.GlobalColor.red
                    itm.setBackground(color)
                else:
                    itm.setBackground(Qt.GlobalColor.white)

    # ---------------------- Poll cycle ------------------------------
    def _poll_cycle(self):
        if not self.worker:
            return
        for reg in REGISTER_ORDER:
            self.worker.send(f"r {reg}")
            time.sleep(0.05)  # slight spacing
            self.worker.send("#")
            time.sleep(0.05)

    # ---------------------- Command helpers ------------------------
    def _send_sequence(self, seq: List[str]):
        if not self.worker:
            QMessageBox.warning(self, "Not connected", "Connect first")
            return
        self._poll_timer.stop()
        for cmd in seq:
            self.worker.send(cmd)
            time.sleep(0.15)
        self._poll_timer.start()

    def _do_setup_env(self):
        seq = ["ton", "w 0005 0x0001", "w 1000 0x0001", "w 2000 0x0001", "w 3000 0x0001"]
        self._send_sequence(seq)

    def _do_setup_replica(self, n: int):
        if n == 1:
            seq = ["w 0001 0x000F", "w 0008 0x0000", "enablepcm"]
        elif n == 2:
            seq = ["w 0001 0x002F", "w 0008 0x00D0", "enablepcm"]
        else:
            seq = ["w 0001 0x000A", "w 0008 0x0005", "enablepcm"]
        self._send_sequence(seq)

    def _do_enable_system(self):
        self._send_sequence(["w 0002 0x1F00", "w 0003 0x1F00"])

    def _module_action(self, action: str):
        sel = self.module_list.currentItem()
        if not sel:
            QMessageBox.information(self, "No selection", "Select a module first")
            return
        mod_name = sel.text()
        mod = next((m for m in MODULES if m.name == mod_name), None)
        if not mod or action not in mod.commands:
            QMessageBox.warning(self, "Not implemented", f"No {action} for {mod_name}")
            return
        self.highlight_bits = {reg: bits for reg, bits in mod.bits.items()}
        self._send_sequence(mod.commands[action])

    # ---------------------- Manual command -------------------------
    def _send_manual_cmd(self):
        cmd = self.line_cmd.text().strip()
        if cmd and self.worker:
            self.worker.send(cmd)
            self.line_cmd.clear()

    # ---------------------- Utilities ------------------------------
    def _save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", "serial_log.txt", "Text Files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.txt_terminal.toPlainText())
            self.status_bar.showMessage(f"Log saved to {path}", 5000)
        except OSError as exc:
            QMessageBox.warning(self, "Error", str(exc))

# --------------------------- main ---------------------------------------------

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()