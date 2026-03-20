import sys
import sqlite3
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QFrame, QGridLayout, QPushButton)
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg
import paho.mqtt.publish as publish # <-- VŨ KHÍ MỚI

STYLESHEET = """
    QMainWindow { background-color: #F0F2F5; }
    QWidget { color: #333333; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
    QFrame#MainFrame, QFrame#GraphPanel { background-color: #FFFFFF; border-radius: 15px; padding: 10px; border: 1px solid #E0E0E0; }
    QFrame#PanelHeader { background-color: #2C3E50; border-radius: 10px; }
    QLabel#TitleLabel { color: #FFFFFF; font-size: 20px; font-weight: bold; }
    QLabel#StatLabel { font-size: 16px; font-weight: bold; color: #FFFFFF; }
    QLabel#StatValue { font-size: 38px; font-weight: bold; color: #FFFFFF; }
    QFrame#TempCard { background-color: #E67E22; border-radius: 10px; }
    QFrame#HumidCard { background-color: #3498DB; border-radius: 10px; }
    QFrame#RelayCard { background-color: #1ABC9C; border-radius: 10px; }
    
    /* STYLE CHO NÚT BẤM ĐIỀU KHIỂN */
    QPushButton#OverrideBtn {
        background-color: #E74C3C; color: white; font-size: 16px; font-weight: bold;
        border-radius: 8px; padding: 10px 20px; border: 2px solid #C0392B;
    }
    QPushButton#OverrideBtn:hover { background-color: #C0392B; }
    QPushButton#OverrideBtn:pressed { background-color: #922B21; }
"""

class LedIndicator(QLabel):
    def __init__(self, color="lime", size=25):
        super().__init__()
        self.setFixedSize(size, size)
        self.color = color
        self.set_state(False)
    def set_state(self, on):
        if on: self.setStyleSheet(f"background-color: {self.color}; border-radius: {self.width()//2}px; border: 3px solid #FFFFFF;")
        else: self.setStyleSheet(f"background-color: #DCDCDC; border-radius: {self.width()//2}px; border: 1px solid #BBBBBB;")

class EdgeAIDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EdgeAI Acoustic Hub - Remote Override")
        self.setGeometry(100, 100, 1000, 750)
        self.setStyleSheet(STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. Header
        header_frame = QFrame()
        header_frame.setObjectName("PanelHeader")
        header_layout = QHBoxLayout(header_frame)
        header_layout.addWidget(QLabel("ACOUSTIC HUB - GIÁM SÁT & ĐIỀU KHIỂN", objectName="TitleLabel"))
        main_layout.addWidget(header_frame)

        # 2. Stats
        stats_layout = QHBoxLayout()
        self.temp_card = self.create_stat_card("Nhiệt độ (°C)", "TempCard")
        self.temp_value = self.temp_card.findChild(QLabel, "StatValue")
        stats_layout.addWidget(self.temp_card)

        self.humid_card = self.create_stat_card("Độ ẩm (%)", "HumidCard")
        self.humid_value = self.humid_card.findChild(QLabel, "StatValue")
        stats_layout.addWidget(self.humid_card)

        self.relay_card, self.led_indicator, self.relay_text = self.create_relay_card()
        stats_layout.addWidget(self.relay_card)
        main_layout.addLayout(stats_layout)

        # 3. CONTROL PANEL (VŨ KHÍ MỚI Ở ĐÂY)
        control_frame = QFrame()
        control_frame.setObjectName("MainFrame")
        control_layout = QHBoxLayout(control_frame)
        control_layout.addWidget(QLabel("<b>🕹️ Bảng điều khiển từ xa (Override):</b>", styleSheet="font-size: 16px;"))
        
        self.btn_toggle = QPushButton("🚨 GỬI LỆNH ĐẢO TRẠNG THÁI ĐÈN (TOGGLE)")
        self.btn_toggle.setObjectName("OverrideBtn")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.send_override_command)
        control_layout.addWidget(self.btn_toggle)
        
        main_layout.addWidget(control_frame)

        # 4. Graph
        graph_frame = QFrame()
        graph_frame.setObjectName("GraphPanel")
        graph_layout = QVBoxLayout(graph_frame)
        self.graph_widget = pg.PlotWidget(background='w')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.addLegend(offset=(10, 10))
        graph_layout.addWidget(self.graph_widget)
        self.temp_line = self.graph_widget.plot([], [], name="Temp (°C)", pen=pg.mkPen(color='#C0392B', width=3))
        self.humid_line = self.graph_widget.plot([], [], name="Humid (%)", pen=pg.mkPen(color='#1B4F72', width=3))
        main_layout.addWidget(graph_frame)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)

    # Hàm gửi lệnh MQTT khi bấm nút
    def send_override_command(self):
        try:
            # Gửi tin nhắn có nội dung "TOGGLE" vào Topic command
            publish.single("namhai/iot/command", payload="TOGGLE", hostname="broker.emqx.io")
            print("🚀 Đã bắn lệnh Override thành công!")
        except Exception as e:
            print(f"Lỗi gửi lệnh: {e}")

    def create_stat_card(self, title, obj_name):
        card = QFrame()
        card.setObjectName(obj_name)
        card.setFixedSize(280, 120)
        layout = QGridLayout(card)
        layout.addWidget(QLabel(title, objectName="StatLabel"), 0, 0)
        layout.addWidget(QLabel("--", objectName="StatValue"), 1, 0)
        return card

    def create_relay_card(self):
        card = QFrame()
        card.setObjectName("RelayCard")
        card.setFixedSize(280, 120)
        layout = QVBoxLayout(card)
        layout.addWidget(QLabel("Trạng thái Đèn", objectName="StatLabel"), alignment=Qt.AlignmentFlag.AlignTop)
        
        led_layout = QHBoxLayout()
        led = LedIndicator(color="#2ECC71", size=30)
        text = QLabel("OFF", styleSheet="font-size: 26px; font-weight: bold; color: white;")
        led_layout.addWidget(led)
        led_layout.addWidget(text)
        layout.addLayout(led_layout)
        return card, led, text

    def update_data(self):
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'edge_ai_project.db')
            if not os.path.exists(db_path): return
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, temperature, humidity, relay_status FROM telemetry ORDER BY id DESC LIMIT 60")
            rows = cursor.fetchall()
            conn.close()

            if not rows: return
            rows.reverse()
            self.temp_line.setData([r[0] for r in rows], [r[1] for r in rows])
            self.humid_line.setData([r[0] for r in rows], [r[2] for r in rows])
            
            latest = rows[-1]
            self.temp_card.findChild(QLabel, "StatValue").setText(f"{latest[1]:.1f}")
            self.humid_card.findChild(QLabel, "StatValue").setText(f"{latest[2]:.0f}")
            
            if latest[3] == "ON":
                self.led_indicator.set_state(True)
                self.relay_text.setText("ON")
            else:
                self.led_indicator.set_state(False)
                self.relay_text.setText("OFF")
        except Exception as e:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EdgeAIDashboard()
    window.show()
    sys.exit(app.exec())