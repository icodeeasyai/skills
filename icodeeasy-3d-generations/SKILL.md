---
name: icodeeasy-3d-generations
description: Use for iCodeEasy 3D model discovery, quoting, or task recovery, or when explicitly invoking $icodeeasy-3d-generations.
---

# iCodeEasy 3D Generations

使用 [3D 任务脚本](scripts/model3d_task.py) 查询模型、报价、生成并下载 3D 文件。将脚本路径解析为绝对路径，从用户项目目录执行。用 `models` 核对用户指定型号的请求 ID 与可用参数。

认证依次读取 `ICODEEASY_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_AUTH_TOKEN`。使用账户 API Key，模型专用 Key 会返回 `403`。默认 API 为 `https://api.icodeeasy.ai`，备用域名为 `https://jp.icodeeasy.ai` 和 `https://sg.icodeeasy.ai`。不要输出或写入密钥。

## 选择输入与报价

先运行 `models`，从响应的 `data` 查询当前模型与输入模式。JSON 生成请求包含 `model`，并从 `prompt`、`image_url`、`image_base64`、`image_views` 中选择一种输入。文字最多 1024 个 Unicode 字符，图片 URL 使用公开可访问的 HTTPS 地址。

先创建 `./out/models/`，把请求保存到其中的 JSON 文件。`--request -` 也可从标准输入读取。`--image-file` 会读取本地 PNG/JPEG，使用它时请求 JSON 只保留型号、纹理及选项，省略其他输入字段。Base64 解码后的图片最多 60 MiB。完整图片和模型限制见对应官方文档。

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py models
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py quote \
  --request ./out/models/request.json
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/request.json --dry-run
```

`quote` 从同一生成请求推导 `mode`，携带相同的 `model`、`texture` 和 `options`。读取实际 `price_rmb`，查询报价不会创建任务。`--dry-run` 可离线预检，无需密钥。

## 生成与恢复

用户明确要求生成 3D 模型时，可使用 `--confirm-paid` 提交付费任务。只查询能力、参数或价格时使用 `models`、`quote` 或离线预检。创建前生成并保留一个唯一幂等键，最长 128 字节。一个键对应一次预期生成。

```bash
mkdir -p ./out/models
task_key=$(python3 -c 'import uuid; print(uuid.uuid4())')
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py run \
  --request ./out/models/request.json --confirm-paid \
  --idempotency-key "$task_key" --output ./out/models/model.glb
```

`run` 创建一次并等待同一任务，可用 `--interval 5 --max-wait 900` 调整等待。需要稍后等待时用 `create`，保留创建响应顶层的 `id`。命令输出 JSON，记录任务 ID、幂等键与请求文件以便恢复。提交结果不确定时，用相同请求和相同幂等键重试。

```bash
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py poll TASK_ID --wait
python3 /absolute/path/to/icodeeasy-3d-generations/scripts/model3d_task.py download TASK_ID \
  --output ./out/models/model.glb
```

`poll TASK_ID` 单次读取状态，`--wait` 持续等待。`queued`、`processing` 继续等待，`completed` 后下载 `asset_url`，预览图可从 `preview_url` 获取。普通结果为 GLB，Tripo P2/H3.1 的 `quad: true` 结果为 FBX，输出文件使用对应扩展名。文件已存在时选择新路径，用户授权覆盖时才添加 `--overwrite`。

轮询超时、`404` 或下载失败后继续查询原任务。签名链接过期时重新查询获取新链接，下载签名资源时省略账户认证。`failed` 是确认失败，`submission_unknown` 需要人工核对。两者均保留任务信息，后者先核对再决定是否新建任务。

交付时提供下载文件的本地绝对路径、实际型号和已返回的最终费用。仅在实际打开或渲染检查后描述模型的外观、拓扑或游戏可用性。

[官方 3D API 文档](https://icodeeasy.ai/docs/3d-generation/)
