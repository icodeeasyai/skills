---
name: icodeeasy-video-generations
description: Use for iCodeEasy video task recovery, video models without a dedicated skill, or when explicitly invoking $icodeeasy-video-generations.
---

# iCodeEasy Video Generations

Create asynchronous video tasks through the iCodeEasy Video API. Use the model-specific Python command so its validation matches the selected model.

## Safe workflow

1. Choose the model and its exact script from [the API reference](references/api.md). Read the script's `--help` for its supported flags and combinations.
2. This API can create paid tasks. Confirm the user explicitly authorizes the paid API call, then pass `--confirm-paid`. Use `--dry-run` to inspect a request without a network call.
3. Prefer `run` when creating a task: it creates once, polls that same task, and can download with `--output`. Use `create` only when the caller will retain the task ID and poll later.
4. For an existing task, use `python3 scripts/video_task.py poll|download|delete`; do not create a duplicate task. A nonzero exit code may mean polling or downloading failed, even when generation succeeded. Check `error.stage`, `status`, `task_id`, and `recovery_action` before explaining the result.

When a task ID has been returned, a polling 404, timeout, or download error does not establish that generation failed. Retain that ID and retry the existing task. If `status` is `succeeded` and `error.stage` is `download`, tell the user the video was generated and only retrieval failed; use `video_task.py download` again. Report a confirmed generation failure only when the task response has `status: failed`. Successful videos can also be recovered from the API Key owner's [usage details](https://icodeeasy.ai/dashboard/logs/).

Credentials are read from `ICODEEASY_API_KEY`, then `OPENAI_API_KEY` and `ANTHROPIC_AUTH_TOKEN`. Do not print, save, or commit keys. Public HTTPS reference URLs are accepted where that model's help says they are supported.

## Example

Preview the request offline. After the user authorizes a paid generation, replace `--dry-run` with `--confirm-paid`.

```bash
mkdir -p ./out
python3 scripts/doubao_seedance_2_5.py run \
  --dry-run \
  --prompt "A lantern boat crossing a misty lake at dawn" \
  --output ./out/lake.mp4
```

If submission status is uncertain, retain the task ID and idempotency key, then retry only with the same `--idempotency-key`. Read [references/api.md](references/api.md) for task lifecycle, idempotency, and error handling.
