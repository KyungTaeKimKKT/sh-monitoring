import requests
import time
import concurrent.futures
# 쓰레드 풀 생성
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

LOKI_URL = 'http://loki.logging.sh/loki/api/v1/push'

def get_stream(
    job:str="PyQt6-Logger", 
    app:str="test-logger", 
    user:str="shinwoohipo", 
    host:str="localhost",
    message:str="test-message"
) -> dict:
    """
    Get stream data for Loki
    
    :param job: Job name
    :param app: Application name
    :param user: User name
    :param host: Host name
    :param message: Message
    :return: Stream data
    """
    timestamp = str(int(time.time() * 1e9))
    return [
        {
            "stream": {
                "job": job,
                "app": app,
                "user": user,
                "host": host
            },
            "values": [
                [timestamp, message]
            ]
        }
    ]

def send_log_to_loki(streams):
    try:
        response = requests.post(LOKI_URL, json={"streams": streams}, timeout=2)
        response.raise_for_status()
        print("로그 전송 성공:", response.text)
        # 성공 여부 무시하거나 로깅할 수 있음
    except Exception as e:
        print("로그 전송 실패:", e)

def logging_loki_async(streams:list):
    executor.submit(send_log_to_loki, streams)

def logging_loki(msg:str):    
    try:
        response = requests.post(LOKI_URL, json={"streams": get_stream(message=msg)})
        response.raise_for_status()
        print("로그 전송 성공:", response.text)
    except requests.exceptions.RequestException as e:
        print("로그 전송 실패:", e)

# 사용 예제
if __name__ == "__main__":
    for i in range(20):
        s = time.perf_counter()
        # logging_loki(msg=f"test-message {i}")
        logging_loki_async(streams=get_stream(message=f"test-message {i}"))
        e = time.perf_counter()
        print(f"소요시간: { int(1000 * (e - s))} milliseconds")
        time.sleep(0.1)


    # 모든 비동기 요청이 끝날 때까지 기다리기
    executor.shutdown(wait=True)