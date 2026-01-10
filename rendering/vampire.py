import arcade
import math
from pygame.math import Vector2 
# Импортируем базу
from .core import solve_ik_2joint, draw_organic_polygon, draw_bone_segment

# --- ПАЛИТРА ---
SKIN_PALE = (245, 240, 250)
CLOTH_MAIN = (25, 20, 30)
CLOTH_ACCENT = (140, 10, 40)
HAIR_COLOR = (15, 15, 20)

def draw_vampire_arcade(center_x, center_y, angle, walk_cycle, vel_length, cape_points, alpha_mult=1.0):
    center = Vector2(center_x, center_y)
    
    # Логика поворота
    facing_right = 270 > angle > 90 or angle < -90
    dir_sk = 1 if facing_right else -1
    is_moving = vel_length > 0.1
    
    # --- 1. СКЕЛЕТ ---
    bounce = abs(math.sin(walk_cycle)) * 4 if is_moving else 0
    
    hip_pos = Vector2(center.x, center.y - 5 + bounce)
    waist_pos = hip_pos + Vector2(0, 12)
    chest_pos = waist_pos + Vector2(0, 15)
    neck_base = chest_pos + Vector2(0, 8)
    head_pos = neck_base + Vector2(2 * dir_sk, 10) 
    
    shoulder_w = 12
    shoulder_l = chest_pos + Vector2(-shoulder_w, 0)
    shoulder_r = chest_pos + Vector2(shoulder_w, 0)

    # --- 2. НОГИ (IK) ---
    ground_y = center_y - 32
    foot_targets = []
    phases = [walk_cycle, walk_cycle + math.pi]
    
    for phase in phases:
        c_x, c_y = math.cos(phase), math.sin(phase)
        step_x = c_x * 20 * dir_sk
        lift = max(0, -c_y) * 10 
        target = Vector2(hip_pos.x + step_x, ground_y + lift)
        
        if is_moving: 
            # Небольшое отставание ног при движении
            shift = math.cos(math.radians(angle)) * vel_length * 0.1
            target.x -= shift

        foot_targets.append(target)
        
    if facing_right:
        idx_back, idx_front = 1, 0
        shoulder_front, shoulder_back = shoulder_l, shoulder_r
    else:
        idx_back, idx_front = 0, 1
        shoulder_front, shoulder_back = shoulder_r, shoulder_l

    # ========= СЛОИ ОТРИСОВКИ =========

    # 1. Задняя нога
    _draw_leg(hip_pos, foot_targets[idx_back], 18, 20, facing_right, is_back=True)

    # 2. Плащ (Задний план)
    if cape_points and len(cape_points) > 2:
        cape_poly = []
        cape_poly.append((shoulder_l.x, shoulder_l.y + 2))
        cape_poly.append((shoulder_r.x, shoulder_r.y + 2))
        
        for i, p in enumerate(cape_points):
            w = 18 * (1 - (i/len(cape_points))**0.6)
            cape_poly.append((p.x + w, p.y))
        for i in range(len(cape_points)-1, -1, -1):
            p = cape_points[i]
            w = 18 * (1 - (i/len(cape_points))**0.6)
            cape_poly.append((p.x - w, p.y))
            
        draw_organic_polygon(cape_poly, (50, 5, 15))

    # 3. Воротник
    col_h = 18
    col_poly = [
        (shoulder_l.x, shoulder_l.y),
        (shoulder_l.x + 3, shoulder_l.y + col_h), 
        (shoulder_r.x - 3, shoulder_r.y + col_h), 
        (shoulder_r.x, shoulder_r.y)
    ]
    draw_organic_polygon(col_poly, CLOTH_MAIN)
    
    # 4. Торс и Жилет
    pelvis_poly = [
        (hip_pos.x - 8, hip_pos.y), (hip_pos.x + 8, hip_pos.y),
        (waist_pos.x + 9, waist_pos.y), (waist_pos.x - 9, waist_pos.y)
    ]
    draw_organic_polygon(pelvis_poly, CLOTH_MAIN)
    
    torso_poly = [
        (waist_pos.x - 9, waist_pos.y), (waist_pos.x + 9, waist_pos.y),
        (shoulder_r.x, shoulder_r.y), (shoulder_l.x, shoulder_l.y)
    ]
    draw_organic_polygon(torso_poly, CLOTH_MAIN)
    
    vest_poly = [
        (waist_pos.x, waist_pos.y - 2),
        (shoulder_r.x - 4, shoulder_r.y),
        (shoulder_l.x + 4, shoulder_l.y)
    ]
    draw_organic_polygon(vest_poly, CLOTH_ACCENT)

    # 5. Голова
    draw_bone_segment(neck_base, head_pos, SKIN_PALE, 6, 6)
    _draw_anime_head(head_pos, angle, dir_sk)

    # 6. Передняя нога
    _draw_leg(hip_pos, foot_targets[idx_front], 18, 20, facing_right, is_back=False)

    # 7. Руки
    arm_back_angle = math.radians(-80 - math.sin(walk_cycle)*20)
    _draw_arm(shoulder_back, arm_back_angle, 13, 12, CLOTH_MAIN, SKIN_PALE)
    
    aim_rad = math.radians(angle)
    _draw_arm(shoulder_front, aim_rad, 13, 12, CLOTH_MAIN, SKIN_PALE, has_magic=True)

