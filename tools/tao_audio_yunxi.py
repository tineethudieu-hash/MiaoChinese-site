# -*- coding: utf-8 -*-
# Tạo giọng đọc Yunxi (Microsoft Edge) cho Bài 1 — chạy trên máy của cô.
# Cách dùng:  pip install edge-tts   rồi   python tao_audio_yunxi.py
# Kết quả: thư mục "audio_moi" gồm các file .mp3 — kéo thả vào thư mục audio/ trên GitHub (ghi đè file cũ).
import asyncio, os, shutil, subprocess, tempfile
import edge_tts
VOICE = "zh-CN-YunxiNeural"
ITEMS = [["好", "27e4fe4c3f.mp3", "-15%"], ["你好！", "440ee0853a.mp3", "-15%"], ["五", "8f07f53d63.mp3", "-15%"], ["八", "2142fb62fd.mp3", "-15%"], ["大", "0889c34972.mp3", "-15%"], ["不", "8fa7401e90.mp3", "-15%"], ["口", "1e7b07e714.mp3", "-15%"], ["白", "4a1ae3cda4.mp3", "-15%"], ["女", "26bc84961c.mp3", "-15%"], ["马", "7d39044ed6.mp3", "-15%"], ["你好吗？", "81bb3feccb.mp3", "-15%"], ["白马", "c14d734dc0.mp3", "-15%"], ["大马", "c5f13b882b.mp3", "-15%"], ["好马", "69e9f8dbef.mp3", "-15%"], ["不好", "46e6fb7ad6.mp3", "-15%"], ["不大", "79fcbded16.mp3", "-15%"], ["来", "4b1d6193e4.mp3", "-15%"], ["北", "48c1462231.mp3", "-15%"], ["狗", "2fcbe72fbf.mp3", "-15%"], ["个", "f7b2a6ee68.mp3", "-15%"], ["偷", "9b1ddb99d7.mp3", "-15%"], ["刀", "c8f6dd0c32.mp3", "-15%"], ["劳", "5148dd7acd.mp3", "-15%"], ["喝", "9982c5ced1.mp3", "-15%"], ["塔", "e8cf911a5c.mp3", "-15%"], ["太", "d2ff8f7020.mp3", "-15%"], ["妈", "e3918a99aa.mp3", "-15%"], ["妮", "098bb0146d.mp3", "-15%"], ["姨", "620e3674e5.mp3", "-15%"], ["宝", "5cb2f5b86f.mp3", "-15%"], ["屋", "dc675fde78.mp3", "-15%"], ["带", "35d40b6e6f.mp3", "-15%"], ["怕", "bc1c58b84b.mp3", "-15%"], ["意", "9d197986e0.mp3", "-15%"], ["打", "6919d5be90.mp3", "-15%"], ["把", "b3ba7814f4.mp3", "-15%"], ["拔", "737c389c6b.mp3", "-15%"], ["掏", "bdc07925b8.mp3", "-15%"], ["搞", "c075942cc6.mp3", "-15%"], ["搭", "59c77cf6a9.mp3", "-15%"], ["摆", "88fc5b4316.mp3", "-15%"], ["无", "72077749f7.mp3", "-15%"], ["椅", "618be2726b.mp3", "-15%"], ["楼", "598e544138.mp3", "-15%"], ["泥", "06859cc518.mp3", "-15%"], ["爸", "a732e56e22.mp3", "-15%"], ["牌", "265dc5ccb6.mp3", "-15%"], ["物", "bea55d0635.mp3", "-15%"], ["科", "dcedab2c4f.mp3", "-15%"], ["考", "ed96d74c8a.mp3", "-15%"], ["胎", "24ac196d5d.mp3", "-15%"], ["腻", "85658ab4f5.mp3", "-15%"], ["衣", "cb6d358425.mp3", "-15%"], ["达", "49b39bc0a1.mp3", "-15%"], ["雷", "deaefde2be.mp3", "-15%"], ["骂", "6343706870.mp3", "-15%"], ["麻", "433ea2216f.mp3", "-15%"]]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_moi")
os.makedirs(OUT, exist_ok=True)
FF = shutil.which("ffmpeg")
async def one(sem, text, fn, rate):
    async with sem:
        for k in range(5):
            try:
                tmp = tempfile.mktemp(suffix=".mp3")
                await asyncio.wait_for(edge_tts.Communicate(text, VOICE, rate=rate).save(tmp), 40)
                out = os.path.join(OUT, fn)
                if FF:
                    subprocess.run([FF, "-loglevel", "error", "-y", "-i", tmp, "-af",
                        "loudnorm=I=-23:TP=-2:LRA=11,adelay=250|250,apad=pad_dur=0.45",
                        "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "48k", out], check=True)
                    os.remove(tmp)
                else:
                    shutil.move(tmp, out)
                print("OK", fn, text); return True
            except Exception as e:
                print("thử lại", fn, str(e)[:60]); await asyncio.sleep(3)
        print("LỖI", fn, text); return False
async def main():
    sem = asyncio.Semaphore(3)
    r = await asyncio.gather(*[one(sem, t, f, rt) for t, f, rt in ITEMS])
    print("\nXong:", sum(r), "/", len(r), "file. Xem thư mục:", OUT)
asyncio.run(main())
