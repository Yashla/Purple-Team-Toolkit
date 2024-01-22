import sys
import subprocess
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit , QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

         # Main window settings
        self.setWindowTitle('Script Runner')
        self.setStyleSheet("background-color: black;")
        self.showMaximized()

        # Layout
        layout = QVBoxLayout()

        # Spacer to push everything else to the bottom
        layout.addStretch(1)  # This will add a stretchable space that takes up half the window

        # Button settings
        self.button = QPushButton('SNMP Walker')
        self.button.setFixedSize(100, 30)  # Set the button to be 100px wide and 30px tall
        self.button.setStyleSheet("background-color: white; color: black;")
        self.button.clicked.connect(self.run_script)
        layout.addWidget(self.button, alignment=Qt.AlignLeft | Qt.AlignTop)        

        # Spacer to separate the button from the output box
        layout.addStretch(1)

        # Output box settings
        self.output_box = QTextEdit()
        self.output_box.setStyleSheet("background-color: white; color: black;")
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box, 1)  # The stretch factor of 1 will allow it to expand

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

  # Input for IP address
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("Enter IP address")
        self.ip_input.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.ip_input)

        # Input for community string
        self.community_input = QLineEdit(self)
        self.community_input.setPlaceholderText("Enter community string")
        self.community_input.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.community_input)

        # Input for OIDs
        self.oids_input = QLineEdit(self)
        self.oids_input.setPlaceholderText("Enter OIDs, comma-separated")
        self.oids_input.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.oids_input)


    def run_script(self):
        # Get the user input data
        ip_address = self.ip_input.text()
        community = self.community_input.text()
        oids = self.oids_input.text()
        
        # Validate inputs
        if not (ip_address and community and oids):
            self.output_box.append('Please fill in all fields.')
            return
        
           # Run the script in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.execute_script, args=(ip_address, community, oids), daemon=True).start()

    def execute_script(self, ip_address, community, oids):
        # Prepare the command with arguments
        command = ['python3', 'snmpwalker.py', ip_address, community, oids]

        # Start the process and capture the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, text=True)
        for line in iter(process.stdout.readline, ''):
            self.output_box.append(line)
        process.stdout.close()
        process.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
