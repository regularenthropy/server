import asyncio

from googlesearch import search as google

async def get_from_google(query):
    result = []
    _google_result = google(query, lang="ja", advanced=True)
    for r in _google_result:
        _google_result_dict = {'url': r.url, 'title': r.title, 'context': r.description}
        result.append(_google_result_dict)

    return result

async def get_from_goo(query):
    await asyncio.sleep(10)  # 遅延をシミュレート
    return [{'url': "aaa", 'title': "あああああ", 'context': "ああああああ"}, {'url': "bbb", 'title': "bbbbbbb", 'context': "aaaaa"}]

async def get_from_neeva(query):
    await asyncio.sleep(2)  # 遅延をシミュレート
    return [{'url': "aaa", 'title': "あああああ", 'context': "ああああああ"}, {'url': "bbb", 'title': "bbbbbbb", 'context': "aaaaa"}]

async def get_result_from_external_engines():
    tasks = []
    query = "systemd"
    
    # 複数の関数を非同期で実行するため、タスクを生成する
    tasks.append(asyncio.create_task(get_from_google(query)))
    tasks.append(asyncio.create_task(get_from_goo(query)))
    
    # 非同期で複数の関数を実行し、結果を待つ
    results = await asyncio.gather(*tasks)
    
    # リストをマージ
    return [item for sublist in results for item in sublist]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    merged_data = loop.run_until_complete(get_result_from_external_engines())
    print(merged_data)

