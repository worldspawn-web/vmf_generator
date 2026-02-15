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

from core.path_generator import PathGenerator, RotationMode
from core.path_types import PathPattern
from vmf.writer import VMFWriter
from gui.preview_widget import PreviewWidget


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self):
        super().__init__()
        self.generator = PathGenerator()
        self.writer = VMFWriter()
        self.generated = False
        
        # Initialize shape manager
        from core.block_shapes import ShapeManager
        self.shape_manager = ShapeManager()

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

        # Start position (compact: X, Y, Z in one line)
        pos_group = QGroupBox("Start position")
        pos_layout = QHBoxLayout()

        pos_layout.addWidget(QLabel("X:"))
        self.start_x = QDoubleSpinBox()
        self.start_x.setRange(-10000, 10000)
        self.start_x.setValue(0)
        self.start_x.setDecimals(0)
        self.start_x.setMaximumWidth(80)
        self.start_x.valueChanged.connect(lambda: self._update_segment_zones_preview())
        pos_layout.addWidget(self.start_x)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.start_y = QDoubleSpinBox()
        self.start_y.setRange(-10000, 10000)
        self.start_y.setValue(0)
        self.start_y.setDecimals(0)
        self.start_y.setMaximumWidth(80)
        self.start_y.valueChanged.connect(lambda: self._update_segment_zones_preview())
        pos_layout.addWidget(self.start_y)
        
        pos_layout.addWidget(QLabel("Z:"))
        self.start_z = QDoubleSpinBox()
        self.start_z.setRange(-10000, 10000)
        self.start_z.setValue(0)
        self.start_z.setDecimals(0)
        self.start_z.setMaximumWidth(80)
        self.start_z.valueChanged.connect(lambda: self._update_segment_zones_preview())
        pos_layout.addWidget(self.start_z)

        pos_layout.addStretch()

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
        spacing_layout.addWidget(QLabel("Block spacing:"))
        self.spacing = QDoubleSpinBox()
        self.spacing.setRange(50, 1000)
        self.spacing.setValue(150)
        self.spacing.setDecimals(0)
        self.spacing.setSuffix(" units")
        spacing_layout.addWidget(self.spacing)
        path_layout.addLayout(spacing_layout)

        # Path width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Path width:"))
        self.path_width = QDoubleSpinBox()
        self.path_width.setRange(128, 2048)
        self.path_width.setValue(512)
        self.path_width.setDecimals(0)
        self.path_width.setSuffix(" units")
        self.path_width.valueChanged.connect(lambda: self._update_segment_zones_preview())
        width_layout.addWidget(self.path_width)
        path_layout.addLayout(width_layout)

        # Max blocks per row
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Max blocks per row:"))
        self.max_blocks_per_row = QSpinBox()
        self.max_blocks_per_row.setRange(1, 10)
        self.max_blocks_per_row.setValue(3)
        row_layout.addWidget(self.max_blocks_per_row)
        path_layout.addLayout(row_layout)

        # Path mode selector
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(QLabel("Path generation mode:"))
        self.path_mode = QComboBox()
        self.path_mode.addItems(["Preset Pattern", "Custom Chain"])
        self.path_mode.setCurrentText("Preset Pattern")
        self.path_mode.currentTextChanged.connect(self._on_path_mode_changed)
        mode_layout.addWidget(self.path_mode)
        path_layout.addLayout(mode_layout)

        # Preset pattern (shown when mode is "Preset Pattern")
        self.preset_pattern_widget = QWidget()
        preset_layout = QVBoxLayout()
        preset_layout.setContentsMargins(0, 0, 0, 0)
        preset_layout.addWidget(QLabel("Path pattern:"))
        self.path_pattern = QComboBox()
        self.path_pattern.addItems(
            ["Straight", "Right Turn", "Left Turn", "S-Curve", "Zigzag"]
        )
        self.path_pattern.setCurrentText("Straight")
        self.path_pattern.currentTextChanged.connect(lambda: self._update_segment_zones_preview())
        preset_layout.addWidget(self.path_pattern)
        self.preset_pattern_widget.setLayout(preset_layout)
        path_layout.addWidget(self.preset_pattern_widget)

        # Custom chain builder (shown when mode is "Custom Chain")
        self.custom_chain_widget = QWidget()
        custom_layout = QVBoxLayout()
        custom_layout.setContentsMargins(0, 0, 0, 0)
        
        custom_layout.addWidget(QLabel("Segment chain:"))
        
        # List of segments
        self.segment_list = QTextEdit()
        self.segment_list.setReadOnly(True)
        self.segment_list.setMaximumHeight(100)
        self.segment_list.setPlaceholderText("No segments added. Click 'Add Segment' to start.")
        custom_layout.addWidget(self.segment_list)
        
        # Buttons for managing segments
        segment_btn_layout = QHBoxLayout()
        self.add_segment_btn = QPushButton("➕ Add Segment")
        self.add_segment_btn.clicked.connect(self._on_add_segment)
        segment_btn_layout.addWidget(self.add_segment_btn)
        
        self.clear_segments_btn = QPushButton("🗑️ Clear All")
        self.clear_segments_btn.clicked.connect(self._on_clear_segments)
        segment_btn_layout.addWidget(self.clear_segments_btn)
        custom_layout.addLayout(segment_btn_layout)
        
        self.custom_chain_widget.setLayout(custom_layout)
        self.custom_chain_widget.setVisible(False)  # Hidden by default
        path_layout.addWidget(self.custom_chain_widget)
        
        # Store custom segments
        self.custom_segments = []

        # Segment length (for patterns)
        seg_length_layout = QHBoxLayout()
        seg_length_layout.addWidget(QLabel("Segment length:"))
        self.segment_length = QDoubleSpinBox()
        self.segment_length.setRange(400, 2000)
        self.segment_length.setValue(800)
        self.segment_length.setDecimals(0)
        self.segment_length.setSuffix(" units")
        self.segment_length.valueChanged.connect(lambda: self._update_segment_zones_preview())
        seg_length_layout.addWidget(self.segment_length)
        path_layout.addLayout(seg_length_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # Grid settings
        grid_group = QGroupBox("Grid settings")
        grid_layout = QVBoxLayout()

        grid_layout.addWidget(QLabel("Grid size (snap):"))
        self.grid_size = QComboBox()
        self.grid_size.addItems(
            ["1", "2", "4", "8", "16", "32", "64", "128", "256", "512"]
        )
        self.grid_size.setCurrentText("32")
        grid_layout.addWidget(self.grid_size)

        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)

        # Types of blocks
        blocks_group = QGroupBox("Block types")
        blocks_layout = QVBoxLayout()

        self.randomize_check = QCheckBox("Randomize sizes (use all types)")
        self.randomize_check.setChecked(True)
        blocks_layout.addWidget(self.randomize_check)

        blocks_layout.addWidget(QLabel("Fixed block size:"))
        self.block_type = QComboBox()
        self.block_type.addItems(
            [
                "small (64x64x32)",
                "medium (96x96x32)",
                "large (128x128x32)",
                "long (128x256x32)",
                "wide (192x128x32)",
            ]
        )
        self.block_type.setCurrentText("medium (96x96x32)")
        self.block_type.setEnabled(False)  # Disabled by default since randomize is ON
        blocks_layout.addWidget(self.block_type)

        # Connect randomize checkbox to enable/disable block type selector
        self.randomize_check.toggled.connect(self._on_randomize_toggled)

        self.randomize_positions_check = QCheckBox("Randomize positions (X axis)")
        self.randomize_positions_check.setChecked(True)
        blocks_layout.addWidget(self.randomize_positions_check)

        blocks_layout.addWidget(QLabel("Block rotation:"))
        self.rotation_mode = QComboBox()
        self.rotation_mode.addItems([
            "No rotation",
            "Priority straight (80% straight)",
            "Full random rotation"
        ])
        self.rotation_mode.setCurrentText("No rotation")
        blocks_layout.addWidget(self.rotation_mode)
        
        # Block shapes button
        self.manage_shapes_btn = QPushButton("🎨 Manage Block Shapes...")
        self.manage_shapes_btn.clicked.connect(self._on_manage_shapes)
        blocks_layout.addWidget(self.manage_shapes_btn)

        blocks_group.setLayout(blocks_layout)
        layout.addWidget(blocks_group)

        # Preview settings
        preview_group = QGroupBox("Preview settings")
        preview_layout = QVBoxLayout()

        self.show_zones_check = QCheckBox("Show Segment Zones")
        self.show_zones_check.setChecked(False)
        self.show_zones_check.toggled.connect(self._on_show_zones_toggled)
        preview_layout.addWidget(self.show_zones_check)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

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
        panel = QGroupBox("Information & Preview")
        layout = QVBoxLayout()

        # Log
        log_label = QLabel("Generation log:")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        layout.addWidget(self.log_text)

        # 2D Preview widget
        preview_label = QLabel("2D Preview (Top View):")
        preview_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)

        panel.setLayout(layout)
        return panel

    def log(self, message: str):
        """Adds a message to the log."""
        self.log_text.append(message)

    def _on_randomize_toggled(self, checked: bool):
        """Handle randomize checkbox toggle."""
        # Enable block type selector only when randomize is OFF
        self.block_type.setEnabled(not checked)

    def _on_manage_shapes(self):
        """Open shape manager dialog."""
        from gui.shape_manager_dialog import ShapeManagerDialog
        
        dialog = ShapeManagerDialog(self.shape_manager, self)
        dialog.exec()

    def _on_path_mode_changed(self, mode: str):
        """Handle path mode change."""
        if mode == "Preset Pattern":
            self.preset_pattern_widget.setVisible(True)
            self.custom_chain_widget.setVisible(False)
        else:  # Custom Chain
            self.preset_pattern_widget.setVisible(False)
            self.custom_chain_widget.setVisible(True)
        
        # Update zones preview
        self._update_segment_zones_preview()

    def _on_add_segment(self):
        """Add a new segment to the custom chain."""
        from PySide6.QtWidgets import QDialog, QDialogButtonBox
        from core.path_types import SegmentDirection
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Segment")
        dialog_layout = QVBoxLayout()
        
        # Direction
        dialog_layout.addWidget(QLabel("Direction:"))
        direction_combo = QComboBox()
        direction_combo.addItems(["Forward", "Right", "Left", "Back"])
        dialog_layout.addWidget(direction_combo)
        
        # Length
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        length_spin = QDoubleSpinBox()
        length_spin.setRange(200, 3000)
        length_spin.setValue(800)
        length_spin.setSuffix(" units")
        length_layout.addWidget(length_spin)
        dialog_layout.addLayout(length_layout)
        
        # Blocks
        blocks_layout = QHBoxLayout()
        blocks_layout.addWidget(QLabel("Blocks:"))
        blocks_spin = QSpinBox()
        blocks_spin.setRange(1, 50)
        blocks_spin.setValue(5)
        blocks_layout.addWidget(blocks_spin)
        dialog_layout.addLayout(blocks_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        
        dialog.setLayout(dialog_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Map direction string to enum
            dir_map = {
                "Forward": SegmentDirection.FORWARD,
                "Right": SegmentDirection.RIGHT,
                "Left": SegmentDirection.LEFT,
                "Back": SegmentDirection.BACK
            }
            
            segment_info = {
                "direction": dir_map[direction_combo.currentText()],
                "direction_name": direction_combo.currentText(),
                "length": length_spin.value(),
                "blocks": blocks_spin.value()
            }
            
            self.custom_segments.append(segment_info)
            self._update_segment_list_display()
            self._update_segment_zones_preview()

    def _on_clear_segments(self):
        """Clear all custom segments."""
        self.custom_segments = []
        self._update_segment_list_display()
        self._update_segment_zones_preview()

    def _update_segment_list_display(self):
        """Update the segment list display."""
        if not self.custom_segments:
            self.segment_list.setPlainText("No segments added.")
            return
        
        lines = []
        for i, seg in enumerate(self.custom_segments, 1):
            lines.append(
                f"{i}. {seg['direction_name']} - {seg['length']:.0f} units - {seg['blocks']} blocks"
            )
        
        self.segment_list.setPlainText("\n".join(lines))

    def _on_show_zones_toggled(self, checked: bool):
        """Handle show zones checkbox toggle."""
        if checked:
            self._update_segment_zones_preview()
        else:
            # Clear zones from preview
            self.preview_widget.clear_segment_zones()

    def _update_segment_zones_preview(self):
        """Update segment zones preview based on current parameters."""
        if not self.show_zones_check.isChecked():
            return

        # Get current parameters
        start_x = self.start_x.value()
        start_y = self.start_y.value()
        start_z = self.start_z.value()
        path_width = self.path_width.value()
        segment_length = self.segment_length.value()
        
        from core.path_types import create_pattern, PathSegment
        
        # Check mode
        if self.path_mode.currentText() == "Preset Pattern":
            # Use preset pattern
            pattern_map = {
                "Straight": PathPattern.STRAIGHT,
                "Right Turn": PathPattern.RIGHT_TURN,
                "Left Turn": PathPattern.LEFT_TURN,
                "S-Curve": PathPattern.S_CURVE,
                "Zigzag": PathPattern.ZIGZAG
            }
            selected_pattern = pattern_map[self.path_pattern.currentText()]
            
            segments = create_pattern(
                selected_pattern,
                10,  # dummy block count, not used for zones
                segment_length,
                path_width
            )
        else:
            # Use custom chain
            if not self.custom_segments:
                self.preview_widget.clear_segment_zones()
                return
            
            segments = []
            for seg_info in self.custom_segments:
                segment = PathSegment(
                    direction=seg_info["direction"],
                    length=seg_info["length"],
                    width=path_width,
                    blocks=seg_info["blocks"]
                )
                segments.append(segment)
        
        # Calculate segment positions
        current_pos = (start_x, start_y, start_z)
        for segment in segments:
            segment.start_pos = current_pos
            segment.calculate_end_pos()
            current_pos = segment.end_pos
        
        # Update preview with segments
        self.preview_widget.update_segment_zones(segments)

    def on_generate(self):
        """Handler of the generate button."""
        try:
            self.log("=" * 50)
            self.log("Starting generation...")

            # Get parameters from UI
            start_x = self.start_x.value()
            start_y = self.start_y.value()
            start_z = self.start_z.value()
            block_count = self.block_count.value()
            spacing = self.spacing.value()
            path_width = self.path_width.value()
            max_blocks_per_row = self.max_blocks_per_row.value()
            segment_length = self.segment_length.value()
            randomize = self.randomize_check.isChecked()
            randomize_positions = self.randomize_positions_check.isChecked()
            grid_size = int(self.grid_size.currentText())
            
            # Map UI pattern to enum
            pattern_map = {
                "Straight": PathPattern.STRAIGHT,
                "Right Turn": PathPattern.RIGHT_TURN,
                "Left Turn": PathPattern.LEFT_TURN,
                "S-Curve": PathPattern.S_CURVE,
                "Zigzag": PathPattern.ZIGZAG,
            }
            selected_pattern = pattern_map[self.path_pattern.currentText()]
            
            # Map UI rotation mode to enum
            rotation_map = {
                "No rotation": RotationMode.NONE,
                "Priority straight (80% straight)": RotationMode.PRIORITY_STRAIGHT,
                "Full random rotation": RotationMode.FULL_RANDOM
            }
            selected_rotation = rotation_map[self.rotation_mode.currentText()]

            # Configure the generator
            self.generator.set_start_position(start_x, start_y, start_z)
            self.generator.set_block_count(block_count)
            self.generator.set_spacing(spacing)
            self.generator.set_path_width(path_width)
            self.generator.set_segment_length(segment_length)
            self.generator.set_max_blocks_per_row(max_blocks_per_row)
            self.generator.set_rotation_mode(selected_rotation)
            self.generator.set_randomize(randomize)
            self.generator.set_randomize_positions(randomize_positions)
            self.generator.set_grid_size(grid_size)
            self.generator.set_shape_manager(self.shape_manager)
            
            # Set block types BEFORE generation
            if not randomize:
                selected_type_text = self.block_type.currentText()
                # Extract type name from "name (dimensions)" format
                selected_type = selected_type_text.split(" ")[0]
                self.generator.set_block_types([selected_type])
            else:
                # Use all types for randomization
                self.generator.set_block_types(
                    ["small", "medium", "large", "long", "wide"]
                )

            self.log(f"Start position: ({start_x}, {start_y}, {start_z})")
            self.log(f"Number of blocks: {block_count}")
            self.log(f"Block spacing: {spacing} units")
            self.log(f"Grid size: {grid_size} units")
            self.log(f"Randomization: {'Yes' if randomize else 'No'}")
            
            # Check which mode to use and generate
            if self.path_mode.currentText() == "Preset Pattern":
                # Use preset pattern - clear any custom segments
                self.generator.segments = []
                self.generator.set_path_pattern(selected_pattern)
                self.log(f"Path pattern: {self.path_pattern.currentText()}")
                solids = self.generator.generate_with_pattern()
            else:
                # Use custom chain
                if not self.custom_segments:
                    self.log("ERROR: No custom segments defined!")
                    return
                
                from core.path_types import PathSegment
                segments = []
                for seg_info in self.custom_segments:
                    segment = PathSegment(
                        direction=seg_info["direction"],
                        length=seg_info["length"],
                        width=path_width,
                        blocks=seg_info["blocks"]
                    )
                    segments.append(segment)
                
                # Set segments in generator
                self.generator.segments = segments
                self.log(f"Custom chain: {len(segments)} segments")
                solids = self.generator.generate_with_pattern()

            self.log(f"Generated {len(solids)} blocks!")

            # Clear the writer and add new solids
            self.writer.clear()
            for solid in solids:
                self.writer.add_solid(solid)

            self.generated = True
            self.save_btn.setEnabled(True)

            # Turn off zone preview when generating actual blocks
            if self.show_zones_check.isChecked():
                self.show_zones_check.setChecked(False)
            self.preview_widget.clear_segment_zones()

            # Update the 2D preview
            self.preview_widget.update_preview(
                solids, (start_x, start_y, start_z), grid_size
            )

            self.log("Generation completed! You can save the file.")
            self.log(f"Path length: ~{(block_count - 1) * spacing:.0f} units")

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
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
                self.log(f"File saved: {filepath}")
                QMessageBox.information(
                    self,
                    "Success",
                    f"VMF file successfully saved!\n\n{filepath}\n\nNow you can open it in Hammer Editor.",
                )

        except Exception as e:
            self.log(f"ERROR saving: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error during saving:\n{str(e)}")
