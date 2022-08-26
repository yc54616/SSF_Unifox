import socket
import pygame
import threading
import json


############# 1. 클라이언트 초기 설정 #############

HOST = '___________________' # <= 클라이언트가 접속할 서버의 IP주소 지정
PORT = '____' # <= 클라이언트가 접속할 서버의 포트번호 지정 
SIZE = 14
RED = (255,0,0)
BLACK = (0,0,0)

BACKGROUND_LOCATION = (0, 0)
MY_SCORE_LOCATION = (20, 608)
SCORE_LOCATION = (52, 658)
TIMER_LOCATION = (1002, 638)
TEXT1_LOCATION = (220, 610)
TEXT2_LOCATION = (220, 660)

clients = {}
result = ''

class Character:
    def __init__(self):
        self.img = pygame.image.load("./img/character.png")
        self.size = self.img.get_rect().size 
        self.width = self.size[0]
        self.height = self.size[1] 
        self.tmp_x = 0 
        self.tmp_y = 0
        self.x = 0
        self.y = 0
        self.speed = 10
        self.score = 0


############# 2. 바이트를 문자열로 바꾸는 함수 완성하기 #############

def byte_to_string(str):
    str = str.decode()
    action = str[0:1]
    id = str[1:3]
    x = str[3:7]
    y = str[7:10]
    questions = str[10:12]
    answer = str[12:13]
    time = str[13:14]

    if action == '0':
        action = 'id'
    elif action == '1':
        action = 'connection'
    elif action == '2':
        action = 'movement'
    elif action == '3':
        action = 'questions'
    elif action == '4':
        action = 'answer'
    elif action == '5':
        action = 'time'
    elif action == '6':
        action = 'disconnection'    

    return '____', '____', '____', '____', '____', '____', '____' # <= 입력받은 바이트를 해석한 변수들의 값들을 반환


############# 3. 문자열을 바이트로 바꾸는 함수 완성하기 #############

def string_to_byte(action='-', id='--', x='----', y='---', questions='--', answer='-', time='-'):
    result = ''

    if action == 'id':
        result += '0'
    elif action == 'connection':
        result += '1'
    elif action == 'movement':
        result += '2'
    elif action == 'questions':
        result += '3'
    elif action == 'answer':
        result += '4'
    elif action == 'time':
        result += '5'
    elif action == 'disconnection':
        result += '6'
    
    result += id.'____' # <= id를 뜻하는 바이트 수만큼 0으로 채우기
    result += x.'____' # <= x좌표를 뜻하는 바이트 수만큼 0으로 채우기
    result += y.'____' # <= y좌표를 뜻하는 바이트 수만큼 0으로 채우기
    result += questions.'____' # <= questions(문제 번호)를 뜻하는 바이트 수만큼 0으로 채우기
    result += answer
    result += time

    return result.encode()


############# 4. 캐릭터의 OX 판별 함수 완성하기 #############

def answer_cheak(answer):
    character = clients[myID]
    if '____': # <= 캐릭터의 x좌표와 캐릭터의 크기를 이용하여 O와 X 중 더 가까운 위치 파악하기
        result = 'X'
    else:
        result = 'O'

    if answer == result:
        character.score+=1
        return '맞았습니다!'
    else:
        return '틀렸습니다'


############# 5. 소켓 데이터 받는 함수 완성하기 #############

