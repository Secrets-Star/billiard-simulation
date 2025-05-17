import numpy as np
from typing import List, Tuple

class Ball:
    """
    Class representing a billiard ball with physical properties.
    """
    def __init__(self, position: np.ndarray, velocity: np.ndarray, radius: float = 0.0286, 
                 mass: float = 0.17, color: Tuple[int, int, int] = (255, 255, 255),
                 number: int = 0, angular_velocity: float = 0.0):
        """
        Initialize a billiard ball with physical properties.
        
        Args:
            position: 2D position vector [x, y] in meters
            velocity: 2D velocity vector [vx, vy] in m/s
            radius: Ball radius in meters (standard billiard ball = 2.86 cm)
            mass: Ball mass in kg (standard = 0.17 kg)
            color: RGB color tuple
            number: Ball number (0 for cue ball)
            angular_velocity: Initial angular velocity (rad/s)
        """
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.radius = radius
        self.mass = mass
        self.color = color
        self.number = number
        self.angular_velocity = angular_velocity
        
        # Moment of inertia for a solid sphere
        self.moment_of_inertia = (2/5) * mass * (radius ** 2)
        
        # Track history of positions for visualization
        self.position_history = [np.copy(position)]
        
    def update(self, dt: float, table_friction: float = 0.03):
        """
        Update ball position and velocity based on physics.
        
        Args:
            dt: Time step in seconds
            table_friction: Coefficient of rolling friction
        """
        # Apply friction to reduce velocity
        if np.linalg.norm(self.velocity) > 0:
            # Rolling friction force
            friction_deceleration = table_friction * 9.81  # μ * g
            
            # Unit vector in direction of velocity
            if np.linalg.norm(self.velocity) > 0:
                velocity_direction = self.velocity / np.linalg.norm(self.velocity)
            else:
                velocity_direction = np.zeros(2)
                
            # Apply friction as deceleration
            friction_deceleration_vector = -velocity_direction * friction_deceleration
            
            # Update velocity with friction
            self.velocity += friction_deceleration_vector * dt
            
            # Stop the ball if it's moving very slowly to prevent endless tiny movements
            if np.linalg.norm(self.velocity) < 0.01:
                self.velocity = np.zeros(2)
        
        # Update position
        self.position += self.velocity * dt
        
        # Update angular velocity (simplified - would be more complex with realistic spin)
        if np.linalg.norm(self.velocity) > 0:
            self.angular_velocity = np.linalg.norm(self.velocity) / self.radius
        
        # Store position for trajectory tracking
        self.position_history.append(np.copy(self.position))
        
        # Limit history length to avoid memory issues
        if len(self.position_history) > 1000:
            self.position_history.pop(0)


