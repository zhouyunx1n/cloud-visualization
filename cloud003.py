import pygame
import pandas as pd
import math
import random

# 日期英文格式
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 读取数据
df = pd.read_csv('cloud.csv', encoding='utf-8')
data = []
for i, row in df.iterrows():
    if pd.isna(row['Month']) or pd.isna(row['Day']) or pd.isna(row['Value']):
        continue
    data.append({
        'month': int(row['Month']),
        'day': int(row['Day']),
        'value': float(row['Value'])
    })

data.sort(key=lambda x: (x['month'], x['day']))

WIDTH, HEIGHT = 1000, 600
LEFT_MARGIN = 120
RIGHT_MARGIN = 80
TOP_MARGIN = 130
BOTTOM_MARGIN = 190
CLOUD_WIDTH = WIDTH - LEFT_MARGIN - RIGHT_MARGIN
CLOUD_HEIGHT = HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

values = [d['value'] for d in data]
min_value = min(values)
max_value = max(values)
num_days = len(data)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Average cloud cover in Hong Kong (percentage)')
font = pygame.font.SysFont('Arial', 32)
info_font = pygame.font.SysFont('Arial', 22)
legend_font = pygame.font.SysFont('Arial', 18)
clock = pygame.time.Clock()

running = True
current = 0

# 蓝色主题颜色函数
def get_blue_color(value):
    # 云量越高，颜色越深
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    # 浅蓝到深蓝
    r = int(80 + ratio * 60)
    g = int(150 + ratio * 80)
    b = int(220 + ratio * 35)
    return (r, g, b)

# 生成云朵点阵
def generate_cloud_points():
    cloud_points = []
    for day_idx, d in enumerate(data):
        # 横坐标
        x = LEFT_MARGIN + day_idx / (num_days-1) * CLOUD_WIDTH
        # 云量决定该列点数和颜色
        value = d['value']
        ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
        # 点数：云量高则密集
        num_points = int(18 + ratio * 32)  # 18~50个点
        # 波浪高度
        for i in range(num_points):
            # y轴分布
            y_ratio = i / (num_points-1) if num_points > 1 else 0.5
            # 基础高度
            base_y = TOP_MARGIN + y_ratio * CLOUD_HEIGHT
            # 波浪形状（正弦+噪声）
            wave = math.sin(day_idx/8 + y_ratio*math.pi*2) * 30
            noise = random.uniform(-8, 8)
            y = base_y + wave + noise
            color = get_blue_color(value)
            cloud_points.append({
                'x': x,
                'y': y,
                'color': color,
                'day_idx': day_idx,
                'value': value
            })
    return cloud_points

cloud_points = generate_cloud_points()

while running:
    screen.fill((0, 0, 0))

    # 标题
    title_text = "Average cloud cover in Hong Kong (percentage)"
    title_surface = font.render(title_text, True, (180, 200, 255))
    screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 30))

    # 当前日期英文
    d = data[current]
    month_name = MONTH_NAMES[d['month']-1]
    info_text = f"{month_name} {d['day']}"
    value_text = f"Cloud cover: {d['value']}%"
    info_surface = info_font.render(info_text, True, (220, 230, 255))
    value_surface = info_font.render(value_text, True, (120, 180, 255))
    info_box_width = max(info_surface.get_width(), value_surface.get_width()) + 40
    info_box_height = 60
    info_box = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
    info_box.fill((30, 30, 60, 180))
    screen.blit(info_box, (WIDTH//2 - info_box_width//2, HEIGHT - info_box_height - 30))
    screen.blit(info_surface, (WIDTH//2 - info_surface.get_width()//2, HEIGHT - info_box_height - 10))
    screen.blit(value_surface, (WIDTH//2 - value_surface.get_width()//2, HEIGHT - info_box_height + 22))

    # 绘制云朵点阵
    for pt in cloud_points:
        # 当前日期高亮
        if pt['day_idx'] == current:
            radius = 6
            color = tuple(min(255, int(c*1.2)) for c in pt['color'])
        else:
            radius = 4
            color = pt['color']
        pygame.draw.circle(screen, color, (int(pt['x']), int(pt['y'])), radius)

    # 图例（左下角）
    legend_x = 40
    legend_y = HEIGHT - 120
    legend_width = 180
    legend_height = 18
    # 渐变条
    for i in range(legend_width):
        ratio = i / legend_width
        value = min_value + ratio * (max_value - min_value)
        color = get_blue_color(value)
        pygame.draw.rect(screen, color, (legend_x+i, legend_y, 1, legend_height))
    # 图例文字
    worse_text = legend_font.render("Lower", True, (180, 200, 255))
    better_text = legend_font.render("Higher", True, (180, 200, 255))
    screen.blit(worse_text, (legend_x, legend_y + legend_height + 4))
    screen.blit(better_text, (legend_x + legend_width - better_text.get_width(), legend_y + legend_height + 4))
    explain_text = legend_font.render("Cloud cover (density & color)", True, (180, 200, 255))
    screen.blit(explain_text, (legend_x, legend_y + legend_height + 28))

    pygame.display.flip()
    clock.tick(8)

    current = (current + 1) % num_days

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
