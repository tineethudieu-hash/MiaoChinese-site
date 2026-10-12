# -*- coding: utf-8 -*-
# Tạo giọng đọc bằng ElevenLabs cho 57 âm của Bài 1 và tự đặt tên file đúng.
# Cách dùng:  pip install requests   rồi   python tao_audio_elevenlabs.py
# Kết quả: thư mục "audio_moi" — kéo thả vào thư mục audio/ trên GitHub (ghi đè file cũ).
import os, time, requests
ITEMS = [["好", "27e4fe4c3f.mp3"], ["你好", "440ee0853a.mp3"], ["五", "8f07f53d63.mp3"], ["八", "2142fb62fd.mp3"], ["大", "0889c34972.mp3"], ["不", "8fa7401e90.mp3"], ["口", "1e7b07e714.mp3"], ["白", "4a1ae3cda4.mp3"], ["女", "26bc84961c.mp3"], ["马", "7d39044ed6.mp3"], ["你好吗", "81bb3feccb.mp3"], ["白马", "c14d734dc0.mp3"], ["大马", "c5f13b882b.mp3"], ["好马", "69e9f8dbef.mp3"], ["不好", "46e6fb7ad6.mp3"], ["不大", "79fcbded16.mp3"], ["来", "4b1d6193e4.mp3"], ["北", "48c1462231.mp3"], ["狗", "2fcbe72fbf.mp3"], ["个", "f7b2a6ee68.mp3"], ["偷", "9b1ddb99d7.mp3"], ["刀", "c8f6dd0c32.mp3"], ["劳", "5148dd7acd.mp3"], ["喝", "9982c5ced1.mp3"], ["塔", "e8cf911a5c.mp3"], ["太", "d2ff8f7020.mp3"], ["妈", "e3918a99aa.mp3"], ["妮", "098bb0146d.mp3"], ["姨", "620e3674e5.mp3"], ["宝", "5cb2f5b86f.mp3"], ["屋", "dc675fde78.mp3"], ["带", "35d40b6e6f.mp3"], ["怕", "bc1c58b84b.mp3"], ["意", "9d197986e0.mp3"], ["打", "6919d5be90.mp3"], ["把", "b3ba7814f4.mp3"], ["拔", "737c389c6b.mp3"], ["掏", "bdc07925b8.mp3"], ["搞", "c075942cc6.mp3"], ["搭", "59c77cf6a9.mp3"], ["摆", "88fc5b4316.mp3"], ["无", "72077749f7.mp3"], ["椅", "618be2726b.mp3"], ["楼", "598e544138.mp3"], ["泥", "06859cc518.mp3"], ["爸", "a732e56e22.mp3"], ["牌", "265dc5ccb6.mp3"], ["物", "bea55d0635.mp3"], ["科", "dcedab2c4f.mp3"], ["考", "ed96d74c8a.mp3"], ["胎", "24ac196d5d.mp3"], ["腻", "85658ab4f5.mp3"], ["衣", "cb6d358425.mp3"], ["达", "49b39bc0a1.mp3"], ["雷", "deaefde2be.mp3"], ["骂", "6343706870.mp3"], ["麻", "433ea2216f.mp3"]]
API_KEY = input("Dán API key ElevenLabs (elevenlabs.io > avatar > API Keys): ").strip()
VOICE_ID = input("Dán Voice ID giọng muốn dùng (Voices > giọng > ID): ").strip()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_moi")
os.makedirs(OUT, exist_ok=True)
ok = 0
for text, fn in ITEMS:
    speed = 0.75 if len(text) >= 6 else 0.85
    for k in range(3):
        r = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID + "?output_format=mp3_44100_64",
            headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
            json={"text": text, "model_id": "eleven_multilingual_v2",
                  "voice_settings": {"stability": 0.6, "similarity_boost": 0.8, "speed": speed}}, timeout=60)
        if r.status_code == 200:
            open(os.path.join(OUT, fn), "wb").write(r.content); ok += 1
            print("OK", fn, text); break
        print("lỗi", r.status_code, r.text[:120]); time.sleep(3)
print("\nXong:", ok, "/", len(ITEMS), "file. Xem thư mục:", OUT)
