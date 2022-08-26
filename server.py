############# 필요한 라이브러리 불러오기 #############

import socket    # <= 소켓 라이브러리
import threading # <= 스레드 라이브러리
import random    # <= 랜덤 라이브러리
import time      # <= 시간 라이브러리
import json      # <= JSON 라이브러리


############# 초기 설정 #############

HOST = '127.0.0.1' # <= 서버 IP주소 설정
PORT = 8888       # <= 서버 포트번호 설정
SIZE = 14          # <= 소켓 바이트 크기 설정
START_CLIENT = 2   # <= 초기 게임 시작인원 수 설정
clients = {}       # <= 연결된 클라이언트 딕셔너리 만들기


############# Client 클래스 #############

class Client:
    def __init__(self, socket): # <= 생성자로 새로운 객체 만들 때 소켓으로 만들기
        self.socket = socket    # <= 소켓을 인스턴스 변수에 저장
        self.x = 0              # <= x위치를 인스턴스 변수에 저장
        self.y = 0              # <= y위치를 인스턴스 변수에 저장


############# 바이트를 문자열로 바꾸기 #############

def byte_to_string(str):
    str = str.decode()     # <= 바이트를 문자열로 디코딩
    action = str[0:1]      # <= 슬라이싱을 이용하여 1번째 바이트 저장
    id = str[1:3]          # <= 슬라이싱을 이용하여 2~3번째 바이트 저장
    x = str[3:7]           # <= 슬라이싱을 이용하여 4~7번째 바이트 저장
    y = str[7:10]          # <= 슬라이싱을 이용하여 8~10번째 바이트 저장
    questions = str[10:12] # <= 슬라이싱을 이용하여 11~12번째 바이트 저장
    answer = str[12:13]    # <= 슬라이싱을 이용하여 13번째 바이트 저장
    time = str[13:14]      # <= 슬라이싱을 이용하여 14번째 바이트 저장

    if action == '0':            # <= 1번째 바이트가 0이라면 
        action = 'id'            #    id 알려주기
    elif action == '1':          # <= 1번째 바이트가 1이라면 
        action = 'connection'    #    연결정보 알려주기
    elif action == '2':          # <= 1번째 바이트가 2이라면 
        action = 'movement'      #    위치정보 알려주기
    elif action == '3':          # <= 1번째 바이트가 3이라면 
        action = 'questions'     #    문제정보 알려주기
    elif action == '4':          # <= 1번째 바이트가 4이라면 
        action = 'answer'        #    문제정답 알려주기
    elif action == '5':          # <= 1번째 바이트가 5이라면 
        action = 'time'          #    시간정보 알려주기
    elif action == '6':          # <= 1번째 바이트가 6이라면 
        action = 'disconnection' #    연결해제정보 알려주기

    return action, id, x, y, questions, answer, time # <= 바이트를 해석한 문자열 반환하기


############# 문자열을 바이트로 바꾸기 #############

def string_to_byte(action='-', id='--', x='----', y='---', questions='--', answer='-', time='-'): # <= 입력받은 값이 없다면 정해질 초기값

    result = '' # <= result을 문자열로 설정

    if action == 'id':              # <= 입력받은 정보가 id라면
        result += '0'               #    result는 0
    elif action == 'connection':    # <= 입력받은 정보가 connection라면
        result += '1'               #    result는 1
    elif action == 'movement':      # <= 입력받은 정보가 movement라면
        result += '2'               #    result는 2
    elif action == 'questions':     # <= 입력받은 정보가 questions라면
        result += '3'               #    result는 3
    elif action == 'answer':        # <= 입력받은 정보가 answer라면
        result += '4'               #    result는 4
    elif action == 'time':          # <= 입력받은 정보가 time라면
        result += '5'               #    result는 5
    elif action == 'disconnection': # <= 입력받은 정보가 disconnection라면
        result += '6'               #    result는 6
    
    result += id.zfill(2)        # <= 남는 자리는 0으로 채워 2자리로 만들기
    result += x.zfill(4)         # <= 남는 자리는 0으로 채워 4자리로 만들기
    result += y.zfill(3)         # <= 남는 자리는 0으로 채워 3자리로 만들기
    result += questions.zfill(2) # <= 남는 자리는 0으로 채워 2자리로 만들기
    result += answer
    result += time

    return result.encode() # <= 문자열을 바이트로 변환해 반환하기


