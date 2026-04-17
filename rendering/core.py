import arcade
import math
from pygame.math import Vector2 

def solve_ik_2joint(start, target, len1, len2, bend_right=True):
    """
    Решает задачу инверсной кинематики для двух сегментов (ноги, руки).
    Возвращает позиции колена/локтя и конца конечности.
    """
    start_vec = Vector2(start)
    target_vec = Vector2(target)
    diff = target_vec - start_vec
    dist = diff.length()
    full_len = len1 + len2
    
    # Если цель слишком далеко — тянемся к ней по прямой
    if dist >= full_len:
        direction = diff.normalize()
        return start_vec + direction * len1, start_vec + direction * full_len
    
    # Теорема косинусов для угла сгиба
    try:
        cos_angle = (len1**2 + dist**2 - len2**2) / (2 * len1 * dist)
        angle_a = math.acos(max(-1, min(1, cos_angle)))
    except ValueError:
        angle_a = 0

    base_angle = math.atan2(diff.y, diff.x)
    
    if bend_right: 
        joint_angle = base_angle + angle_a
    else: 
        joint_angle = base_angle - angle_a
        
    joint_pos = start_vec + Vector2(math.cos(joint_angle), math.sin(joint_angle)) * len1
    return joint_pos, target_vec

def draw_organic_polygon(point_list, color):
    """Рисует полигон, принимая список Vector2 или кортежей."""
    clean_points = [(p[0], p[1]) for p in point_list]
    arcade.draw_polygon_filled(clean_points, color)

def draw_bone_segment(start, end, color, width_start, width_end):
    """Рисует сегмент конечности с закругленными краями."""
    start = Vector2(start)
    end = Vector2(end)
    vec = end - start
    if vec.length() < 1: return
    
    # В Arcade Y растет вверх, перпендикуляр считаем соответственно
    perp = Vector2(vec.y, -vec.x).normalize()
    
    p1 = start + perp * (width_start / 2)
    p2 = end + perp * (width_end / 2)
    p3 = end - perp * (width_end / 2)
    p4 = start - perp * (width_start / 2)
    
    points = [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y), (p4.x, p4.y)]
    arcade.draw_polygon_filled(points, color)
    arcade.draw_circle_filled(start.x, start.y, width_start / 2, color)
    arcade.draw_circle_filled(end.x, end.y, width_end / 2, color)