---
name: hunyuan-3d-3-1-icodeeasy
description: Use when generating 3D models with Hunyuan 3D 3.1 (hy-3d-3.1) on iCodeEasy or invoking $hunyuan-3d-3-1-icodeeasy.
---

# 混元 3D 3.1

此入口固定使用 `hy-3d-3.1`。使用 [共享 3D 脚本](../icodeeasy-3d-generations/scripts/model3d_task.py)，并读取 [认证、报价与任务恢复](../icodeeasy-3d-generations/SKILL.md)。将脚本路径解析为安装后的绝对路径，从用户项目目录执行。

支持文字、单图及 2–8 张多视图。先运行 `models`，仅在 `prices.image.untextured` 或 `prices.multiview.untextured` 为正数时使用相应图片模式。固定 `texture: false`。

多视图使用 `image_views` 对象，`front` 必填，另选 `left`、`right`、`back`、`top`、`bottom`、`left_front`、`right_front`。左右前视角为 45°，每个值为同一物体的公网 HTTPS 图片地址。

图片宽高各为 128–5000 像素。公网 URL 图片应最多 8 MiB，上传或 Base64 图片超过 8 MiB 时服务端会重新编码，最长边最多 1536 像素。

仅在 `models` 返回 `face_counts` 时添加 `options.face_count`，以返回值为准。文档列出的面数为 `50000`、`500000`、`1000000`、`1500000`，省略时默认 `500000`。改变面数后重新报价。

先创建 `./out/models/`，将生成请求保存为 `./out/models/hy-3d-3-1.json`。每次选择一种输入，文字用 `prompt`，公网单图用 `image_url`。

```json
{"model":"hy-3d-3.1","prompt":"圆润的陶瓷茶壶，弯曲把手，清晰的壶嘴","texture":false}
```

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/hy-3d-3-1.json
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/hy-3d-3-1.json --dry-run --output ./out/models/hy-3d-3-1.glb
```

本地 PNG/JPEG 用 `--image-file ./reference.png`，同时从 JSON 中删除其他输入字段，在报价和生成时使用同一图片。实际生成获得付费授权后，用 `--confirm-paid` 替换 `--dry-run`，并保留请求、任务 ID 和幂等键。

中断后用共享脚本的 `poll TASK_ID --wait` 或 `download TASK_ID --output PATH` 恢复原任务。交付实际型号与本地文件绝对路径。

[模型 API 文档](https://icodeeasy.ai/docs/hy-3d-3-1/)
