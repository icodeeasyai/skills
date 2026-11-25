# Ice Skills

I Code Easy 的 Agent Skills，支持 Codex 和 Claude Code，使用同一套模型说明与调用脚本。

English version: [README.en.md](README.en.md)

## 安装目录与调用

先在当前终端选择安装目录，再运行下方对应的安装命令。命令使用 `curl` 和 `tar`，会把模型入口和共享脚本放在同一目录下。

| 客户端 | 安装目录 | 聊天中的调用 |
| --- | --- | --- |
| Codex，已有本仓库安装 | `~/.codex/skills/` | `$seedance-2-5-flash-icodeeasy` |
| Codex，新安装 | `~/.agents/skills/` | `$seedance-2-5-flash-icodeeasy` |
| Claude Code | `~/.claude/skills/` | `/seedance-2-5-flash-icodeeasy` |

已有 Codex 安装可直接运行下方命令，默认更新 `~/.codex/skills/`。如果已安装在 `~/.agents/skills/`，继续选择该目录。为同一客户端保留一份安装，避免重复发现同名 skill。

新安装 Codex 时，在当前终端运行：

```bash
export ICODEEASY_SKILLS_DIR="$HOME/.agents/skills"
```

安装到 Claude Code 时，在当前终端运行：

```bash
export ICODEEASY_SKILLS_DIR="$HOME/.claude/skills"
```

切回旧版 Codex 安装目录时，设置 `ICODEEASY_SKILLS_DIR="$HOME/.codex/skills"`。安装或更新后，重新启动所用客户端并开始新聊天。下面的 `$skill-name` 示例用于 Codex，在 Claude Code 中使用 `/skill-name`，后面的生成要求相同。

## Skills

### 图片生成

按模型和输出格式选择 skill，直接描述想要的画面。

| 模型与输出 | Skill |
| --- | --- |
| Image 2 | [image2-icodeeasy](image2-icodeeasy/SKILL.md) |
| Image 2.5 静态图片 | [Flare](image25-flare-icodeeasy/SKILL.md) · [Sunburst](image25-sunburst-icodeeasy/SKILL.md) |
| Image 2.6 静态图片 | [Flare](image26-flare-icodeeasy/SKILL.md) · [Sunburst](image26-sunburst-icodeeasy/SKILL.md) |
| Image 2.6 GIF | [Flare](image26-gif-flare-icodeeasy/SKILL.md) · [Sunburst](image26-gif-sunburst-icodeeasy/SKILL.md) |
| Seedream 5 | [5.5](seedream-5-5-icodeeasy/SKILL.md) · [5 Flash](seedream-5-0-flash-icodeeasy/SKILL.md) · [5 Pro](seedream-5-0-pro-icodeeasy/SKILL.md) · [5.0 Lite](seedream-5-0-lite-icodeeasy/SKILL.md) |
| Seedream 4 | [4.5](seedream-4-5-icodeeasy/SKILL.md) · [4.0](seedream-4-0-icodeeasy/SKILL.md) |
| FLUX 2 | [Pro](flux-2-pro-icodeeasy/SKILL.md) · [Max](flux-2-max-icodeeasy/SKILL.md) · [Flex](flux-2-flex-icodeeasy/SKILL.md) |
| FLUX 3 | [Image](flux-3-image-icodeeasy/SKILL.md) · [Image Klein](flux-3-image-klein-icodeeasy/SKILL.md) |

例如，使用 `$image26-sunburst-icodeeasy 生成一张咖啡杯产品图` 或 `$image26-gif-flare-icodeeasy 生成一盏轻轻摇晃的灯笼 GIF`。生成后会等待完成、下载并展示图片。静态图片编辑时附上参考图即可。

Image 2.6 静态图片按成功结果收费。Flare 和 Sunburst 的 1K PNG 每张 ¥0.0833，2K 每张 ¥0.294，4K 每张 ¥0.392。2K 和 4K 的参考图使用 PNG、JPEG 或 WebP。

GIF 可以纯文生，也可以附参考图，帧数、帧间隔和尺寸由模型决定。纯文生 GIF 标准价为每个成功结果 ¥0.0833，参考图生成 GIF 按实际用量结算。

以下命令会安装或更新所有图片与 GIF skill 及其共用脚本。下载和解包成功后才覆盖已有文件。

```bash
(
  skills_dir="${ICODEEASY_SKILLS_DIR:-$HOME/.codex/skills}"
  update_dir=$(mktemp -d) || exit 1
  trap 'rm -rf "$update_dir"' EXIT
  curl -fL https://github.com/icodeeasyai/skills/archive/refs/heads/main.tar.gz -o "$update_dir/skills.tar.gz" &&
  tar -xzf "$update_dir/skills.tar.gz" -C "$update_dir" &&
  for skill_dir in "$update_dir"/skills-main/icodeeasy-image-generations \
                   "$update_dir"/skills-main/image*-icodeeasy \
                   "$update_dir"/skills-main/seedream*-icodeeasy \
                   "$update_dir"/skills-main/flux*-icodeeasy; do
    skill_name=${skill_dir##*/}
    mkdir -p "$skills_dir/$skill_name" &&
    cp -R "$skill_dir/." "$skills_dir/$skill_name/" || exit 1
  done
)
```

