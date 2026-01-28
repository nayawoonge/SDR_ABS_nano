import time
import os
import csv

CSV_FILE = '/tmp/ue_metrics.csv'

print(f"Waiting for metrics file: {CSV_FILE}...")

# 파일이 생성될 때까지 대기
while not os.path.exists(CSV_FILE):
    time.sleep(1)

print("File found! Reading metrics...")

try:
    with open(CSV_FILE, 'r') as f:
        # 파일 끝으로 이동 (과거 데이터 무시)
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1) # 데이터가 들어올 때까지 대기
                continue
            
            # 데이터 파싱
            # CSV 헤더 예시: time, cc, pci, rsrp, pl, ...
            # 보통 rsrp는 'dl_rsrp' 또는 'rsrp' 같은 컬럼에 있습니다.
            # 간단하게 쉼표로 분리해서 확인
            
            try:
                parts = line.strip().split(';') # srsRAN CSV는 세미콜론(;) 또는 콤마(,) 사용
                if len(parts) < 2: 
                     parts = line.strip().split(',')

                # 데이터가 헤더(Header)가 아니고 숫자일 때만 출력
                # 보통 RSRP는 뒤쪽 컬럼에 위치합니다. 
                # 정확한 인덱스는 첫 줄(헤더)을 봐야 알지만, 일단 전체를 출력해서 확인해봅시다.
                
                print(f"New Data: {line.strip()}")
                
                # 만약 특정 값(RSRP)만 뽑고 싶다면, 
                # 실행된 CSV 파일의 첫 줄(헤더)을 보고 인덱스를 맞춰야 합니다.
                # 예: rsrp = parts[5] 
                
            except Exception as e:
                print(f"Error parsing line: {e}")

except KeyboardInterrupt:
    print("Stopping...")