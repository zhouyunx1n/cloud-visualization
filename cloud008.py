import pygame
import pandas as pd
import math

# ====== 可修改参数 ======
CSV_FILE = 'cloud.csv'
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
BG_COLOR = (10, 10, 20)
TITLE_COLOR = (255, 255, 255)
AXIS_COLOR = (180, 180, 180)
LABEL_COLOR = (220, 220, 220)
FONT_NAME = 'arial'
TITLE_FONT_SIZE = 36
LABEL_FONT_SIZE = 20
TICK_FONT_SIZE = 16
LEGEND_FONT_SIZE = 18
POINT_RADIUS = 7
LINE_WIDTH = 3

# 渐变色（低云量到高云量）
COLOR_LOW = (255, 120, 80)   # 橙色
COLOR_HIGH = (80, 180, 255)  # 蓝色

df = pd.read_csv(CSV_FILE, encoding='utf-8')
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
print(df.columns)  # 调试用，确认列名

def get_col(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    raise Exception(f"列名不匹配,请检查csv文件,候选：{candidates}")

cols = list(df.columns)
year_col = get_col(cols, ['year', '年/year'])
month_col = get_col(cols, ['month', '月/month'])
day_col = get_col(cols, ['day', '日/day'])
value_col = get_col(cols, ['value', '數值/value'])

dates = [f"{int(row[year_col])}-{int(row[month_col]):02d}-{int(row[day_col]):02d}" for _, row in df.iterrows()]
values = [float(row[value_col]) for _, row in df.iterrows()]
n_points = len(values)
min_val, max_val = min(values), max(values)

# ====== pygame初始化 ======
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('The average daily cloud content in Hong Kong')

# ====== 字体设置 ======
title_font = pygame.font.SysFont(FONT_NAME, TITLE_FONT_SIZE, bold=True)
label_font = pygame.font.SysFont(FONT_NAME, LABEL_FONT_SIZE)
tick_font = pygame.font.SysFont(FONT_NAME, TICK_FONT_SIZE)
legend_font = pygame.font.SysFont(FONT_NAME, LEGEND_FONT_SIZE)

# ====== 坐标轴区域 ======
LEFT_MARGIN = 120
RIGHT_MARGIN = 80
TOP_MARGIN = 100
BOTTOM_MARGIN = 120
plot_width = WINDOW_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
plot_height = WINDOW_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

def get_x(i):
    return LEFT_MARGIN + int(i * plot_width / (n_points - 1))

def get_y(val):
    return TOP_MARGIN + int((max_val - val) * plot_height / (max_val - min_val + 1e-6))

def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def smooth_curve(points, smoothness=0.2):
    # 用贝塞尔曲线平滑折线
    result = []
    for i in range(len(points)-1):
        p0 = points[i]
        p1 = points[i+1]
        mid = ((p0[0]+p1[0])//2, (p0[1]+p1[1])//2)
        result.append(p0)
        # 插入中点
        for t in [smoothness, 1-smoothness]:
            x = int(p0[0] * (1-t) + p1[0] * t)
            y = int(p0[1] * (1-t) + p1[1] * t)
            result.append((x, y))
    result.append(points[-1])
    return result

def draw():
    screen.fill(BG_COLOR)

    # 标题
    title_surf = title_font.render('The average daily cloud content in Hong Kong', True, TITLE_COLOR)
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, TOP_MARGIN // 2))
    screen.blit(title_surf, title_rect)

    # 坐标轴
    pygame.draw.line(screen, AXIS_COLOR, (LEFT_MARGIN, TOP_MARGIN), (LEFT_MARGIN, WINDOW_HEIGHT - BOTTOM_MARGIN), 2)
    pygame.draw.line(screen, AXIS_COLOR, (LEFT_MARGIN, WINDOW_HEIGHT - BOTTOM_MARGIN), (WINDOW_WIDTH - RIGHT_MARGIN, WINDOW_HEIGHT - BOTTOM_MARGIN), 2)

    # Y轴刻度和标签
    n_ticks = 5
    for i in range(n_ticks + 1):
        val = int(min_val + i * (max_val - min_val) / n_ticks)
        y = get_y(val)
        tick_surf = tick_font.render(f'{val}', True, LABEL_COLOR)
        screen.blit(tick_surf, (LEFT_MARGIN - 50, y - 10))
        pygame.draw.line(screen, AXIS_COLOR, (LEFT_MARGIN - 8, y), (LEFT_MARGIN + 8, y), 2)
    label_surf = label_font.render('Cloud Content (%)', True, LABEL_COLOR)
    screen.blit(label_surf, (LEFT_MARGIN - 90, TOP_MARGIN - 40))

    # X轴刻度和标签（只显示部分日期，防止重叠）
    step = max(1, n_points // 8)
    for i in range(0, n_points, step):
        x = get_x(i)
        tick_surf = tick_font.render(dates[i], True, LABEL_COLOR)
        tick_rect = tick_surf.get_rect(center=(x, WINDOW_HEIGHT - BOTTOM_MARGIN + 25))
        screen.blit(tick_surf, tick_rect)
        pygame.draw.line(screen, AXIS_COLOR, (x, WINDOW_HEIGHT - BOTTOM_MARGIN - 8), (x, WINDOW_HEIGHT - BOTTOM_MARGIN + 8), 2)
    label_surf = label_font.render('Date', True, LABEL_COLOR)
    screen.blit(label_surf, (WINDOW_WIDTH - RIGHT_MARGIN - 60, WINDOW_HEIGHT - BOTTOM_MARGIN + 50))

    # 数据点和渐变色
    points = [(get_x(i), get_y(values[i])) for i in range(n_points)]
    smooth_points = smooth_curve(points, smoothness=0.3)

    # 绘制平滑曲线
    for i in range(len(smooth_points)-1):
        # 按云量渐变色
        idx = min(i, n_points-1)
        t = (values[idx] - min_val) / (max_val - min_val + 1e-6)
        color = lerp_color(COLOR_LOW, COLOR_HIGH, t)
        pygame.draw.line(screen, color, smooth_points[i], smooth_points[i+1], LINE_WIDTH)

    # 绘制数据点
    for i, (x, y) in enumerate(points):
        t = (values[i] - min_val) / (max_val - min_val + 1e-6)
        color = lerp_color(COLOR_LOW, COLOR_HIGH, t)
        pygame.draw.circle(screen, color, (x, y), POINT_RADIUS)

    # 图例（渐变条）
    legend_x, legend_y = LEFT_MARGIN, WINDOW_HEIGHT - BOTTOM_MARGIN + 70
    legend_w, legend_h = 220, 18
    for i in range(legend_w):
        t = i / legend_w
        color = lerp_color(COLOR_LOW, COLOR_HIGH, t)
        pygame.draw.rect(screen, color, (legend_x + i, legend_y, 1, legend_h))
    # 图例文字
    legend_text1 = legend_font.render('Lower', True, COLOR_LOW)
    legend_text2 = legend_font.render('Higher', True, COLOR_HIGH)
    screen.blit(legend_text1, (legend_x - 10, legend_y + legend_h + 5))
    screen.blit(legend_text2, (legend_x + legend_w - 60, legend_y + legend_h + 5))
    legend_label = legend_font.render('Cloud Content (%)', True, LABEL_COLOR)
    screen.blit(legend_label, (legend_x + legend_w // 2 - 60, legend_y - 28))

# ====== 主循环 ======
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    draw()
    pygame.display.flip()

pygame.quit()
