import arcade
import math
from pygame.math import Vector2

# ==========================================
# --- ПАЛИТРА (VAMPIRE PALE) ---
# ==========================================
C_SKIN_BASE = (235, 235, 245)      # Мертвенно-бледный
C_SKIN_SHADOW = (190, 190, 210)    # Холодная тень
C_OUTLINE = (20, 15, 25)           # Темный контур
C_EYE_GLOW = (255, 50, 50)         # Красные глаза

# --- ПАЛИТРА КОСТЮМА ---
C_CLOTH_MAIN = (35, 30, 40)        # Темно-серый/почти черный
C_CLOTH_ACCENT = (140, 20, 40)     # Кроваво-бордовый

# ==========================================
# --- ВСПЫМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
# ==========================================
def clean_polygon_points(points, min_dist_sq=0.25):
    """
    Удаляет слишком близкие точки из полигона, чтобы Arcade мог его залить.
    Необходима для сложных контуров из кривых Безье.
    """
    if not points: return []
    clean = [points[0]]
    for p in points[1:]:
        if p.distance_squared_to(clean[-1]) > min_dist_sq:
            clean.append(p)
    return clean

# ==========================================
# --- АДАПТЕРЫ ARCADE ---
# ==========================================
def draw_polygon_arcade(points, color):
    if len(points) < 3: return
    # Arcade принимает список точек [(x,y), ...]
    pts = [(p.x, p.y) if hasattr(p, 'x') else p for p in points]
    arcade.draw_polygon_filled(pts, color)

def draw_line_strip_arcade(points, color, line_width=1.5):
    if len(points) < 2: return
    pts = [(p.x, p.y) if hasattr(p, 'x') else p for p in points]
    arcade.draw_line_strip(pts, color, line_width)

def draw_circle_arcade(center, radius, color):
    cx = center.x if hasattr(center, 'x') else center[0]
    cy = center.y if hasattr(center, 'y') else center[1]
    arcade.draw_circle_filled(cx, cy, radius, color)

def draw_circle_outline_arcade(center, radius, color, width=1.5):
    cx = center.x if hasattr(center, 'x') else center[0]
    cy = center.y if hasattr(center, 'y') else center[1]
    arcade.draw_circle_outline(cx, cy, radius, color, width)

# ==========================================
# --- МАТЕМАТИКА ---
# ==========================================
def get_bezier_points(p0, p1, control, segments=12):
    points = []
    for i in range(segments + 1):
        t = i / segments
        x = (1-t)**2 * p0.x + 2*(1-t)*t * control.x + t**2 * p1.x
        y = (1-t)**2 * p0.y + 2*(1-t)*t * control.y + t**2 * p1.y
        points.append(Vector2(x, y))
    return points

def get_cubic_curve(p0, p1, p2, p3, segments=16):
    res = []
    for i in range(segments+1):
        t = i / segments
        u = 1 - t
        tt, uu = t * t, u * u
        uuu, ttt = uu * u, tt * t
        p = uuu * p0 + 3 * uu * t * p1 + 3 * u * tt * p2 + ttt * p3
        res.append(p)
    return res

def normalize_vec(vec):
    if vec.length_squared() < 0.001: return Vector2(0, 1)
    return vec.normalize()

# ==========================================
# --- АНАТОМИЯ: НОГИ ---
# ==========================================

