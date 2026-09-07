# Jason XHS AI Share

**把 AI 工具经验和知识，做成有点击理由、读得下去、风格统一的小红书图文。**

`jason-xhs-ai-share` 是一套面向 AI 知识分享的 Agent Skill，覆盖选题梳理、标题与文案、图片拆页、图像生成、逐图校对和素材打包。默认采用简洁的蓝紫编辑风格，交付图片、可复制的发布正文及 ZIP。

## 效果预览

| 封面 | 内容页 | 效果说明页 |
| :---: | :---: | :---: |
| <img src="assets/style-cover.png" width="280" alt="深蓝背景、蓝紫光感和大标题的封面示例"> | <img src="assets/style-content.png" width="280" alt="雾白背景、清晰文字层级的内容页示例"> | <img src="assets/style-benefit.png" width="280" alt="蓝紫双栏分工与效果说明的内容页示例"> |

预览来自 ChatGPT＋Codex 工作流分享案例，用于展示视觉方向。新主题会重新策划文案，不沿用示例中的观点或产品结论。

## 它能做什么

- **把角度讲准确**：提取受众、真实痛点与核心观点，避免生成一篇偏离本意的泛泛科普。
- **让标题有点击理由**：分别设计发布标题与封面标题，覆盖关键痛点，并在正文中兑现承诺。
- **安排阅读顺序**：每页一个重点，从问题推进到方法，再给读者可执行的下一步。
- **保持视觉一致**：蓝紫主色、深浅底搭配、大标题、清晰对齐与充足留白。
- **核对实际成图**：检查错字、漏字、品牌名、数字、流程箭头、角标与手机阅读效果。
- **保留修改结果**：小改只处理相关页面，重新核对整张图，避免改页码时文案又回到旧版。
- **整理发布素材**：按上传顺序交付图片与正文，打包时排除原参考、旧版本和失败候选。

适合 AI 工具教程、工作流拆解、使用经验、概念科普和有依据的工具对比。

## 安装

### 从 GitHub 安装

将命令中的 `YOUR_GITHUB_NAME/YOUR_REPO` 替换为实际托管此 skill 的仓库地址，再执行：

```bash
npx skills add YOUR_GITHUB_NAME/YOUR_REPO --skill jason-xhs-ai-share -g
```

