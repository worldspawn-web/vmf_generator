"""Widget for 2D preview of generated blocks."""

from typing import List, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from vmf.brushes import Solid


class PreviewWidget(QWidget):
    """Widget for 2D preview of blocks (top view)."""

    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(6, 8), facecolor="black")
        self.canvas = FigureCanvas(self.figure)
        self.ax = None

        # Data
        self.solids: List[Solid] = []
        self.grid_size = 32
        self.start_pos = (0, 0, 0)

        # Interactive state
        self.pressed = False
        self.press_x = 0
        self.press_y = 0
        self.hovered_solid: Optional[int] = None

        # Artists (for selective redraw)
        self.grid_lines = []
        self.block_patches = []
        self.player_marker = None
        self.hover_patch = None
        self.size_texts = []

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connect mouse events
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("resize_event", self.on_resize)

        self._init_plot()

    def _init_plot(self):
        """Initialize empty plot."""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("black")
        # Don't set aspect here - will set in update_preview with adjustable='datalim'

        # No labels, no title, no ticks
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Placeholder text
        self.ax.text(
            0.5,
            0.5,
            "Generate blocks to see preview",
            ha="center",
            va="center",
            transform=self.ax.transAxes,
            color="#505050",
            fontsize=12,
            style="italic",
        )

        self.canvas.draw()

    def update_preview(
        self, solids: List[Solid], start_pos: tuple, grid_size: int = 32
    ):
        """Update preview with new blocks."""
        if not solids:
            self._init_plot()
            return

        self.solids = solids
        self.start_pos = start_pos
        self.grid_size = grid_size

        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("black")
        # Use aspect='equal' with adjustable='datalim' to fill entire axes
        self.ax.set_aspect("equal", adjustable="datalim")

        # Clean UI
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Calculate boundaries
        all_x = [s.pos[0] for s in solids] + [s.pos[0] + s.size[0] for s in solids]
        all_y = [s.pos[1] for s in solids] + [s.pos[1] + s.size[1] for s in solids]
        padding = max(200, grid_size * 5)
        x_min, x_max = min(all_x) - padding, max(all_x) + padding
        y_min, y_max = min(all_y) - padding, max(all_y) + padding

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        # Draw everything
        self._draw_grid_for_viewport()
        self._draw_blocks()
        self._draw_player()

        self.canvas.draw()

    def _draw_grid_for_viewport(self):
        """Draw grid for current viewport + large margin."""
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        # Add MASSIVE margin to ensure grid covers everything during pan/zoom
        margin = max(abs(x_max - x_min), abs(y_max - y_min)) * 10

        x_start = int((x_min - margin) / self.grid_size) * self.grid_size
        x_end = int((x_max + margin) / self.grid_size + 1) * self.grid_size
        y_start = int((y_min - margin) / self.grid_size) * self.grid_size
        y_end = int((y_max + margin) / self.grid_size + 1) * self.grid_size

        self.grid_lines = []

        # Vertical lines
        x = x_start
        while x <= x_end:
            line = self.ax.axvline(
                x, color="#707070", linewidth=0.5, alpha=0.8, zorder=0
            )
            self.grid_lines.append(line)
            x += self.grid_size

        # Horizontal lines
        y = y_start
        while y <= y_end:
            line = self.ax.axhline(
                y, color="#707070", linewidth=0.5, alpha=0.8, zorder=0
            )
            self.grid_lines.append(line)
            y += self.grid_size

    def _draw_blocks(self):
        """Draw blocks."""
        size_colors = {
            (64, 64, 32): "#FF6B6B",
            (96, 96, 32): "#4ECDC4",
            (128, 128, 32): "#95E1D3",
            (128, 256, 32): "#F38181",
            (192, 128, 32): "#FFE66D",
        }

        self.block_patches = []
        for solid in self.solids:
            x, y, z = solid.pos
            w, l, h = solid.size
            color = size_colors.get(solid.size, "#808080")

            rect = Rectangle(
                (x, y),
                w,
                l,
                facecolor=color,
                edgecolor="white",
                linewidth=1,
                alpha=0.6,
                zorder=10,
            )
            self.ax.add_patch(rect)
            self.block_patches.append(rect)

    def _draw_player(self):
        """Draw start player point."""
        player_x, player_y, _ = self.start_pos
        self.player_marker = self.ax.plot(
            player_x,
            player_y,
            "g^",
            markersize=10,
            markeredgecolor="white",
            markeredgewidth=1.5,
            zorder=100,
        )[0]

    def on_press(self, event):
        """Mouse press handler."""
        if event.inaxes != self.ax:
            return
        self.pressed = True
        self.press_x = event.xdata
        self.press_y = event.ydata

    def on_release(self, event):
        """Mouse release handler."""
        self.pressed = False

    def on_motion(self, event):
        """Mouse motion handler."""
        # Pan
        if self.pressed and event.xdata and event.ydata:
            dx = event.xdata - self.press_x
            dy = event.ydata - self.press_y

            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()

            self.ax.set_xlim(x_min - dx, x_max - dx)
            self.ax.set_ylim(y_min - dy, y_max - dy)

            # Only redraw canvas, no grid regeneration
            self.canvas.draw_idle()
            return

        # Hover detection (only when not dragging)
        if not self.solids or not event.xdata or not event.ydata:
            if self.hovered_solid is not None:
                self.hovered_solid = None
                self._update_hover()
            return

        hovered = None
        for i, solid in enumerate(self.solids):
            x, y, z = solid.pos
            w, l, h = solid.size
            if x <= event.xdata <= x + w and y <= event.ydata <= y + l:
                hovered = i
                break

        if hovered != self.hovered_solid:
            self.hovered_solid = hovered
            self._update_hover()

    def on_scroll(self, event):
        """Mouse scroll handler (zoom)."""
        if not event.xdata or not event.ydata:
            return

        # Zoom factor (smaller for smoother zoom)
        scale_factor = 1.15 if event.button == "down" else 1 / 1.15

        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        # Calculate zoom around mouse position
        x_data = event.xdata
        y_data = event.ydata

        # New ranges
        new_width = (x_max - x_min) * scale_factor
        new_height = (y_max - y_min) * scale_factor

        # Calculate new limits preserving mouse position
        x_ratio = (x_data - x_min) / (x_max - x_min)
        y_ratio = (y_data - y_min) / (y_max - y_min)

        new_x_min = x_data - new_width * x_ratio
        new_x_max = x_data + new_width * (1 - x_ratio)
        new_y_min = y_data - new_height * y_ratio
        new_y_max = y_data + new_height * (1 - y_ratio)

        self.ax.set_xlim(new_x_min, new_x_max)
        self.ax.set_ylim(new_y_min, new_y_max)

        # Only redraw canvas
        self.canvas.draw_idle()

    def on_resize(self, event):
        """Handle canvas resize - redraw grid to cover new viewport."""
        if not self.solids:
            return

        # Remove old grid lines
        for line in self.grid_lines:
            line.remove()
        self.grid_lines = []

        # Redraw grid for new viewport size
        self._draw_grid_for_viewport()

        # Redraw canvas
        self.canvas.draw_idle()

    def _update_hover(self):
        """Update hover display."""
        # Remove old hover elements
        if self.hover_patch:
            self.hover_patch.remove()
            self.hover_patch = None
        for text in self.size_texts:
            text.remove()
        self.size_texts = []

        # Add new hover elements
        if self.hovered_solid is not None:
            solid = self.solids[self.hovered_solid]
            x, y, z = solid.pos
            w, l, h = solid.size

            # Highlight border
            self.hover_patch = Rectangle(
                (x, y),
                w,
                l,
                facecolor="none",
                edgecolor="yellow",
                linewidth=3,
                zorder=50,
            )
            self.ax.add_patch(self.hover_patch)

            # Width label (bottom)
            text_w = self.ax.text(
                x + w / 2,
                y - 10,
                f"{int(w)}",
                ha="center",
                va="top",
                color="yellow",
                fontsize=10,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.8),
                zorder=60,
            )
            self.size_texts.append(text_w)

            # Length label (left side)
            text_l = self.ax.text(
                x - 10,
                y + l / 2,
                f"{int(l)}",
                ha="right",
                va="center",
                color="yellow",
                fontsize=10,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.8),
                zorder=60,
            )
            self.size_texts.append(text_l)

        self.canvas.draw_idle()

    def clear_preview(self):
        """Clear preview."""
        self._init_plot()