def draw_shin_shape(knee_pos, ankle_pos, width_knee, width_ankle, is_left_leg, color, outline_color):
    vec = ankle_pos - knee_pos
    length = vec.length()
    if length < 1: return
    
    normal = Vector2(-vec.y, vec.x).normalize()
    
    if is_left_leg:
        dir_outer = normal
        dir_inner = -normal
    else:
        dir_outer = -normal
        dir_inner = normal

    ratio_outer = 0.65
    ratio_inner = 0.55
    width_tendon_top = width_ankle * 2.3  
    width_ankle_base = width_ankle        
    outer_bulge = 8.0     
    inner_bulge = 3.5     

    p_knee_out = knee_pos + dir_outer * (width_knee * 0.5)
    p_knee_in  = knee_pos + dir_inner * (width_knee * 0.5)
    pos_mid_outer = knee_pos.lerp(ankle_pos, ratio_outer)
    pos_mid_inner = knee_pos.lerp(ankle_pos, ratio_inner)
    p_muscle_end_out = pos_mid_outer + dir_outer * (width_tendon_top * 0.5)
    p_muscle_end_in  = pos_mid_inner + dir_inner * (width_tendon_top * 0.5)
    p_ankle_out = ankle_pos + dir_outer * (width_ankle_base * 0.5)
    p_ankle_in  = ankle_pos + dir_inner * (width_ankle_base * 0.5)

    ctrl_outer_pos = p_knee_out.lerp(p_muscle_end_out, 0.4) 
    ctrl_outer = ctrl_outer_pos + dir_outer * outer_bulge
    curve_outer = get_bezier_points(p_knee_out, p_muscle_end_out, ctrl_outer, segments=8)
    
    ctrl_inner_pos = p_knee_in.lerp(p_muscle_end_in, 0.4)
    ctrl_inner = ctrl_inner_pos + dir_inner * inner_bulge
    curve_inner = get_bezier_points(p_muscle_end_in, p_knee_in, ctrl_inner, segments=8)
    
    poly_points_vec = curve_outer + [p_ankle_out, p_ankle_in, p_muscle_end_in] + curve_inner[1:]
    
    draw_polygon_arcade(poly_points_vec, color)
    if outline_color:
        draw_line_strip_arcade(poly_points_vec, outline_color)

def draw_divine_foot(ankle_pos, toe_tip_pos, is_left_leg, color, outline_color):
    vec = toe_tip_pos - ankle_pos
    length = vec.length()
    if length < 1: return
    
    tangent = vec.normalize()
    normal = Vector2(-tangent.y, tangent.x)
    
    if is_left_leg:
        dir_inner = -normal
        dir_outer = normal
    else:
        dir_inner = normal
        dir_outer = -normal

    heel_offset = length * 0.25
    heel_width_shift = length * 0.15
    heel_pos = ankle_pos - tangent * heel_offset + dir_outer * heel_width_shift
    instep_height = length * 0.35
    instep_ctrl = ankle_pos + tangent * (length * 0.4) + dir_inner * instep_height
    ball_pos = ankle_pos + tangent * (length * 0.75) + dir_inner * (length * 0.05)
    
    ankle_top = ankle_pos + dir_inner * 2
    curve_top = get_bezier_points(ankle_top, toe_tip_pos, instep_ctrl, segments=6)
    curve_sole = get_bezier_points(toe_tip_pos, heel_pos, ball_pos + dir_outer * (length*0.1), segments=6)
    
    heel_back_ctrl = heel_pos - tangent * 2 + dir_outer * 2
    ankle_back = ankle_pos + dir_outer * 2
    curve_heel = get_bezier_points(heel_pos, ankle_back, heel_back_ctrl, segments=4)

    poly_vec = curve_top + curve_sole + curve_heel
    draw_polygon_arcade(poly_vec, color)
    if outline_color:
        draw_line_strip_arcade(poly_vec, outline_color)

def draw_joint(center, radius, color, outline_color):
    draw_circle_arcade(center, radius, color)
    draw_circle_outline_arcade(center, radius, outline_color)

