import time
from pymavlink import mavutil

# --- 설정 ---
# Jetson GPIO 연결 기준
CONNECTION_STRING = '/dev/ttyTHS0'
BAUD_RATE = 921600

def main():
    # 1. 드론 연결
    print(f"Connecting to {CONNECTION_STRING}...")
    master = mavutil.mavlink_connection(CONNECTION_STRING, baud=BAUD_RATE)
    master.wait_heartbeat()
    print("✅ Heartbeat received! Connected.")

    # 2. 모드 변경 (안전을 위해 STABILIZED 모드로 변경)
    # (Offboard 제어가 아니라 단순 시동 테스트이므로 기본 모드 사용)
    # custom_mode_id, custom_sub_mode_id 등은 펌웨어마다 다르지만
    # 여기서는 기본 Arming 명령만 보냅니다.

    # 3. 시동 걸기 (Arming)
    print("⚠️ Arming in 3 seconds... (Make sure PROPS ARE REMOVED!)")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    
    # 픽스호크의 안전 스위치(GPS에 달린 버튼)를 꾹 눌러서 LED가 빠르게 깜빡이거나 
    # 고정된 상태여야 시동이 걸립니다! (Pre-Arm Check)
    
    print("🚀 Sending ARM command!")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0) # param1=1 (Arm), param1=0 (Disarm)

    # 4. 결과 확인 (ACK 기다리기)
    print("Waiting for Arming confirmation...")
    ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack:
        print(f"Result: {ack.result}")
        if ack.result == 0:
            print("🎉 ARMING SUCCESS! Motors should be spinning.")
        else:
            print(f"❌ ARMING FAILED. Error code: {ack.result}")
            print("Tip: Check Safety Switch, Battery, or GPS Lock.")
    else:
        print("❌ No response from drone.")

    # 5. 5초 후 시동 끄기 (Disarm)
    time.sleep(5)
    print("\n🛑 Sending DISARM command...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0, 0, 0, 0, 0, 0, 0) # param1=0 (Disarm)
    
    print("Disarm command sent.")

if __name__ == '__main__':
    main()