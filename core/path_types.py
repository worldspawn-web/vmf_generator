"""Path pattern types and segment definitions."""
from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass


class SegmentDirection(Enum):
    """Direction of path segment."""
    FORWARD = "forward"  # Along +Y axis
    RIGHT = "right"      # Along +X axis
    LEFT = "left"        # Along -X axis
    BACK = "back"        # Along -Y axis


@dataclass
class PathSegment:
    """
    Represents a segment of the path with its own corridor.
    
    Attributes:
        direction: Direction of the segment
        length: Length of the segment in units
        width: Width of the corridor in units
        blocks: Number of blocks to generate in this segment
        start_pos: Starting position (x, y, z) of the segment
        end_pos: Ending position (x, y, z) of the segment (calculated)
    """
    direction: SegmentDirection
    length: float
    width: float
    blocks: int
    start_pos: Tuple[float, float, float] = (0, 0, 0)
    end_pos: Tuple[float, float, float] = (0, 0, 0)
    
    def calculate_end_pos(self):
        """Calculate end position based on direction and length."""
        x, y, z = self.start_pos
        
        if self.direction == SegmentDirection.FORWARD:
            self.end_pos = (x, y + self.length, z)
        elif self.direction == SegmentDirection.RIGHT:
            self.end_pos = (x + self.length, y, z)
        elif self.direction == SegmentDirection.LEFT:
            self.end_pos = (x - self.length, y, z)
        elif self.direction == SegmentDirection.BACK:
            self.end_pos = (x, y - self.length, z)
    
    def is_position_in_corridor(self, pos: Tuple[float, float, float],
                                block_size: Tuple[float, float, float]) -> bool:
        """
        Check if a block at given position fits within this segment's corridor.
        
        Args:
            pos: (x, y, z) position of the block
            block_size: (width, length, height) size of the block
            
        Returns:
            True if block is within corridor bounds
        """
        bx, by, bz = pos
        bw, bl, bh = block_size
        sx, sy, sz = self.start_pos
        ex, ey, ez = self.end_pos
        
        half_width = self.width / 2
        
        if self.direction == SegmentDirection.FORWARD:
            # Corridor extends along Y axis, centered on start X
            in_y = sy <= by and (by + bl) <= ey
            in_x = (sx - half_width) <= bx and (bx + bw) <= (sx + half_width)
            return in_y and in_x
            
        elif self.direction == SegmentDirection.RIGHT:
            # Corridor extends along +X axis, centered on start Y
            in_x = sx <= bx and (bx + bw) <= ex
            in_y = (sy - half_width) <= by and (by + bl) <= (sy + half_width)
            return in_x and in_y
            
        elif self.direction == SegmentDirection.LEFT:
            # Corridor extends along -X axis, centered on start Y
            in_x = ex <= bx and (bx + bw) <= sx
            in_y = (sy - half_width) <= by and (by + bl) <= (sy + half_width)
            return in_x and in_y
            
        elif self.direction == SegmentDirection.BACK:
            # Corridor extends along -Y axis, centered on start X
            in_y = ey <= by and (by + bl) <= sy
            in_x = (sx - half_width) <= bx and (bx + bw) <= (sx + half_width)
            return in_y and in_x
        
        return False


class PathPattern(Enum):
    """Predefined path patterns."""
    STRAIGHT = "straight"
    RIGHT_TURN = "right_turn"
    LEFT_TURN = "left_turn"
    S_CURVE = "s_curve"
    ZIGZAG = "zigzag"
    CUSTOM = "custom"


def create_pattern(pattern: PathPattern, total_blocks: int,
                   segment_length: float = 800,
                   corridor_width: float = 512) -> List[PathSegment]:
    """
    Create a list of segments for a given pattern.
    
    Args:
        pattern: Type of pattern to create
        total_blocks: Total number of blocks to distribute
        segment_length: Length of each segment in units
        corridor_width: Width of corridors in units
        
    Returns:
        List of PathSegment objects
    """
    segments = []
    
    if pattern == PathPattern.STRAIGHT:
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length * 3,
            width=corridor_width,
            blocks=total_blocks
        ))
    
    elif pattern == PathPattern.RIGHT_TURN:
        # Forward segment
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 2
        ))
        # Right turn segment
        segments.append(PathSegment(
            direction=SegmentDirection.RIGHT,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 2
        ))
    
    elif pattern == PathPattern.LEFT_TURN:
        # Forward segment
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 2
        ))
        # Left turn segment
        segments.append(PathSegment(
            direction=SegmentDirection.LEFT,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 2
        ))
    
    elif pattern == PathPattern.S_CURVE:
        # Forward
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 3
        ))
        # Right
        segments.append(PathSegment(
            direction=SegmentDirection.RIGHT,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 3
        ))
        # Forward again
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length,
            width=corridor_width,
            blocks=total_blocks // 3
        ))
    
    elif pattern == PathPattern.ZIGZAG:
        blocks_per_seg = total_blocks // 4
        # Forward
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length,
            width=corridor_width,
            blocks=blocks_per_seg
        ))
        # Right
        segments.append(PathSegment(
            direction=SegmentDirection.RIGHT,
            length=segment_length // 2,
            width=corridor_width,
            blocks=blocks_per_seg
        ))
        # Left
        segments.append(PathSegment(
            direction=SegmentDirection.LEFT,
            length=segment_length // 2,
            width=corridor_width,
            blocks=blocks_per_seg
        ))
        # Forward
        segments.append(PathSegment(
            direction=SegmentDirection.FORWARD,
            length=segment_length,
            width=corridor_width,
            blocks=blocks_per_seg
        ))
    
    return segments