class BilliardTable:
    """
    Class representing a billiard table with dimensions and physics.
    """
    def __init__(self, length: float = 2.7, width: float = 1.35, 
                 cushion_elasticity: float = 0.7, friction: float = 0.03):
        """
        Initialize a billiard table with physical properties.
        
        Args:
            length: Table length in meters (standard table = 2.7m)
            width: Table width in meters (standard table = 1.35m)
            cushion_elasticity: Coefficient of restitution for cushions (0-1)
            friction: Coefficient of rolling friction
        """
        self.length = length
        self.width = width
        self.cushion_elasticity = cushion_elasticity
        self.friction = friction
        
        # Define pockets (as positions [x, y] and radius)
        pocket_radius = 0.06  # meters
        
        # Corner pockets
        corner_inset = 0.04  # How far in from the edge the pocket centers are
        self.pockets = [
            (np.array([corner_inset, corner_inset]), pocket_radius),  # Top left
            (np.array([length - corner_inset, corner_inset]), pocket_radius),  # Top right
            (np.array([corner_inset, width - corner_inset]), pocket_radius),  # Bottom left
            (np.array([length - corner_inset, width - corner_inset]), pocket_radius),  # Bottom right
        ]
        
        # Middle pockets (on long sides)
        middle_pocket_radius = 0.055  # Slightly smaller than corner pockets
        self.pockets.extend([
            (np.array([length / 2, 0]), middle_pocket_radius),  # Middle top
            (np.array([length / 2, width]), middle_pocket_radius),  # Middle bottom
        ])
        
    def check_cushion_collisions(self, ball: Ball):
        """
        Check and handle collisions with table cushions.
        
        Args:
            ball: Ball object to check for cushion collisions
        
        Returns:
            bool: Whether a collision occurred
        """
        collision = False
        
        # Check collision with left and right cushions
        if ball.position[0] - ball.radius < 0:
            ball.position[0] = ball.radius  # Reposition to prevent sticking
            ball.velocity[0] = -ball.velocity[0] * self.cushion_elasticity
            collision = True
            
        elif ball.position[0] + ball.radius > self.length:
            ball.position[0] = self.length - ball.radius  # Reposition to prevent sticking
            ball.velocity[0] = -ball.velocity[0] * self.cushion_elasticity
            collision = True
        
        # Check collision with top and bottom cushions
        if ball.position[1] - ball.radius < 0:
            ball.position[1] = ball.radius  # Reposition to prevent sticking
            ball.velocity[1] = -ball.velocity[1] * self.cushion_elasticity
            collision = True
            
        elif ball.position[1] + ball.radius > self.width:
            ball.position[1] = self.width - ball.radius  # Reposition to prevent sticking
            ball.velocity[1] = -ball.velocity[1] * self.cushion_elasticity
            collision = True
            
        return collision
    
    def check_pocket_collisions(self, ball: Ball) -> bool:
        """
        Check if a ball has fallen into a pocket.
        
        Args:
            ball: Ball to check
            
        Returns:
            bool: True if ball is in a pocket, False otherwise
        """
        for pocket_pos, pocket_radius in self.pockets:
            distance = np.linalg.norm(ball.position - pocket_pos)
            if distance < pocket_radius:
                return True
        
        return False


