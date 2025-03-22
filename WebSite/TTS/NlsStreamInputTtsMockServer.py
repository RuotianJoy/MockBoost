from enum import IntEnum
import os
import time
import json
import asyncio
import websockets
from urllib.parse import urlparse, parse_qs

# 此脚本模拟阿里云流式语音合成服务，用于开发者测试流式语音合成协议。
# 请将此服务运行并且调用成功后再切换到线上服务调试。

### constant
PROP_TTS_FORMAT = "format";
PROP_TTS_SAMPLE_RATE = "sample_rate";
PROP_TTS_TEXT = "text";
PROP_TTS_VOICE = "voice";
PROP_TTS_SPEECH_RATE = "speech_rate";
PROP_TTS_PITCH_RATE = "pitch_rate";
PROP_TTS_VOLUME = "volume";
PROP_TTS_METHOD = "method";
VALUE_NAMESPACE_TTS = "SpeechSynthesizer";
VALUE_NAMESPACE_LONG_TTS = "SpeechLongSynthesizer";
VALUE_NAMESPACE_STREAM_REALTIME_TTS = "FlowingSpeechSynthesizer";
VALUE_NAME_TTS_START = "StartSynthesis";
VALUE_NAME_TTS_STARTED = "SynthesisStarted";
VALUE_NAME_RUN_SYNTHESIS = "RunSynthesis"
VALUE_NAME_TTS_STOP = "StopSynthesis";
VALUE_SENTENCE_BGIN = "SentenceBegin";
VALUE_SENTENCE_SYNTHESIS = "SentenceSynthesis";
VALUE_SENTENCE_END = "SentenceEnd";
VALUE_NAME_TTS_COMPLETE = "SynthesisCompleted";

# get task failed response
def task_failed_response(reason):
    response = {
        "header": {
            "namespace": "Default",
            "name": "TaskFailed",
            "status": 40000000,
            "message_id": "mock_server_message_id********",
            "task_id": "mock_server_task_id********",
            "status_text": reason
        }
    }
    print(f'\033[91m[Send]: {response}\033[0m')
    print('\033[91m################ TASK_FAILED ################\033[0m')
    return json.dumps(response)

# get response by name
def response(request, name):
    response = {
        "header": {
            "message_id": "mock_server_message_id********",
            "task_id": request['header']['task_id'],
            "namespace": request['header']['namespace'],
            "name": name,
            "status": 20000000,
            "status_message": "GATEWAY|SUCCESS|Success.",
        },
        "payload": {
            "session_id": "sssssssss",
            "index": 1,
        }
    }
    print(f'[Send]: {response}')
    return json.dumps(response)


# get one frame audio data (random samples), you can use your own audio file 
# by the follow codes
'''
audio_data = open('test.wav', 'rb').read()
ptr = 0
def binary_audio_frame():
    global ptr, audio_data
    audio_frame = audio_data[ptr:ptr+8000]
    ptr += 8000
    ptr = ptr % len(audio_data)
    return audio_frame
'''
def binary_audio_frame():
    binary_data = os.urandom(100)
    print(f'[Send]: pcm')
    return binary_data

# get SentenceSynthesis response with timestamp
def sentence_synthesis_response(request, name):
    response = {
        "header": {
            "message_id": "mock_server_message_id********",
            "task_id": request['header']['task_id'],
            "namespace": request['header']['namespace'],
            "name": name,
            "status": 20000000,
            "status_message": "GATEWAY|SUCCESS|Success.",
        },
        "payload": {
            "subtitles": [
                {
                    "text": "",
                    "begin_time": 0,
                    "end_time": 0,
                    "begin_index": 0,
                    "end_index": 1,
                    "sentence": True,
                    "phoneme_list": []
                },
                {
                    "text": "今",
                    "begin_time": 0,
                    "end_time": 175,
                    "begin_index": 0,
                    "end_index": 1,
                    "sentence": False,
                    "phoneme_list": [
                        {
                            "begin_time": 0,
                            "end_time": 120,
                            "text": "j_c",
                            "tone": "1"
                        },
                        {
                            "begin_time": 120,
                            "end_time": 170,
                            "text": "in_c",
                            "tone": "1"
                        }
                    ]
                }
            ]
        }
    }
    print(f'[Send]: {response}')
    return json.dumps(response, ensure_ascii=False)


