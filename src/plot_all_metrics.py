import sys
import os
import math
import matplotlib
matplotlib.use('Agg') # 화면 없는 환경 지원
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_all_columns(target_file):
    if not target_file or not os.path.exists(target_file):
        print(f"[Error] 파일을 찾을 수 없습니다: {target_file}")
        return

    try:
        print(f"[*] 데이터 분석 시작: {target_file}")
        
        # 1. CSV 파일 읽기
        df = pd.read_csv(target_file, sep=';', low_memory=False)

        # 2. 데이터 전처리 (문자열 제거 및 숫자 변환)
        # 모든 열을 숫자로 변환 시도, 실패하면 NaN
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 시간(time) 데이터가 없는 행 삭제 (헤더 중복 등 제거)
        df = df.dropna(subset=['time'])
        
        # 시간 단위 변환 (ms -> sec)
        df['time_sec'] = df['time'] / 1000.0
        
        # 3. 그릴 항목 선정 (X축인 time, time_sec 제외)
        # 데이터가 모두 NaN인 컬럼(예: 이웃 기지국 정보가 없는 경우)은 제외
        exclude_cols = ['time', 'time_sec']
        plot_cols = []
        
        for col in df.columns:
            if col not in exclude_cols:
                # 유효한 데이터가 하나라도 있는 경우에만 포함
                if df[col].notna().any():
                    plot_cols.append(col)

        num_plots = len(plot_cols)
        if num_plots == 0:
            print("[Error] 그릴 데이터가 없습니다.")
            return

        print(f"[*] 총 {num_plots}개의 항목을 그래프로 그립니다.")

        # 4. 그래프 레이아웃 설정 (3열 배치)
        cols_per_row = 3
        rows = math.ceil(num_plots / cols_per_row)
        
        # 그래프 크기 동적 조절 (행당 3인치 높이)
        figsize_h = max(10, rows * 3)
        fig, axes = plt.subplots(rows, cols_per_row, figsize=(15, figsize_h))
        
        # 1차원 배열로 평탄화 (반복문 돌리기 편하게)
        if rows > 1:
            axes_flat = axes.flatten()
        else:
            axes_flat = [axes] if cols_per_row == 1 else axes

        fig.suptitle(f'Log Analysis: {os.path.basename(target_file)}', fontsize=20)

        # 5. 반복문으로 모든 그래프 그리기
        for i, col_name in enumerate(plot_cols):
            ax = axes_flat[i]
            
            # 데이터 플로팅
            # 끊긴 데이터도 이어보이게 하려면 linestyle='-' 사용
            ax.plot(df['time_sec'], df[col_name], marker='.', markersize=2, linestyle='-', linewidth=0.5)
            
            ax.set_title(col_name, fontsize=10, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.6)
            
            # X축 라벨은 맨 아래 행에만 표시 (공간 절약)
            if i >= (rows - 1) * cols_per_row:
                ax.set_xlabel('Time (s)')

        # 남은 빈 서브플롯 숨기기
        for j in range(i + 1, len(axes_flat)):
            axes_flat[j].axis('off')

        plt.tight_layout(rect=[0, 0.03, 1, 0.97]) # 제목 공간 확보
        
        # 6. 저장
        output_png = target_file.replace('.csv', '_full_report.png')
        plt.savefig(output_png, dpi=150) # 해상도 높임
        print(f"[*] 전체 분석 리포트 저장 완료! >> {output_png}")

    except Exception as e:
        print(f"[Error] 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input("CSV 파일 경로를 입력하세요: ").strip()

    plot_all_columns(input_path)