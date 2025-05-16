"""
Created on Thu May 15 22:37:26 2025

@author: nakkachy
"""

import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QCheckBox, QFileDialog, QMessageBox, QSpinBox,
                             QGroupBox, QFrame, QTabWidget, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype

class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

class PayoutCurveSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Payout Curve Simulator")
        self.setGeometry(100, 100, 1400, 900)
        

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTableWidget {
                font-size: 13px;
                border: 1px solid #ddd;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
            }
            QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                min-width: 100px;
                background-color: white;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
        """)
        

        self.data = None
        self.levels = 6
        self.x_values = [95, 100, 105, 110, 115, 120, 200]  # Attainment breakpoints (%)
        self.y_values = [50, 100, 120, 140, 160, 180, 200]  # Payout breakpoints (%)
        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        

        self.left_panel = QWidget()
        self.left_panel.setMaximumWidth(400)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(5, 5, 5, 5)
        self.left_layout.setSpacing(10)
        

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(5, 5, 5, 5)
        self.right_layout.setSpacing(10)
        

        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.right_panel)

        self.init_file_controls()
        self.init_level_controls()
        self.init_filter_controls()
        self.init_graph()
        self.init_results_display()
        

        self.add_separator(self.left_layout)
        

        self.statusBar().showMessage("Ready")

    def add_separator(self, layout):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
    def init_file_controls(self):

        file_group = QGroupBox("Data Source")
        file_layout = QVBoxLayout(file_group)
        

        self.file_label = QLabel("No data file loaded")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("font-style: italic; color: #666;")
        

        self.browse_button = StyledButton("Browse Excel File")
        self.browse_button.clicked.connect(self.load_excel_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.browse_button)
        self.left_layout.addWidget(file_group)
        
    def init_level_controls(self):

        level_group = QGroupBox("Payout Curve Configuration")
        level_layout = QVBoxLayout(level_group)
        

        count_group = QWidget()
        count_layout = QHBoxLayout(count_group)
        count_layout.addWidget(QLabel("Number of Levels:"))
        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(10)
        self.level_spin.setValue(self.levels)
        self.level_spin.valueChanged.connect(self.update_level_count)
        count_layout.addWidget(self.level_spin)
        count_layout.addStretch()
        level_layout.addWidget(count_group)
        

        self.level_table = QTableWidget()
        self.level_table.setColumnCount(2)
        self.level_table.setHorizontalHeaderLabels(["Attainment (%)", "Payout (%)"])
        self.level_table.horizontalHeader().setStretchLastSection(True)
        self.level_table.verticalHeader().setVisible(False)
        self.level_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        self.update_level_table()
        level_layout.addWidget(self.level_table)
        

        self.simulate_button = StyledButton("Run Simulation")
        self.simulate_button.clicked.connect(self.simulate)
        self.simulate_button.setEnabled(False)
        level_layout.addWidget(self.simulate_button)
        
        self.left_layout.addWidget(level_group)
        
    def init_filter_controls(self):

        filter_group = QGroupBox("Data Filters")
        filter_layout = QVBoxLayout(filter_group)
        


        

        

        region_group = QWidget()
        region_layout = QHBoxLayout(region_group)
        region_layout.addWidget(QLabel("Region :"))
        self.region_combo = QComboBox()
        self.region_combo.addItem("All")
        region_layout.addWidget(self.region_combo)
        filter_layout.addWidget(region_group)
        

        bu_group = QWidget()
        bu_layout = QHBoxLayout(bu_group)
        bu_layout.addWidget(QLabel("BU:"))
        self.bu_combo = QComboBox()
        self.bu_combo.addItem("All")
        bu_layout.addWidget(self.bu_combo)
        filter_layout.addWidget(bu_group)
        

        component_group = QWidget()
        component_layout = QHBoxLayout(component_group)
        component_layout.addWidget(QLabel("FrequencyPayout:"))
        self.component_combo = QComboBox()
        self.component_combo.addItem("All")
        component_layout.addWidget(self.component_combo)
        filter_layout.addWidget(component_group)
        

        self.reset_filters_button = StyledButton("Reset All Filters")
        self.reset_filters_button.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_filters_button)
        
        self.left_layout.addWidget(filter_group)
        
    def init_graph(self):

        self.graph_tabs = QTabWidget()
        self.graph_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 0px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover {
                background: #e9e9e9;
            }
        """)
        

        self.curve_tab = QWidget()
        self.curve_layout = QVBoxLayout(self.curve_tab)
        self.figure_curve = Figure(figsize=(8, 6), facecolor='none')
        self.canvas_curve = FigureCanvas(self.figure_curve)
        self.canvas_curve.setStyleSheet("background-color: transparent;")
        self.toolbar_curve = NavigationToolbar(self.canvas_curve, self)
        self.curve_layout.addWidget(self.toolbar_curve)
        self.curve_layout.addWidget(self.canvas_curve)
        self.graph_tabs.addTab(self.curve_tab, "Payout Curve")
        

        self.data_tab = QWidget()
        self.data_layout = QVBoxLayout(self.data_tab)
        self.data_preview_table = QTableWidget()
        self.data_preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_preview_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)

        

        self.analysis_tab = QWidget()
        self.analysis_layout = QVBoxLayout(self.analysis_tab)
        self.figure_analysis = Figure(figsize=(8, 6), facecolor='none')
        self.canvas_analysis = FigureCanvas(self.figure_analysis)
        self.canvas_analysis.setStyleSheet("background-color: transparent;")
        self.toolbar_analysis = NavigationToolbar(self.canvas_analysis, self)
        self.analysis_layout.addWidget(self.toolbar_analysis)
        self.analysis_layout.addWidget(self.canvas_analysis)
        self.graph_tabs.addTab(self.analysis_tab, "Analysis")
        

        self.pivot_tab = QWidget()
        self.pivot_layout = QVBoxLayout(self.pivot_tab)
        self.pivot_table = QTableWidget()
        self.pivot_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pivot_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pivot_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        scroll_area_pivot = QWidget()
        scroll_layout_pivot = QVBoxLayout(scroll_area_pivot)
        scroll_layout_pivot.addWidget(self.pivot_table)
        scroll_layout_pivot.setContentsMargins(0, 0, 0, 0)
        self.pivot_layout.addWidget(scroll_area_pivot)
        self.graph_tabs.addTab(self.pivot_tab, "Pivot Analysis")
        
        self.right_layout.addWidget(self.graph_tabs)
        
    def init_results_display(self):

        results_group = QGroupBox("Simulation Results")
        results_layout = QVBoxLayout(results_group)
        

        self.results_label = QLabel("Simulation results will appear here")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 15px;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        

        self.metrics_widget = QWidget()
        self.metrics_layout = QHBoxLayout(self.metrics_widget)
        
        self.simulated_metric = self.create_metric_widget("Simulated Earnings", "$0.00", "#4CAF50")
        self.actual_metric = self.create_metric_widget("2025 Actual Earnings", "$0.00", "#2196F3")
        self.difference_metric = self.create_metric_widget("Difference", "$0.00 (0.00%)", "#FF9800")
        
        self.metrics_layout.addWidget(self.simulated_metric)
        self.metrics_layout.addWidget(self.actual_metric)
        self.metrics_layout.addWidget(self.difference_metric)
        
        results_layout.addWidget(self.metrics_widget)
        results_layout.addWidget(self.results_label)
        
        self.right_layout.addWidget(results_group)
        
    def create_metric_widget(self, title, value, color):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("value")  
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        return widget
        
    def load_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Excel File", 
            "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            try:
            
                self.data = pd.read_excel(file_path, sheet_name="Base Work _ Simulation")
                
                
                required_columns = [
                    'CompPlanID 2025', 'ComponentName 2025', 'Region ', 'BU',
                    'Attainment', 'FY TIN (USD)', 'Earn Scenario 2025', 'PayeeID'
                ]
                
             
                has_scenario1 = 'Earn Scenario 1' in self.data.columns
                has_scenario2 = 'Earn Scenario 2' in self.data.columns
                
                missing_columns = [col for col in required_columns if col not in self.data.columns]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
                self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
                self.file_label.setStyleSheet("font-style: normal; color: #4CAF50;")
                self.simulate_button.setEnabled(True)
                
                status_msg = f"Loaded {len(self.data)} records"
                if has_scenario1:
                    status_msg += " (with Scenario 1)"
                if has_scenario2:
                    status_msg += " (with Scenario 2)"
                self.statusBar().showMessage(status_msg, 5000)
                
              
                self.update_filter_options()
                
            
                self.update_data_preview()
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to load Excel file:\n{str(e)}"
                )
                self.statusBar().showMessage("Error loading file", 5000)
                self.data = None
                self.simulate_button.setEnabled(False)
    
    def update_data_preview(self):
        if self.data is not None:
            
            has_simulation = 'Payout_Percentage' in self.data.columns and 'Simulated_Earn' in self.data.columns
            
           
            base_cols = self.data.shape[1]
            extra_cols = 2 if has_simulation else 0
            self.data_preview_table.setColumnCount(base_cols + extra_cols)
            
            
            headers = list(self.data.columns)
            if has_simulation:
                headers.extend(['Simulated Payout %', 'Simulated Earnings'])
            self.data_preview_table.setHorizontalHeaderLabels(headers)
            
            
            rows = min(self.data.shape[0], 1000)  # Limit to 1000 rows for performance
            self.data_preview_table.setRowCount(rows)
            
            for i in range(rows):
               
                for j in range(self.data.shape[1]):
                    item = QTableWidgetItem(str(self.data.iloc[i, j]))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                    self.data_preview_table.setItem(i, j, item)
                
              
                if has_simulation:
                    # Payout Percentage
                    payout_item = QTableWidgetItem(f"{self.data.iloc[i]['Payout_Percentage']:.2f}%")
                    payout_item.setFlags(payout_item.flags() & ~Qt.ItemIsEditable)
                    self.data_preview_table.setItem(i, base_cols, payout_item)
                    

                    earn_item = QTableWidgetItem(f"${self.data.iloc[i]['Simulated_Earn']:,.2f}")
                    earn_item.setFlags(earn_item.flags() & ~Qt.ItemIsEditable)
                    self.data_preview_table.setItem(i, base_cols + 1, earn_item)
            

            self.data_preview_table.resizeColumnsToContents()
            

            if self.data.shape[0] > 1000:
                self.statusBar().showMessage(f"Showing first 1000 rows of {self.data.shape[0]} total rows", 5000)
    
    def update_filter_options(self):
        if self.data is not None:



            

            self.region_combo.clear()
            self.region_combo.addItem("All")
            self.region_combo.addItems(sorted(self.data['Region '].astype(str).unique()))
            

            self.bu_combo.clear()
            self.bu_combo.addItem("All")
            self.bu_combo.addItems(sorted(self.data['BU'].astype(str).unique()))
            

            self.component_combo.clear()
            self.component_combo.addItem("All")
            self.component_combo.addItems(sorted(self.data['FrequencyPayout'].astype(str).unique()))
    
    def reset_filters(self):
        """Reset all filter comboboxes to 'All'"""
        self.comp_plan_combo.setCurrentIndex(0)  # 'All'
        self.country_combo.setCurrentIndex(0)     # 'All'
        self.region_combo.setCurrentIndex(0)      # 'All'
        self.bu_combo.setCurrentIndex(0)          # 'All'
        self.component_combo.setCurrentIndex(0)    # 'All'
        self.statusBar().showMessage("All filters reset", 3000)
        

        if self.simulate_button.isEnabled():
            self.simulate()
    
    def update_level_count(self):
        self.levels = self.level_spin.value()
        

        if len(self.x_values) < self.levels + 1:

            last_x = self.x_values[-1]
            last_y = self.y_values[-1]
            for i in range(len(self.x_values), self.levels + 1):
                self.x_values.append(last_x + 5)  # Adding 5% increments by default
                self.y_values.append(last_y + 20)  # Adding 20% payout increments by default
        elif len(self.x_values) > self.levels + 1:

            self.x_values = self.x_values[:self.levels + 1]
            self.y_values = self.y_values[:self.levels + 1]
        
        self.update_level_table()
    
    def update_level_table(self):
        self.level_table.setRowCount(self.levels + 1)
        
        for i in range(self.levels + 1):

            x_item = QTableWidgetItem(str(self.x_values[i]))
            self.level_table.setItem(i, 0, x_item)
            

            y_item = QTableWidgetItem(str(self.y_values[i]))
            self.level_table.setItem(i, 1, y_item)
    
    def get_level_values(self):
        x_values = []
        y_values = []
        
        for i in range(self.level_table.rowCount()):
            x_item = self.level_table.item(i, 0)
            y_item = self.level_table.item(i, 1)
            
            if x_item and y_item:
                try:
                    x = float(x_item.text())
                    y = float(y_item.text())
                    x_values.append(x)
                    y_values.append(y)
                except ValueError:
                    QMessageBox.warning(
                        self, 
                        "Invalid Input", 
                        "Please enter valid numbers for all levels"
                    )
                    return None, None
        

        if x_values and x_values[0] < 95:
            x_values[0] = 95
            self.level_table.item(0, 0).setText("95")
        
        return x_values, y_values
    
    def calculate_payout(self, attainment_decimal, x_values, y_values):
        """
        Calculate payout percentage based on attainment decimal.
        attainment_decimal: The attainment value from data (e.g., 0.9 for 90%)
        x_values: List of attainment breakpoints (in percentages, e.g., [95, 100, 105])
        y_values: List of payout breakpoints (in percentages, e.g., [50, 100, 120])
        """

        attainment_percentage = attainment_decimal * 100
        

        if attainment_percentage >= 200:
            return 300
        

        if attainment_percentage < 95:
            return 0
        

        for i in range(len(x_values)):
            if abs(attainment_percentage - x_values[i]) < 0.0001:  
                return y_values[i]
        

        for i in range(len(x_values) - 1):
            if x_values[i] < attainment_percentage < x_values[i+1]:

                return y_values[i] + (attainment_percentage - x_values[i]) * \
                       (y_values[i+1] - y_values[i]) / (x_values[i+1] - x_values[i])
        

        return y_values[-1]

    def simulate(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load an Excel file first")
            return
        
        x_values, y_values = self.get_level_values()
        if not x_values or not y_values:
            return
        

        filtered_data = self.data.copy()
        


        if self.region_combo.currentText() != "All":
            filtered_data = filtered_data[filtered_data['Region '].astype(str) == self.region_combo.currentText()]
        
        if self.bu_combo.currentText() != "All":
            filtered_data = filtered_data[filtered_data['BU'].astype(str) == self.bu_combo.currentText()]
        
        if self.component_combo.currentText() != "All":
            filtered_data = filtered_data[filtered_data['FrequencyPayout'].astype(str) == self.component_combo.currentText()]
        
        if filtered_data.empty:
            QMessageBox.warning(self, "No Data", "No records match the selected filters")
            return
        

        filtered_data['Payout_Percentage'] = filtered_data['Attainment'].apply(
            lambda x: self.calculate_payout(x, x_values, y_values))
        

        filtered_data['Simulated_Earn'] = filtered_data['FY TIN (USD)'] * (filtered_data['Payout_Percentage'] / 100)
        

        self.data = filtered_data

        total_simulated = filtered_data['Simulated_Earn'].sum()
        total_actual = filtered_data['Earn Scenario 2025'].sum()

        has_scenario1 = 'Earn Scenario 1' in filtered_data.columns
        has_scenario2 = 'Earn Scenario 2' in filtered_data.columns
        
        total_scenario1 = filtered_data['Earn Scenario 1'].sum() if has_scenario1 else 0
        total_scenario2 = filtered_data['Earn Scenario 2'].sum() if has_scenario2 else 0
        

        delta_actual = total_simulated - total_actual
        delta_scenario1 = total_simulated - total_scenario1 if has_scenario1 else 0
        delta_scenario2 = total_simulated - total_scenario2 if has_scenario2 else 0
        

        self.update_results_display(total_simulated, total_actual, delta_actual, 
                                  total_scenario1, delta_scenario1,
                                  total_scenario2, delta_scenario2,
                                  has_scenario1, has_scenario2)
        

        self.plot_payout_curve(x_values, y_values)
        

        self.plot_analysis_chart(total_simulated, total_actual, 
                                total_scenario1, total_scenario2,
                                delta_actual, delta_scenario1, delta_scenario2,
                                has_scenario1, has_scenario2)
        

        self.generate_pivot_analysis(filtered_data, x_values)
        

        self.update_data_preview()
        

        self.statusBar().showMessage(f"Simulation completed with {len(filtered_data)} records", 5000)

    def update_results_display(self, simulated, actual, delta_actual,
                             scenario1, delta_scenario1,
                             scenario2, delta_scenario2,
                             has_scenario1, has_scenario2):

        results_text = (f"<b>Simulation Results</b><br><br>"
                       f"<b>Total Simulated Earnings:</b> ${simulated:,.2f}<br>"
                       f"<b>Total 2025 Actual Earnings:</b> ${actual:,.2f} (Δ: ${delta_actual:,.2f})<br>")
        
        if has_scenario1:
            results_text += f"<b>Total Scenario 1 Earnings:</b> ${scenario1:,.2f} (Δ: ${delta_scenario1:,.2f})<br>"
        if has_scenario2:
            results_text += f"<b>Total Scenario 2 Earnings:</b> ${scenario2:,.2f} (Δ: ${delta_scenario2:,.2f})<br>"
        
        self.results_label.setText(results_text)
        

        self.simulated_metric.findChild(QLabel, "value").setText(f"${simulated:,.2f}")
        self.actual_metric.findChild(QLabel, "value").setText(f"${actual:,.2f}")
        self.difference_metric.findChild(QLabel, "value").setText(
            f"${delta_actual:,.2f}<br>({(delta_actual/actual*100):+.2f}%)" if actual != 0 else "N/A"
        )

    def plot_payout_curve(self, x_values, y_values):
        self.figure_curve.clear()
        ax = self.figure_curve.add_subplot(111)
        
        # Set background color
        ax.set_facecolor('#f9f9f9')
        self.figure_curve.set_facecolor('none')
        
        # Generate points for smooth curve
        x_plot = [0, 94.999]  # Before threshold
        y_plot = [0, 0]
        
        # Add breakpoints
        for i in range(len(x_values)):
            x_plot.append(x_values[i])
            y_plot.append(y_values[i])
            
            # Add midpoint for smooth curve
            if i < len(x_values) - 1:
                x_plot.append((x_values[i] + x_values[i+1]) / 2)
                y_plot.append((y_values[i] + y_values[i+1]) / 2)
        
        # Add cap
        x_plot.extend([200, 250])
        y_plot.extend([300, 300])
        
        # Plot main curve
        ax.plot(x_plot, y_plot, color='#4CAF50', linewidth=2.5, label='Payout Curve')
        
        # Plot breakpoints
        ax.scatter(x_values, y_values, color='red', s=80, label='Breakpoints', zorder=5)
        
        # Add markers
        ax.axvline(x=95, color='blue', linestyle=':', alpha=0.7)
        ax.text(96, 10, 'Minimum 95%', color='blue')
        
        ax.axhline(y=300, color='orange', linestyle='--', alpha=0.7)
        ax.text(150, 310, '300% Cap', color='orange')
        
        # Styling
        ax.set_xlabel('Attainment (%)', fontsize=12)
        ax.set_ylabel('Payout (%)', fontsize=12)
        ax.set_title('Payout Curve Simulation', fontsize=14, pad=20)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper left')
        ax.set_xlim(0, 220)
        ax.set_ylim(0, 320)
        
        self.canvas_curve.draw()

    def plot_analysis_chart(self, simulated, actual, scenario1, scenario2,
                          delta_actual, delta_scenario1, delta_scenario2,
                          has_scenario1, has_scenario2):
        self.figure_analysis.clear()
        ax = self.figure_analysis.add_subplot(111)
        
        # Set background color
        ax.set_facecolor('#f9f9f9')
        self.figure_analysis.set_facecolor('none')
        
        # Prepare data for plotting
        scenarios = ['Simulated', 'Actual 2025']
        values = [simulated, actual]
        deltas = [0, delta_actual]
        colors = ['#4CAF50', '#2196F3']  # Green, Blue
        
        if has_scenario1:
            scenarios.append('Scenario 1')
            values.append(scenario1)
            deltas.append(delta_scenario1)
            colors.append('#FF9800')  # Orange
        
        if has_scenario2:
            scenarios.append('Scenario 2')
            values.append(scenario2)
            deltas.append(delta_scenario2)
            colors.append('#9C27B0')  # Purple
        
        # Create bars
        x = range(len(scenarios))
        bars = ax.bar(x, values, color=colors)
        
        # Add delta annotations
        for i, (val, delta) in enumerate(zip(values, deltas)):
            if delta != 0:  # Skip simulated (no delta)
                ax.text(i, val + (0.05 * max(values)), 
                       f"Δ: ${delta:,.2f}",
                       ha='center', va='bottom', fontsize=10,
                       bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        

        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)
        ax.set_ylabel('Earnings (USD)')
        ax.set_title('Earnings Scenario Comparison', fontsize=14, pad=20)
        ax.grid(True, linestyle='--', alpha=0.6, axis='y')
        

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.2f}',
                    ha='center', va='bottom', fontsize=10)
        

        if len(scenarios) > 2:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.canvas_analysis.draw()

    def generate_pivot_analysis(self, data, x_values):
        """Generate pivot table showing payee distribution by tier and earnings"""
        if data is None or len(data) == 0:
            return
            

        x_values_sorted = sorted(x_values)
        

        bins = [0] + x_values_sorted + [float('inf')]
        labels = [f"<{x_values_sorted[0]}%"] + \
                 [f"{x_values_sorted[i]}-{x_values_sorted[i+1]}%" for i in range(len(x_values_sorted)-1)] + \
                 [f"≥{x_values_sorted[-1]}%"]
        

        data['Attainment Tier'] = pd.cut(data['Attainment'] * 100,  # Convert decimal to %
                                        bins=bins,
                                        labels=labels,
                                        right=False)
        

        pivot_data = data[data['Earn Scenario 2025'] > 0].groupby('Attainment Tier').agg({
            'PayeeID': 'nunique',
            'Earn Scenario 2025': 'sum',
            'Simulated_Earn': 'sum',
            'Earn Scenario 1': 'sum' if 'Earn Scenario 1' in data.columns else None,
            'Earn Scenario 2': 'sum' if 'Earn Scenario 2' in data.columns else None
        }).reset_index()

        if 'Earn Scenario 1' in pivot_data.columns:
            pivot_data['Delta vs Scenario 1'] = pivot_data['Simulated_Earn'] - pivot_data['Earn Scenario 1']
        if 'Earn Scenario 2' in pivot_data.columns:
            pivot_data['Delta vs Scenario 2'] = pivot_data['Simulated_Earn'] - pivot_data['Earn Scenario 2']

        currency_cols = [col for col in pivot_data.columns if 'Earn' in col or 'Delta' in col]
        for col in currency_cols:
            if col in pivot_data.columns:
                pivot_data[col] = pivot_data[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
        

        self.update_pivot_table(pivot_data)

    def update_pivot_table(self, pivot_data):
        """Update the pivot table widget with the calculated data"""
        self.pivot_table.clear()
        
        if pivot_data is None or len(pivot_data) == 0:
            return
            

        rows, cols = pivot_data.shape
        self.pivot_table.setRowCount(rows + 1)  # +1 for totals row
        self.pivot_table.setColumnCount(cols)
        

        self.pivot_table.setHorizontalHeaderLabels(pivot_data.columns)
        

        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(str(pivot_data.iloc[i, j]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.pivot_table.setItem(i, j, item)
        

        totals_item = QTableWidgetItem("Totals")
        totals_item.setFlags(totals_item.flags() & ~Qt.ItemIsEditable)
        self.pivot_table.setItem(rows, 0, totals_item)
        

        for j in range(1, cols):
            try:
                if pivot_data.columns[j] == 'PayeeID':
                    total = pivot_data.iloc[:, j].sum()
                    item = QTableWidgetItem(str(total))
                else:
                    # Extract numbers from currency strings
                    nums = [float(str(x).replace('$', '').replace(',', '')) 
                           for x in pivot_data.iloc[:, j] if str(x).startswith('$')]
                    if nums:
                        total = sum(nums)
                        item = QTableWidgetItem(f"${total:,.2f}")
                    else:
                        item = QTableWidgetItem("")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.pivot_table.setItem(rows, j, item)
            except:
                item = QTableWidgetItem("")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.pivot_table.setItem(rows, j, item)
        

        self.pivot_table.resizeColumnsToContents()

def main():

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = PayoutCurveSimulator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
