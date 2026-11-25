---
name: tripo-h3-1-icodeeasy
description: Use when generating 3D models with Tripo H3.1 (tripo-h3.1) on iCodeEasy or invoking $tripo-h3-1-icodeeasy.
---

# Tripo H3.1

此入口固定使用 `tripo-h3.1`。使用 [共享 3D 脚本](../icodeeasy-3d-generations/scripts/model3d_task.py)，并读取 [认证、报价与任务恢复](../icodeeasy-3d-generations/SKILL.md)。将脚本路径解析为安装后的绝对路径，从用户项目目录执行。

支持文字、单图及 2–4 张多视图。默认 `texture: false`，需要纹理时设为 `true`。多视图使用 `image_views` 对象，`front` 必填，另选 `left`、`right`、`back`，每个值为公网 HTTPS 图片地址。

图片宽高各为 256–5000 像素。上传或 Base64 图片超过 10 MiB 时服务端会重新编码，最长边最多 1536 像素。

选项放入 `options`。`face_limit` 为 500–1500000，`geometry_quality: "detailed"` 时上限为 2000000。`enable_image_autofix: true` 只适用于单图。`texture_quality` 可为 `standard`、`detailed`、`extreme`，与 `pbr: true` 均要求 `texture: true`。

`generate_parts: true` 要求 `texture: false`、关闭 PBR，与 `quad` 互斥，输出包含可编辑部件的 GLB。`quad: true` 输出 FBX，`face_limit` 上限为 150000，此时将输出文件名改为 `.fbx`。

先创建 `./out/models/`，将生成请求保存为 `./out/models/tripo-h3-1.json`。每次选择一种输入，文字用 `prompt`，公网单图用 `image_url`。

```json
{"model":"tripo-h3.1","prompt":"圆润的陶瓷茶壶，弯曲把手，清晰的壶嘴","texture":false,"options":{"face_limit":10000}}
```

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/tripo-h3-1.json
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/tripo-h3-1.json --dry-run --output ./out/models/tripo-h3-1.glb
```

本地 PNG/JPEG 用 `--image-file ./reference.png`，同时从 JSON 中删除其他输入字段，在报价和生成时使用同一图片。实际生成获得付费授权后，用 `--confirm-paid` 替换 `--dry-run`，并保留请求、任务 ID 和幂等键。

中断后用共享脚本的 `poll TASK_ID --wait` 或 `download TASK_ID --output PATH` 恢复原任务。交付实际型号与本地文件绝对路径。

[模型 API 文档](https://icodeeasy.ai/docs/tripo-h3-1/)