############# 소켓으로 데이터 보내기 #############

def send(client_socket, data):
    try:
        client_socket.send(data) # <= 소켓으로 데이터 보내기, 연결되는 시간을 줄이기 위해 스레드로 실행
    except Exception as e: # <= 모든 오류 예외처리
        print('>> Send Error\n'+str(e))

############# 연결된 클라이언트들에게 데이터 보내기 #############

def send_data(data, client_socket = None): # <= 소켓을 같이 입력받지 않는다면 None으로 설정

    for client_key in clients.keys():   # <= 모든 클라이언트 key로 접근
        try:
            if client_socket == clients[client_key].socket: # <= 만약 입력받은 소켓이라면 데이터 보내지 말기
                continue
            
            sender = threading.Thread(target=send, args=(clients[client_key].socket, data,)) # <= 스레드로 send 함수 실행
            sender.daemon = True                                                            # <= 데몬 스레드로 설정
            sender.start()                                                                  # <= 스레드 실행

        except Exception as e: # <= 모든 오류 예외처리
            print('>> Send Error\n'+str(e))


############# 연결된 클라이언트들에게 데이터 받기 #############

def recv_data(client_socket):
    global running, questions_num, timer
    while True:
        try:
            data = client_socket.recv(SIZE)                                  # <= 14바이트의 크기로 데이터 받기
            action, id, x, y, questions, answer, time = byte_to_string(data) # <= 받은 바이트 데이터를 문자열로 변환 후 언패킹으로 각 변수에 저장
            print(byte_to_string(data))                                      # <= 받은 데이터 출력

            send_data(data, client_socket=client_socket) # <= 보낸 클라이언트를 제외한 모든 연결된 클라이언트들에게 데이터 보내기             

            if action == 'movement':                         # <= 위치정보라면 
                clients[id].x = int(x[:3].lstrip('0')+x[3:]) #    클라이언트 id를 가진 x좌표 업데이트
                clients[id].y = int(y[:2].lstrip('0')+y[2:]) #    클라이언트 id를 가진 y좌표 업데이트

            if action == 'disconnection':                                                  # <= 연결해제정보라면 
                del clients[id]                                                            #    clients의 해당 id를 가진 클라이언트 제거
                if len(clients) < START_CLIENT:                                            # <= 만약 연결된 클라이언트들이 초기 게임시작 인원수를 넘지 못한다면
                    running = False                                                        #    문제 알려주기 running을 False로 바꿔 멈추기 
                    questions_num = '00'                                                   # <= 문제정보를 00으로 설정
                    send_data(string_to_byte(action='questions', questions=questions_num)) # <= 연결된 클라이언트들에게 문제정보 알리기
                    timer = 'X'                                                            # <= 타이머를 X로 설정
                    send_data(string_to_byte(action='time', time=timer))                   # <= 연결된 클라이언트들에게 시간정보 알리기
                break

        except OSError as e: # <= OSError 오류 발생(클라이언트가 강제로 게임을 종료)시 예외처리
            print('>> OS Error\n'+str(e))
            
            for client_key in clients.keys():  
                if clients[client_key].socket == client_socket:
                    send_data(string_to_byte(action='disconnection', id=client_key), client_socket=client_socket) # <= 연결된 클라이언트들에게 disconnection데이터 보내기
                    del clients[client_key]                                                                       # <= clients의 해당 id를 가진 클라이언트 제거
                    break

            if len(clients) < START_CLIENT:                                            # <= 만약 연결된 클라이언트들이 초기 게임시작 인원수를 넘지 못한다면
                running = False                                                        #    문제 알려주기 running을 False로 바꿔 멈추기 
                questions_num = '00'                                                   # <= 문제정보를 00으로 설정
                send_data(string_to_byte(action='questions', questions=questions_num)) # <= 연결된 클라이언트들에게 문제정보 알리기
                timer = 'X'                                                            # <= 타이머를 X로 설정
                send_data(string_to_byte(action='time', time=timer))                   # <= 연결된 클라이언트들에게 시간정보 알리기
            break

        except Exception as e: # <= 모든 오류 예외처리
            print('>> Recv Error\n'+str(e))

    client_socket.close()


############# 초기 게임시작 인원 확인 후 문제 알려주기 #############

