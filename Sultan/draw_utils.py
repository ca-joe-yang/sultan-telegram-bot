from PIL import Image, ImageDraw, ImageFont

def draw_prison(draw, x, y, w, h):
    draw.line(
        [(x, y), (x, y+h)], 
        fill="black", width=15) 
    draw.line(
        [(x, y), (x+w, y)], 
        fill="black", width=15) 
    draw.line(
        [(x+w, y+h), (x, y+h)], 
        fill="black", width=15) 
    draw.line(
        [(x+w, y+h), (x+w, y)], 
        fill="black", width=15) 

    N = 3
    for i in range(1, N+1):
        x_ = int(x + i*w/(N+1))
        draw.line(
            [(x_, y), (x_, y+h)], 
            fill="black", width=15) 

def draw_cross(draw, x, y, w, h):
    draw.line(
        [(x, y), (x+w, y+h)], 
        fill="red", width=15) 
    draw.line(
        [(x+w, y), (x, y+h)], 
        fill="red", width=15)

def draw_border(draw, x, y, w, h, fill='black', width=15):
    draw.line(
        [(x, y), (x, y+h)], 
        fill=fill, width=width) 
    draw.line(
        [(x, y), (x+w, y)], 
        fill=fill, width=width) 
    draw.line(
        [(x+w, y+h), (x, y+h)], 
        fill=fill, width=width) 
    draw.line(
        [(x+w, y+h), (x+w, y)], 
        fill=fill, width=width) 

def get_visual_layout_config(n):
    if n < 8:
        raise
    elif n == 8:
        return get_visual_layout_config_rect(3, 3, 1+2)
    elif n == 9:
        return get_visual_layout_config_rect(4, 3, 1+2)
    elif n == 10:
        return get_visual_layout_config_rect(4, 4, 1+2)
    elif n == 11:
        return get_visual_layout_config_rect(5, 4, 1+2)
    elif n == 12:
        return get_visual_layout_config_rect(5, 5, 1+2)
    elif n == 13:
        return get_visual_layout_config_rect(5, 4, 2+2)
    elif n == 14:
        return get_visual_layout_config_rect(5, 5, 2+2)
    elif n == 15:
        return get_visual_layout_config_rect(6, 5, 2+2)

def get_visual_layout_config_rect(top, bottom, side):
    interval_t = 1 / top
    interval_b = 1 / bottom
    interval_s = 1 / side

    layout = []
    for i in range(top):
        x = interval_t * (i + 0.5)
        y = interval_s / 2
        layout.append([x, y])

    for i in range(1, side):
        x = interval_t * (top - 0.5)
        y = interval_s * (i + 0.5)
        layout.append([x, y])

    for i in range(bottom-2, 0, -1):
        x = interval_b * (i + 0.5)
        y = interval_s * (side - 0.5)
        layout.append([x, y])

    for i in range(side-1, 0, -1):
        x = interval_t * 0.5
        y = interval_s * (i + 0.5)
        layout.append([x, y])
    return layout


VISUAL_LAYOUT_CONFIG = {
    6: [
        (0.15, 0.50),
        (0.20, 0.65),
        (0.75, 0.65),
        (0.80, 0.50),
        (0.75, 0.35),
        (0.20, 0.55)
    ],
    8: [
        (0.25, 0.50),
        (0.25, 0.75),
        (0.50, 0.75),
        (0.75, 0.75),
        (0.75, 0.50),
        (0.75, 0.25),
        (0.50, 0.25),
        (0.25, 0.25),
    ],
    10: [
        (0.167, 0.125), (0.167, 0.375), (0.167, 0.625), (0.167, 0.875),
        (0.500, 0.875),
        (0.833, 0.875), (0.833, 0.625), (0.833, 0.375), (0.833, 0.125),
        (0.500, 0.125),
    ],
    12: [
        (0.167, 0.100), (0.167, 0.300), (0.167, 0.500), (0.167, 0.700), (0.167, 0.900),
        (0.25, 0.68),
        (0.25, 0.86),
        (0.50, 0.86),
        (0.75, 0.86),
        (0.75, 0.68),
        (0.75, 0.50),
        (0.75, 0.32),
        (0.75, 0.14),
        (0.50, 0.14),
        (0.25, 0.14),
        (0.25, 0.32),
    ],
    14: [
        (0.083, 0.125), (0.250, 0.125), (0.417, 0.125), (0.583, 0.125), (0.750, 0.125), (0.917, 0.125),
        (0.917, 0.375),
        (0.917, 0.625),
        (0.917, 0.875), (0.709, 0.875), (0.500, 0.875), (0.292, 0.875), (0.083, 0.875),
        (0.083, 0.625),
        (0.083, 0.375),
    ],
    15: [
        (0.083, 0.125), (0.250, 0.125), (0.417, 0.125), (0.583, 0.125), (0.750, 0.125), (0.917, 0.125),
        (0.917, 0.375),
        (0.917, 0.625),
        (0.917, 0.875), (0.709, 0.875), (0.500, 0.875), (0.292, 0.875), (0.083, 0.875),
        (0.083, 0.625),
        (0.083, 0.375),
    ]
}