def draw_legs_main(cx, cy, color_base, color_shadow, outline_color, time_ticks):
    # Анимация
    sway_y = math.sin(time_ticks * 0.05) * 4 
    sway_x = math.cos(time_ticks * 0.04) * 2
    
    # Пропорции
    THIGH_LENGTH = 42         
    SHIN_LENGTH = 60          
    FOOT_LENGTH = 16 
    HIP_W = 16.0      
    THIGH_W_KNEE = 6.0        
    ANKLE_WIDTH = 2.8 
    
    # Y-координаты (ARCADE: Y растет ВВЕРХ)
    HIP_LINE_Y = cy - 10 
    CROTCH_Y = HIP_LINE_Y - 18
    KNEE_Y = CROTCH_Y - THIGH_LENGTH
    ANKLE_Y = KNEE_Y - SHIN_LENGTH
    
    # Позиции
    L_KNEE_POS = Vector2(cx - 7 + sway_x * 0.3, KNEE_Y + sway_y * 0.5)
    L_ANKLE_POS = Vector2(cx - 10 + sway_x * 0.5, ANKLE_Y + sway_y)
    L_TOE_POS = L_ANKLE_POS + Vector2(-2, -FOOT_LENGTH)
    
    R_KNEE_POS = Vector2(cx + 7 + sway_x * 0.3, KNEE_Y + sway_y * 0.5)
    R_ANKLE_POS = Vector2(cx + 10 + sway_x * 0.5, ANKLE_Y + sway_y)
    R_TOE_POS = R_ANKLE_POS + Vector2(2, -FOOT_LENGTH)

    # --- БЕДРА ---
    # Левое
    p2_hip_out = Vector2(cx - (HIP_W - 4), HIP_LINE_Y + 6)
    p3_ctrl_out = Vector2(cx - HIP_W - 8, HIP_LINE_Y - 20)
    p4_knee_out = L_KNEE_POS + Vector2(-THIGH_W_KNEE/2, 0)
    p5_knee_in = L_KNEE_POS + Vector2(THIGH_W_KNEE/2, 0)
    p1_hip_in = Vector2(cx - 1, HIP_LINE_Y - 5 + 6)
    
    outer_thigh_l = get_bezier_points(p2_hip_out, p4_knee_out, p3_ctrl_out, segments=8)
    inner_thigh_l = [p5_knee_in, p1_hip_in]
    poly_l = outer_thigh_l + inner_thigh_l
    
    draw_polygon_arcade(poly_l, color_base)
    draw_line_strip_arcade(outer_thigh_l, outline_color)

    # Правое
    p2_hip_out_r = Vector2(cx + (HIP_W - 4), HIP_LINE_Y + 6)
    p3_ctrl_out_r = Vector2(cx + HIP_W + 8, HIP_LINE_Y - 20)
    p4_knee_out_r = R_KNEE_POS + Vector2(THIGH_W_KNEE/2, 0)
    p5_knee_in_r = R_KNEE_POS + Vector2(-THIGH_W_KNEE/2, 0)
    p1_hip_in_r = Vector2(cx + 1, HIP_LINE_Y - 5 + 6)
    
    outer_thigh_r = get_bezier_points(p2_hip_out_r, p4_knee_out_r, p3_ctrl_out_r, segments=8)
    inner_thigh_r = [p5_knee_in_r, p1_hip_in_r]
    poly_r = outer_thigh_r + inner_thigh_r
    
    draw_polygon_arcade(poly_r, color_base)
    draw_line_strip_arcade(outer_thigh_r, outline_color)

    # Колени
    draw_joint(L_KNEE_POS, THIGH_W_KNEE * 0.6, color_base, outline_color)
    draw_joint(R_KNEE_POS, THIGH_W_KNEE * 0.6, color_base, outline_color)

    # Голени
    draw_shin_shape(L_KNEE_POS, L_ANKLE_POS, THIGH_W_KNEE, ANKLE_WIDTH, True, color_base, outline_color)
    draw_shin_shape(R_KNEE_POS, R_ANKLE_POS, THIGH_W_KNEE, ANKLE_WIDTH, False, color_base, outline_color)

    # Стопы
    draw_divine_foot(L_ANKLE_POS, L_TOE_POS, True, color_base, outline_color)
    draw_divine_foot(R_ANKLE_POS, R_TOE_POS, False, color_base, outline_color)
    # ==========================================
    # === ОДЕЖДА: ШОРТЫ (Верхняя половина бедра) ===
    # ==========================================
    
    # Левая штанина
    # Находим середину внутренней части бедра (от паха до колена)
    mid_inner_l = p1_hip_in.lerp(p5_knee_in, 0.5)
    
    # Берем точки внешней кривой бедра ровно до середины (индексы от 0 до 4)
    shorts_poly_l = outer_thigh_l[:5] + [mid_inner_l, p1_hip_in]
    draw_polygon_arcade(shorts_poly_l, C_CLOTH_MAIN)
    
    # Бордовая окантовка по нижнему краю шорт
    draw_line_strip_arcade([outer_thigh_l[4], mid_inner_l], C_CLOTH_ACCENT, 2.5)
    # Контур ткани
    draw_line_strip_arcade(shorts_poly_l, outline_color, 1.5)

    # Правая штанина
    mid_inner_r = p1_hip_in_r.lerp(p5_knee_in_r, 0.5)
    
    shorts_poly_r = outer_thigh_r[:5] + [mid_inner_r, p1_hip_in_r]
    draw_polygon_arcade(shorts_poly_r, C_CLOTH_MAIN)
    
    draw_line_strip_arcade([outer_thigh_r[4], mid_inner_r], C_CLOTH_ACCENT, 2.5)
    draw_line_strip_arcade(shorts_poly_r, outline_color, 1.5)
    # Голени (Высокие сапоги-чулки)
    # Заменили color_base на C_CLOTH_MAIN
    draw_shin_shape(L_KNEE_POS, L_ANKLE_POS, THIGH_W_KNEE, ANKLE_WIDTH, True, C_CLOTH_MAIN, outline_color)
    draw_shin_shape(R_KNEE_POS, R_ANKLE_POS, THIGH_W_KNEE, ANKLE_WIDTH, False, C_CLOTH_MAIN, outline_color)

    # Стопы (Туфли)
    draw_divine_foot(L_ANKLE_POS, L_TOE_POS, True, C_CLOTH_MAIN, outline_color)
    draw_divine_foot(R_ANKLE_POS, R_TOE_POS, False, C_CLOTH_MAIN, outline_color)

