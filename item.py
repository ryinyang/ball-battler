import pygame
import pymunk
import config

class Item:
    def __init__(self, space, x, y):
        self.space = space
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x, y)
        
        self.shape = pymunk.Circle(self.body, config.ITEM_RADIUS)
        self.shape.sensor = True # Items are collected, not collided with
        self.shape.collision_type = config.COLLISION_TYPE_ITEM
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_ITEM)
        self.shape.item = self # Link back to the item instance
        
        self.color = config.COLOR_ITEM_DEFAULT
        self.space.add(self.body, self.shape)

    def draw(self, screen):
        """Placeholder draw method."""
        pos = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, self.color, pos, config.ITEM_RADIUS)
        pygame.draw.circle(screen, (255, 255, 255), pos, config.ITEM_RADIUS, 2) # White border

    def apply_effect(self, ball):
        """Placeholder for item effect logic."""
        print(f"Item collected by {ball.name}, but has no effect yet.")
        pass

    def remove(self):
        """Safely remove the item from the space."""
        self.space.remove(self.body, self.shape)

class Potion(Item):
    def __init__(self, space, x, y):
        super().__init__(space, x, y)
        self.color = config.COLOR_ITEM_HEAL

    def apply_effect(self, ball):
        old_hp = ball.hp
        ball.hp = min(ball.max_hp, ball.hp + config.ITEM_HEAL_AMOUNT)
        print(f"{ball.name} healed for {int(ball.hp - old_hp)} HP!")