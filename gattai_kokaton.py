"""
スイカゲーム（背景のみ）
=======================================
・ウィンドウ表示と背景描画だけを行うベース部分
・フルーツや物理演算、スコアなどはまだ実装していない
"""
import os
import sys
import math
import pygame as pg
os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH, HEIGHT = 600, 800
FLOOR_Y = HEIGHT - 60
WALL_MARGIN = 40
GAME_OVER_LINE_Y = 120  # このラインを超えて積み上がったらゲームオーバー（予定）
GRAVITY = 0.5
RESTITUTION = 0.3  # 反発係数（0〜1）
FPS = 60
BALL_RADIUS = 12


class Score:  # 実装Score
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-750

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class Ball:
    """落ちてくる小さい球（画像で表示）"""
    def __init__(self, x: float, y: float, image: pg.Surface, ball_type: int = 0):
        self.x = x
        self.y = y
        self.vy = 0.0
        self.falling = False  # Enterキーが押されるまでは静止
        self.image_テスト = ball_type  # これが衝突判定に使われる種類ID
        size = BALL_RADIUS * 2
        self.image = pg.transform.smoothscale(image, (size, size))

    def update_physics(self):
        if not self.falling:
            return
        self.vy += GRAVITY
        self.y += self.vy
        # 床との衝突
        if self.y + BALL_RADIUS > FLOOR_Y:
            self.y = FLOOR_Y - BALL_RADIUS
            self.vy *= -RESTITUTION
            if abs(self.vy) < 1.0:
                self.vy = 0.0

    def draw(self, screen: pg.Surface):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect)

def resolve_ball_collision(a: Ball, b: Ball, score: Score, hit_sound: pg.mixer.Sound, sound_type8: pg.mixer.Sound):  # 実装Score  実装Sound
    """2つの球が重なっていたら押し戻し、簡易的に弾き合う"""
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = BALL_RADIUS * 2

    if dist == 0 or dist >= min_dist:
        return
    # 同じ種類同士がぶつかった時のみ」効果音を鳴らし、点数を計算する
    if hasattr(a, "image_テスト") and hasattr(b, "image_テスト"):
        if a.image_テスト == b.image_テスト:  # 種類が同じかチェック
            hit_sound.play()  # 同じ種類が当たった時だけ音を鳴らす
            ball_type = a.image_テスト
            if ball_type == 0:
                score.value += 1   # 種類0なら1点
            elif ball_type == 1:
                score.value += 5   # 種類1なら5点
            elif ball_type == 2:
                score.value += 10  # 種類2なら10点
            elif ball_type == 3:
                score.value += 20  # 種類3なら20点
            elif ball_type == 4:
                score.value += 30  # 種類4なら30点
            elif ball_type == 5:
                score.value += 40  # 種類5なら40点
            elif ball_type == 6:
                score.value += 50  # 種類6なら50点
            elif ball_type == 7:
                score.value += 60  # 種類7なら60点
            elif ball_type == 8:
                score.value += 100 # 種類8なら100点
                sound_type8.play() # 種類8同士の専用サウンド

    overlap = min_dist - dist
    nx, ny = dx / dist, dy / dist
    # 重なりを均等に押し戻す
    a.x -= nx * overlap / 2
    a.y -= ny * overlap / 2
    b.x += nx * overlap / 2
    b.y += ny * overlap / 2
    # 簡易的な反発（速度を軽く交換して弾く）
    a.vy -= ny * 1.5
    b.vy += ny * 1.5


class Game:
    """ゲーム全体の進行を管理するクラス"""
    def __init__(self):
        pg.init()
        pg.mixer.init()  # 実装Sound
        self.hit_sound = pg.mixer.Sound("決定ボタンを押す52.wav")  # 実装Sound
        self.sound_type8 = pg.mixer.Sound("金額表示.wav")  # 実装Sound
        pg.display.set_caption("スイカゲーム（背景のみ）")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.ball_images = []
        for i in range(9):  # 0から8まで
            img = pg.image.load(f"fig/{i}.png").convert_alpha()
            self.ball_images.append(img)
        self.balls: list[Ball] = []
        #  次に作成するボールの種類を管理する変数（最初は種類 0）
        self.next_ball_type = 0
        # 画像(第3引数)と種類ID(第4引数)を連動させる
        self.current_ball = Ball(WIDTH // 2, GAME_OVER_LINE_Y, self.ball_images[self.next_ball_type], self.next_ball_type)
        self.score = Score()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self._drop_ball()

    def _drop_ball(self):
        self.current_ball.falling = True
        self.balls.append(self.current_ball)
        # 落としたら、次のボールの種類を「0」と「1」で交互に切り替える
        if self.next_ball_type == 0:
            self.next_ball_type = 1
        else:
            self.next_ball_type = 0
        # 画像の番号（第3引数）と 種類ID（第4引数）に同じ変数（self.next_ball_type）を渡して同期！
        self.current_ball = Ball(WIDTH // 2, GAME_OVER_LINE_Y, self.ball_images[self.next_ball_type], self.next_ball_type)

    def update(self):
        for ball in self.balls:
            ball.update_physics()
        for i in range(len(self.balls)):  
            for j in range(i + 1, len(self.balls)):
                resolve_ball_collision(self.balls[i], self.balls[j], self.score, self.hit_sound, self.sound_type8)

    def draw(self):
        self.screen.fill((250, 240, 210))
        # ゲームオーバーライン
        pg.draw.line(self.screen, (255, 0, 0), (WALL_MARGIN, GAME_OVER_LINE_Y),
                     (WIDTH - WALL_MARGIN, GAME_OVER_LINE_Y), 2)
        # 壁と床
        pg.draw.line(self.screen, (100, 60, 30), (WALL_MARGIN, 0), (WALL_MARGIN, FLOOR_Y), 4)
        pg.draw.line(self.screen, (100, 60, 30), (WIDTH - WALL_MARGIN, 0), (WIDTH - WALL_MARGIN, FLOOR_Y), 4)
        pg.draw.line(self.screen, (100, 60, 30), (WALL_MARGIN, FLOOR_Y), (WIDTH - WALL_MARGIN, FLOOR_Y), 4)
        for ball in self.balls:
            ball.draw(self.screen)
        self.current_ball.draw(self.screen)
        self.score.update(self.screen)
        pg.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
if __name__ == "__main__":
    Game().run()