# ==========================================
# --- АНАТОМИЯ: ТОРС И ГРУДЬ ---
# ==========================================

def draw_chest_naked(cx, top_y, bottom_y, width_total, color_base, color_shadow, outline_color):
    h = top_y - bottom_y
    neck_narrowness = 0.6
    bulb_width = 1.9
    
    # Левая грудь
    l_start = Vector2(cx - width_total * neck_narrowness, top_y)
    l_end = Vector2(cx - width_total * 0.4, bottom_y)
    l_cp1 = Vector2(cx - width_total * 0.15, top_y - h * 0.19)
    l_cp2 = Vector2(cx - width_total * bulb_width, bottom_y + h * 0.05)
    
    l_outer = get_cubic_curve(l_start, l_cp1, l_cp2, l_end, 10)
    l_inner_start = Vector2(cx - 5, bottom_y + 3)
    l_inner_end = Vector2(cx, top_y - h * 0.2)
    l_inner = get_bezier_points(l_end, l_inner_end, l_inner_start, 6)
    
    l_poly = l_outer + l_inner
    # !!! ИСПРАВЛЕНИЕ ПРОЗРАЧНОСТИ: Чистим точки перед заливкой
    draw_polygon_arcade(clean_polygon_points(l_poly), color_base)
    draw_line_strip_arcade(l_outer, outline_color)
    
    # Правая грудь
    r_start = Vector2(cx + width_total * neck_narrowness, top_y)
    r_end = Vector2(cx + width_total * 0.4, bottom_y)
    r_cp1 = Vector2(cx + width_total * 0.15, top_y - h * 0.19)
    r_cp2 = Vector2(cx + width_total * bulb_width, bottom_y + h * 0.05)
    
    r_outer = get_cubic_curve(r_start, r_cp1, r_cp2, r_end, 10)
    r_inner_start = Vector2(cx + 5, bottom_y + 3)
    r_inner_end = Vector2(cx, top_y - h * 0.2)
    r_inner = get_bezier_points(r_end, r_inner_end, r_inner_start, 6)
    
    r_poly = r_outer + r_inner
    # !!! ИСПРАВЛЕНИЕ ПРОЗРАЧНОСТИ: Чистим точки перед заливкой
    draw_polygon_arcade(clean_polygon_points(r_poly), color_base)
    draw_line_strip_arcade(r_outer, outline_color)

def draw_anatomical_shoulder(center, width, is_left_visual, color, outline_color):
    side_mult = 1 if is_left_visual else -1
    cx, cy = center.x, center.y
    radius_h = width * 0.5
    
    p_top = Vector2(cx - (width * 0.1 * side_mult), cy + radius_h * 0.8)
    p_out = Vector2(cx + (width * 0.4 * side_mult), cy)
    p_bot = Vector2(cx, cy - radius_h * 0.9)
    p_in = Vector2(cx - (width * 0.5 * side_mult), cy - radius_h * 0.2)
    
    ctrl_top = Vector2(p_out.x - (2 * side_mult), p_top.y)
    seg_outer_top = get_bezier_points(p_top, p_out, ctrl_top, 6)
    
    ctrl_bot = Vector2(p_out.x - (2 * side_mult), p_bot.y)
    seg_outer_bot = get_bezier_points(p_out, p_bot, ctrl_bot, 6)
    
    seg_inner = get_bezier_points(p_bot, p_in, Vector2(p_in.x, p_bot.y), 4)
    seg_close = get_bezier_points(p_in, p_top, Vector2(p_in.x, p_top.y), 4)
    
    full_poly = seg_outer_top + seg_outer_bot + seg_inner + seg_close
    
    # !!! ИСПРАВЛЕНИЕ ПРОЗРАЧНОСТИ: Чистим точки перед заливкой
    draw_polygon_arcade(clean_polygon_points(full_poly), color)
    if outline_color:
        draw_line_strip_arcade(seg_outer_top + seg_outer_bot, outline_color)

