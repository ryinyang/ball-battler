## Phase 0: The Minimum Viable Physics (MVP)

The goal of this phase is strictly a "Zero-Player Game" where circles bounce in a box. No classes or stats yet—just a functional environment, collision, and rendering.

1. WSL & Environment Setup:
    - Open your WSL terminal and initialize the project: `uv init ball-battler`.
    - Pin the Python version to 3.12 to ensure compatibility: `uv python pin 3.12`.
    - Add the required dependencies: `uv add pygame pymunk`.
2. The Pymunk Space:
    - Initialize a `pymunk.Space()`.
    - Set a baseline gravity vector (e.g., g=(0,900)).
3. The Arena Walls:
    - Create four `pymunk.Segment` objects attached to the space's static body to form a closed rectangular screen boundary. Set their elasticity so balls can bounce.
4. The Combatants (Basic Balls):
    - Create a simple `Ball` class that wraps a `pymunk.Body` (set to dynamic) and a `pymunk.Circle` shape.
5. The Game Loop:
    - Implement the standard Pygame `while` loop.
    - In each iteration, call `space.step(dt)` to advance the physics, clear the screen, and draw the Pygame circles at the coordinates of the Pymunk bodies.
6. Documentation:
    - Update the README.md to document the project's overview and architecture, set up, and how to run the game
---
## Phase 1: Core Combat & Stats

In this phase, we move from "bouncing balls" to "battling balls" by introducing stats and hit registration.

- Stat Component: Expand the `Ball` class with attributes: `hp`, `max_hp`, `attack`, `defense`, `attack_speed` (which will act as a cooldown timer between hits), and `speed` (to apply periodic impulses so they keep moving).
    - Collision Callbacks: Use Pymunk’s `CollisionHandler` to trigger logic when two ball shapes overlap.
    - Damage Logic: When a valid collision occurs (and attack cooldown is 0), calculate damage. A standard formula works well here:
        Damage=max(1,Attackeratk​−Defenderdef​)
    - Death Loop: If a ball's `hp` drops to 0 or below, safely remove its body and shape from the Pymunk space and its instance from the Pygame render list.
---
## Phase 2: Basic UI & Physics Tweaks

In this phase, we add some basic UI to keep track of the main stats of each ball and tweak the physics.

- Basic UI: 
    - Name and Status: On either side of the arena, show the HP, of each ball
- Physics Tweaks:
    - When the balls collide, add a small amount of velocity ~1%
    - Colliding with walls should not reduce the velocity
    - Add an attraction force between balls. As they get closer to each other, they accelerate a towards each other. Ensure this attraction force is much smaller than the gravity force.
---
## Phase 3: Add Weapons & Class Logic

In this phase, we transition from simple collisions to "Weapon-to-Body" combat. Each ball becomes a composite object: a core (the Ball) and an orbiting limb (the Weapon).

### Phase 3.1: The Physics of Attachment

To make weapons feel "connected" but physically reactive, you shouldn't just hard-code their position. Use Pymunk’s constraints.

1. Weapon Initialization:
    - Create a `Weapon` class that holds a `pymunk.Poly` (the rectangle) and a `pymunk.Body`.
    - The Pivot: Use a `pymunk.PivotJoint` to anchor the weapon body to the ball body.
    - The Motor: Use a `pymunk.SimpleMotor` or `pymunk.GearJoint` between the ball and the weapon to keep the weapon spinning at a constant `angular_velocity`.
2. Collision Filtering:
    - Assign `collision_type` integers (e.g., BALL=1, WEAPON=2).
    - Use `shape.filter` to ensure a Ball's weapon passes through its own owner but still hits the enemy Ball and the enemy's Weapon (clashing).

### Phase 3.2: RPG Classes & Scaling Weapons

Create a class hierarchy where each subclass defines its own weapon "feel" and its unique `on_hit` stat-scaling logic.

|Class|Weapon Physics|Scaling Logic (Triggered On-Hit)|
|---|---|---|
|Rogue|Dagger: Short, light-weight rectangle with high motor speed.|`self.speed_limit *= 1.05`. Incremental speed boost makes it harder to hit but more chaotic.|
|Berserker|Axe: Long, heavy rectangle with high moment of inertia.|`self.attack += 2`. Damage increases linearly; rewards staying alive.|
|Paladin|Mace: Huge mass, slow rotation, high elasticity.|`self.defense += 1`. Increases the "damage reduction" constant in your Phase 1 formula.|
|Monk|Fists: Two very small, very fast-rotating shapes.|`self.cooldown_mod *= 0.95`. Decreases the internal timer between allowed damage ticks.|

### Phase 3.3: The "On-Hit" Pipeline

To make the scaling work, you need a clean communication line between Pymunk and your Python classes:

1. Collision Data: Attach the Python object instance to the Pymunk shape using `shape.parent = self`.    
2. The Callback: In your Pymunk `PostSolve` collision handler:
    - Identify if a `Weapon` hit a `Ball`.
    - Retrieve the owner of the weapon.
    - Call `owner.on_hit(target)` to trigger the class-specific scaling logic (e.g., the Rogue getting faster).
3. Visual "Oomph": When `on_hit` triggers, change the weapon color briefly to a "glow" state to show the player that a stat-up just occurred.

---
## Phase 4: Custom Arenas & Obstacles

Once combat is functional, it's time to extend the environment beyond a simple box to create tactical depth.

- Arena Factory: Create an `Arena` class that accepts a list of coordinates to draw complex boundary polygons instead of just a rectangle.
    - Static Obstacles: Add interior walls or "bumpers" (static Pymunk circles or polygons) that balls can bounce off of to disrupt trajectories.
    - Kinematic Hazards: Introduce slowly spinning kinematic platforms in the center of the arena that alter the physics of the battle without taking damage.
---
## Phase 5: UI & Polish

Make the simulation readable and satisfying to watch.

- Health Bars: Use Pygame's drawing functions to render a small green/red rectangle directly above each ball's current (x,y) coordinates.
    - Visual Feedback: Briefly flash the ball white when it takes damage, or add a small colored particle effect when a class scales its stat.
    - Match State: Add text to display the winner when only one class/team remains, and a keybind to reset the arena.

---
## Phase 6: Refactoring and Testing

Refactor the code to clean everything up. Add tests to ensure features are built correctly.

- Extensible
- Clean Code
- Modular
- Pytest
    - Layer A: Logic & Physics (Headless): This is where you test Pymunk. You don’t need a Pygame window to open for this.
        - What to test: Does a ball fall at the correct rate? Do two objects trigger a collision callback?
        - How: Create a Pymunk Space, add bodies, and call space.step(dt) manually in your test. Assert that the body.position is what you expect.
    - Layer B: Input & Events
        - What to test: Does pressing 'Space' apply an impulse to the player character?
        - How: Use pygame.event.post() to inject a fake keyboard event into the queue, then run one frame of your update logic and check the physics body's velocity.
    - Layer C: Rendering (Visual Regression)
        - What to test: Is the player sprite actually being drawn at the physics body's coordinates?
        - How: You can use "Snapshot Testing." Save a "golden" image of a frame and compare the pixel data of your current Surface against it using pygame.image.tostring().