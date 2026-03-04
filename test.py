
import dashscope
import os
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
print(f'API Key: {dashscope.api_key[:10]}...' if dashscope.api_key else 'No API Key')
resp = dashscope.Generation.call(model='qwen-max', prompt='Hello')

print(f'Status: {resp.status_code if hasattr(resp, "status_code") else "N/A"}')
print(f'Code: {getattr(resp, "code", "N/A")}')
print(f'Message: {getattr(resp, "message", "N/A")}')
print(f'Output: {resp.output if hasattr(resp, "output") else "N/A"}')
(flora) PS E:\Data\Flora-evaluation>   $env:COOP_EVAL_EXECUTION="1"; $env:PYTHONPATH="."; python coop_eval_actual/run_experiment.py --max_tasks 1
