---
name: tripo-p1-icodeeasy
description: Use when generating 3D models with Tripo P1 (tripo-p1) on iCodeEasy or invoking $tripo-p1-icodeeasy.
---

# Tripo P1

此入口固定使用 `tripo-p1`。使用 [共享 3D 脚本](../icodeeasy-3d-generations/scripts/model3d_task.py)，并读取 [认证、报价与任务恢复](../icodeeasy-3d-generations/SKILL.md)。将脚本路径解析为安装后的绝对路径，从用户项目目录执行。

支持文字、单图及 2–4 张多视图。默认 `texture: false`，需要纹理时设为 `true`。多视图使用 `image_views` 对象，`front` 必填，另选 `left`、`right`、`back`，每个值为公网 HTTPS 图片地址。

`options.face_limit` 可选 500–20000，省略时由模型决定。上传或 Base64 图片超过 10 MiB 时服务端会重新编码，最长边最多 1536 像素。结果保存为 GLB。

先创建 `./out/models/`，将生成请求保存为 `./out/models/tripo-p1.json`。每次选择一种输入，文字用 `prompt`，公网单图用 `image_url`。

```json
{"model":"tripo-p1","prompt":"圆润的陶瓷茶壶，弯曲把手，清晰的壶嘴","texture":false,"options":{"face_limit":10000}}
```

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/tripo-p1.json
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/tripo-p1.json --dry-run --output ./out/models/tripo-p1.glb
```

本地 PNG/JPEG 用 `--image-file ./reference.png`，同时从 JSON 中删除其他输入字段，在报价和生成时使用同一图片。实际生成获得付费授权后，用 `--confirm-paid` 替换 `--dry-run`，并保留请求、任务 ID 和幂等键。

中断后用共享脚本的 `poll TASK_ID --wait` 或 `download TASK_ID --output PATH` 恢复原任务。交付实际型号与本地文件绝对路径。

[模型 API 文档](https://icodeeasy.ai/docs/tripo-p1/)
