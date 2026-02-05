import sys
import os
import matplotlib
# 화면 없는 환경(Headless) 지원
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd

def plot_cellular_log(target_file):
    if not target_file or not os.path.exists(target_file):
        print(f"[Error] 파일을 찾을 수 없습니다: {target_file}")
        return

    try:
        print(f"[*] 데이터 분석 시작: {target_file}")
        
        # 1. CSV 파일 읽기
        # low_memory=False: 데이터 타입 추론 경고 방지
        df = pd.read_csv(target_file, sep=';', low_memory=False)

        # ---------------------------------------------------------
        # [핵심 수정] 데이터 전처리 (문자열 제거 및 숫자 변환)
        # ---------------------------------------------------------
        
        # 'time' 열을 강제로 숫자로 변환합니다.
        # errors='coerce' 옵션은 숫자가 아닌 것(예: 중간에 낀 헤더 문자열)을 NaN(빈 값)으로 바꿉니다.
        df['time'] = pd.to_numeric(df['time'], errors='coerce')
        df['rsrp'] = pd.to_numeric(df['rsrp'], errors='coerce')
        df['dl_snr'] = pd.to_numeric(df['dl_snr'], errors='coerce')
        df['pci'] = pd.to_numeric(df['pci'], errors='coerce')

        # 숫자가 아닌 행(NaN)을 싹 지워버립니다.
        original_count = len(df)
        df = df.dropna(subset=['time', 'rsrp'])
        dropped_count = original_count - len(df)
        
        if dropped_count > 0:
            print(f"[*] 알림: {dropped_count}개의 잘못된 데이터 라인(중복 헤더 등)을 제거했습니다.")

        if df.empty:
            print("[Error] 유효한 데이터가 하나도 없습니다.")
            return
        # ---------------------------------------------------------

        # 시간 단위 변환 (ms -> sec)
        # 이제 'time' 열이 무조건 실수형(float)이므로 에러가 나지 않습니다.
        df['time_sec'] = df['time'] / 1000.0

        # 그래프 그리기
        plt.figure(figsize=(12, 10))
        plt.suptitle(f'Log Analysis: {os.path.basename(target_file)}', fontsize=16)

        # (1) RSRP
        plt.subplot(3, 1, 1)
        plt.plot(df['time_sec'], df['rsrp'], 'b-', linewidth=1, label='RSRP')
        plt.title('Signal Strength (RSRP)', fontsize=14, fontweight='bold')
        plt.ylabel('RSRP (dBm)', fontsize=12)
        plt.grid(True, which='both', linestyle='--')
        plt.legend()
        # 그래프 범위가 너무 튀지 않게 조정
        if not df['rsrp'].empty:
             plt.ylim(df['rsrp'].min() - 5, df['rsrp'].max() + 5)

        # (2) SNR
        plt.subplot(3, 1, 2)
        plt.plot(df['time_sec'], df['dl_snr'], 'g-', linewidth=1, label='SNR')
        plt.title('Signal Quality (SNR)', fontsize=14, fontweight='bold')
        plt.ylabel('SNR (dB)', fontsize=12)
        plt.grid(True, linestyle='--')
        plt.legend()

        # (3) PCI
        plt.subplot(3, 1, 3)
        plt.step(df['time_sec'], df['pci'], 'r-', where='mid', label='PCI')
        plt.title('Serving Cell ID (PCI)', fontsize=14, fontweight='bold')
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('PCI', fontsize=12)
        plt.grid(True, linestyle='--')
        plt.legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        output_png = target_file.replace('.csv', '.png')
        plt.savefig(output_png)
        print(f"[*] 그래프 저장 완료! >> {output_png}")

    except Exception as e:
        print(f"[Error] 처리 중 오류 발생: {e}")
        # 디버깅을 위해 에러 상세 정보 출력
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input("CSV 파일 경로를 입력하세요: ").strip()

    plot_cellular_log(input_path)