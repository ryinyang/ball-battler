# Ball Battler

A physics-based Auto-Battler where RPG-themed balls battle in an arena. Built with Python, Pygame, and Pymunk. Heavily inspired by Earclacks.

## Overview

Ball Battler is a simulation where autonomous circles ("balls") fight in a closed arena. Each ball represents an RPG class (Rogue, Berserker, Paladin, Monk) with unique stats and weapon scaling mechanics. The game relies on Pymunk for physics simulation (movement, collisions, bounces) and Pygame for rendering.

## Architecture

- **Language**: Python 3.12+
- **Rendering**: Pygame
- **Physics Engine**: Pymunk
- **Package Manager**: uv

## Setup

This project uses `uv` for dependency management.

1. **Install uv**:
   If you haven't already, install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Initialize Environment**:
   Navigate to the project folder and sync dependencies:
   ```bash
   uv sync
   ```
   *Note: The project is pinned to Python 3.12 to ensure compatibility with Pygame wheels.*

## Running the Game

To start the simulation:

```bash
uv run main.py
```
