# Ice Skills

Codex skills for local workflows.

中文版本: [README.md](README.md)

Skills install into `~/.codex/skills/`. The commands below use `curl` and `tar`.

## Skills

### Image generation

Choose a skill by model and output format, then describe the result you want.

| Model and output | Skill |
| --- | --- |
| Image 2 | [image2-icodeeasy](image2-icodeeasy/SKILL.md) |
| Image 2.5 static images | [Flare](image25-flare-icodeeasy/SKILL.md) · [Sunburst](image25-sunburst-icodeeasy/SKILL.md) |
| Image 2.6 static images | [Flare](image26-flare-icodeeasy/SKILL.md) · [Sunburst](image26-sunburst-icodeeasy/SKILL.md) |
| Image 2.6 GIF | [Flare](image26-gif-flare-icodeeasy/SKILL.md) · [Sunburst](image26-gif-sunburst-icodeeasy/SKILL.md) |
| Seedream 5 | [5.5](seedream-5-5-icodeeasy/SKILL.md) · [5 Flash](seedream-5-0-flash-icodeeasy/SKILL.md) · [5 Pro](seedream-5-0-pro-icodeeasy/SKILL.md) · [5.0 Lite](seedream-5-0-lite-icodeeasy/SKILL.md) |
| Seedream 4 | [4.5](seedream-4-5-icodeeasy/SKILL.md) · [4.0](seedream-4-0-icodeeasy/SKILL.md) |
| FLUX 2 | [Pro](flux-2-pro-icodeeasy/SKILL.md) · [Max](flux-2-max-icodeeasy/SKILL.md) · [Flex](flux-2-flex-icodeeasy/SKILL.md) |
| FLUX 3 | [Image](flux-3-image-icodeeasy/SKILL.md) · [Image Klein](flux-3-image-klein-icodeeasy/SKILL.md) |

Try `$image26-sunburst-icodeeasy create a coffee cup product photo` or `$image26-gif-flare-icodeeasy create a looping GIF of a swaying lantern`. The skills wait for completion, download the result, and display it. Include a reference image when requesting a static edit.

For both Image 2.6 variants, each successful PNG costs ¥0.0833 at 1K, ¥0.294 at 2K, or ¥0.392 at 4K. Use PNG, JPEG, or WebP reference images at 2K and 4K.

GIFs support text prompts with optional reference images. The model sets frame count, timing, and dimensions. The standard price for a successful text-only GIF is ¥0.0833. GIFs generated with reference images are billed by actual usage.

Install or update all image and GIF skills and their shared scripts. The command replaces existing files after a successful download and extraction.

```bash
(
  update_dir=$(mktemp -d) || exit 1
  trap 'rm -rf "$update_dir"' EXIT
  curl -fL https://github.com/icodeeasyai/skills/archive/refs/heads/main.tar.gz -o "$update_dir/skills.tar.gz" &&
  tar -xzf "$update_dir/skills.tar.gz" -C "$update_dir" &&
  for skill_dir in "$update_dir"/skills-main/icodeeasy-image-generations \
                   "$update_dir"/skills-main/image*-icodeeasy \
                   "$update_dir"/skills-main/seedream*-icodeeasy \
                   "$update_dir"/skills-main/flux*-icodeeasy; do
    skill_name=${skill_dir##*/}
    mkdir -p "$HOME/.codex/skills/$skill_name" &&
    cp -R "$skill_dir/." "$HOME/.codex/skills/$skill_name/" || exit 1
  done
)
```

After updating an older installation, you can remove just the `SKILL.md` files from `image25-icodeeasy`, `image26-icodeeasy`, `image26-gif-icodeeasy`, `seedream-icodeeasy`, and `flux-icodeeasy` under `~/.codex/skills/`. You can keep any other files in those directories. Restart Codex to refresh the skill list.

Configure the API key, then invoke the desired skill in a new chat.

```bash
export OPENAI_API_KEY="<your-api-key>"
```

Authentication also supports `ANTHROPIC_AUTH_TOKEN`. Generated images and downloads belong in the project’s `out/images/`. Treat long-lived result URLs as sensitive.

The general [icodeeasy-image-generations](icodeeasy-image-generations/SKILL.md) skill defaults to Image 2 when you leave the model unspecified. If you ask for Image 2.5 or 2.6 without naming a variant, it uses Flare for that version.

