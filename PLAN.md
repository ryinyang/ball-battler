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
## Phase 1: Core Combat & Stats

In this phase, we move from "bouncing balls" to "battling balls" by introducing stats and hit registration.

- Stat Component: Expand the `Ball` class with attributes: `hp`, `max_hp`, `attack`, `defense`, `attack_speed`, and `speed` (to apply periodic impulses so they keep moving).
    - Collision Callbacks: Use Pymunk’s `CollisionHandler` to trigger logic when two ball shapes overlap.
    - Damage Logic: When a valid collision occurs, calculate damage. A standard formula works well here:
        Damage=max(1,Attackeratk​−Defenderdef​)
    - Death Loop: If a ball's `hp` drops to 0 or below, safely remove its body and shape from the Pymunk space and its instance from the Pygame render list.
## Phase 2: Basic UI & Physics Tweaks

In this phase, we add some basic UI to keep track of the main stats of each ball and tweak the physics.

- Basic UI: 
    - Name and Status: On either side of the arena, show the HP, of each ball
- Physics Tweaks:
    - When the balls collide, add a small amount of velocity ~1%
    - Colliding with walls should not reduce the velocity
    - Add an attraction force between balls. As they get closer to each other, they accelerate a towards each other. Ensure this attraction force is much smaller than the gravity force.
## Phase 3: The Ghost-Weapon System

The goal of this phase is to attach a rotating weapon to each ball that detects hits but exerts zero physical force on the owner while still exerting physical force on the target.

### Step 3.1: Defining the Sensor Hitbox

Instead of a physical object that bounces, the weapon will be a "Sensor" attached to the Ball’s existing body.
- The Shape: Add a `pymunk.Poly` (rectangle) to the same `Body` as the Ball.
- The Sensor Flag: Set `shape_weapon.sensor = True`. This allows the weapon to overlap with other objects without causing a collision response (no bouncing, no friction).
- Collision Filtering: Assign the weapon a unique `collision_type` (e.g., `2`) so the physics engine can distinguish between a "Body-to-Body" bump and a "Weapon-to-Body" strike.

### Step 3.2: Decoupled Rotation Logic

To prevent the weapon from spinning the ball like a top, you will handle the weapon’s rotation independently in the game loop.
- The Offset Math: Do not rely on the Ball's own rotation (which changes when it hits walls). Instead, maintain a `self.weapon_angle` variable in your Ball class.
- Manual Update: Every frame, increment `self.weapon_angle` based on the class’s `attack_speed`.
- Vertex Transformation: Update the weapon shape’s vertices every frame using a rotation matrix so it orbits the center of the ball.
    
    x′=xcos(θ)−ysin(θ)
    y′=xsin(θ)+ycos(θ)

### Step 3.3: The "Trigger" Callback

Since the weapon is a sensor, it won't "hit" the enemy automatically. You must catch the overlap event.

- Collision Handler: Register a `begin` callback in Pymunk for `(BALL_TYPE, WEAPON_TYPE)`.
- The Logic:
    1. Check if the weapon’s owner is different from the ball being hit.
    2. If ready: Apply damage to the target and trigger the attacker's `on_hit()` scaling logic (e.g., Rogue gains +5% speed).
- Visual-Only Knockback: If you want the hit to _look_ powerful, manually apply a small `impulse` to the target ball only inside this callback. This keeps the attacker’s movement "pure."


### Step 3.4: Visual Rendering

Since the sensor is invisible in the physics simulation, you must draw it manually in Pygame.
- Use `pygame.draw.polygon()` using the coordinates calculated in Step 3.2.
- Polish: Color the weapon based on the class (Rogue = Purple, Berserker = Red) and make it flash white for 2 frames when it successfully triggers a hit.
## Phase 4: Refactor

In this phase, we will refactor our existing codebase so that it is readable, clean, and extensible.

### Recommended Patterns

Inheritance & Polymorphism (The RPG Classes)
- Why: Phase 4 requires distinct classes (Rogue, Berserker, etc.) with unique weapon shapes, rotation speeds, and on_hit behaviors.
- How: Refactor Ball into a base class containing the core physics and stat logic. Create subclasses (Rogue, Berserker) that override specific methods like _setup_weapon() and on_hit().

The "Game Director" Pattern (Encapsulation)
- Why: Currently, main.py relies on global variables and a raw while loop. This makes it difficult to reset the game (Phase 6) or manage complex states.
- How: Encapsulate the game state (Pymunk space, Pygame screen, entity lists) into a Game class. This class handles initialization, the main loop, and cleanup.

Composition (The Arena)
- Why: Phase 5 introduces custom arenas and obstacles. Hardcoding segments in main.py is not scalable.
- How: Create an Arena class responsible for generating walls and static obstacles. The Game class simply asks the Arena to "build" itself into the space.

Separation of Physics & Logic
- Why: Collision handlers currently mix logging, damage calculation, and physics impulses.
- How: Keep collision callbacks focused. They should identify the entities involved and delegate the gameplay logic (damage, effects) to the entities themselves (e.g., attacker.deal_damage(target)).

## Phase 5: Add RPG Classes

Each class will now define the _dimensions_ of its sensor and the _speed_ of its rotation.

