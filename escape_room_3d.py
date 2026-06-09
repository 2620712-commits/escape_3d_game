import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
from enum import Enum
import json

# 게임 상태
class GameState(Enum):
    PLAYING = 1
    PASSWORD_INPUT = 2
    ESCAPED = 3
    GAME_OVER = 4

# 퍼즐 상태
class PuzzleState:
    def __init__(self):
        self.puzzle1_solved = False  # 수학 퍼즐
        self.puzzle2_solved = False  # 그림 맞추기
        self.puzzle3_solved = False  # 숨겨진 물건
        self.password_digits = ['?', '?', '?']
        self.correct_password = ['0', '0', '0']  # 나중에 설정
        
    def solve_puzzle(self, puzzle_num, digit):
        if puzzle_num == 1 and not self.puzzle1_solved:
            self.puzzle1_solved = True
            self.password_digits[0] = digit
            self.correct_password[0] = digit
            return True
        elif puzzle_num == 2 and not self.puzzle2_solved:
            self.puzzle2_solved = True
            self.password_digits[1] = digit
            self.correct_password[1] = digit
            return True
        elif puzzle_num == 3 and not self.puzzle3_solved:
            self.puzzle3_solved = True
            self.password_digits[2] = digit
            self.correct_password[2] = digit
            return True
        return False

# 3D 큐브 그리기
def draw_cube(size=1.0):
    vertices = [
        [size, size, -size],
        [size, -size, -size],
        [-size, -size, -size],
        [-size, size, -size],
        [size, size, size],
        [size, -size, size],
        [-size, -size, size],
        [-size, size, size]
    ]
    
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    glBegin(GL_LINES)
    glColor3f(1, 1, 1)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# 바닥 그리기
def draw_floor():
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.5, 0.5)
    glVertex3f(-20, 0, -20)
    glVertex3f(20, 0, -20)
    glVertex3f(20, 0, 20)
    glVertex3f(-20, 0, 20)
    glEnd()

# 벽 그리기
def draw_wall(x, y, z, width, height, depth, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glBegin(GL_QUADS)
    glColor3f(*color)
    
    # 앞면
    glVertex3f(-width/2, 0, 0)
    glVertex3f(width/2, 0, 0)
    glVertex3f(width/2, height, 0)
    glVertex3f(-width/2, height, 0)
    
    glEnd()
    glPopMatrix()

# 방 그리기
def draw_room():
    # 바닥
    draw_floor()
    
    # 앞 벽
    glBegin(GL_QUADS)
    glColor3f(0.7, 0.7, 0.8)
    glVertex3f(-15, 0, 15)
    glVertex3f(15, 0, 15)
    glVertex3f(15, 10, 15)
    glVertex3f(-15, 10, 15)
    glEnd()
    
    # 뒷 벽
    glBegin(GL_QUADS)
    glColor3f(0.6, 0.6, 0.7)
    glVertex3f(-15, 0, -15)
    glVertex3f(15, 0, -15)
    glVertex3f(15, 10, -15)
    glVertex3f(-15, 10, -15)
    glEnd()
    
    # 좌측 벽
    glBegin(GL_QUADS)
    glColor3f(0.8, 0.7, 0.7)
    glVertex3f(-15, 0, -15)
    glVertex3f(-15, 0, 15)
    glVertex3f(-15, 10, 15)
    glVertex3f(-15, 10, -15)
    glEnd()
    
    # 우측 벽
    glBegin(GL_QUADS)
    glColor3f(0.7, 0.8, 0.7)
    glVertex3f(15, 0, -15)
    glVertex3f(15, 0, 15)
    glVertex3f(15, 10, 15)
    glVertex3f(15, 10, -15)
    glEnd()
    
    # 천장
    glBegin(GL_QUADS)
    glColor3f(0.9, 0.9, 0.9)
    glVertex3f(-15, 10, -15)
    glVertex3f(15, 10, -15)
    glVertex3f(15, 10, 15)
    glVertex3f(-15, 10, 15)
    glEnd()

# 문 그리기 (탈출 목표)
def draw_door():
    glPushMatrix()
    glTranslatef(0, 0, 15.5)
    
    # 문 프레임
    glBegin(GL_LINE_LOOP)
    glColor3f(0.5, 0.3, 0.1)
    glVertex3f(-2, 0, 0)
    glVertex3f(2, 0, 0)
    glVertex3f(2, 7, 0)
    glVertex3f(-2, 7, 0)
    glEnd()
    
    # 문
    glBegin(GL_QUADS)
    glColor3f(0.6, 0.4, 0.2)
    glVertex3f(-1.9, 0.1, 0)
    glVertex3f(1.9, 0.1, 0)
    glVertex3f(1.9, 6.9, 0)
    glVertex3f(-1.9, 6.9, 0)
    glEnd()
    
    # 자물쇠
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(1, 0.84, 0)
    for i in range(20):
        angle = i * 2 * math.pi / 20
        glVertex3f(0.5 * math.cos(angle), 3.5 + 0.3 * math.sin(angle), 0.1)
    glEnd()
    
    glPopMatrix()

# 퍼즐 1: 수학 퍼즐
def draw_puzzle1_display():
    glPushMatrix()
    glTranslatef(-10, 5, -14.5)
    
    # 퍼즐 박스
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.2, 0.3)
    glVertex3f(-2, -1, 0)
    glVertex3f(2, -1, 0)
    glVertex3f(2, 1, 0)
    glVertex3f(-2, 1, 0)
    glEnd()
    
    glPopMatrix()