def draw_torso_main(cx, cy, color_base, color_shadow, outline_color):
    # Координаты (Y вверх)
    RIBCAGE_LENGTH_OFFSET = 20  
    WAIST_Y_OFFSET = -16
    HIP_Y_OFFSET = -13
    CROTCH_Y_OFFSET = -18
    
    ribcage_bottom_y = cy + RIBCAGE_LENGTH_OFFSET
    waist_y = ribcage_bottom_y + WAIST_Y_OFFSET
    hip_line_y = waist_y + HIP_Y_OFFSET
    crotch_y = hip_line_y + CROTCH_Y_OFFSET
    
    shoulder_y = cy + 31
    armpit_y = shoulder_y - 12
    neck_y = shoulder_y + 8
    
    shoulder_width_total = 7.0
    ribcage_w = 10.5
    waist_w = 6.5
    hip_w = 16.0
    neck_w = 5
    
    anim_shoulder_l = Vector2(cx - (shoulder_width_total + 9), shoulder_y)
    anim_shoulder_r = Vector2(cx + (shoulder_width_total + 9), shoulder_y)
    
    # --- ГЕНЕРАЦИЯ КОНТУРА ТЕЛА ---
    trap_l = get_bezier_points(Vector2(cx - neck_w, neck_y), anim_shoulder_l, Vector2(cx - neck_w - 5, shoulder_y + 5), 4)
    shoulder_cap_l = get_bezier_points(anim_shoulder_l, Vector2(cx - shoulder_width_total + 2, armpit_y), Vector2(anim_shoulder_l.x + 22, shoulder_y - 10), 4)
    
    p_armpit_l = Vector2(cx - shoulder_width_total + 2, armpit_y)
    p_rib_bottom_l = Vector2(cx - ribcage_w, ribcage_bottom_y)
    ctrl_side_l = p_armpit_l.lerp(p_rib_bottom_l, 0.5) + Vector2(2, 0)
    side_l = get_bezier_points(p_armpit_l, p_rib_bottom_l, ctrl_side_l, 4)
    
    stomach_l = get_bezier_points(Vector2(cx - ribcage_w, ribcage_bottom_y), Vector2(cx - waist_w, waist_y), Vector2(cx - ribcage_w, (ribcage_bottom_y + waist_y)/2), 4)
    hip_curve_l = get_bezier_points(Vector2(cx - waist_w, waist_y), Vector2(cx - hip_w, hip_line_y), Vector2(cx - waist_w - 5, (waist_y + hip_line_y)/2), 4)
    
    crotch_pt = Vector2(cx, crotch_y)
    crotch_l = get_bezier_points(Vector2(cx - hip_w, hip_line_y), crotch_pt, Vector2(cx - hip_w * 0.4, crotch_y + 1), 3)
    
    crotch_r = get_bezier_points(crotch_pt, Vector2(cx + hip_w, hip_line_y), Vector2(cx + hip_w * 0.4, crotch_y + 1), 3)
    hip_curve_r = get_bezier_points(Vector2(cx + hip_w, hip_line_y), Vector2(cx + waist_w, waist_y), Vector2(cx + waist_w + 5, (waist_y + hip_line_y)/2), 4)
    stomach_r = get_bezier_points(Vector2(cx + waist_w, waist_y), Vector2(cx + ribcage_w, ribcage_bottom_y), Vector2(cx + ribcage_w, (ribcage_bottom_y + waist_y)/2), 4)
    
    p_armpit_r = Vector2(cx + shoulder_width_total - 2, armpit_y)
    p_rib_bottom_r = Vector2(cx + ribcage_w, ribcage_bottom_y)
    side_r = get_bezier_points(p_rib_bottom_r, p_armpit_r, p_armpit_r.lerp(p_rib_bottom_r, 0.5) + Vector2(-2, 0), 4)
    shoulder_cap_r = get_bezier_points(p_armpit_r, anim_shoulder_r, Vector2(anim_shoulder_r.x - 22, shoulder_y - 10), 4)
    trap_r = get_bezier_points(anim_shoulder_r, Vector2(cx + neck_w, neck_y), Vector2(cx + neck_w + 5, shoulder_y + 5), 4)
    
    neck_connect = [Vector2(cx - neck_w, neck_y)]
    
    full_poly_vec = trap_l + shoulder_cap_l + side_l + stomach_l + hip_curve_l + crotch_l + crotch_r + hip_curve_r + stomach_r + side_r + shoulder_cap_r + trap_r + neck_connect
    
    # 1. Заливка тела (с очисткой точек)
    draw_polygon_arcade(clean_polygon_points(full_poly_vec), color_base)
    
    # ==========================================
    # === ДЕТАЛИЗАЦИЯ ТАЗА (КРИВЫЕ) ===
    # ==========================================
    # Рисуем анатомические складки между ногой и телом
    
    # Левая складка
    hip_crease_start_l = Vector2(cx - hip_w + 3, hip_line_y + 2)
    hip_crease_end_l = Vector2(cx - 2, crotch_y + 4)
    # Контрольная точка чуть внутрь и вверх для изгиба
    hip_crease_ctrl_l = hip_crease_start_l.lerp(hip_crease_end_l, 0.3) + Vector2(4, 2)
    crease_l = get_bezier_points(hip_crease_start_l, hip_crease_end_l, hip_crease_ctrl_l, 6)
    draw_line_strip_arcade(crease_l, outline_color, 1.5)

    # Правая складка (зеркально)
    hip_crease_start_r = Vector2(cx + hip_w - 3, hip_line_y + 2)
    hip_crease_end_r = Vector2(cx + 2, crotch_y + 4)
    hip_crease_ctrl_r = hip_crease_start_r.lerp(hip_crease_end_r, 0.3) + Vector2(-4, 2)
    crease_r = get_bezier_points(hip_crease_start_r, hip_crease_end_r, hip_crease_ctrl_r, 6)
    draw_line_strip_arcade(crease_r, outline_color, 1.5)
    
    # Пупок
    belly_button_y = hip_line_y + 10
    draw_circle_arcade((cx, belly_button_y), 1.5, C_SKIN_SHADOW)
    # ==========================================

    # Контур тела
    draw_line_strip_arcade(full_poly_vec, outline_color, 1.5)
    
    # Плечи и грудь (рисуются поверх тела)
    draw_anatomical_shoulder(anim_shoulder_l, 10, True, color_base, outline_color)
    draw_anatomical_shoulder(anim_shoulder_r, 10, False, color_base, outline_color)
    # обнаженная версия draw_chest_naked(cx, armpit_y + 16, cy + 20, ribcage_w + 8.0, color_base, C_SKIN_SHADOW, outline_color)
    # Теперь грудь закрыта тканью (верх корсета)
    draw_chest_naked(cx, armpit_y + 16, cy + 20, ribcage_w + 8.0, C_CLOTH_MAIN, C_SKIN_SHADOW, outline_color)
    
    # Элегантная бордовая окантовка по линии декольте
    chest_top_y = armpit_y + 16
    arcade.draw_line(cx - ribcage_w * 0.6, chest_top_y, cx, chest_top_y - 3, C_CLOTH_ACCENT, 2.5)
    arcade.draw_line(cx + ribcage_w * 0.6, chest_top_y, cx, chest_top_y - 3, C_CLOTH_ACCENT, 2.5)
    # Шея
    n_top_y = neck_y + 25
    n_base_y = neck_y - 4
    n_w_top = 4.5
    n_w_base = 6.5
    
    p_neck_tl = Vector2(cx - n_w_top, n_top_y)
    p_neck_bl = Vector2(cx - n_w_base, n_base_y)
    p_neck_tr = Vector2(cx + n_w_top, n_top_y)
    p_neck_br = Vector2(cx + n_w_base, n_base_y)
    
    draw_polygon_arcade([p_neck_tl, p_neck_bl, p_neck_br, p_neck_tr], color_base)
    draw_line_strip_arcade([p_neck_tl, p_neck_bl], outline_color)
    draw_line_strip_arcade([p_neck_tr, p_neck_br], outline_color)

    # ==========================================
    # === ОДЕЖДА: КОРСЕТ И НИЗ ===
    # ==========================================
    
    # 1. Плавки / Короткие шорты (поверх таза)
    panty_pts = [
        Vector2(cx - hip_w, hip_line_y + 2),
        Vector2(cx, crotch_y + 3),
        Vector2(cx + hip_w, hip_line_y + 2),
        Vector2(cx, waist_y - 2)
    ]
    draw_polygon_arcade(panty_pts, C_CLOTH_MAIN)
    draw_line_strip_arcade(panty_pts + [panty_pts[0]], outline_color, 1.5)

    # 2. Корсет (поверх груди и живота)
    corset_top_y = armpit_y - 2
    corset_bot_y = waist_y
    corset_w_top = ribcage_w + 1
    corset_w_bot = waist_w + 1.5
    
    corset_pts = [
        Vector2(cx - corset_w_top, corset_top_y),
        Vector2(cx - corset_w_bot, corset_bot_y),
        Vector2(cx, corset_bot_y - 6), # Острый мысик корсета вниз
        Vector2(cx + corset_w_bot, corset_bot_y),
        Vector2(cx + corset_w_top, corset_top_y),
        Vector2(cx, corset_top_y - 5)  # Глубокий вырез на груди
    ]
    draw_polygon_arcade(corset_pts, C_CLOTH_MAIN)
    draw_line_strip_arcade(corset_pts + [corset_pts[0]], outline_color, 1.5)
    
    # Бордовая лента на талии
    arcade.draw_line(cx - corset_w_bot + 1, corset_bot_y - 2, 
                     cx + corset_w_bot - 1, corset_bot_y - 2, 
                     C_CLOTH_ACCENT, 3.5)

    return anim_shoulder_l, anim_shoulder_r, Vector2(cx, n_top_y)