# get SentenceEnd response with timestamp
def sentence_end_response(request, name):
    response = {
        "header": {
            "message_id": "mock_server_message_id********",
            "task_id": request['header']['task_id'],
            "namespace": request['header']['namespace'],
            "name": name,
            "status": 20000000,
            "status_message": "GATEWAY|SUCCESS|Success.",
        },
        "payload": {
            "subtitles": [
                {
                    "text": "",
                    "begin_time": 0,
                    "end_time": 0,
                    "begin_index": 0,
                    "end_index": 1,
                    "sentence": True,
                    "phoneme_list": []
                },
                {
                    "text": "今",
                    "begin_time": 0,
                    "end_time": 175,
                    "begin_index": 0,
                    "end_index": 1,
                    "sentence": False,
                    "phoneme_list": [
                        {
                            "begin_time": 0,
                            "end_time": 120,
                            "text": "j_c",
                            "tone": "1"
                        },
                        {
                            "begin_time": 120,
                            "end_time": 170,
                            "text": "in_c",
                            "tone": "1"
                        }
                    ]
                },
                {
                    "text": "天",
                    "begin_time": 175,
                    "end_time": 320,
                    "begin_index": 1,
                    "end_index": 2,
                    "sentence": False,
                    "phoneme_list": [
                        {
                            "begin_time": 0,
                            "end_time": 120,
                            "text": "t_c",
                            "tone": "1"
                        },
                        {
                            "begin_time": 120,
                            "end_time": 170,
                            "text": "ian_c",
                            "tone": "1"
                        }
                    ]
                }
            ]
        }
    }
    print(f'[Send]: {response}')
    return json.dumps(response, ensure_ascii=False)


class status(IntEnum):
    Begin = 1
    Started = 2
    Completed = 3


# mock a tts server
async def echo(websocket, path):
    print('################ TASK START ################')
    # check if token in url
    parsed_url = urlparse(path)
    query_params = parse_qs(parsed_url.query)
    token = query_params.get('token', None)
    if token is None:
        # check the websocket header
        ws_headers = websocket.request_headers
        print('[Recv]: ws_headers', ws_headers)
        if 'X-NLS-Token' not in ws_headers:
            print('[Recv]: X-NLS-Token not found')
            await websocket.send(task_failed_response(" X-NLS-Token not found in ws header"))
            await websocket.close()
            return
    else:
        print('[Recv] token found in url: ', token)
    
    state = status.Begin
    task_id = None
    
    async for message in websocket:
        print('[Recv]: message', message)
        try:
            data = json.loads(message)
        except:
            await websocket.send(task_failed_response(f"Message Not Json: {message}"))
            await websocket.close()
            return
        # handle StartSynthesis
        if (VALUE_NAME_TTS_START == data['header']['name']):
            if (VALUE_NAMESPACE_STREAM_REALTIME_TTS == data['header']['namespace']):
                if state == status.Begin:
                    task_id = data['header']['task_id']
                    await websocket.send(response(data, VALUE_NAME_TTS_STARTED))
                    state = status.Started
                else:
                    await websocket.send(task_failed_response("[StartSynthesis] Connection already started"))
                    await websocket.close()
                    return
            else:
                await websocket.send(task_failed_response("Invalid namespace"))
                await websocket.close()
                return
        # handle RunSynthesis
        elif (VALUE_NAME_RUN_SYNTHESIS == data['header']['name']):
            if state == status.Started:
                if task_id != data['header']['task_id']:
                    await websocket.send(task_failed_response("[RunSynthesis] Task ID not match"))
                    await websocket.close()
                    return
                await websocket.send(response(data, VALUE_SENTENCE_BGIN))
                # simulate send audio frame
                for _ in range(2):
                    time.sleep(0.05)
                    await websocket.send(binary_audio_frame())
                    time.sleep(0.05)
                    await websocket.send(sentence_synthesis_response(data, VALUE_SENTENCE_SYNTHESIS))
                await websocket.send(sentence_end_response(data, VALUE_SENTENCE_END))
            else:
                await websocket.send(task_failed_response("[RunSynthesis] Connection not started or already stopped"))
                await websocket.close()                
                return
        # handle StopSynthesis
        elif (VALUE_NAME_TTS_STOP == data['header']['name']):
            if state == status.Started:
                if task_id != data['header']['task_id']:
                    await websocket.send(task_failed_response("[RunSynthesis] Task ID not match"))
                    await websocket.close()
                    return
                # simulate send audio frame
                for _ in range(2):
                    time.sleep(0.05)
                    await websocket.send(binary_audio_frame())
                    time.sleep(0.05)
                    await websocket.send(sentence_synthesis_response(data, VALUE_SENTENCE_SYNTHESIS))

                await websocket.send(response(data, VALUE_NAME_TTS_COMPLETE))
                state = status.Completed
                print('\033[92m################ TASK COMPLETE, SUCCESS ################\033[0m')
                await websocket.close()                
                return
            else:
                await websocket.send(task_failed_response("[StopSynthesis] Connection not started or already stopped"))
                await websocket.close()                
                return
        else:
            await websocket.send(task_failed_response(f'Invalid Message: {message}'))
            await websocket.close()            
            return

port = 12345
# default url: ws://127.0.0.1:12345

async def main():
    start_server = websockets.serve(echo, 'localhost', port, ping_interval=None)
    print('\033[92m< websocket server running at ws://127.0.0.1:{} >\033[0m'.format(port))
    await start_server
    # Keep the server running forever
    await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