# 퍼즐 2: 그림 맞추기
def draw_puzzle2_display():
    glPushMatrix()
    glTranslatef(10, 5, -14.5)
    
    # 퍼즐 박스
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.2, 0.2)
    glVertex3f(-2, -1, 0)
    glVertex3f(2, -1, 0)
    glVertex3f(2, 1, 0)
    glVertex3f(-2, 1, 0)
    glEnd()
    
    glPopMatrix()

# 퍼즐 3: 숨겨진 물건
def draw_puzzle3_object():
    glPushMatrix()
    glTranslatef(-10, 2, 10)
    glColor3f(1, 0.5, 0)
    draw_cube(0.5)
    glPopMatrix()

# 플레이어 카메라 클래스
class Player:
    def __init__(self):
        self.x = 0
        self.y = 1.7
        self.z = 0
        self.angle_x = 0
        self.angle_y = 0
        self.speed = 0.3
        self.mouse_sensitivity = 0.05
        
    def update(self, keys, mouse_rel):
        # 마우스 카메라 조작
        self.angle_y += mouse_rel[0] * self.mouse_sensitivity
        self.angle_x -= mouse_rel[1] * self.mouse_sensitivity
        
        # 각도 제한
        self.angle_x = max(-89, min(89, self.angle_x))
        
        # WASD 이동
        if keys[K_w]:
            self.x += math.sin(math.radians(self.angle_y)) * self.speed
            self.z -= math.cos(math.radians(self.angle_y)) * self.speed
        if keys[K_s]:
            self.x -= math.sin(math.radians(self.angle_y)) * self.speed
            self.z += math.cos(math.radians(self.angle_y)) * self.speed
        if keys[K_a]:
            self.x -= math.cos(math.radians(self.angle_y)) * self.speed
            self.z -= math.sin(math.radians(self.angle_y)) * self.speed
        if keys[K_d]:
            self.x += math.cos(math.radians(self.angle_y)) * self.speed
            self.z += math.sin(math.radians(self.angle_y)) * self.speed
        
        # 맵 경계
        self.x = max(-14, min(14, self.x))
        self.z = max(-14, min(14, self.z))
        
    def set_camera(self):
        glLoadIdentity()
        gluPerspective(45, (800 / 600), 0.1, 50)
        
        # 카메라 회전
        glRotatef(self.angle_x, 1, 0, 0)
        glRotatef(self.angle_y, 0, 1, 0)
        
        # 카메라 이동
        glTranslatef(-self.x, -self.y, -self.z)