# ==========================================
# --- ГОЛОВА ---
# ==========================================
def draw_head(center, color_base, color_shadow, outline_color):
    cx, cy = center.x, center.y
    head_y = cy
    
    face_w = 14.0
    chin_drop = 22
    chin_pt = Vector2(cx, head_y - chin_drop)
    jaw_y = head_y - 12
    temple_w = face_w + 1
    jaw_w = face_w * 0.75
    
    # Контур лица
    pts_l = get_bezier_points(Vector2(cx - temple_w, head_y + 5), Vector2(cx - jaw_w, jaw_y), Vector2(cx - temple_w, jaw_y + 5), 4)
    pts_l2 = get_bezier_points(Vector2(cx - jaw_w, jaw_y), chin_pt, Vector2(cx - jaw_w * 0.6, chin_pt.y + 2), 4)
    pts_r2 = get_bezier_points(chin_pt, Vector2(cx + jaw_w, jaw_y), Vector2(cx + jaw_w * 0.6, chin_pt.y + 2), 4)
    pts_r = get_bezier_points(Vector2(cx + jaw_w, jaw_y), Vector2(cx + temple_w, head_y + 5), Vector2(cx + temple_w, jaw_y + 5), 4)
    
    forehead = [pts_l[0], pts_r[-1]]
    face_poly = pts_l + pts_l2 + pts_r2 + pts_r + forehead
    
    draw_polygon_arcade(clean_polygon_points(face_poly), color_base)
    draw_line_strip_arcade(face_poly, outline_color)
    
    # Глаза
    eye_y = head_y - 6
    eye_spacing = 7.5
    draw_circle_arcade((cx - eye_spacing, eye_y), 3, C_EYE_GLOW)
    draw_circle_arcade((cx + eye_spacing, eye_y), 3, C_EYE_GLOW)
    
    # Рот
    mouth_y = head_y - 17
    arcade.draw_line(cx - 3, mouth_y, cx + 3, mouth_y, (100, 50, 50), 1.5)

