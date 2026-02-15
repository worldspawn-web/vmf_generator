"""Dialog for managing block shapes and their probabilities."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
    QWidget, QGridLayout, QScrollArea, QMenu
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QPen, QBrush, QPolygonF, QMouseEvent, QAction
from core.block_shapes import ShapeManager, ShapeType, SHAPE_DISPLAY_NAMES
import math


class ShapeWidget(QWidget):
    """Interactive widget for a single shape."""
    
    def __init__(self, shape, shape_manager, parent_dialog, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.shape_manager = shape_manager
        self.parent_dialog = parent_dialog
        self.is_hovered = False
        self._border_opacity = 1.0 if shape.enabled else 0.0
        
        self.setFixedSize(160, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Enable context menu for custom shapes
        if shape.shape_type == ShapeType.CUSTOM:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Animation for border
        self.anim = QPropertyAnimation(self, b"border_opacity")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def get_border_opacity(self):
        return self._border_opacity
    
    def set_border_opacity(self, value):
        self._border_opacity = value
        self.update()
    
    border_opacity = Property(float, get_border_opacity, set_border_opacity)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Toggle shape on click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.shape.enabled = not self.shape.enabled
            
            # Animate to new state
            self.anim.stop()
            self.anim.setStartValue(self._border_opacity)
            self.anim.setEndValue(1.0 if self.shape.enabled else 0.0)
            self.anim.start()
    
    def enterEvent(self, event):
        """Mouse enter - show light border."""
        self.is_hovered = True
        if not self.shape.enabled:
            self.anim.stop()
            self.anim.setStartValue(self._border_opacity)
            self.anim.setEndValue(0.3)
            self.anim.start()
        self.update()
    
    def leaveEvent(self, event):
        """Mouse leave - hide border if not enabled."""
        self.is_hovered = False
        if not self.shape.enabled:
            self.anim.stop()
            self.anim.setStartValue(self._border_opacity)
            self.anim.setEndValue(0.0)
            self.anim.start()
        self.update()
    
    def _show_context_menu(self, pos):
        """Show context menu for custom shapes."""
        menu = QMenu(self)
        
        delete_action = QAction("🗑️ Delete Shape", self)
        delete_action.triggered.connect(self._on_delete_requested)
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def _on_delete_requested(self):
        """Handle delete request."""
        self.parent_dialog.on_delete_shape(self.shape.name)
    
    def paintEvent(self, event):
        """Paint the shape icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        size = min(self.width(), self.height())
        
        # Fill background
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        # Draw grid
        grid_cells = 8
        cell_size = size / grid_cells
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        for i in range(grid_cells + 1):
            painter.drawLine(int(i * cell_size), 0, int(i * cell_size), size)
            painter.drawLine(0, int(i * cell_size), size, int(i * cell_size))
        
        # Calculate shape dimensions
        margin = size * 0.15
        max_mult = max(self.shape.size_multiplier)
        shape_width = (size - 2 * margin) * self.shape.size_multiplier[0] / max_mult
        shape_height = (size - 2 * margin) * self.shape.size_multiplier[1] / max_mult
        
        center_x = size / 2
        center_y = size / 2
        
        # Set pen/brush based on state
        border_color = QColor(100, 255, 100)
        border_color.setAlphaF(self._border_opacity)
        
        painter.setPen(QPen(border_color, 3))
        painter.setBrush(QBrush(QColor(100, 255, 100, int(40 * self._border_opacity))))
        
        # Draw shape based on type
        self._draw_shape_geometry(painter, center_x, center_y, shape_width, shape_height)
        
        painter.end()
    
    def _draw_shape_geometry(self, painter, cx, cy, w, h):
        """Draw the actual shape geometry."""
        from PySide6.QtCore import QPointF
        
        if self.shape.shape_type == ShapeType.SQUARE or self.shape.shape_type == ShapeType.RECTANGLE:
            x = cx - w / 2
            y = cy - h / 2
            painter.drawRect(int(x), int(y), int(w), int(h))
        
        elif self.shape.shape_type == ShapeType.TRIANGLE:
            polygon = QPolygonF([
                QPointF(cx, cy - h / 2),
                QPointF(cx - w / 2, cy + h / 2),
                QPointF(cx + w / 2, cy + h / 2),
            ])
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.CIRCLE or self.shape.shape_type == ShapeType.OVAL:
            x = cx - w / 2
            y = cy - h / 2
            painter.drawEllipse(int(x), int(y), int(w), int(h))
        
        elif self.shape.shape_type == ShapeType.ELLIPSE:
            x = cx - w / 2
            y = cy - h / 2
            painter.drawEllipse(int(x), int(y), int(w), int(h))
        
        elif self.shape.shape_type == ShapeType.RHOMBUS:
            polygon = QPolygonF([
                QPointF(cx, cy - h / 2),
                QPointF(cx + w / 2, cy),
                QPointF(cx, cy + h / 2),
                QPointF(cx - w / 2, cy),
            ])
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.PARALLELOGRAM:
            offset = w * 0.2
            polygon = QPolygonF([
                QPointF(cx - w / 2 + offset, cy - h / 2),
                QPointF(cx + w / 2 + offset, cy - h / 2),
                QPointF(cx + w / 2 - offset, cy + h / 2),
                QPointF(cx - w / 2 - offset, cy + h / 2),
            ])
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.TRAPEZOID:
            top_width = w * 0.6
            polygon = QPolygonF([
                QPointF(cx - top_width / 2, cy - h / 2),
                QPointF(cx + top_width / 2, cy - h / 2),
                QPointF(cx + w / 2, cy + h / 2),
                QPointF(cx - w / 2, cy + h / 2),
            ])
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.PENTAGON:
            polygon = QPolygonF()
            radius = min(w, h) / 2
            for i in range(5):
                angle = math.radians(i * 72 - 90)
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                polygon.append(QPointF(px, py))
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.HEXAGON:
            polygon = QPolygonF()
            radius = min(w, h) / 2
            for i in range(6):
                angle = math.radians(i * 60 - 90)
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                polygon.append(QPointF(px, py))
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.OCTAGON:
            polygon = QPolygonF()
            radius = min(w, h) / 2
            for i in range(8):
                angle = math.radians(i * 45 - 90)
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                polygon.append(QPointF(px, py))
            painter.drawPolygon(polygon)
        
        elif self.shape.shape_type == ShapeType.CUSTOM:
            if self.shape.vertices and len(self.shape.vertices) >= 3:
                canvas_size = min(w, h) * 2
                margin_custom = (self.width() - canvas_size) / 2
                polygon = QPolygonF()
                for vx, vy in self.shape.vertices:
                    px = margin_custom + vx * canvas_size
                    py = margin_custom + vy * canvas_size
                    polygon.append(QPointF(px, py))
                painter.drawPolygon(polygon)
            else:
                x = cx - w / 2
                y = cy - h / 2
                painter.drawRect(int(x), int(y), int(w), int(h))