def questions_send():
    global running, questions_num, timer
    while True:
        if len(clients) >= START_CLIENT:                                           # <= 연결된 클라이언트가 초기 게임시작 인원보다 많다면
            questions_num = str(random.randint(1, 99)).zfill(2)                    #    1부터 99까지의 랜덤 문제번호 정하기
            send_data(string_to_byte(action='questions', questions=questions_num)) # <= 연결된 클라이언트들에게 문제번호 보내기

            running = True # <= running을 True로 정하기
            i = 9          # <= i, 즉 타이머 시간을 9초로 정하기

            while running:
                timer = str(i) # <= i를 문자열로 바꾸고 timer에 저장

                if int(timer) == 0:                                                                            # <= timer가 0초라면 
                    send_data(string_to_byte(action='answer', answer=questions_dict[questions_num]['answer'])) #    연결된 클라이언트들에게 문제정답 보내기
                    time.sleep(2)                                                                              # <= 2초 기다리기
                    break

                send_data(string_to_byte(action='time', time=timer)) # <= timer가 0초가 아니라면 
                time.sleep(1)                                        # <= 1초 기다리기
                i-=1                                                 # <= i 1감소 (timer 1감소)

        time.sleep(1) # <= 연결된 클라이언트가 초기 게임시작 인원보다 적다면 1초 기다리기


if __name__ == '__main__':

    ############# 서버 소켓 만들고 대기 #############

    print('>> Server Start')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # <= TCP 형식으로 서버 소켓 만들기
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # <= 포트 재사용 시간 없애기
    server_socket.bind((HOST, PORT))                                    # <= IP주소와 포트번호 할당
    server_socket.listen()                                              # <= 클라이언트 연결 대기
    print('>> Server Listening')


    ############# 문제 JSON 파일 불러오기 #############    

    questions_json = open('./OX/question.json', encoding = 'utf-8') # <= json 파일 불러오기
    questions_dict = json.load(questions_json)                      # <= 불러온 파일을 python 딕셔너리 형태로 변환


    ############# 스레드로 questions_send 함수 실행 #############   

    questions_sender = threading.Thread(target=questions_send) # <= 스레드로 questions_send 함수 실행
    questions_sender.daemon = True                             # <= 데몬 스레드로 설정
    questions_sender.start()                                   # <= 스레드 시작


    ############# 새로운 클라이언트의 연결 후 작업 #############   

    id = 0               # <= 초기 클라이언트 번호 설정
    questions_num = '00' # <= 초기 문제번호 설정
    timer = 'X'          # <= 초기 타이머 설정
    while True:
        client_socket, addr = server_socket.accept() # <= 새로운 클라이언트의 연결된 소켓
        print('>> Connection ' + addr[0])

        new_clinet = Client(client_socket)      # <= 연결된 소켓으로 Client 객체 만들기
        clients[str(id).zfill(2)] = new_clinet  # <= id key로 clients 딕셔너리의 항목 추가

        client_socket.send(string_to_byte(action='id', id=str(id)))                     # <= 연결된 클라이언트 id 알려주기
        client_socket.send(string_to_byte(action='questions', questions=questions_num)) # <= 연결된 클라이언트 문제번호 알려주기
        client_socket.send(string_to_byte(action='time', time=timer))                   # <= 연결된 클라이언트 타이머 알려주기

        for client_key in clients.keys():                                                                                                  # <= 모든 클라이언트들에게 보내기(key로 접근)
            client_socket.send(string_to_byte(action='connection', id=client_key))                                                         # <= 모든 클라이언트들에게 새롭게 연결된 클라이언트 id 보내기
            client_socket.send(string_to_byte(action='movement', id=client_key, x=str(clients[client_key].x), y=str(clients[client_key].y))) # <= 모든 클라이언트들에게 새롭게 연결된 클라이언트 위치 보내기

        send_data(string_to_byte(action='connection', id=str(id)), client_socket=client_socket) # <= 이미 연결되어 있던 클라이언트들에게 새롭게 연결된 클라이언트 id 보내기
        
        id+=1 # <= id 1 증가

        print(clients) # <= clients 딕셔너리 출력(연결되어 있는 클라이언트 확인)

        recver = threading.Thread(target=recv_data, args=(client_socket,)) # <= 스레드로 새로운 클라이언트의 연결된 소켓, recv_data 함수 실행
        recver.daemon = True                                               # <= 데몬스레드로 설정
        recver.start()                                                     # <= 스레드 시작

        