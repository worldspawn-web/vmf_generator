import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QTextEdit,
    QFileDialog,
    QComboBox,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtGui import QFont

from core.path_generator import PathGenerator
from vmf.writer import VMFWriter


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self):
        super().__init__()
        self.generator = PathGenerator()
        self.writer = VMFWriter()
        self.generated = False

        self.init_ui()

    def init_ui(self):
        """Initialization of the interface."""
        self.setWindowTitle("VMF Spawner v0.1")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel - settings
        left_panel = self._create_settings_panel()
        main_layout.addWidget(left_panel, 1)

        # Right panel - information
        right_panel = self._create_info_panel()
        main_layout.addWidget(right_panel, 1)

    def _create_settings_panel(self) -> QWidget:
        """Creates the settings panel."""
        panel = QGroupBox("Generation parameters")
        layout = QVBoxLayout()

        # Start position
        pos_group = QGroupBox("Start position")
        pos_layout = QVBoxLayout()

        # X coordinate
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X:"))
        self.start_x = QDoubleSpinBox()
        self.start_x.setRange(-10000, 10000)
        self.start_x.setValue(0)
        self.start_x.setDecimals(0)
        x_layout.addWidget(self.start_x)
        pos_layout.addLayout(x_layout)

        # Y coordinate
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y:"))
        self.start_y = QDoubleSpinBox()
        self.start_y.setRange(-10000, 10000)
        self.start_y.setValue(0)
        self.start_y.setDecimals(0)
        y_layout.addWidget(self.start_y)
        pos_layout.addLayout(y_layout)

        # Z coordinate
        z_layout = QHBoxLayout()
        z_layout.addWidget(QLabel("Z:"))
        self.start_z = QDoubleSpinBox()
        self.start_z.setRange(-10000, 10000)
        self.start_z.setValue(0)
        self.start_z.setDecimals(0)
        z_layout.addWidget(self.start_z)
        pos_layout.addLayout(z_layout)

        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)

        # Path parameters
        path_group = QGroupBox("Path parameters")
        path_layout = QVBoxLayout()

        # Number of blocks
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Number of blocks:"))
        self.block_count = QSpinBox()
        self.block_count.setRange(1, 100)
        self.block_count.setValue(10)
        count_layout.addWidget(self.block_count)
        path_layout.addLayout(count_layout)

        # Distance between blocks
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Distance:"))
        self.spacing = QDoubleSpinBox()
        self.spacing.setRange(50, 1000)
        self.spacing.setValue(150)
        self.spacing.setDecimals(0)
        self.spacing.setSuffix(" units")
        spacing_layout.addWidget(self.spacing)
        path_layout.addLayout(spacing_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # Types of blocks
        blocks_group = QGroupBox("Block types")
        blocks_layout = QVBoxLayout()

        blocks_layout.addWidget(QLabel("Block size:"))
        self.block_type = QComboBox()
        self.block_type.addItems(["small", "medium", "large", "long", "wide"])
        self.block_type.setCurrentText("medium")
        blocks_layout.addWidget(self.block_type)

        self.randomize_check = QCheckBox("Randomize sizes")
        self.randomize_check.setChecked(True)
        blocks_layout.addWidget(self.randomize_check)

        blocks_group.setLayout(blocks_layout)
        layout.addWidget(blocks_group)

        # Action buttons
        buttons_layout = QVBoxLayout()

        self.generate_btn = QPushButton("🔨 Generate")
        self.generate_btn.clicked.connect(self.on_generate)
        self.generate_btn.setStyleSheet(
            "QPushButton { font-size: 14px; padding: 10px; }"
        )
        buttons_layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("💾 Save VMF")
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; }")
        buttons_layout.addWidget(self.save_btn)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_info_panel(self) -> QWidget:
        """Creates the information panel."""
        panel = QGroupBox("Information")
        layout = QVBoxLayout()

        # Log
        log_label = QLabel("Generation log:")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

        # Information about block sizes
        sizes_label = QLabel("Available block sizes:")
        sizes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(sizes_label)

        self.sizes_text = QTextEdit()
        self.sizes_text.setReadOnly(True)
        self.sizes_text.setMaximumHeight(150)
        self.sizes_text.setText(self.generator.get_block_size_info())
        layout.addWidget(self.sizes_text)

        # Preview (just a placeholder)
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText(
            "Here will be displayed information about the generated path..."
        )
        layout.addWidget(self.preview_text)

        panel.setLayout(layout)
        return panel

    def log(self, message: str):
        """Adds a message to the log."""
        self.log_text.append(message)

    def on_generate(self):
        """Handler of the generate button."""
        try:
            self.log("=" * 50)
            self.log("🚀 Starting generation...")

            # Get parameters from UI
            start_x = self.start_x.value()
            start_y = self.start_y.value()
            start_z = self.start_z.value()
            block_count = self.block_count.value()
            spacing = self.spacing.value()
            randomize = self.randomize_check.isChecked()

            # Configure the generator
            self.generator.set_start_position(start_x, start_y, start_z)
            self.generator.set_block_count(block_count)
            self.generator.set_spacing(spacing)
            self.generator.set_randomize(randomize)

            # If randomization is disabled, use the selected type
            if not randomize:
                selected_type = self.block_type.currentText()
                self.generator.set_block_types([selected_type])
            else:
                # Use all types for randomization
                self.generator.set_block_types(
                    ["small", "medium", "large", "long", "wide"]
                )

            self.log(f"📍 Start position: ({start_x}, {start_y}, {start_z})")
            self.log(f"🔢 Number of blocks: {block_count}")
            self.log(f"📏 Distance: {spacing} units")
            self.log(f"🎲 Randomization: {'Yes' if randomize else 'No'}")

            # Generate the path
            solids = self.generator.generate_straight_line()

            self.log(f"✅ Generated {len(solids)} blocks!")

            # Clear the writer and add new solids
            self.writer.clear()
            for solid in solids:
                self.writer.add_solid(solid)

            self.generated = True
            self.save_btn.setEnabled(True)

            # Update the preview
            preview_info = f"Generated blocks: {len(solids)}\n"
            preview_info += f"Path length: ~{(block_count - 1) * spacing:.0f} units\n"
            preview_info += (
                f"End point: Y = {start_y + (block_count - 1) * spacing:.0f}\n"
            )
            self.preview_text.setText(preview_info)

            self.log("🎉 Generation completed! You can save the file.")

        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error during generation:\n{str(e)}")

    def on_save(self):
        """Handler of the save button."""
        if not self.generated:
            QMessageBox.warning(self, "Attention", "First generate the path!")
            return

        try:
            # Save file dialog
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Save VMF file",
                os.path.expanduser("~/Desktop/bhop_generated.vmf"),
                "VMF Files (*.vmf);;All Files (*)",
            )

            if filepath:
                # Save
                self.writer.save(filepath)
                self.log(f"💾 File saved: {filepath}")
                QMessageBox.information(
                    self,
                    "Success",
                    f"VMF file successfully saved!\n\n{filepath}\n\nNow you can open it in Hammer Editor.",
                )

        except Exception as e:
            self.log(f"❌ ERROR saving: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error during saving:\n{str(e)}")