def recv_data():
    global myID, running, result, score_time
    running = True
    while running:
        try:
            data = client_socket.recv('____') # <= client_socket 소켓을 이용하여 정해진 바이트 크기만큼 받기
            print(byte_to_string(data))
            action, id, x, y, questions, answer, time = byte_to_string(data)
            if action == 'id':
                myID = id

            if action == 'connection':
                new_clinet = Character()
                clients[id] = new_clinet

            if action == 'movement':
                clients[id].x = int(x[:3].lstrip('0')+x[3:])
                clients[id].y = int(y[:2].lstrip('0')+y[2:])

            if action == 'questions':
                result = questions_dict[questions]['questions']
            
            if action == 'answer':
                result = '정답은 '+answer+'입니다. ('+answer_cheak(answer)+')'
            
            if action == 'time':
                score_time = time

            if action == 'disconnection':
                del clients[id]

        except '____' as e: # <= OSError 발생 시 예외 처리해주기
            print('>> OS Error\n'+str(e))
            break

        except Exception as e:
            print('>> Recv Error\n'+str(e))

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    client_socket.connect((HOST, PORT)) 

    print('>> Server Connect!')


    ############# 6. recv_data 함수 스레드로 실행하기 #############

    recver = '__________' # <= recv_data 함수를 실행하는 recver 스레드 생성
    recver.daemon = True
    recver.'____' # <= 스레드 실행하기

    questions_json = open('./OX/question.json', encoding = 'utf-8')
    questions_dict = json.load(questions_json)

    pygame.init()

    screen_width = 1080
    screen_height = 720

    game_width = 1080
    game_height = 586

    screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("UNIFOX OX퀴즈 게임")

    clock = pygame.time.Clock()


    ############# 7. 게임 초기 설정 #############

    background = '____' # <= pygame 라이브러리를 이용하여 게임의 배경 사진을 불러오기
    
    small_font = pygame.font.Font('./fonts/Maplestory Bold.ttf', 32)
    big_font = pygame.font.Font('./fonts/Maplestory Bold.ttf', 40)

    my_score = small_font.render('MY SCORE', True, RED)

    while True:
        fps = clock.tick(30)
        event = pygame.event.poll() 
        if event.type == pygame.QUIT:
            client_socket.send(string_to_byte(action='disconnection', id=myID))
            running = False
            client_socket.close()
            break


        ############# 8. 캐릭터 조작하기 #############

        character = clients[myID]
        keys = pygame.key.get_pressed()
        if '__________': # <= 오른쪽 키 눌렀을 때 
            '__________' # 캐릭터의 속도만큼 x좌표 이동하기

        if '__________': # <= 왼쪽 키 눌렀을 때 
            '__________' # 캐릭터의 속도만큼 x좌표 이동하기

        if '__________': # <= 아래키 키 눌렀을 때 
            '__________' # 캐릭터의 속도만큼 y좌표 이동하기

        if '__________': # <= 위쪽 키 눌렀을 때 
            '__________' # 캐릭터의 속도만큼 y좌표 이동하기

        if character.x < 0:
            character.x = 0
        if character.x > game_width - character.width:
            character.x = game_width - character.width
        if character.y < 0:
            character.y = 0
        if character.y > game_height - character.height:
            character.y = game_height - character.height

        if character.x != character.tmp_x or character.y != character.tmp_y:
            client_socket.send(string_to_byte(action='movement', id=myID, x=str(character.x), y=str(character.y)))
            character.tmp_x = character.x
            character.tmp_y= character.y

        if len(' '.join((result.split(' ')[:6]))) > 30:
            result1 = ' '.join((result.split(' ')[:5]))
            result2 = ' '.join((result.split(' ')[5:]))
        elif len(' '.join((result.split(' ')[:7]))) > 30:
            result1 = ' '.join((result.split(' ')[:6]))
            result2 = ' '.join((result.split(' ')[6:]))    
        elif len(' '.join((result.split(' ')[:8]))) > 30:
            result1 = ' '.join((result.split(' ')[:7]))
            result2 = ' '.join((result.split(' ')[7:]))    
        else:
            result1 = ' '.join((result.split(' ')[:8]))
            result2 = ' '.join((result.split(' ')[8:]))

        text1 = small_font.render(result1, True, BLACK)
        text2 = small_font.render(result2, True, BLACK)
        timer = big_font.render(score_time, True, BLACK)
        score = big_font.render(str(character.score).zfill(4), True, RED)
        

        ############# 9. 클라이언트들 그리기 #############

        screen.blit(background, BACKGROUND_LOCATION) 
        for key in '__________': # <= clients 딕셔너리의 키를 이용하여
            '__________'        # 각 클라이언트의 x좌표와 y좌표에 이미지 그리기
        screen.blit(my_score, MY_SCORE_LOCATION)
        screen.blit(score, SCORE_LOCATION)
        screen.blit(timer, TIMER_LOCATION)
        screen.blit(text1, TEXT1_LOCATION)
        screen.blit(text2, TEXT2_LOCATION)


        ############# 10. 화면 새로고침하기 #############

        '__________' # <= pygame 라이브러리를 이용하여 게임 화면을 새로고침

    pygame.quit()