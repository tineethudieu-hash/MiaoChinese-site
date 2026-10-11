import asyncio, subprocess, edge_tts, os
os.makedirs("audio/demo", exist_ok=True)
S="我去邮局寄包裹顺便去书店买一本书"
V={'a':('顺便',None),'b':('顺变',None),'c':('顺便。',None),'d':('顺便',S),'e':('顺变',S),'f':('顺便',S)}
async def main():
    for k,t in [('a','顺便'),('b','顺变'),('c','顺便。'),('d',S),('e',S.replace('顺便','顺变')),('f',S.replace('顺便','顺 便').replace(' ',''))]:
        for r in ['-15%','-5%']:
            try:
                await edge_tts.Communicate(t,'zh-CN-YunxiNeural',rate=r).save('/tmp/d.mp3')
                subprocess.run(['ffmpeg','-loglevel','error','-y','-i','/tmp/d.mp3','-af','loudnorm=I=-23:TP=-2','-ar','24000','-ac','1','-b:a','48k',f'audio/demo/sb_{k}{r[1:-1]}.mp3'],check=True)
            except Exception as e: print('FAIL',k,r,e)
asyncio.run(main())