### 3D and video generation

| Model | Skill |
| --- | --- |
| Hunyuan 3D 3.1 | [hunyuan-3d-3-1-icodeeasy](hunyuan-3d-3-1-icodeeasy/SKILL.md) |
| Hunyuan 3D Express | [hunyuan-3d-express-icodeeasy](hunyuan-3d-express-icodeeasy/SKILL.md) |
| Tripo H3.1 | [tripo-h3-1-icodeeasy](tripo-h3-1-icodeeasy/SKILL.md) |
| Tripo P1 | [tripo-p1-icodeeasy](tripo-p1-icodeeasy/SKILL.md) |
| Tripo P2 | [tripo-p2-icodeeasy](tripo-p2-icodeeasy/SKILL.md) |
| Seedance 2.5 | [seedance-2-5-icodeeasy](seedance-2-5-icodeeasy/SKILL.md) |
| Seedance 2.5 Flash | [seedance-2-5-flash-icodeeasy](seedance-2-5-flash-icodeeasy/SKILL.md) |
| Seedance 2.0 | [seedance-2-0-icodeeasy](seedance-2-0-icodeeasy/SKILL.md) |
| Seedance 2.0 Fast | [seedance-2-0-fast-icodeeasy](seedance-2-0-fast-icodeeasy/SKILL.md) |
| Seedance 2.0 Mini | [seedance-2-0-mini-icodeeasy](seedance-2-0-mini-icodeeasy/SKILL.md) |
| Seedance 1.5 Pro | [seedance-1-5-pro-icodeeasy](seedance-1-5-pro-icodeeasy/SKILL.md) |
| MiniMax H3 video | [minimax-h3-icodeeasy](minimax-h3-icodeeasy/SKILL.md) |

The [general 3D skill](icodeeasy-3d-generations/SKILL.md) covers model discovery, price quotes, generation, polling, and downloads. The [general video skill](icodeeasy-video-generations/SKILL.md) also covers other supported video models and recovery of existing tasks.

Install or update the model skills and their shared scripts with the command below.

```bash
(
  update_dir=$(mktemp -d) || exit 1
  trap 'rm -rf "$update_dir"' EXIT
  set -- icodeeasy-3d-generations icodeeasy-video-generations \
         hunyuan-3d-3-1-icodeeasy hunyuan-3d-express-icodeeasy \
         tripo-h3-1-icodeeasy tripo-p1-icodeeasy tripo-p2-icodeeasy \
         seedance-2-5-icodeeasy seedance-2-5-flash-icodeeasy \
         seedance-2-0-icodeeasy seedance-2-0-fast-icodeeasy seedance-2-0-mini-icodeeasy \
         seedance-1-5-pro-icodeeasy minimax-h3-icodeeasy
  curl -fL https://github.com/icodeeasyai/skills/archive/refs/heads/main.tar.gz -o "$update_dir/skills.tar.gz" &&
  tar -xzf "$update_dir/skills.tar.gz" -C "$update_dir" || exit 1
  for skill_name do
    test -f "$update_dir/skills-main/$skill_name/SKILL.md" || exit 1
  done
  for skill_name do
    mkdir -p "$HOME/.codex/skills/$skill_name" &&
    cp -R "$update_dir/skills-main/$skill_name/." "$HOME/.codex/skills/$skill_name/" || exit 1
  done
)
```

If you installed the previous release, you can remove the old `SKILL.md` files from the `hunyuan-3d-icodeeasy`, `tripo-3d-icodeeasy`, and `seedance-icodeeasy` directories under `~/.codex/skills/`. Restart Codex to use the entries in the table.

Set your iCodeEasy account API key in its own environment variable.

```bash
export ICODEEASY_API_KEY="<your-api-key>"
```

Try `$hunyuan-3d-3-1-icodeeasy create a low-poly ceramic cup as a GLB` or `$seedance-2-5-flash-icodeeasy create a six-second video of morning mist on a lake`. Creating a task incurs charges. Use `--confirm-paid` after the user authorizes the call. Use `--dry-run` to inspect a request or `quote` to check the current price of a 3D request.

If polling or downloading is interrupted, keep the task ID and recover the same task. Completed videos are also available in the API key owner's [usage details](https://icodeeasy.ai/dashboard/logs/).
