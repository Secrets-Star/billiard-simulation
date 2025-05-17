import pygame
import numpy as np
from physics import Ball, BilliardTable, PhysicsEngine

class BilliardVisualizer:
    """
    Class for visualizing the billiard simulation using Pygame.
    """
    def __init__(self, physics_engine: PhysicsEngine, width: int = 1000, height: int = 500):
        """
        Initialize the visualizer with a physics engine.
        
        Args:
            physics_engine: Physics engine containing the simulation state
            width: Width of the window in pixels
            height: Height of the window in pixels
        """
        # Initialize pygame
        pygame.init()
        
        # Store references
        self.physics_engine = physics_engine
        self.table = physics_engine.table
        
        # Set up the display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Billiard Simulation")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Conversion factors (meters to pixels)
        self.scale_x = (width * 0.95) / self.table.length
        self.scale_y = (height * 0.95) / self.table.width
        
        # Offsets for centering the table
        self.offset_x = (width - self.table.length * self.scale_x) / 2
        self.offset_y = (height - self.table.width * self.scale_y) / 2
        
        # Font for rendering text
        self.font = pygame.font.SysFont('Arial', 14)
        
        # Colors
        self.colors = {
            'table': (0, 100, 0),     # Dark green
            'cushion': (50, 50, 50),  # Dark gray
            'pocket': (0, 0, 0),      # Black
            'cue': (255, 255, 255),   # White
            'text': (255, 255, 255),  # White
            'trajectory': (200, 200, 200, 128)  # Light gray, semi-transparent
        }
        
        # Cue stick variables
        self.cue_active = False
        self.cue_start = None
        self.cue_end = None
        self.cue_power = 0.0
        self.max_cue_power = 20.0  # Maximum cue power in m/s
        
        # Game state
        self.paused = False
        self.show_trajectories = True
        self.show_velocities = True
        
    def meters_to_pixels(self, position):
        """
        Convert a position from meters to pixels.
        
        Args:
            position: Position in meters [x, y]
            
        Returns:
            tuple: Position in pixels (x, y)
        """
        return (
            int(position[0] * self.scale_x + self.offset_x),
            int(position[1] * self.scale_y + self.offset_y)
        )
    
    def pixels_to_meters(self, pixel_pos):
        """
        Convert a position from pixels to meters.
        
        Args:
            pixel_pos: Position in pixels (x, y)
            
        Returns:
            ndarray: Position in meters [x, y]
        """
        return np.array([
            (pixel_pos[0] - self.offset_x) / self.scale_x,
            (pixel_pos[1] - self.offset_y) / self.scale_y
        ])
    
    def draw_table(self):
        """Draw the billiard table with cushions and pockets."""
        # Draw table background
        table_rect = (
            self.offset_x, 
            self.offset_y, 
            self.table.length * self.scale_x, 
            self.table.width * self.scale_y
        )
        pygame.draw.rect(self.screen, self.colors['table'], table_rect)
        
        # Draw cushions (borders)
        cushion_width = 20
        cushion_rects = [
            # Top cushion
            (self.offset_x - cushion_width, self.offset_y - cushion_width, 
             self.table.length * self.scale_x + 2 * cushion_width, cushion_width),
            # Bottom cushion
            (self.offset_x - cushion_width, self.offset_y + self.table.width * self.scale_y, 
             self.table.length * self.scale_x + 2 * cushion_width, cushion_width),
            # Left cushion
            (self.offset_x - cushion_width, self.offset_y - cushion_width, 
             cushion_width, self.table.width * self.scale_y + 2 * cushion_width),
            # Right cushion
            (self.offset_x + self.table.length * self.scale_x, self.offset_y - cushion_width, 
             cushion_width, self.table.width * self.scale_y + 2 * cushion_width)
        ]
        
        for rect in cushion_rects:
            pygame.draw.rect(self.screen, self.colors['cushion'], rect)
        
        # Draw pockets
        for pocket_pos, pocket_radius in self.table.pockets:
            pocket_pixel_pos = self.meters_to_pixels(pocket_pos)
            pocket_pixel_radius = int(pocket_radius * self.scale_x)
            pygame.draw.circle(self.screen, self.colors['pocket'], pocket_pixel_pos, pocket_pixel_radius)
    
    def draw_ball(self, ball: Ball):
        """
        Draw a billiard ball on the screen.
        
        Args:
            ball: Ball object to draw
        """
        # Convert position to pixels
        pixel_pos = self.meters_to_pixels(ball.position)
        pixel_radius = int(ball.radius * self.scale_x)
        
        # Draw the ball
        pygame.draw.circle(self.screen, ball.color, pixel_pos, pixel_radius)
        
        # Draw ball number
        if ball.number > 0:
            # For numbered balls, draw a white circle with the number
            number_radius = int(pixel_radius * 0.7)
            pygame.draw.circle(self.screen, (255, 255, 255), pixel_pos, number_radius)
            
            # Draw the number
            text = self.font.render(str(ball.number), True, (0, 0, 0))
            text_rect = text.get_rect(center=pixel_pos)
            self.screen.blit(text, text_rect)
        
        # Optionally draw velocity vector
        if self.show_velocities and np.linalg.norm(ball.velocity) > 0.01:
            # Scale velocity vector for visualization
            vel_scale = 0.2
            end_pos = ball.position + ball.velocity * vel_scale
            end_pixel_pos = self.meters_to_pixels(end_pos)
            
            # Draw the velocity vector
            pygame.draw.line(self.screen, (255, 0, 0), pixel_pos, end_pixel_pos, 2)
    
    def draw_trajectory(self, ball: Ball):
        """
        Draw the trajectory of a ball.
        
        Args:
            ball: Ball object whose trajectory to draw
        """
        if len(ball.position_history) < 2:
            return
            
        # Convert trajectory points to pixel coordinates
        pixel_points = [self.meters_to_pixels(pos) for pos in ball.position_history]
        
        # Draw the trajectory as a line
        pygame.draw.lines(self.screen, self.colors['trajectory'], False, pixel_points, 1)
    
    def draw_cue_stick(self):
        """Draw the cue stick when the player is aiming."""
        if self.cue_active and self.cue_start is not None and self.cue_end is not None:
            # Draw the cue stick as a line
            pygame.draw.line(self.screen, (139, 69, 19), self.cue_start, self.cue_end, 4)
            
            # Draw the power indicator
            power_pct = self.cue_power / self.max_cue_power
            power_color = (int(255 * power_pct), int(255 * (1 - power_pct)), 0)
            power_text = self.font.render(f"Power: {int(power_pct * 100)}%", True, power_color)
            self.screen.blit(power_text, (10, 10))
    
    def draw_game_info(self):
        """Draw game information on the screen."""
        # Game state text
        state_text = "PAUSED" if self.paused else "Running"
        text = self.font.render(f"State: {state_text}", True, self.colors['text'])
        self.screen.blit(text, (10, 30))
        
        # Ball count
        active_count = len(self.physics_engine.active_balls)
        pocketed_count = len(self.physics_engine.pocketed_balls)
        text = self.font.render(f"Balls: {active_count} active, {pocketed_count} pocketed", 
                              True, self.colors['text'])
        self.screen.blit(text, (10, 50))
        
        # Controls help
        help_texts = [
            "SPACE: Pause/Resume",
            "R: Reset table",
            "T: Toggle trajectories",
            "V: Toggle velocity vectors",
            "Click & drag: Aim cue stick"
        ]
        
        for i, help_text in enumerate(help_texts):
            text = self.font.render(help_text, True, self.colors['text'])
            self.screen.blit(text, (self.width - 200, 10 + i * 20))
    
    def handle_events(self):
        """
        Handle pygame events.
        
        Returns:
            bool: True if the simulation should continue, False if it should quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Mouse events for cue control
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if the click is on the cue ball
                mouse_pos = pygame.mouse.get_pos()
                mouse_pos_meters = self.pixels_to_meters(mouse_pos)
                
                for ball in self.physics_engine.active_balls:
                    if ball.number == 0:  # Cue ball
                        dist = np.linalg.norm(ball.position - mouse_pos_meters)
                        if dist < ball.radius * 3:  # Some leeway for clicking near the ball
                            self.cue_active = True
                            self.cue_start = self.meters_to_pixels(ball.position)
                            self.cue_end = mouse_pos
                            
            elif event.type == pygame.MOUSEMOTION and self.cue_active:
                self.cue_end = pygame.mouse.get_pos()
                
                # Calculate cue power based on distance
                if self.cue_start is not None:
                    dist = np.sqrt((self.cue_end[0] - self.cue_start[0])**2 + 
                                  (self.cue_end[1] - self.cue_start[1])**2)
                    self.cue_power = min(dist / 10, self.max_cue_power)
                
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.cue_active:
                if self.cue_start is not None and self.cue_end is not None and not self.paused:
                    # Calculate force vector (direction from cue end to cue ball)
                    force_direction = np.array([
                        self.cue_start[0] - self.cue_end[0],
                        self.cue_start[1] - self.cue_end[1]
                    ])
                    
                    # Normalize and scale by power
                    if np.linalg.norm(force_direction) > 0:
                        force_direction = force_direction / np.linalg.norm(force_direction)
                        force_vector = force_direction * self.cue_power
                        
                        # Convert to meters and apply to physics engine
                        force_vector_meters = np.array([
                            force_vector[0] / self.scale_x,
                            force_vector[1] / self.scale_y
                        ])
                        
                        self.physics_engine.strike_cue_ball(force_vector_meters)
                
                # Reset cue state
                self.cue_active = False
                self.cue_start = None
                self.cue_end = None
                self.cue_power = 0
                
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.physics_engine.setup_rack()
                elif event.key == pygame.K_t:
                    self.show_trajectories = not self.show_trajectories
                elif event.key == pygame.K_v:
                    self.show_velocities = not self.show_velocities
        
        return True
    
    def update(self, dt: float):
        """
        Update the visualization for one time step.
        
        Args:
            dt: Time step in seconds
        """
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Draw the table
        self.draw_table()
        
        # Draw trajectories
        if self.show_trajectories:
            for ball in self.physics_engine.active_balls:
                self.draw_trajectory(ball)
        
        # Draw active balls
        for ball in self.physics_engine.active_balls:
            self.draw_ball(ball)
        
        # Draw cue stick if active
        self.draw_cue_stick()
        
        # Draw game information
        self.draw_game_info()
        
        # Update the display
        pygame.display.flip()
    
    def run(self, target_fps: int = 60):
        """
        Run the visualization loop.
        
        Args:
            target_fps: Target frames per second
        """
        running = True
        dt = 1.0 / target_fps  # Time step in seconds
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update physics if not paused
            if not self.paused:
                self.physics_engine.update(dt)
            
            # Update visualization
            self.update(dt)
            
            # Control frame rate
            self.clock.tick(target_fps)
        
        # Clean up
        pygame.quit()