| Class     | Sensor Dimensions          | Rotation Behavior                       |
| --------- | -------------------------- | --------------------------------------- |
| Rogue     | Thin & Short (Dagger)      | High RPM; resets angle slightly on hit. |
| Berserker | Wide & Long (Axe)          | Slow RPM; heavy visual trail.           |
| Monk      | Two small Squares (Fists)  | Rapid 180-degree alternating strikes.   |
| Ranger    | Shoots arrows out of a bow | High RPM                                |
## Phase 6: Combat Tweaks

- Bullet Time: When a weapon connects with a target ball, temporarily slow down time to emphasize the hit.
    - Visually highlight which balls are in bullet time
- Counter Rotation: When a weapon connects with a target ball, reverse the direction of the weapon's rotation.
- Weapon collisions: When a weapon connects with another weapon, deal no damage, reverse weapon rotation, and apply knockback impulse

## Phase 7: Custom Arenas & Obstacles

Once combat is functional, it's time to extend the environment beyond a simple box to create tactical depth.

- [x] Arena Refactor
	- [x] Arena Factory: Create an `Arena` class that accepts a list of coordinates to draw complex boundary polygons instead of just a rectangle.
	- [x] Refactor the original rectangle arena as a new class using the factory. Call this class BasicArena
	- [x] New Arena: The Octagon
	    - This arena is a standard 8 sided octagon
	    - The bottom wall will be extra bouncy, causing balls to rapidly increase velocity
- Obstacles: Some wall or structure in the Arena that impacts the battle. Usually permanent.
	- Neutral Obstacles:
		- [x] Bumper Obstacle: When a ball contacts a Bumper, increase the speed of that ball.
	- Hazardous Obstacles: (Later)
		- [ ] Sticker Obstacle: When a ball contacts a Sticker, make it stick to the wall temporarily, then reduce its velocity.
		- [ ] Poker Obstacle: When a ball contacts a Poker, deal damage to that ball
		- [ ] Slow-Mo-Zone: The first ball to enter this zone slows down to 1% normal speed. Has a cool down until another ball can trigger this effect.
		- [ ] Speed Boost Zone: When a ball enters this zone, it accelerates in the direction of the boost.
	- Buffing Obstacles:
		- [ ] Attack Buff: When a ball contacts a Attack Buff, increase that ball's attack.
- Items: A item is something that can give a Ball some benefit. Usually temporary or consumable.
	- [x] Healing Ball: A consumable that, when collected by a ball, heals that ball by X HP
- Anomalies: Special effects that Arenas may contain that drastically change the way that the battle is played. Usually unique to an Arena.
	- [x] Black hole: A non-solid, temporary, strong attraction force that pulls all balls towards it. Manifests as a black hole that draws a circle in the middle of the arena. After slowly walking the circular path, it disappears, allowing balls to resume their original trajectories.

Misc Changes:
- [x] Remove Defense as a stat. As a viewer, it is difficult to understand defense. To rebalance, add more HP relative to the defense characters had.
- [ ] Refactor the logic that populates an Arena with Obstacles, Items, and Anomalies such that the game client can decide at run time which things to add to an Arena. Make it modular and easy to customize.
- [ ] Refactor Obstacles into a separate file
## Phase 8: UI & Polish

Make the simulation readable and satisfying to watch.

Classes
- Select a few classes from Earclacks to emulate. Replace the ones we have now.

Combat
- Add unique scaling for each class type.

UI
- Health Display on Balls: Show the current HP on the ball itself as well
- Visual Feedback: 
	- Attack Feedback: Briefly flash the ball white when it takes damage, or add a small colored particle effect when a class scales its stat.
	- Bumper Feedback
	- Bouncy Wall Feedback
- Match State: Add text to display the winner when only one class/team remains, and a keybind to reset the arena.
- Pixel Art: Add pixel art for each weapon type using OpenMoji and PixelIt
- Sounds
    - Weapon on Weapon CLANG
    - Weapon on Ball OOF

UX
- Customizable Frame Rate
- Octagon Arena:
    - Add some visual indicator that the bottom wall accelerates the ball
- Post Battle Screen (Metrics):
    - Who won?
    - How much damage did each ball do?
    - What was the average speed of each ball?
    - Superlatives
        - Most damage, highest speed, most hits
- Build your own battlers
    - Select base, weapon, class? Would probably require a full refactor of the data models/classes.

Arenas
- New Arena: Wrestling Ring
    - The walls of this Arena are elastic, like the a Wrestling Ring
    - Bouncing on the wall will 
        - Start Bullet Time
        - Aim the ball directly towards a target ball
    - For balance reasons, the wall should have some cooldown time or maybe switch to a different wall
    - Balance Idea: Bottom wall is bouncy while top wall aims directly to the target ball

## Phase 9: Machine Learning

In this phase, we add Machine Learning techniques to play around with the classes, their stats, and balance.

- Refactor so that we can tweak all aspects of config, including:
    - Ball stats
    - Physics
    - Battle configurations (number of balls, which ball types)
- Refactor so that we can run the simulation in 2 modes:
    - Normal mode: allow user to view the battles as normal
    - Instant mode: don't render anything to the user, just simulate the battle internally and return the results
- Add libs (research which makes the most sense for our usecase)

## Phase x: Refactoring and Testing and Bug Fixes

Refactor the code to clean everything up. Add tests to ensure features are built correctly.

- Extensible
- Clean Code
- Modular
- main.py
    - Separate physics, drawing, and logic
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