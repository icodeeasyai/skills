---
name: seedance-1-5-pro-icodeeasy
description: Use when generating Seedance 1.5 Pro videos (doubao-seedance-1-5-pro) through iCodeEasy from text prompts, or explicitly invoking $seedance-1-5-pro-icodeeasy.
---

# Seedance 1.5 Pro · iCodeEasy

此入口固定使用 `doubao-seedance-1-5-pro`，通过 [doubao_seedance_1_5_pro.py](../icodeeasy-video-generations/scripts/doubao_seedance_1_5_pro.py) 创建任务。安装时同时安装 `icodeeasy-video-generations`，将脚本路径解析为实际绝对路径，从用户项目目录执行。

分辨率支持 480p、720p、1080p，时长 4–12 秒。默认 480p、9:16、4 秒。

此脚本提供文生视频。需要使用图片输入时，先核对当前脚本 `run --help` 和 [视频 API 文档](https://icodeeasy.ai/docs/video-generation/) 的能力。

默认开启音轨，可加 `--no-generate-audio` 关闭。比例可选 `16:9`、`4:3`、`1:1`、`3:4`、`9:16`、`21:9`。

先用下列命令离线预检。用户授权付费生成后，用 `--confirm-paid` 替换 `--dry-run`，并先创建输出目录。

```bash
python3 /absolute/path/to/icodeeasy-video-generations/scripts/doubao_seedance_1_5_pro.py --json run \
  --prompt "镜头跟随一艘灯船穿过清晨薄雾" --ratio 16:9 --duration 6 \
  --dry-run --output ./out/lantern.mp4
```

保存任务 ID 和幂等键。等待或下载中断时，用 [video_task.py](../icodeeasy-video-generations/scripts/video_task.py) 的 `poll TASK_ID --wait` 或 `download TASK_ID --output PATH` 恢复同一任务。提交结果不明时使用原请求与原幂等键重试。完成后交付本地视频绝对路径和实际型号。认证和恢复细节见 [视频 skill API 参考](../icodeeasy-video-generations/references/api.md)。
