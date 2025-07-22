import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

ETERNAL_RETURN_API_BASE = "https://open-api.bser.io"
ETERNAL_RETURN_API_KEY = os.getenv('EternalReturn_API_KEY')

async def test_api():
    print(f"API 키: {ETERNAL_RETURN_API_KEY[:10]}...")
    
    async with aiohttp.ClientSession() as session:
        # 다양한 헤더 형식 테스트
        headers_list = [
            {
                'x-api-key': ETERNAL_RETURN_API_KEY,
                'Accept': 'application/json'
            },
            {
                'X-API-KEY': ETERNAL_RETURN_API_KEY,
                'Accept': 'application/json'
            },
            {
                'Authorization': f'Bearer {ETERNAL_RETURN_API_KEY}',
                'Accept': 'application/json'
            },
            {
                'apikey': ETERNAL_RETURN_API_KEY,
                'Accept': 'application/json'
            }
        ]
        
        # 여러 헤더 형식으로 테스트
        for i, headers in enumerate(headers_list):
            print(f"=== 헤더 형식 {i+1} 테스트 ===")
            print(f"헤더: {headers}")
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/user/nickname"
            params = {'query': '모묘모'}
            print(f"요청 URL: {url}")
            print(f"파라미터: {params}")
            
            try:
                async with session.get(url, headers=headers, params=params, timeout=10) as response:
                    print(f"응답 상태: {response.status}")
                    text = await response.text()
                    print(f"응답 내용: {text}")
                    
                    if response.status == 200:
                        print("✅ 성공! 이 헤더 형식을 사용하세요.")
                        break
                    elif response.status == 429:
                        print("⚠️ Rate limit 초과, 잠시 기다려주세요.")
                    
            except Exception as e:
                print(f"요청 중 오류: {e}")
            
            # 각 테스트 사이에 rate limit 대기
            if i < len(headers_list) - 1:  # 마지막이 아니면
                print("다음 테스트를 위해 1초 대기...")
                await asyncio.sleep(1.1)
                print()
        
        # 메타데이터도 간단히 테스트
        print(f"\n=== 메타데이터 테스트 (첫 번째 헤더 사용) ===")
        meta_url = f"{ETERNAL_RETURN_API_BASE}/v1/data/Character"
        print(f"요청 URL: {meta_url}")
        
        try:
            await asyncio.sleep(1.1)  # rate limit 대기
            async with session.get(meta_url, headers=headers_list[0], timeout=10) as response:
                print(f"메타데이터 응답 상태: {response.status}")
                text = await response.text()
                print(f"메타데이터 응답 내용: {text[:200]}...")
                    
        except Exception as e:
            print(f"메타데이터 요청 중 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())