按 CLI 提示选择 Codex。`-g` 表示用户范围安装；该方式需要可运行 `npx` 的 Node.js/npm 环境。命令格式见 [Skills CLI](https://github.com/vercel-labs/skills#usage)。

### 从 ZIP 安装

解压后，将完整的 `jason-xhs-ai-share` 文件夹放入用户级 skills 目录，保持以下结构：

```text
~/.agents/skills/jason-xhs-ai-share/
├── SKILL.md
├── agents/
├── assets/
├── references/
└── scripts/
```

本地发现位置以当前客户端配置为准；`~/.agents/skills` 是官方文档列出的用户级目录。参见 [OpenAI：本地 skills 的加载位置](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

### 运行条件

- 支持 Agent Skills 的 Codex 环境。
- 生成或修改图片时，当前会话需要提供可用的原生图像生成能力；本 skill 本身不附带图像模型。
- 校验与 ZIP 打包脚本需要 Python 3.9+，仅使用标准库，无需额外 Python 依赖。

如果当前环境没有图像工具，仍可完成策划、文案和逐图提示词；图片生成会明确标记为未完成。不会自动切换到付费 API。

## 快速使用

安装后，直接在任务中调用：

```text
用 $jason-xhs-ai-share，把「ChatGPT＋Codex 的工作闭环」
做成 6 张小红书 AI 分享图文，核对后打包。
```

### 给出自己的分享角度

```text
用 $jason-xhs-ai-share 制作一篇 AI 工作流分享。

受众：刚开始用 Codex 的设计师。
我的角度：经常理解错需求、越改越偏、额度消耗快。
核心观点：先讨论目标与边界，再执行、自检和复盘。
要求：6 张图，简洁蓝紫风格，给出可复制的操作模板。
涉及产品能力和额度的说法先核实，不编造亲测数据。
完成后核对文案、顺序、角标并打包。
```

### 只做初版规划

```text
用 $jason-xhs-ai-share，先规划一篇「AI 提示词为什么越写越长」
的图文帖。给我推荐标题、核心观点和逐页文案，暂不出图。
```

### 修改已有图片

```text
用 $jason-xhs-ai-share 修改这套图的第 5 张。
保留现有排版和配色，把底部说明改成两栏分工说明。
核对整张图，保留其他已确认的修改，更新素材包。
```

调用时附上目标图片或可访问的本地路径。新增、删除或调整页面顺序时，会重新计算上传顺序与正文角标。

## 默认风格与编号

| 项目 | 默认设定 |
| --- | --- |
| 语言 | 简体中文 |
| 数量 | 6 张：1 张封面＋5 张正文，可按主题调整 |
| 画幅 | 3:4 竖版，目标 1080×1440 或更高，同套尺寸一致 |
| 配色 | 雾白、深墨蓝、钴蓝、蓝紫，允许克制的渐变与光晕 |
| 排版 | 无衬线字体、大标题、明确对齐、充足留白 |
| 封面 | 不显示页码 |
| 正文 | 仅左上角从 01 连续编号 |
| 右下角 | 不显示页码或总页数 |
| 水印 | 默认不加账号、水印或二维码 |

**文件序号用于上传排序，包含封面；画面上的正文页码不包含封面。**

| 上传顺序 | 文件示例 | 画面左上角页码 |
| --- | --- | --- |
| 第 1 张 | `01-cover.png` | 无 |
| 第 2 张 | `02-problem.png` | 01 |
| 第 3 张 | `03-method.png` | 02 |
| 第 4 张 | `04-workflow.png` | 03 |
| 第 5 张 | `05-benefit.png` | 04 |
| 第 6 张 | `06-action.png` | 05 |

正文内的列表数字和流程步骤数字正常保留。完整视觉说明见 [视觉规范](references/visual-system.md)。

## 从主题到素材包

```text
梳理意图 → 策划标题与文案 → 建立逐页清单 → 保存提示词并出图
    → 逐张读图核对 → 检查整套衔接与编号 → 修正问题页 → 打包交付
```

新系列先建立封面风格，再生成后续页面。用户只要求规划时停在规划阶段；已要求直接制作时，按已确认的偏好继续执行。

图片文案、发布正文与核对记录使用同一份当前清单。重要修改会生成新版本，保留原稿，方便追溯。

## 两层校对

### 逐图阅读与内容审阅

由执行 skill 的助手查看实际成图，核对全文、品牌拼写、数字、否定词、流程箭头、角标、裁切和可读性，再检查整套图文是否连贯。OCR 可以辅助，不能代替看图。

涉及产品版本、功能、收费或额度时，核查适用的一手资料；不把工作流建议写成已经验证的产品能力，也不编造量化收益。详见 [编辑规范](references/editorial-guide.md)。

### 脚本校验

`check_release.py` 检查清单与已记录的观察结果，包括：

- 上传顺序、数量、重复文件与缺失图片。
- 左上角编号是否符合“封面不计数”，右下角是否记录为无页码。
- 观察到的文字与当前文案是否一致。
- 图片尺寸、比例与文件哈希。
- 图片或清单是否在核对后被更改。
- ZIP 是否只包含清单指定的正式素材。

**脚本不会识别图片文字，也不能独立证明事实正确或设计美观。** 它验证真实读图记录与文件的一致性；不能把提示词复制成观察结果来获得“通过”。

记录格式和操作步骤见 [核对契约](references/qa-contract.md)。

## 输出内容

```text
image-cards/{topic}/release-vN/
├── images/             # 按上传顺序命名的正式图片
├── prompts/            # 实际使用的逐图提示词
├── caption.txt         # 发布标题、正文与话题
├── plan.md             # 定位、拆页与视觉规划
├── manifest.json       # 当前文案与发布清单
├── review.json         # 实际读图记录
├── qa-report.json      # 校验结果
├── sources.md          # 有事实来源需要记录时提供
└── release.zip         # 发布素材包
```

本 skill 负责准备素材，发布到小红书需要另外明确提出。

## 开发与验证

在本仓库根目录运行回归测试：

```bash
python3 scripts/test_check_release.py
```

当前包含 16 项测试，覆盖页码冲突、右下角残留、文案回退、缺页、重复图片、过期核对记录与打包顺序等问题。测试使用模拟观察记录验证脚本逻辑，不代表自动完成了视觉审阅。

对一套已准备好清单和读图记录的素材执行校验：

```bash
python3 scripts/check_release.py path/to/release/manifest.json --stage plan

python3 scripts/check_release.py path/to/release/manifest.json \
  --review path/to/release/review.json \
  --package path/to/release/final.zip
```

ZIP 已存在时使用新的版本文件名。校验失败时修复对应问题并重新核对，不会直接打包。

## 仓库结构与自定义

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | 任务范围、默认偏好和完整执行流程 |
| [agents/openai.yaml](agents/openai.yaml) | 显示名称与默认调用提示 |
| [references/visual-system.md](references/visual-system.md) | 配色、排版、参考图与手机阅读标准 |
| [references/editorial-guide.md](references/editorial-guide.md) | 标题、阅读顺序、事实核查与发布文案 |
| [references/qa-contract.md](references/qa-contract.md) | 清单、观察记录与校验契约 |
| [scripts/check_release.py](scripts/check_release.py) | 校验与发布包生成 |
| [scripts/test_check_release.py](scripts/test_check_release.py) | 回归测试 |
| [assets/](assets/) | 三张风格参考图 |

只调整某一篇帖子时，在请求中说明新偏好即可。要长期改变风格或流程，可修改对应规范；改变编号规则时，需要同步修改核对契约、校验器与测试。

## 致谢

本项目参考了 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills#baoyu-xhs-images) 中 `baoyu-xhs-images` 的拆页、逐图提示词、封面风格参考与定点修订方法，结合实际制作反馈形成这套个人工作流。

本 skill 已包含独立执行所需的流程，不强制依赖 `baoyu-xhs-images`。在 Codex 环境中，图像生成与编辑使用当前可用的原生 `imagegen` 能力。