class ShapeManagerDialog(QDialog):
    """Dialog for managing block shapes and probabilities."""
    
    def __init__(self, shape_manager: ShapeManager, parent=None):
        super().__init__(parent)
        self.shape_manager = shape_manager
        self.setWindowTitle("Manage Block Shapes")
        self.setMinimumSize(800, 700)
        
        self.shape_widgets = []
        
        self.init_ui()
        self.load_shapes()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Block Shapes")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info label
        info = QLabel("Click on shapes to enable/disable. All enabled shapes have equal probability.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888; font-size: 11px; margin: 5px;")
        layout.addWidget(info)
        
        # Scroll area for shapes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: #1e1e1e; }")
        
        # Container for shape grid
        self.shapes_container = QWidget()
        self.shapes_grid = QGridLayout()
        self.shapes_grid.setSpacing(15)
        self.shapes_grid.setContentsMargins(15, 15, 15, 15)
        self.shapes_container.setLayout(self.shapes_grid)
        
        scroll_area.setWidget(self.shapes_container)
        layout.addWidget(scroll_area)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_custom_btn = QPushButton("➕ Add Custom Shape")
        self.add_custom_btn.clicked.connect(self.on_add_custom)
        btn_layout.addWidget(self.add_custom_btn)
        
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_shapes(self):
        """Load shapes into grid."""
        # Clear existing widgets
        for widget in self.shape_widgets:
            widget.deleteLater()
        self.shape_widgets = []
        
        # Add shapes to grid (4 columns)
        columns = 4
        for idx, shape in enumerate(self.shape_manager.shapes):
            row = idx // columns
            col = idx % columns
            
            shape_widget = ShapeWidget(shape, self.shape_manager, self, self)
            self.shapes_grid.addWidget(shape_widget, row, col)
            self.shape_widgets.append(shape_widget)
    
    def on_delete_shape(self, shape_name: str):
        """Delete a custom shape."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete shape '{shape_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.shape_manager.remove_custom_shape(shape_name)
            self.load_shapes()
    
    def _create_shape_icon_old(self, shape) -> QLabel:
        """Create a visual icon for the shape."""
        import math
        from PySide6.QtCore import QPointF
        
        label = QLabel()
        
        # Create pixmap
        size = 200
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(30, 30, 30))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw grid
        grid_cells = 8
        cell_size = size / grid_cells
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        for i in range(grid_cells + 1):
            painter.drawLine(int(i * cell_size), 0, int(i * cell_size), size)
            painter.drawLine(0, int(i * cell_size), size, int(i * cell_size))
        
        # Calculate shape dimensions
        margin = size * 0.2
        max_mult = max(shape.size_multiplier)
        shape_width = (size - 2 * margin) * shape.size_multiplier[0] / max_mult
        shape_height = (size - 2 * margin) * shape.size_multiplier[1] / max_mult
        
        center_x = size / 2
        center_y = size / 2
        
        painter.setPen(QPen(QColor(100, 255, 100), 3))
        painter.setBrush(QBrush(QColor(100, 255, 100, 60)))
        
        # Draw different shapes based on type
        if shape.shape_type == ShapeType.SQUARE or shape.shape_type == ShapeType.RECTANGLE:
            # Rectangle
            x = center_x - shape_width / 2
            y = center_y - shape_height / 2
            painter.drawRect(int(x), int(y), int(shape_width), int(shape_height))
        
        elif shape.shape_type == ShapeType.TRIANGLE:
            # Triangle (pointing up)
            polygon = QPolygonF([
                QPointF(center_x, center_y - shape_height / 2),  # Top
                QPointF(center_x - shape_width / 2, center_y + shape_height / 2),  # Bottom left
                QPointF(center_x + shape_width / 2, center_y + shape_height / 2),  # Bottom right
            ])
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.CIRCLE or shape.shape_type == ShapeType.OVAL:
            # Circle/Oval
            x = center_x - shape_width / 2
            y = center_y - shape_height / 2
            painter.drawEllipse(int(x), int(y), int(shape_width), int(shape_height))
        
        elif shape.shape_type == ShapeType.ELLIPSE:
            # Ellipse (horizontal)
            x = center_x - shape_width / 2
            y = center_y - shape_height / 2
            painter.drawEllipse(int(x), int(y), int(shape_width), int(shape_height))
        
        elif shape.shape_type == ShapeType.RHOMBUS:
            # Diamond/Rhombus
            polygon = QPolygonF([
                QPointF(center_x, center_y - shape_height / 2),  # Top
                QPointF(center_x + shape_width / 2, center_y),  # Right
                QPointF(center_x, center_y + shape_height / 2),  # Bottom
                QPointF(center_x - shape_width / 2, center_y),  # Left
            ])
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.PARALLELOGRAM:
            # Parallelogram (skewed rectangle)
            offset = shape_width * 0.2
            polygon = QPolygonF([
                QPointF(center_x - shape_width / 2 + offset, center_y - shape_height / 2),
                QPointF(center_x + shape_width / 2 + offset, center_y - shape_height / 2),
                QPointF(center_x + shape_width / 2 - offset, center_y + shape_height / 2),
                QPointF(center_x - shape_width / 2 - offset, center_y + shape_height / 2),
            ])
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.TRAPEZOID:
            # Trapezoid
            top_width = shape_width * 0.6
            polygon = QPolygonF([
                QPointF(center_x - top_width / 2, center_y - shape_height / 2),
                QPointF(center_x + top_width / 2, center_y - shape_height / 2),
                QPointF(center_x + shape_width / 2, center_y + shape_height / 2),
                QPointF(center_x - shape_width / 2, center_y + shape_height / 2),
            ])
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.PENTAGON:
            # Pentagon (5 sides)
            polygon = QPolygonF()
            radius = min(shape_width, shape_height) / 2
            for i in range(5):
                angle = math.radians(i * 72 - 90)  # Start from top
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                polygon.append(QPointF(px, py))
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.HEXAGON:
            # Hexagon (6 sides)
            polygon = QPolygonF()
            radius = min(shape_width, shape_height) / 2
            for i in range(6):
                angle = math.radians(i * 60 - 90)
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                polygon.append(QPointF(px, py))
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.OCTAGON:
            # Octagon (8 sides)
            polygon = QPolygonF()
            radius = min(shape_width, shape_height) / 2
            for i in range(8):
                angle = math.radians(i * 45 - 90)
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                polygon.append(QPointF(px, py))
            painter.drawPolygon(polygon)
        
        elif shape.shape_type == ShapeType.CUSTOM:
            # Custom shape from vertices
            if shape.vertices and len(shape.vertices) >= 3:
                polygon = QPolygonF()
                for vx, vy in shape.vertices:
                    px = margin + vx * (size - 2 * margin)
                    py = margin + vy * (size - 2 * margin)
                    polygon.append(QPointF(px, py))
                painter.drawPolygon(polygon)
            else:
                # Fallback to rectangle
                x = center_x - shape_width / 2
                y = center_y - shape_height / 2
                painter.drawRect(int(x), int(y), int(shape_width), int(shape_height))
        
        # Draw shape name
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, shape.name)
        
        painter.end()
        
        label.setPixmap(pixmap.scaled(180, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return label
    
    
    def on_save(self):
        """Save configuration."""
        # Shapes are already updated in real-time by ShapeWidget clicks
        self.shape_manager.save_config()
        
        QMessageBox.information(
            self,
            "Success",
            "Shape configuration saved successfully!"
        )
        
        self.accept()
    
    def on_add_custom(self):
        """Add a custom shape."""
        from gui.custom_shape_editor import CustomShapeEditor
        
        dialog = CustomShapeEditor(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, vertices = dialog.get_shape()
            
            # Check if name already exists
            if any(s.name == name for s in self.shape_manager.shapes):
                QMessageBox.warning(
                    self,
                    "Duplicate Name",
                    f"Shape with name '{name}' already exists!"
                )
                return
            
            self.shape_manager.add_custom_shape(name, vertices)
            
            # Reload table
            self.load_shapes()
            
            QMessageBox.information(
                self,
                "Success",
                f"Custom shape '{name}' added successfully!"
            )
    