旧版安装更新后，可从所选安装目录删除 `image25-icodeeasy`、`image26-icodeeasy`、`image26-gif-icodeeasy`、`seedream-icodeeasy` 和 `flux-icodeeasy` 各目录中的 `SKILL.md`。目录里的其他文件可保留。重启客户端后，旧入口会从技能列表消失。

配置 API Key 后，在新聊天中直接调用对应 skill。

```bash
export OPENAI_API_KEY="<your-api-key>"
```

认证也兼容 `ANTHROPIC_AUTH_TOKEN`。图片与下载输出放在项目的 `out/images/`。图片结果链接长期有效，按敏感信息处理。

[icodeeasy-image-generations](icodeeasy-image-generations/SKILL.md) 是通用生图入口，未指定模型时使用 Image 2。指定 Image 2.5 或 2.6 而未指定变体时，默认使用对应版本的 Flare。

### 3D 生成与视频生成

| 模型 | Skill |
| --- | --- |
| 混元 3D 3.1 | [hunyuan-3d-3-1-icodeeasy](hunyuan-3d-3-1-icodeeasy/SKILL.md) |
| 混元 3D Express | [hunyuan-3d-express-icodeeasy](hunyuan-3d-express-icodeeasy/SKILL.md) |
| Tripo H3.1 | [tripo-h3-1-icodeeasy](tripo-h3-1-icodeeasy/SKILL.md) |
| Tripo P1 | [tripo-p1-icodeeasy](tripo-p1-icodeeasy/SKILL.md) |
| Tripo P2 | [tripo-p2-icodeeasy](tripo-p2-icodeeasy/SKILL.md) |
| Seedance 2.5 | [seedance-2-5-icodeeasy](seedance-2-5-icodeeasy/SKILL.md) |
| Seedance 2.5 Flash | [seedance-2-5-flash-icodeeasy](seedance-2-5-flash-icodeeasy/SKILL.md) |
| Seedance 2.0 | [seedance-2-0-icodeeasy](seedance-2-0-icodeeasy/SKILL.md) |
| Seedance 2.0 Fast | [seedance-2-0-fast-icodeeasy](seedance-2-0-fast-icodeeasy/SKILL.md) |
| Seedance 2.0 Mini | [seedance-2-0-mini-icodeeasy](seedance-2-0-mini-icodeeasy/SKILL.md) |
| Seedance 1.5 Pro | [seedance-1-5-pro-icodeeasy](seedance-1-5-pro-icodeeasy/SKILL.md) |
| MiniMax H3 视频 | [minimax-h3-icodeeasy](minimax-h3-icodeeasy/SKILL.md) |

[通用 3D skill](icodeeasy-3d-generations/SKILL.md) 提供模型查询、报价、生成、轮询和下载。[通用视频 skill](icodeeasy-video-generations/SKILL.md) 继续提供其他已支持的视频模型和已有任务的恢复。

下面的命令安装或更新各模型入口及其共用脚本。

```bash
(
  skills_dir="${ICODEEASY_SKILLS_DIR:-$HOME/.codex/skills}"
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
    mkdir -p "$skills_dir/$skill_name" &&
    cp -R "$update_dir/skills-main/$skill_name/." "$skills_dir/$skill_name/" || exit 1
  done
)
```

升级后，若已安装旧的品牌入口，可从所选安装目录下的 `hunyuan-3d-icodeeasy`、`tripo-3d-icodeeasy`、`seedance-icodeeasy` 目录移除各自的 `SKILL.md`。重启客户端后，使用上表中的模型入口。

在环境中配置 iCodeEasy 的账号 API Key，避免和其他服务的 Key 混用。

```bash
export ICODEEASY_API_KEY="<your-api-key>"
```

例如 `$hunyuan-3d-3-1-icodeeasy 生成一个低模陶杯并保存为 GLB`，或 `$seedance-2-5-flash-icodeeasy 生成一段 6 秒的湖面晨雾视频`。实际创建任务会产生付费调用，获得授权后使用 `--confirm-paid`。可以先用 `--dry-run` 检查请求，3D 任务还可以用 `quote` 查询当前报价。

等待或下载中断时，保存任务 ID 并查询、下载同一任务。成功的视频也可以从 API Key 所属账号的[日志明细](https://icodeeasy.ai/dashboard/logs/)找回。
