---
name: seedance-icodeeasy
description: Use when creating Seedance videos through iCodeEasy, including Seedance 2.5, 2.5 Flash, 2.0 variants, and 1.5 Pro, from text, frames, or supported reference videos.
---

# Seedance · iCodeEasy

按用户指定的版本选脚本。只说 Seedance 时使用 2.5。脚本和 [任务恢复工具](../icodeeasy-video-generations/scripts/video_task.py) 随 `icodeeasy-video-generations` 一起安装。

| 版本 | 请求模型 ID | 脚本 |
| --- | --- | --- |
| 2.5 | `doubao-seedance-2.5` | [doubao_seedance_2_5.py](../icodeeasy-video-generations/scripts/doubao_seedance_2_5.py) |
| 2.5 Flash | `doubao-seedance-2-5-flash` | [doubao_seedance_2_5_flash.py](../icodeeasy-video-generations/scripts/doubao_seedance_2_5_flash.py) |
| 2.0 | `doubao-seedance-2.0` | [doubao_seedance_2_0.py](../icodeeasy-video-generations/scripts/doubao_seedance_2_0.py) |
| 2.0 Fast | `doubao-seedance-2.0-fast` | [doubao_seedance_2_0_fast.py](../icodeeasy-video-generations/scripts/doubao_seedance_2_0_fast.py) |
| 2.0 Mini | `doubao-seedance-2.0-mini` | [doubao_seedance_2_0_mini.py](../icodeeasy-video-generations/scripts/doubao_seedance_2_0_mini.py) |
| 1.5 Pro | `doubao-seedance-1-5-pro` | [doubao_seedance_1_5_pro.py](../icodeeasy-video-generations/scripts/doubao_seedance_1_5_pro.py) |

2.5 和 2.5 Flash 支持 480p、720p 和 4–30 秒。文生默认 480p、9:16、4 秒并开启音轨，可用 `--no-generate-audio` 关闭。其他版本用所选脚本的 `run --help` 核对规格。

- 首帧用 `--first-frame HTTPS_URL`，首尾帧再加 `--last-frame HTTPS_URL`。2.5 和 2.5 Flash 的帧引导模式省略 `--ratio` 或设为 `adaptive`。想要固定画幅时先裁剪首帧。
- 2.5 和 2.5 Flash 的参考视频模式用可重复的 `--reference-video HTTPS_URL`，分别最多 10 段和 5 段。每段 MP4/MOV 2–30 秒，合计最多 30 秒，可同时用 `--reference-image HTTPS_URL` 提供最多两张普通参考图。按传入顺序在提示词里写 `@Video1`、`@Video2`。此模式可以设固定比例。格式限制和输入、输出计费规则见 [视频生成 API](https://icodeeasy.ai/docs/video-generation/)。

在用户项目目录执行，用安装后的绝对路径替换脚本路径。以下示例用于离线预检。得到付费授权后，用 `--confirm-paid` 替换 `--dry-run` 再提交。

```bash
python3 /absolute/path/to/icodeeasy-video-generations/scripts/doubao_seedance_2_5_flash.py --json run \
  --prompt "镜头跟随一艘灯船穿过清晨薄雾" --ratio 16:9 --duration 6 \
  --dry-run --output ./out/lantern.mp4
```

实际生成前创建输出目录。提交成功后保存任务 ID 和幂等键，查询或下载中断时用 `video_task.py poll TASK_ID --wait` 或 `video_task.py download TASK_ID --output PATH` 恢复。提交结果不明时，仅用同一请求和原幂等键重试。完成后交付视频的本地绝对路径和实际型号。凭据、错误和下载规则见 [视频 skill API 参考](../icodeeasy-video-generations/references/api.md)。
