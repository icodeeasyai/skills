---
name: hunyuan-3d-express-icodeeasy
description: Use when generating 3D models with Hunyuan 3D Express (hy-3d-express) on iCodeEasy or invoking $hunyuan-3d-express-icodeeasy.
---

# 混元 3D Express

此入口固定使用 `hy-3d-express`。使用 [共享 3D 脚本](../icodeeasy-3d-generations/scripts/model3d_task.py)，并读取 [认证、报价与任务恢复](../icodeeasy-3d-generations/SKILL.md)。将脚本路径解析为安装后的绝对路径，从用户项目目录执行。

支持文字或单张图片。先运行 `models`，仅在 `prices.image.untextured` 为正数时使用图片模式。固定 `texture: false`，省略 `options`。

图片宽高各为 128–5000 像素。公网 URL 图片应最多 8 MiB，上传或 Base64 图片超过 8 MiB 时服务端会重新编码，最长边最多 1536 像素。

先创建 `./out/models/`，将生成请求保存为 `./out/models/hy-3d-express.json`。每次选择一种输入，文字用 `prompt`，公网单图用 `image_url`。

```json
{"model":"hy-3d-express","prompt":"圆润的陶瓷茶壶，弯曲把手，清晰的壶嘴","texture":false}
```

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/hy-3d-express.json
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/hy-3d-express.json --dry-run --output ./out/models/hy-3d-express.glb
```

本地 PNG/JPEG 用 `--image-file ./reference.png`，同时从 JSON 中删除其他输入字段，在报价和生成时使用同一图片。实际生成获得付费授权后，用 `--confirm-paid` 替换 `--dry-run`，并保留请求、任务 ID 和幂等键。

中断后用共享脚本的 `poll TASK_ID --wait` 或 `download TASK_ID --output PATH` 恢复原任务。交付实际型号与本地文件绝对路径。

[模型 API 文档](https://icodeeasy.ai/docs/hy-3d-express/)
