import paho.mqtt.client as mqtt
import time

# --- 設定區 ---
# 請填入 Mosquitto Server 的 IP
BROKER_ADDRESS = "10.30.8.115"
PORT = 1883
TOPIC = "test/chat"

# 建立 Client 物件
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    client.connect(BROKER_ADDRESS, PORT, 60)
    # 啟動背景子執行緒處理網路傳輸 (非 blocking 模式)
    client.loop_start()
    
    print(f"已連線到 {BROKER_ADDRESS}")
    print("請輸入要發送的文字 (輸入 'exit' 或 'q' 離開):")

    while True:
        # 等待使用者輸入
        msg = input(">>> ")
        
        if msg.lower() in ["exit", "q"]:
            break
        
        # 發送訊息
        info = client.publish(TOPIC, msg)
        # info.wait_for_publish() # 如果需要確認送達再解開這行
        
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
    print("已斷線")