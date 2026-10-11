import asyncio, subprocess, edge_tts, os
os.makedirs("audio/demo", exist_ok=True)
V={'xiaoxiao':'zh-CN-XiaoxiaoNeural','xiaoyi':'zh-CN-XiaoyiNeural','yunxi':'zh-CN-YunxiNeural','yunjian':'zh-CN-YunjianNeural'}
T={'1':'今天下雨我打的去上班','2':'林老师教我们阅读和听力','3':'我去邮局寄包裹顺便去书店买一本书','4':'银行'}
async def main():
    for v,n in V.items():
        for k,t in T.items():
            tmp='/tmp/d.mp3'
            try:
              await edge_tts.Communicate(t.replace('打的','打滴').replace('教我们','交我们'),n,rate='-15%').save(tmp)
              subprocess.run(['ffmpeg','-loglevel','error','-y','-i',tmp,'-af','loudnorm=I=-23:TP=-2','-ar','24000','-ac','1','-b:a','48k',f'audio/demo/{v}{k}.mp3'],check=True)
            except Exception as e: print('FAIL',v,k,repr(e),flush=True)
asyncio.run(main())
