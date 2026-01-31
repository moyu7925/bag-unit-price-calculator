import requests
import json

url = 'https://api.github.com/repos/moyu7925/bag-unit-price-calculator/actions/runs/21542986681'
headers = {'Accept': 'application/vnd.github.v3+json'}

try:
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"状态: {data.get('status')}")
        print(f"结果: {data.get('conclusion')}")
        print(f"开始时间: {data.get('created_at')}")
        print(f"结束时间: {data.get('updated_at')}")

        # 获取jobs信息
        jobs_url = data.get('jobs_url', '')
        if jobs_url:
            r2 = requests.get(jobs_url, headers=headers, timeout=30)
            if r2.status_code == 200:
                jobs = r2.json().get('jobs', [])
                for job in jobs:
                    print(f"\nJob: {job.get('name')}")
                    print(f"  状态: {job.get('status')}")
                    print(f"  结论: {job.get('conclusion')}")
                    steps = job.get('steps', [])
                    for step in steps:
                        if step.get('conclusion') == 'failure':
                            print(f"  失败步骤: {step.get('name')}")
                            print(f"    结论: {step.get('conclusion')}")
    else:
        print(f'状态码: {r.status_code}')
except Exception as e:
    print(f'错误: {e}')
