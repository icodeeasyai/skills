---
name: hunyuan-3d-icodeeasy
description: Use when generating 3D models from text or images with Hunyuan 3D 3.1 or Hunyuan 3D Express on iCodeEasy, or invoking $hunyuan-3d-icodeeasy.
---

# 混元 3D

通过 [共享 3D 任务脚本](../icodeeasy-3d-generations/scripts/model3d_task.py) 生成混元 GLB 文件。先读 [认证、报价与任务恢复](../icodeeasy-3d-generations/SKILL.md)，将脚本路径替换为实际绝对路径，从用户项目目录执行。

| 用户选择 | 请求 `model` | 输入与设置 |
| --- | --- | --- |
| 混元 3D 3.1 | `hy-3d-3.1` | 文字、单图、2–8 张多视图，`texture: false` |
| 混元 3D Express | `hy-3d-express` | 文字、单图，`texture: false`，省略 `options` |

保留用户指定的型号。仅指定混元 3D 时使用 `hy-3d-3.1`。先运行 `models` 检查当次可用输入，`prices.image.untextured` 为正数时开放单图，3.1 的 `prices.multiview.untextured` 为正数时开放多视图。

## 文字或图片生成

先创建 `./out/models/`，把生成请求保存为 `./out/models/hunyuan.json`。文字与图片每次选择一种输入。

```json
{"model":"hy-3d-3.1","prompt":"圆润的陶瓷茶壶，弯曲把手，清晰的壶嘴","texture":false}
```

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py models
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/hunyuan.json
mkdir -p ./out/models
task_key=$(python3 -c 'import uuid; print(uuid.uuid4())')
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/hunyuan.json --confirm-paid \
  --idempotency-key "$task_key" --output ./out/models/hunyuan.glb
```

用户明确要求生成时使用 `--confirm-paid`。离线预检使用 `run --request … --dry-run`。本地图片使用 `--image-file ./reference.png`，同时从 JSON 中删除 `prompt` 及其他输入字段，并在 `quote`、`run` 中传入同一图片。

公网单图使用 `image_url`。3.1 多视图使用 `image_views` 对象，`front` 必填，另选 `left`、`right`、`back`、`top`、`bottom`、`left_front`、`right_front`，总数 2–8 张，同一物体的左右前视角为 45°。每个值为公网 HTTPS 图片地址。

```json
{"model":"hy-3d-3.1","image_views":{"front":"https://example.com/front.png","left":"https://example.com/left.png"},"texture":false}
```

图片宽高各为 128–5000 像素。公网 URL 图片应最多 8 MiB，上传或 Base64 图片超过 8 MiB 时服务端会重新编码，最长边最多 1536 像素。

## 面数与交付

仅在 `models` 返回 `face_counts` 时，为 3.1 添加 `options.face_count`，可选值以响应为准。文档列出的值为 `50000`、`500000`、`1000000`、`1500000`，省略时默认 `500000`。改变面数后使用同一请求重新 `quote`，读取实际人民币报价。

`run` 等待并下载 GLB。中断后使用共享脚本的 `poll TASK_ID --wait` 与 `download TASK_ID --output ./out/models/hunyuan.glb` 恢复原任务，保留任务 ID 和幂等键。交付实际型号与本地文件绝对路径。

[混元 3D 3.1 文档](https://icodeeasy.ai/docs/hy-3d-3-1/) · [混元 3D Express 文档](https://icodeeasy.ai/docs/hy-3d-express/)
