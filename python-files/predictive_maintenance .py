import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import tkinter as tk
from tkinter import messagebox
import re

class PredictiveMaintenanceSystem:
    def __init__(self):
        self.config = {
            'window_size': 50,
            'step_size': 25,
            'batch_size': 64,
            'learning_rate': 0.001,
            'max_epochs': 200,
            'validation_split': 0.2,
            'patience': 10
        }
        self.class_names = ['STOP', 'NEW', 'OLD']
        self.X_train = self.X_test = self.y_train = self.y_test = None
        self.model = None

    def generate_peristaltic_pump_data(self, num_samples=5000):
        columns = ['class', 'accel_x', 'accel_y', 'accel_z', 
                  'gyro_x', 'gyro_y', 'gyro_z',
                  'magnet_x', 'magnet_y', 'magnet_z']

        np.random.seed(42)
        data = {col: [] for col in columns}
        classes = np.random.choice(['STOP', 'NEW', 'OLD'], num_samples, p=[0.3, 0.35, 0.35])

        for pump_class in classes:
            if pump_class == 'STOP':
                data['accel_x'].append(np.random.normal(0, 0.05))
                data['accel_y'].append(np.random.normal(0, 0.05))
                data['accel_z'].append(np.random.normal(-0.95, 0.02))
                data['gyro_x'].append(np.random.normal(0, 0.01))
                data['gyro_y'].append(np.random.normal(0, 0.01))
                data['gyro_z'].append(np.random.normal(0, 0.01))
                data['magnet_x'].append(np.random.normal(0, 0.005))
                data['magnet_y'].append(np.random.normal(0, 0.005))
                data['magnet_z'].append(np.random.normal(1.0, 0.005))
            elif pump_class == 'NEW':
                data['accel_x'].append(np.random.normal(0.1, 0.1))
                data['accel_y'].append(np.random.normal(0.1, 0.1))
                data['accel_z'].append(np.random.normal(-0.95, 0.05))
                data['gyro_x'].append(np.random.normal(0.02, 0.05))
                data['gyro_y'].append(np.random.normal(0.02, 0.05))
                data['gyro_z'].append(np.random.normal(0.02, 0.05))
                data['magnet_x'].append(np.random.normal(0.05, 0.02))
                data['magnet_y'].append(np.random.normal(0.05, 0.02))
                data['magnet_z'].append(np.random.normal(1.0, 0.02))
            else:
                data['accel_x'].append(np.random.normal(0.3, 0.2))
                data['accel_y'].append(np.random.normal(0.3, 0.2))
                data['accel_z'].append(np.random.normal(-0.95, 0.1))
                data['gyro_x'].append(np.random.normal(0.1, 0.1))
                data['gyro_y'].append(np.random.normal(0.1, 0.1))
                data['gyro_z'].append(np.random.normal(0.1, 0.1))
                data['magnet_x'].append(np.random.normal(0.05, 0.03))
                data['magnet_y'].append(np.random.normal(0.05, 0.03))
                data['magnet_z'].append(np.random.normal(1.0, 0.03))
            data['class'].append(pump_class)

        df = pd.DataFrame(data, columns=columns)
        df.to_csv('peristaltic_pump_data.csv', index=False)
        return df

    def load_and_preprocess(self, file_path='peristaltic_pump_data.csv'):
        df = pd.read_csv(file_path)
        required_columns = ['class', 'accel_x', 'accel_y', 'accel_z',
                           'gyro_x', 'gyro_y', 'gyro_z',
                           'magnet_x', 'magnet_y', 'magnet_z']

        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns")

        features = df.drop('class', axis=1).values
        labels = df['class'].values

        le = LabelEncoder()
        encoded_labels = le.fit_transform(labels)
        categorical_labels = pd.get_dummies(encoded_labels).values

        def create_windows(data, labels):
            windows, window_labels = [], []
            for i in range(0, len(data) - self.config['window_size'], self.config['step_size']):
                windows.append(data[i:i + self.config['window_size']])
                window_labels.append(labels[i + self.config['window_size'] // 2])
            return np.array(windows), np.array(window_labels)

        X_windows, y_windows = create_windows(features, categorical_labels)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X_windows, y_windows, test_size=0.2, 
            stratify=np.argmax(y_windows, axis=1),
            random_state=42
        )

    def build_lstm_model(self):
        class LSTMModel(nn.Module):
            def __init__(self, input_size=9, hidden_size=32, output_size=3):
                super().__init__()
                self.lstm1 = nn.LSTM(input_size, hidden_size, batch_first=True)
                self.bn1 = nn.BatchNorm1d(hidden_size)
                self.lstm2 = nn.LSTM(hidden_size, hidden_size//2, batch_first=True)
                self.bn2 = nn.BatchNorm1d(hidden_size//2)
                self.fc = nn.Sequential(
                    nn.Linear(hidden_size//2, 16),
                    nn.ReLU(),
                    nn.Dropout(0.5),
                    nn.Linear(16, output_size),
                    nn.Softmax(dim=1)
                )

            def forward(self, x):
                out, _ = self.lstm1(x)
                out = out[:, -1, :]
                out = self.bn1(out)

                out, _ = self.lstm2(out.unsqueeze(1))
                out = out[:, -1, :]
                out = self.bn2(out)

                out = self.fc(out)
                return out

        self.model = LSTMModel()
        return self.model

    def train_model(self):
        X_tensor = torch.FloatTensor(self.X_train)
        y_tensor = torch.LongTensor(np.argmax(self.y_train, axis=1))

        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=self.config['batch_size'], shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.config['learning_rate'])
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3)

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(self.config['max_epochs']):
            self.model.train()
            total_loss = 0

            for inputs, targets in dataloader:
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(torch.FloatTensor(self.X_train))
                val_loss = criterion(val_outputs, torch.LongTensor(np.argmax(self.y_train, axis=1))).item()

            scheduler.step(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                torch.save(self.model.state_dict(), 'best_lstm.pth')
            else:
                patience_counter += 1

            if patience_counter >= self.config['patience']:
                break

        self.model.load_state_dict(torch.load('best_lstm.pth'))
        return self.model

    def evaluate_model(self):
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(torch.FloatTensor(self.X_test))
            y_pred = torch.argmax(outputs, dim=1).numpy()
            y_true = np.argmax(self.y_test, axis=1)

            report = classification_report(y_true, y_pred, target_names=self.class_names)
            cm = confusion_matrix(y_true, y_pred)

            print("\nClassification Report:")
            print(report)
            print("\nConfusion Matrix:")
            print(cm)

            return report, cm

    def test_pump_gui(self):
        def predict():
            try:
                input_text = entry.get().strip()
                values = re.split(r'[,\s]+', input_text)
                values = [v for v in values if v]

                if len(values) != 9:
                    raise ValueError(f"Must enter exactly 9 values (found {len(values)})")

                values = list(map(float, values))
                repeated_values = values * 50
                sample = np.array(repeated_values).reshape(1, 50, 9)

                self.model.eval()
                with torch.no_grad():
                    output = self.model(torch.FloatTensor(sample))
                    result = self.class_names[torch.argmax(output).item()]

                messagebox.showinfo("Prediction", f"Pump Condition: {result}")

            except ValueError as ve:
                messagebox.showerror("Input Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        root = tk.Tk()
        root.title("Predictive Maintenance System")
        root.geometry("500x300")

        tk.Label(root, text="Enter 9 Sensor Values:", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(root, width=50)
        entry.pack(pady=10)

        tk.Button(root, text="Test Pump", command=predict, font=("Arial", 12)).pack(pady=20)
        root.mainloop()

if __name__ == "__main__":
    torch.manual_seed(42)
    np.random.seed(42)

    pms = PredictiveMaintenanceSystem()
    print("1. Generating synthetic dataset...")
    pms.generate_peristaltic_pump_data()

    print("2. Loading data...")
    pms.load_and_preprocess()

    print("3. Building model...")
    pms.build_lstm_model()

    print("4. Training model...")
    pms.train_model()

    print("5. Evaluating model...")
    pms.evaluate_model()

    print("6. Starting GUI test interface...")
    pms.test_pump_gui()
