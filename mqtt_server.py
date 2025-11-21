import paho.mqtt.client as mqtt

# --- 設定區 ---
# 如果接收端跟 Mosquitto 在同一台電腦，用 "localhost"
# 如果是不同電腦，請填 Mosquitto 那台的 IP (例如 "192.168.1.10")
BROKER_ADDRESS = "10.30.8.115" 
PORT = 1883
TOPIC = "test/chat"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"已連線到 Broker (Result: {reason_code})")
    # 連線成功後馬上訂閱 Topic
    client.subscribe(TOPIC)
    print(f"正在監聽 Topic: {TOPIC} ...")

def on_message(client, userdata, msg):
    # 收到訊息時執行的動作
    try:
        message = msg.payload.decode('utf-8')
        print(f"收到訊息: {message}")
    except Exception as e:
        print(f"解碼失敗: {e}")

# 建立 Client 物件 (使用新的 API 版本)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# 設定回呼函式
client.on_connect = on_connect
client.on_message = on_message

try:
    # 開始連線
    client.connect(BROKER_ADDRESS, PORT, 60)
    # 保持連線並持續監聽 (這行會讓程式一直跑，直到你按 Ctrl+C)
    client.loop_forever()
except KeyboardInterrupt:
    print("程式結束")