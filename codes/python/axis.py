import math


def player_axis(angle):
    rad = math.radians(angle)
    x_axis = (math.sin(rad), math.cos(rad))
    y_axis = (math.cos(rad), -math.sin(rad))
    return x_axis, y_axis


def world_to_player(dx_world, dy_world, angle):
    x_axis, y_axis = player_axis(angle)
    px = dx_world * x_axis[0] + dy_world * x_axis[1]
    py = dx_world * y_axis[0] + dy_world * y_axis[1]
    return px, py
