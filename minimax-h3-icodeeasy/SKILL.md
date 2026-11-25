---
name: minimax-h3-icodeeasy
description: Use when generating MiniMax H3 video through iCodeEasy from a prompt, a first frame, or first and last frames. Applies to the MiniMax-H3 video model.
---

# MiniMax H3 视频 · iCodeEasy

使用 [minimax_h3.py](../icodeeasy-video-generations/scripts/minimax_h3.py) 提交 `MiniMax-H3`。脚本随 `icodeeasy-video-generations` 一起安装。

- 纯文本用 `--prompt` 或 `--prompt-file`。首帧用 `--first-frame HTTPS_URL`，有尾帧时同时传 `--last-frame HTTPS_URL`。
- 分辨率支持 `768P`、`2K`，时长 4–15 秒，比例支持 `21:9`、`16:9`、`4:3`、`1:1`、`3:4`、`9:16`。默认 `768P`、`9:16`、5 秒。帧引导也使用上述固定比例。H3 没有公开生成音轨开关。详见 [MiniMax H3 API](https://icodeeasy.ai/docs/model-minimax-h3/)。

在用户项目目录执行，用安装后的绝对路径替换脚本路径。以下示例用于离线预检。得到付费授权后，用 `--confirm-paid` 替换 `--dry-run` 再提交。

```bash
python3 /absolute/path/to/icodeeasy-video-generations/scripts/minimax_h3.py --json run \
  --prompt "海浪拍打黑色礁石，镜头缓慢推近" --resolution 768P --ratio 16:9 \
  --dry-run --output ./out/coast.mp4
```

实际生成前创建输出目录。保存任务 ID 和幂等键。等待或下载中断时用 [video_task.py](../icodeeasy-video-generations/scripts/video_task.py) 的 `poll TASK_ID --wait` 或 `download TASK_ID --output PATH` 恢复。提交结果不明时，仅用同一请求和原幂等键重试。完成后交付视频的本地绝对路径。凭据和任务规则见 [视频 skill API 参考](../icodeeasy-video-generations/references/api.md)。
