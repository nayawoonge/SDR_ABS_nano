import time
import os
import sys
from datetime import datetime

# ==========================================
# 설정 (Configuration)
# ==========================================
# srsUE가 생성하는 소스 파일 (RAM 디스크 경로)
SOURCE_FILE = '/tmp/ue_metrics.csv'

# 데이터를 저장할 파일 이름 생성 (예: flight_log_2024-05-20_14-30-00.csv)
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = f'flight_log_{current_time}.csv'

# ==========================================
# 메인 로직
# ==========================================
def follow(source_path, output_path):
    print(f"[*] Waiting for srsUE source file: {source_path}...")

    # 1. 소스 파일이 생길 때까지 대기
    while not os.path.exists(source_path):
        time.sleep(1)

    print(f"[*] Source found! Saving data to: {output_path}")
    print(f"[*] Press Ctrl+C to stop logging.")

    try:
        # 소스 파일(읽기)과 저장 파일(쓰기) 열기
        with open(source_path, 'r') as f_in, open(output_path, 'w') as f_out:
            
            # (선택) 기존 파일의 끝으로 이동하여 '실시간' 데이터만 가져오기
            # 처음부터 다 가져오고 싶다면 아래 줄을 주석 처리하세요.
            f_in.seek(0, os.SEEK_END)

            while True:
                line = f_in.readline()
                
                if not line:
                    time.sleep(0.1)  # 데이터가 없으면 잠시 대기
                    continue

                # 2. 데이터를 저장 파일에 쓰기
                f_out.write(line)
                
                # 중요: 버퍼에 머물지 않고 즉시 파일에 쓰도록 강제 (전원 끊김 대비)
                f_out.flush() 

                # 3. 화면에도 출력 (모니터링용)
                # 줄바꿈 문자 제거 후 출력
                clean_line = line.strip()
                
                # 데이터가 비어있지 않은 경우에만 출력 및 처리
                if clean_line:
                    print(f"[DATA] {clean_line}")
                    
                    # (옵션) 여기서 RSRP 값만 파싱해서 보기 좋게 출력 가능
                    # srsRAN CSV는 보통 세미콜론(;)으로 구분됩니다.
                    parts = clean_line.split(';')
                    if len(parts) > 1:
                        # 헤더가 아닐 경우 RSRP 출력 (보통 뒤쪽에 위치, 인덱스는 버전에 따라 다름)
                        # 예시: 단순히 전체 길이를 보고 데이터 라인인지 판단
                        pass 

    except KeyboardInterrupt:
        print("\n[*] Stopping data logging...")
        print(f"[*] Data saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    follow(SOURCE_FILE, OUTPUT_FILE)