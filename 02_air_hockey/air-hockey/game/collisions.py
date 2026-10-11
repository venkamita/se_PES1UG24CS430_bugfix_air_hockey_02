"""
collisions: puck-vs-paddle collision handling.
"""


def handle_paddle_collision(puck, paddle):
    """
    If the puck overlaps the paddle, reflect its velocity along the
    collision normal (the vector from paddle centre to puck centre)
    and push the puck outside the paddle so it can't tunnel or stick.
    Returns True if a collision was handled this frame.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    # Avoid division-by-zero if centres perfectly overlap
    if distance == 0:
        distance = 0.001
        dx, dy = 1, 0

    min_dist = puck.radius + paddle.radius
    if distance < min_dist:
        # 1. Collision normal (unit vector pointing from paddle → puck)
        nx = dx / distance
        ny = dy / distance

        # 2. Reflect velocity along the normal ONLY if puck is moving
        #    toward the paddle (dot < 0). If it's already separating,
        #    skip the flip — just let the positional push-out do its job.
        #    Without this guard the formula reverses an outgoing puck
        #    back into the paddle, producing the 180° "through the bat" bug.
        dot = puck.vx * nx + puck.vy * ny
        if dot < 0:
            puck.vx -= 2 * dot * nx
            puck.vy -= 2 * dot * ny

        # 3. Push puck outside the paddle so next frame won't re-trigger
        overlap = min_dist - distance
        puck.x += nx * overlap
        puck.y += ny * overlap

        return True

    return False
