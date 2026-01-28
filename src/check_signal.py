import socket
import json

# 설정한 IP와 포트
UDP_IP = "127.0.0.1"
UDP_PORT = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for srsUE metrics on {UDP_IP}:{UDP_PORT}...")

try:
    while True:
        data, addr = sock.recvfrom(4096) # 버퍼 크기
        try:
            # JSON 데이터 파싱
            json_data = json.loads(data.decode('utf-8'))
            
            # RSRP 값 추출 (데이터 구조에 따라 경로가 다를 수 있음)
            # 보통 json_data['cc0']['rsrp'] 또는 비슷한 경로에 위치함
            # 전체 데이터를 보려면 print(json_data) 사용
            
            if 'cc0' in json_data and 'rsrp' in json_data['cc0']:
                rsrp = json_data['cc0']['rsrp']
                print(f"Current RSRP: {rsrp} dBm")
            else:
                # 데이터 구조 확인용 (처음에만 주석 해제해서 확인해보세요)
                # print(json_data)
                pass

        except json.JSONDecodeError:
            print("JSON decoding error")
            
except KeyboardInterrupt:
    print("Stopping...")