# ==========================================
# --- РУКИ (ПРОСТЫЕ) ---
# ==========================================
def draw_forearm_shape(start, end, color, outline_color, w_upper=10, is_left_visual=True):
    vec = end - start
    length = vec.length()
    if length < 1: return
    normal = normalize_vec(Vector2(-vec.y, vec.x))
    
    points_pos = [] 
    points_neg = [] 
    segments = 8
    
    base_thick = 3.0
    start_thick = w_upper / 2

    for i in range(segments + 1):
        t = i / segments
        pos = start + vec * t
        
        start_taper = (1-t) * start_thick + t * base_thick
        end_taper = (1-t) * base_thick + t * 3.5 
        curr_thick = start_taper * (1-t) + end_taper * t

        bulge_pos = 0.5 * math.sin(t * math.pi) if is_left_visual else 1.5 * math.sin(t * math.pi)
        bulge_neg = 1.5 * math.sin(t * math.pi) if is_left_visual else 0.5 * math.sin(t * math.pi)

        points_pos.append(pos + normal * (curr_thick + bulge_pos))
        points_neg.append(pos - normal * (curr_thick + bulge_neg))
        
    poly = points_pos + points_neg[::-1]
    draw_polygon_arcade(poly, color)
    if outline_color:
        draw_line_strip_arcade(points_pos, outline_color)
        draw_line_strip_arcade(points_neg, outline_color)