class PhysicsEngine:
    """
    Physics engine to simulate billiard ball dynamics.
    """
    def __init__(self, table: BilliardTable):
        """
        Initialize the physics engine.
        
        Args:
            table: BilliardTable object defining the playing surface
        """
        self.table = table
        self.balls = []
        self.active_balls = []  # Balls still on the table
        self.pocketed_balls = []  # Balls that have fallen into pockets
        
    def add_ball(self, ball: Ball):
        """
        Add a ball to the simulation.
        
        Args:
            ball: Ball object to add
        """
        self.balls.append(ball)
        self.active_balls.append(ball)
        
    def handle_ball_collision(self, ball1: Ball, ball2: Ball) -> bool:
        """
        Handle collision physics between two balls using conservation of momentum
        and energy with elastic collision equations.
        
        Args:
            ball1: First ball
            ball2: Second ball
            
        Returns:
            bool: Whether a collision occurred
        """
        # Vector from ball1 to ball2
        pos_diff = ball2.position - ball1.position
        distance = np.linalg.norm(pos_diff)
        
        # No collision if balls are too far apart
        if distance > ball1.radius + ball2.radius:
            return False
            
        # Normalize the position difference vector
        if distance > 0:
            normal = pos_diff / distance
        else:
            # If balls are exactly at the same position (should never happen),
            # use a random normal vector to push them apart
            normal = np.array([1, 0])
            
        # Relative velocity
        rel_velocity = ball2.velocity - ball1.velocity
        
        # Check if balls are moving toward each other
        velocity_along_normal = np.dot(rel_velocity, normal)
        
        # No collision if balls are moving away from each other
        if velocity_along_normal > 0:
            return False
            
        # Coefficient of restitution (1 for perfectly elastic collisions)
        restitution = 0.95
        
        # Calculate impulse scalar
        impulse = -(1 + restitution) * velocity_along_normal
        impulse /= (1 / ball1.mass + 1 / ball2.mass)
        
        # Apply impulse to ball velocities
        ball1.velocity -= (impulse / ball1.mass) * normal
        ball2.velocity += (impulse / ball2.mass) * normal
        
        # Move balls apart to prevent sticking (resolving penetration)
        penetration_depth = (ball1.radius + ball2.radius) - distance
        if penetration_depth > 0:
            # Move each ball proportionally to its mass
            total_mass = ball1.mass + ball2.mass
            ball1.position -= (penetration_depth * ball2.mass / total_mass) * normal
            ball2.position += (penetration_depth * ball1.mass / total_mass) * normal
        
        return True
    
    def update(self, dt: float):
        """
        Update all balls in the simulation for one time step.
        
        Args:
            dt: Time step in seconds
        """
        # Update ball positions and velocities
        for ball in self.active_balls:
            ball.update(dt, self.table.friction)
            
        # Check for ball-cushion collisions
        for ball in self.active_balls:
            self.table.check_cushion_collisions(ball)
            
        # Check for ball-ball collisions
        n = len(self.active_balls)
        for i in range(n):
            for j in range(i + 1, n):
                self.handle_ball_collision(self.active_balls[i], self.active_balls[j])
                
        # Check for pocket collisions and remove pocketed balls
        still_active = []
        for ball in self.active_balls:
            if self.table.check_pocket_collisions(ball):
                self.pocketed_balls.append(ball)
            else:
                still_active.append(ball)
                
        self.active_balls = still_active
        
    def strike_cue_ball(self, force_vector: np.ndarray):
        """
        Apply a force to the cue ball (ball with number 0).
        
        Args:
            force_vector: 2D force vector [fx, fy] representing the direction and 
                         magnitude of the strike
        """
        for ball in self.active_balls:
            if ball.number == 0:  # Cue ball
                # F = ma, so a = F/m
                acceleration = force_vector / ball.mass
                # Assume the force is applied instantaneously (impulse)
                ball.velocity += acceleration
                return True
        
        return False  # Cue ball not found
    
    def is_simulation_still(self) -> bool:
        """
        Check if all balls have stopped moving.
        
        Returns:
            bool: True if all balls are still, False otherwise
        """
        for ball in self.active_balls:
            if np.linalg.norm(ball.velocity) > 0.01:  # Threshold for considering a ball "moving"
                return False
        
        return True
    
    def reset_simulation(self):
        """Reset the simulation by clearing all balls."""
        self.balls = []
        self.active_balls = []
        self.pocketed_balls = []
    
    def setup_rack(self, initial_cue_position=None):
        """
        Set up a standard 15-ball rack plus the cue ball.
        
        Args:
            initial_cue_position: Optional custom position for the cue ball
        """
        self.reset_simulation()
        
        # Ball radius and spacing
        radius = 0.0286  # meters
        spacing = 2 * radius * 1.01  # slight spacing between balls
        
        # Ball colors (simplified)
        colors = {
            'cue': (255, 255, 255),
            'solid': [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                     (0, 128, 0), (0, 0, 255), (75, 0, 130), (128, 0, 0)],
            'stripe': [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                      (0, 128, 0), (0, 0, 255), (75, 0, 130), (128, 0, 0)],
            'black': (0, 0, 0)
        }
        
        # Position of the apex ball (front of the rack)
        apex_position = np.array([self.table.length * 0.75, self.table.width / 2])
        
        # Set up the triangle rack
        ball_number = 1
        row_sizes = [1, 2, 3, 4, 5]  # Number of balls in each row
        
        # Place balls row by row
        for row_idx, row_size in enumerate(row_sizes):
            for i in range(row_size):
                # Calculate position in the rack
                x = apex_position[0] - row_idx * spacing * np.cos(np.pi/6)
                y = apex_position[1] + (i - (row_size - 1) / 2) * spacing
                
                # Determine color based on ball number
                if ball_number == 8:
                    color = colors['black']
                elif ball_number < 8:
                    color = colors['solid'][ball_number - 1]
                else:
                    color = colors['stripe'][ball_number - 9]
                
                # Create the ball
                new_ball = Ball(
                    position=np.array([x, y]),
                    velocity=np.zeros(2),
                    radius=radius,
                    color=color,
                    number=ball_number
                )
                
                self.add_ball(new_ball)
                ball_number += 1
        
        # Add cue ball
        if initial_cue_position is None:
            initial_cue_position = np.array([self.table.length * 0.25, self.table.width / 2])
            
        cue_ball = Ball(
            position=initial_cue_position,
            velocity=np.zeros(2),
            radius=radius,
            color=colors['cue'],
            number=0
        )
        
        self.add_ball(cue_ball)