def _draw_anime_head(center, angle, dir_sk):
    chin_y = -8
    height_up = 9
    width = 7
    
    face_poly = [
        (center.x - width * dir_sk, center.y + height_up),
        (center.x + (width-1) * dir_sk, center.y + height_up),
        (center.x + (width) * dir_sk, center.y),
        (center.x + 2 * dir_sk, center.y + chin_y),
        (center.x - (width-1) * dir_sk, center.y + chin_y + 2),
        (center.x - width * dir_sk, center.y)
    ]
    draw_organic_polygon(face_poly, SKIN_PALE)
    
    face_off = Vector2(3 * dir_sk, 1)
    eye_pos = center + face_off
    arcade.draw_circle_filled(eye_pos.x, eye_pos.y, 1.5, (220, 20, 20))

    hair_back = [
        (center.x - 5*dir_sk, center.y + 8),
        (center.x - 9*dir_sk, center.y - 4),
        (center.x - 3*dir_sk, center.y - 12),
        (center.x + 3*dir_sk, center.y + 4)
    ]
    draw_organic_polygon(hair_back, HAIR_COLOR)

def _draw_leg(hip, target, l1, l2, facing_right, is_back):
    knee, ankle = solve_ik_2joint(hip, target, l1, l2, bend_right=facing_right)
    col = CLOTH_MAIN if not is_back else (15, 10, 15)
    draw_bone_segment(hip, knee, col, 8, 6)
    draw_bone_segment(knee, ankle, col, 6, 4)
    
    boot_toe = ankle + Vector2(5 if facing_right else -5, -2)
    boot_poly = [(ankle.x-2, ankle.y+1), (ankle.x+2, ankle.y+1), (boot_toe.x, boot_toe.y+2), (boot_toe.x, boot_toe.y-2)]
    draw_organic_polygon(boot_poly, (10, 10, 10))

def _draw_arm(shoulder, angle, l1, l2, color, skin, has_magic=False):
    elbow = shoulder + Vector2(math.cos(angle), math.sin(angle)) * l1
    hand_angle = angle - math.radians(20* (1 if angle < 0 or angle > math.pi else -1)) 
    hand = elbow + Vector2(math.cos(hand_angle), math.sin(hand_angle)) * l2
    
    draw_bone_segment(shoulder, elbow, color, 7, 5)
    draw_bone_segment(elbow, hand, color, 5, 4)
    arcade.draw_circle_filled(hand.x, hand.y, 3, skin)
    
    if has_magic:
        arcade.draw_circle_filled(hand.x, hand.y, 5, (255, 50, 50, 150))
        arcade.draw_circle_filled(hand.x, hand.y, 3, (255, 200, 200))