def draw_arm_upper(shoulder, elbow, is_left_visual, color, outline_color):
    w_start = 9
    w_end = 7
    vec = elbow - shoulder
    if vec.length() < 1: return
    normal = normalize_vec(Vector2(-vec.y, vec.x))
    
    p1 = shoulder + normal * (w_start / 2)
    p2 = shoulder - normal * (w_start / 2)
    p3 = elbow - normal * (w_end / 2)
    p4 = elbow + normal * (w_end / 2)
    
    draw_polygon_arcade([p1, p2, p3, p4], color)
    draw_circle_arcade((elbow.x, elbow.y), 5.0, color)
    if outline_color:
        arcade.draw_line(p1.x, p1.y, p4.x, p4.y, outline_color, 1.5)
        arcade.draw_line(p2.x, p2.y, p3.x, p3.y, outline_color, 1.5)

def draw_arm_full(shoulder, elbow, hand, is_left):
    draw_arm_upper(shoulder, elbow, is_left, C_SKIN_BASE, C_OUTLINE)
    draw_forearm_shape(elbow, hand, C_SKIN_BASE, C_OUTLINE, 10, is_left)
    draw_circle_arcade((hand.x, hand.y), 4, C_SKIN_BASE)

# ==========================================
# --- ГЛАВНАЯ ФУНКЦИЯ ОТРИСОВКИ ---
# ==========================================
from .core import solve_ik_2joint

def draw_vampire_arcade(center_x, center_y, angle, walk_cycle, vel_length, cape_points, alpha_mult=1.0):
    cx, cy = center_x, center_y
    time_ticks = walk_cycle * 10
    
    # 1. ТЕЛО И НОГИ
    # Сначала рисуем ноги, чтобы они были "под" телом
    draw_legs_main(cx, cy, C_SKIN_BASE, C_SKIN_SHADOW, C_OUTLINE, time_ticks)
    # Затем рисуем торс с деталями паха, перекрывая верх ног
    sh_l, sh_r, head_pos = draw_torso_main(cx, cy, C_SKIN_BASE, C_SKIN_SHADOW, C_OUTLINE)
    
    # 2. ГОЛОВА
    draw_head(head_pos, C_SKIN_BASE, C_SKIN_SHADOW, C_OUTLINE)
    
    # 3. РУКИ (IK)
    aim_rad = math.radians(angle)
    hand_l_target = Vector2(cx + math.cos(aim_rad) * 30, cy + math.sin(aim_rad) * 30 + 10)
    back_angle = math.radians(-80 - math.sin(walk_cycle)*20)
    hand_r_target = Vector2(cx + math.cos(back_angle) * 20, cy + math.sin(back_angle) * 20 - 10)
    
    elbow_l, hand_l = solve_ik_2joint(sh_l, hand_l_target, 20, 18, bend_right=False)
    elbow_r, hand_r = solve_ik_2joint(sh_r, hand_r_target, 20, 18, bend_right=True)
    
    draw_arm_full(sh_r, elbow_r, hand_r, False) # Задняя
    draw_arm_full(sh_l, elbow_l, hand_l, True)  # Передняя
    
    arcade.draw_circle_filled(hand_l.x, hand_l.y, 4, (255, 0, 0, 150))