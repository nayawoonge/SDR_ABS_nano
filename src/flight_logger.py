import time
import csv
import math
from datetime import datetime
from pymavlink import mavutil

# --- 설정 구간 ---
# Jetson 시리얼 포트로 연결
CONNECTION_STRING = '/dev/ttyTHS0,921600'

# 로그 파일 이름 생성 (현재 시간 기준)
log_filename = f"/home/jetsonnx/SDR_ABS_nano/logs/flight_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

def connect_drone():
    print(f"Waiting for connection on {CONNECTION_STRING}...")
    # 연결 객체 생성
    master = mavutil.mavlink_connection(CONNECTION_STRING)
    
    # 첫 Heartbeat 기다림 (연결 확인용)
    master.wait_heartbeat()
    print(f"Heartbeat received! System ID: {master.target_system}, Component ID: {master.target_component}")
    return master

def main():
    master = connect_drone()

    # CSV 파일 열기 및 헤더 작성
    with open(log_filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'mode', 'lat', 'lon', 'alt_rel', 'roll', 'pitch', 'yaw', 'gps_fix', 'satellites']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        print(f"Logging started! Saving to {log_filename}")
        print("Press Ctrl+C to stop logging.\n")

        try:
            while True:
                # 메시지 받아오기 (0.1초 타임아웃)
                msg = master.recv_match(blocking=True, timeout=0.1)
                
                if not msg:
                    continue

                # 데이터 저장용 딕셔너리 초기화
                data = {}
                
                # 1. 위치 데이터 (GLOBAL_POSITION_INT)
                if msg.get_type() == 'GLOBAL_POSITION_INT':
                    data['lat'] = msg.lat / 1e7  # 정수를 실수(도)로 변환
                    data['lon'] = msg.lon / 1e7
                    data['alt_rel'] = msg.relative_alt / 1000.0  # mm를 m로 변환
                    
                    # GPS 상태 확인을 위해 GPS_RAW_INT 메시지도 확인 필요하지만
                    # 여기서는 편의상 GLOBAL_POSITION_INT가 들어오면 기록
                    
                # 2. 자세 데이터 (ATTITUDE) - 캘리브레이션 잘 됐는지 확인용
                elif msg.get_type() == 'ATTITUDE':
                    data['roll'] = math.degrees(msg.roll)
                    data['pitch'] = math.degrees(msg.pitch)
                    data['yaw'] = math.degrees(msg.yaw)

                # 3. GPS 상태 (GPS_RAW_INT) - Fix type 확인
                elif msg.get_type() == 'GPS_RAW_INT':
                    data['gps_fix'] = msg.fix_type  # 0-1: no fix, 3: 3D fix
                    data['satellites'] = msg.satellites_visible

                # 4. 현재 비행 모드 (HEARTBEAT)
                elif msg.get_type() == 'HEARTBEAT':
                    # 모드 이름 파싱 (예: STABILIZED, OFFBOARD)
                    data['mode'] = mavutil.mode_string_v10(msg)

                # --- 화면 출력 및 CSV 저장 (데이터가 모였을 때) ---
                # 간단한 로직: 자세(Attitude) 메시지가 올 때마다 현재 상태를 저장/출력
                if msg.get_type() == 'ATTITUDE':
                    # 현재 시간
                    current_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    
                    # CSV에 쓸 데이터 조합 (없는 값은 N/A 처리)
                    row = {
                        'timestamp': current_time,
                        'mode': data.get('mode', 'N/A'),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0),
                        'alt_rel': data.get('alt_rel', 0),
                        'roll': f"{data.get('roll', 0):.2f}",
                        'pitch': f"{data.get('pitch', 0):.2f}",
                        'yaw': f"{data.get('yaw', 0):.2f}",
                        'gps_fix': data.get('gps_fix', 'N/A'),
                        'satellites': data.get('satellites', 'N/A')
                    }
                    
                    # 파일 저장
                    writer.writerow(row)
                    
                    # 화면 출력 (보기 좋게)
                    print(f"[{current_time}] Roll: {row['roll']:>6} | Pitch: {row['pitch']:>6} | Yaw: {row['yaw']:>6} | Alt: {row['alt_rel']}m")

        except KeyboardInterrupt:
            print("\n Logging stopped by user.")
            print(f"Data saved to {log_filename}")

if __name__ == '__main__':
    main()