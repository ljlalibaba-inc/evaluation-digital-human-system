#!/usr/bin/env python3
import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-5271400b0b9b4277bc8409ce1461e615'

from master_digital_human import MasterDigitalHuman, TaskConfig

master = MasterDigitalHuman(config={
    'qwen_config': {
        'api_mode': 'dashscope',
        'api_key': 'sk-5271400b0b9b4277bc8409ce1461e615',
        'model': 'qwen-turbo'
    }
})

config = TaskConfig(
    name="千问DashScope测试",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1"],
        "scenarios": ["S1"],
        "categories": ["C5"]
    },
    cases_per_combination=1,
    dimensions=["accuracy", "timeliness"],
    delay_ms=100
)

execution = master.submit_task(config)

import time
while execution.status.value == "running":
    time.sleep(2)

print(f"\n任务状态: {execution.status.value}")
print(f"阶段数: {len(execution.stages)}")
for stage in execution.stages:
    print(f"  - {stage.name}: {stage.status.value}")
