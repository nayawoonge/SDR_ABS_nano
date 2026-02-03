import time
import os
import sys
from datetime import datetime

# ==========================================
# 사용자 설정 (Configuration)
# ==========================================
# srsUE가 실시간으로 데이터를 쏟아내는 임시 파일 경로
SOURCE_FILE = '/tmp/ue_metrics.csv'

# 로그를 저장할 디렉토리 (현재 폴더)
LOG_DIR = '/home/jetsonnx/SDR_ABS_nano/logs'

# ==========================================
# 메인 로직
# ==========================================
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def tail_and_save(source_path):
    # 1. 저장할 파일명 생성 (예: Cell_log_2026-02-02_14-30-00.csv)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ensure_dir(LOG_DIR)
    output_path = os.path.join(LOG_DIR, f'Cell_log_{current_time}.csv')

    print(f"[info] Waiting for srsUE source file: {source_path}...")

    # 2. 소스 파일이 생성될 때까지 대기 (srsUE가 켜질 때까지 기다림)
    while not os.path.exists(source_path):
        time.sleep(1)

    print(f"[info] Source found! Logging started.")
    print(f"[info] Saving data to: {output_path}")
    print(f"[info] Press Ctrl+C to stop logging.\n")

    try:
        with open(source_path, 'r') as f_in, open(output_path, 'w') as f_out:
            # 파일의 끝으로 이동하여 '과거 데이터'는 무시하고 '새 데이터'만 기록
            # srsUE를 껐다 켰을 때 이전 로그가 섞이는 것을 방지합니다.
            f_in.seek(0, os.SEEK_END)

            while True:
                # 한 줄 읽기
                line = f_in.readline()
                
                # 데이터가 아직 안 들어왔으면 잠시 대기
                if not line:
                    time.sleep(0.01) # CPU 점유율을 낮추기 위한 대기
                    continue

                # 3. 데이터 저장 (가장 중요)
                f_out.write(line)
                
                # [중요] 버퍼를 비워 즉시 파일에 씀 (전원 차단 대비)
                f_out.flush() 

                # 4. 화면 출력 (모니터링용)
                # 불필요한 공백 제거 후 출력
                clean_line = line.strip()
                if clean_line:
                    print(f"[REC] {clean_line}")

    except KeyboardInterrupt:
        print("\n\n[*] Logging stopped by user.")
        print(f"[*] File saved successfully: {output_path}")
    except Exception as e:
        print(f"\n[!] Error occurred: {e}")

if __name__ == "__main__":
    tail_and_save(SOURCE_FILE)