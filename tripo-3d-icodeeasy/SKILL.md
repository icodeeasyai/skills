---
name: tripo-3d-icodeeasy
description: Use when generating 3D models from text, one image, or multiple views with Tripo H3.1, P1, or P2 on iCodeEasy, or invoking $tripo-3d-icodeeasy.
---

# Tripo 3D

通过 [共享 3D 任务脚本](../icodeeasy-3d-generations/scripts/model3d_task.py) 生成 Tripo GLB 或 FBX 文件。先读 [认证、报价与任务恢复](../icodeeasy-3d-generations/SKILL.md)，将脚本路径替换为实际绝对路径，从用户项目目录执行。

保留用户指定的型号。仅指定 Tripo 时使用 `tripo-h3.1`。`tripo-h3.1`、`tripo-p1`、`tripo-p2` 均支持文字、单图、2–4 张多视图。默认 `texture: false`，需要纹理时设为 `true`。

## 输入、报价与生成

先运行 `models` 查询当次模型与价格。创建 `./out/models/`，把生成请求保存为 `./out/models/tripo.json`，从 `prompt`、`image_url`、`image_base64`、`image_views` 中选择一种输入。

```json
{"model":"tripo-h3.1","prompt":"一只有圆耳朵的木雕小熊，站立姿态","texture":false,"options":{"face_limit":10000}}
```

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py models
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/tripo.json
mkdir -p ./out/models
task_key=$(python3 -c 'import uuid; print(uuid.uuid4())')
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/tripo.json --confirm-paid \
  --idempotency-key "$task_key" --output ./out/models/tripo.glb
```

用户明确要求生成时使用 `--confirm-paid`。离线预检使用 `run --request … --dry-run`。本地 PNG/JPEG 使用 `--image-file ./reference.png`，同时从 JSON 中删除其他输入字段，在 `quote`、`run` 中使用同一图片。

公网单图使用 `image_url`。多视图使用 `image_views` 对象，`front` 必填，另选 `left`、`right`、`back`，每个值为公网 HTTPS 图片地址。

```json
{"model":"tripo-h3.1","image_views":{"front":"https://example.com/front.png","right":"https://example.com/right.png"},"texture":true}
```

H3.1 图片宽高各为 256–5000 像素。上传或 Base64 图片超过 10 MiB 时服务端会重新编码，最长边最多 1536 像素。

## 型号选项

所有选项放入 `options`。变更后重新 `quote`，使用同一 `model`、输入模式、`texture` 和 `options` 的实际人民币报价。

| 型号 | `options` 与组合限制 |
| --- | --- |
| `tripo-p1` | `face_limit` 为 500–20000，省略时由模型决定 |
| `tripo-p2` | `face_limit` 为 500–50000。`delight: true` 要求图片输入与 `texture: true`。`quad: true` 输出 FBX，面数上限 25000 |
| `tripo-h3.1` | `face_limit` 为 500–1500000，`geometry_quality: "detailed"` 时上限 2000000。`enable_image_autofix: true` 只适用于单图。`texture_quality` 可为 `standard`、`detailed`、`extreme`，与 `pbr: true` 均要求 `texture: true` |

H3.1 的 `generate_parts: true` 要求 `texture: false`、关闭 PBR，与 `quad` 互斥，输出包含可编辑部件的 GLB。`quad: true` 输出 FBX，`face_limit` 上限 150000。

普通结果保存为 `.glb`。P2/H3.1 开启 `quad` 时将 `--output` 改为 `.fbx`。中断后使用共享脚本的 `poll TASK_ID --wait` 与 `download TASK_ID --output PATH` 恢复原任务，保留任务 ID 和幂等键。交付实际型号与本地文件绝对路径。

[Tripo H3.1 文档](https://icodeeasy.ai/docs/tripo-h3-1/) · [Tripo P1 文档](https://icodeeasy.ai/docs/tripo-p1/) · [Tripo P2 文档](https://icodeeasy.ai/docs/tripo-p2/)
