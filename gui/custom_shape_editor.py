"""Editor for creating custom block shapes."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from typing import List, Tuple


class ShapeCanvas(QWidget):
    """Canvas for drawing custom shapes."""
    
    def __init__(self, grid_size: int = 32):
        super().__init__()
        self.grid_size = grid_size
        self.grid_cells = 16  # 16x16 grid
        self.vertices: List[Tuple[int, int]] = []
        
        self.setMinimumSize(512, 512)
        self.setMaximumSize(512, 512)
        
        # Mouse state
        self.hover_pos = None
    
    def mousePressEvent(self, event):
        """Handle mouse click to add/remove vertex."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert to grid coordinates
            x = int(event.pos().x() / (self.width() / self.grid_cells))
            y = int(event.pos().y() / (self.height() / self.grid_cells))
            
            if 0 <= x < self.grid_cells and 0 <= y < self.grid_cells:
                pos = (x, y)
                
                # Toggle vertex
                if pos in self.vertices:
                    self.vertices.remove(pos)
                else:
                    self.vertices.append(pos)
                
                self.update()
    
    def mouseMoveEvent(self, event):
        """Track mouse for hover effect."""
        x = int(event.pos().x() / (self.width() / self.grid_cells))
        y = int(event.pos().y() / (self.height() / self.grid_cells))
        
        if 0 <= x < self.grid_cells and 0 <= y < self.grid_cells:
            self.hover_pos = (x, y)
        else:
            self.hover_pos = None
        
        self.update()
    
    def leaveEvent(self, event):
        """Clear hover when mouse leaves."""
        self.hover_pos = None
        self.update()
    
    def paintEvent(self, event):
        """Paint the grid and shape."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        cell_width = self.width() / self.grid_cells
        cell_height = self.height() / self.grid_cells
        
        # Draw grid
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        for i in range(self.grid_cells + 1):
            # Vertical lines
            x = i * cell_width
            painter.drawLine(int(x), 0, int(x), self.height())
            
            # Horizontal lines
            y = i * cell_height
            painter.drawLine(0, int(y), self.width(), int(y))
        
        # Draw center cross
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        center_x = self.width() / 2
        center_y = self.height() / 2
        painter.drawLine(int(center_x), 0, int(center_x), self.height())
        painter.drawLine(0, int(center_y), self.width(), int(center_y))
        
        # Draw hover cell
        if self.hover_pos:
            hx, hy = self.hover_pos
            painter.fillRect(
                QRectF(hx * cell_width, hy * cell_height, cell_width, cell_height),
                QColor(100, 100, 255, 50)
            )
        
        # Draw vertices
        for vx, vy in self.vertices:
            painter.fillRect(
                QRectF(vx * cell_width, vy * cell_height, cell_width, cell_height),
                QColor(255, 100, 100, 150)
            )
            
            # Draw vertex marker
            center_x = (vx + 0.5) * cell_width
            center_y = (vy + 0.5) * cell_height
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(QPointF(center_x, center_y), 5, 5)
        
        # Draw shape outline if we have at least 3 vertices
        if len(self.vertices) >= 3:
            polygon = QPolygonF()
            for vx, vy in self.vertices:
                center_x = (vx + 0.5) * cell_width
                center_y = (vy + 0.5) * cell_height
                polygon.append(QPointF(center_x, center_y))
            
            painter.setPen(QPen(QColor(100, 255, 100), 3))
            painter.setBrush(QBrush(QColor(100, 255, 100, 30)))
            painter.drawPolygon(polygon)
    
    def clear(self):
        """Clear all vertices."""
        self.vertices = []
        self.update()
    
    def get_normalized_vertices(self) -> List[Tuple[float, float]]:
        """Get vertices normalized to 0-1 range."""
        if not self.vertices:
            return []
        
        # Normalize to 0-1 range
        return [
            (x / self.grid_cells, y / self.grid_cells)
            for x, y in self.vertices
        ]


class CustomShapeEditor(QDialog):
    """Dialog for creating custom block shapes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Custom Shape")
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Draw Custom Block Shape")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Click on the grid to add vertices.\n"
            "Click again to remove a vertex.\n"
            "Minimum 3 vertices required."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Shape Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter shape name...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Canvas
        self.canvas = ShapeCanvas()
        layout.addWidget(self.canvas)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.on_clear)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton("✅ Create")
        self.ok_btn.clicked.connect(self.on_create)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def on_clear(self):
        """Clear the canvas."""
        self.canvas.clear()
    
    def on_create(self):
        """Validate and create the shape."""
        # Validate name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Please enter a name for the shape."
            )
            return
        
        # Validate vertices
        if len(self.canvas.vertices) < 3:
            QMessageBox.warning(
                self,
                "Invalid Shape",
                "Shape must have at least 3 vertices!"
            )
            return
        
        # Check for self-intersections (basic check)
        if not self._is_valid_shape():
            QMessageBox.warning(
                self,
                "Invalid Shape",
                "Shape appears to be invalid or self-intersecting.\n"
                "Please ensure vertices form a valid polygon."
            )
            return
        
        self.accept()
    
    def _is_valid_shape(self) -> bool:
        """Check if the shape is valid (basic validation)."""
        # For now, just check that we have at least 3 unique vertices
        return len(set(self.canvas.vertices)) >= 3
    
    def get_shape(self) -> Tuple[str, List[Tuple[float, float]]]:
        """Get the shape name and normalized vertices."""
        return self.name_input.text().strip(), self.canvas.get_normalized_vertices()