# 메인 게임 클래스
class EscapeRoom3D:
    def __init__(self):
        pygame.init()
        self.display = (800, 600)
        self.screen = pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Escape Room")
        
        # OpenGL 설정
        glEnable(GL_DEPTH_TEST)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        
        # 게임 변수
        self.player = Player()
        self.puzzle_state = PuzzleState()
        self.game_state = GameState.PLAYING
        self.password_input = ""
        self.message = ""
        self.message_time = 0
        self.clock = pygame.time.Clock()
        
        # 퍼즐 답변 생성
        self.generate_puzzles()
        
    def generate_puzzles(self):
        # 각 퍼즐의 답
        self.puzzle_answers = {
            1: str(random.randint(0, 9)),
            2: str(random.randint(0, 9)),
            3: str(random.randint(0, 9))
        }
        self.puzzle_state.correct_password = [
            self.puzzle_answers[1],
            self.puzzle_answers[2],
            self.puzzle_answers[3]
        ]
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == KEYDOWN:
                if self.game_state == GameState.PLAYING:
                    if event.key == K_e:
                        self.check_puzzle_proximity()
                    if event.key == K_ESCAPE:
                        return False
                        
                elif self.game_state == GameState.PASSWORD_INPUT:
                    if event.key == K_BACKSPACE:
                        self.password_input = self.password_input[:-1]
                    elif event.unicode.isdigit():
                        if len(self.password_input) < 3:
                            self.password_input += event.unicode
                    elif event.key == K_RETURN:
                        self.check_password()
                    elif event.key == K_ESCAPE:
                        self.game_state = GameState.PLAYING
                        self.password_input = ""
        
        return True
    
    def check_puzzle_proximity(self):
        # 퍼즐 1 근처
        dist1 = math.sqrt((self.player.x + 10)**2 + (self.player.z + 10)**2)
        if dist1 < 3 and not self.puzzle_state.puzzle1_solved:
            self.show_puzzle(1)
            return
        
        # 퍼즐 2 근처
        dist2 = math.sqrt((self.player.x - 10)**2 + (self.player.z + 10)**2)
        if dist2 < 3 and not self.puzzle_state.puzzle2_solved:
            self.show_puzzle(2)
            return
        
        # 퍼즐 3 근처
        dist3 = math.sqrt((self.player.x + 10)**2 + (self.player.z - 10)**2)
        if dist3 < 3 and not self.puzzle_state.puzzle3_solved:
            self.show_puzzle(3)
            return
        
        # 문 근처
        dist_door = math.sqrt(self.player.x**2 + (self.player.z - 15)**2)
        if dist_door < 3:
            self.game_state = GameState.PASSWORD_INPUT
            self.message = "문이 잠겨있습니다. 비밀번호를 입력하세요 (E키 취소)"
            self.message_time = 300
            
    def show_puzzle(self, puzzle_num):
        if puzzle_num == 1:
            result = self.puzzle_state.solve_puzzle(1, self.puzzle_answers[1])
            if result:
                self.message = f"[퍼즐 1] 10 ÷ 2 = 5. 답: {self.puzzle_answers[1]} ✓"
                self.message_time = 200
        elif puzzle_num == 2:
            result = self.puzzle_state.solve_puzzle(2, self.puzzle_answers[2])
            if result:
                self.message = f"[퍼즐 2] 모양 맞춤. 답: {self.puzzle_answers[2]} ✓"
                self.message_time = 200
        elif puzzle_num == 3:
            result = self.puzzle_state.solve_puzzle(3, self.puzzle_answers[3])
            if result:
                self.message = f"[퍼즐 3] 숨겨진 상자 발견! 답: {self.puzzle_answers[3]} ✓"
                self.message_time = 200
    
    def check_password(self):
        correct = "".join(self.puzzle_state.correct_password)
        if self.password_input == correct:
            self.game_state = GameState.ESCAPED
            self.message = "비밀번호 정답! 문이 열렸습니다!"
            self.message_time = 300
        else:
            self.message = "비밀번호 오답입니다. 다시 시도하세요."
            self.message_time = 150
            self.password_input = ""
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        self.player.set_camera()
        
        # 그리기
        draw_room()
        draw_door()
        draw_puzzle1_display()
        draw_puzzle2_display()
        draw_puzzle3_object()
        
        pygame.display.flip()
    
    def render_ui(self):
        # 2D UI 렌더링 (간단한 텍스트)
        if self.message_time > 0:
            self.message_time -= 1
    
    def run(self):
        running = True
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        
        while running and self.game_state != GameState.ESCAPED:
            running = self.handle_events()
            
            keys = pygame.key.get_pressed()
            mouse_rel = pygame.mouse.get_rel()
            self.player.update(keys, mouse_rel)
            
            self.render()
            self.render_ui()
            self.clock.tick(60)
        
        # 탈출 성공 화면
        if self.game_state == GameState.ESCAPED:
            self.show_ending()
        
        pygame.quit()
    
    def show_ending(self):
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == KEYDOWN:
                    waiting = False
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(0.0, 0.0, 0.0, 1.0)
            
            # 2D 오버레이 (간단한 구현)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, 800, 600, 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            glDisable(GL_DEPTH_TEST)
            
            # 검은 배경
            glClear(GL_COLOR_BUFFER_BIT)
            
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            pygame.display.flip()
            self.clock.tick(30)
        
        print("\n" + "="*50)
        print("🎉 축하합니다! 탈출 성공! 🎉")
        print("="*50)
        print("\n방 안의 모든 퍼즐을 풀고 비밀번호를 찾아냈습니다!")
        print(f"입력한 비밀번호: {self.password_input}")
        print(f"정답: {''.join(self.puzzle_state.correct_password)}")
        print("\n문이 열리고 자유로워졌습니다!")
        print("게임을 플레이해주셔서 감사합니다!")
        print("="*50 + "\n")

# 메인
if __name__ == "__main__":
    print("\n3D 방탈출 게임 시작!")
    print("조작: WASD 이동, 마우스 시점 조작")
    print("E키: 퍼즐 풀기 / 문 열기")
    print("ESC: 게임 종료\n")
    
    game = EscapeRoom3D()
    game.run()
