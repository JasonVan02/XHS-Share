# 文案、成图与发布包核对契约

这一契约解决实际发生过的问题：上传序号与正文页码混用、右下角总页码残留、换图后沿用旧核对记录、只检查文案却漏掉图片中的错字。脚本只验证结构和记录，必须先实际读图。

## 1. 清单

`manifest.json` 是当前版本的内容依据。以实际上传顺序列出 `cards`，只有第一个是 `cover`。`order` 从 1 连续递增；正文可见页码为 `order - 1`，补足两位。页头由页码和 `section_label` 组成；封面页头只使用 `section_label`。右下角不允许出现页码。

文件命名前两位代表上传顺序，例如 `images/05-benefit.png` 对应左上角 `04`。不要为了让文件名等于可见页码，把封面排到最后。

```json
{
  "schema_version": 1,
  "title": "这篇帖子的发布标题",
  "total_images": 2,
  "canvas": {"aspect_ratio": [3, 4], "min_width": 1080},
  "caption_file": "caption.txt",
  "support_files": ["plan.md", "sources.md"],
  "cards": [
    {
      "id": "cover",
      "order": 1,
      "kind": "cover",
      "file": "images/01-cover.png",
      "prompt": "prompts/01-cover.md",
      "section_label": "AI WORKFLOW",
      "text_blocks": ["把 AI 用在真正需要的地方", "从任务拆解开始"]
    },
    {
      "id": "first-step",
      "order": 2,
      "kind": "content",
      "file": "images/02-first-step.png",
      "prompt": "prompts/02-first-step.md",
      "section_label": "先把目标说清楚",
      "text_blocks": ["先定义结果，再安排执行。", "目标、边界、验收标准。"]
    }
  ]
}
```

`text_blocks` 按阅读顺序记录所有可见正文，包括标题、品牌名、流程号、效果说明和脚注；不包括自动派生的左上角页头。按逻辑文本块记录，换行可合并。不要省略不显眼的小字。无支持文件时用空数组，不留指向不存在文件的条目。

计划阶段只检查清单字段、编号推导、排序与路径，不要求已生成图片。正式检查要求图片、提示词、正文和列出的支持文件实际存在。图片默认 PNG；脚本读尺寸和哈希，不生成、修改或修补图片。

## 2. 观察记录

先打开当前图片核对，再写 `review.json`。哈希使用文件实际字节的 SHA-256。填写内容来自图像观察，不能复制清单来冒充读图。为每张图填写与清单 id 对应的记录：

```json
{
  "schema_version": 1,
  "manifest_sha256": "当前 manifest.json 文件的 SHA-256",
  "editorial": {
    "title_body_aligned": true,
    "claims_checked": true,
    "story_order_checked": true,
    "caption_consistent": true,
    "issues": []
  },
  "cards": [
    {
      "id": "cover",
      "image_sha256": "当前 PNG 文件的 SHA-256",
      "reviewed_at": "2026-09-07T18:00:00+08:00",
      "method": "visual",
      "top_left_text": "AI WORKFLOW",
      "bottom_right_page_marker": null,
      "other_page_markers": [],
      "text_blocks": ["把 AI 用在真正需要的地方", "从任务拆解开始"],
      "checks": {
        "legibility": true,
        "layout": true,
        "style_consistency": true,
        "content_numbers_and_arrows": true
      },
      "issues": []
    }
  ]
}
```

上例只展示一张观察记录的写法；正式记录必须包含清单中的每张图。正文第一页的 `top_left_text` 应为 `01 先把目标说清楚`。

`bottom_right_page_marker` 专指页码：正确值为 null；若仍出现 `02 / 06`，就如实记录该字符串并修复。`other_page_markers` 记录在其他角落发现的额外页码；正文的列表号不放入此字段。正常正文或设计线条可以出现在右下方，不应为了清角标而删掉内容。

`method` 只能记录实际执行的 `visual` 或 `visual+ocr`。`claims_checked` 是对当前文字中的相关事实进行过适当审阅，不表示必须给每个普通观点联网找来源；涉及不确定或时效事实按编辑规范处理。

## 3. 人工读图清单

| 层级 | 需要实际检查 |
|---|---|
| 全文 | 漏字、多字、乱码、错别字；品牌名、数字、单位、标点；否定词或程度词导致的语义变化 |
| 角标 | 封面无数字；正文左上角连续；右下角无页码；其他角落无重复页码 |
| 流程 | 列表顺序、节点对应、箭头方向、循环终点和验收出口；正文步骤号未被误删 |
| 视觉 | 手机上可读；不压线、不越界、不裁字；字级明确；渐变对比足够；风格一致 |
| 整套 | 发布顺序正确；无缺页或重复页；每页推进内容；图与标题、发布正文不矛盾 |
| 修订 | 最新用户修改保留；改编号没有重置文案；最终文件与本次观察记录一致 |

核对后再运行脚本。它只忽略空白字符来比较逻辑文本，不忽略汉字、品牌拼写、数字或标点差异。对看不清的字先提高查看尺寸；仍不确定就修图，不默认通过。

## 4. 机械检查与打包

```bash
python3 "$SKILL_DIR/scripts/check_release.py" "$RELEASE/manifest.json" --stage plan
python3 "$SKILL_DIR/scripts/check_release.py" "$RELEASE/manifest.json" --review "$RELEASE/review.json"
python3 "$SKILL_DIR/scripts/check_release.py" "$RELEASE/manifest.json" --review "$RELEASE/review.json" --package "$RELEASE/final.zip"
```

通过后生成 `qa-report.json`，打包时图片按清单顺序加入。ZIP 仅纳入清单指定的图片、提示词、发布正文、支持文件与核对记录。不会扫描整个工作目录，不把原参考和旧图自动打包。

如果同名 ZIP 已存在，使用新的版本文件名。脚本检查 PNG 格式、统一尺寸和比例、缺文件、重复 id/路径/图像、顺序、观察文本、角标、检查项及哈希；不靠视觉模型生成“全部通过”的结论。

清单改变会让整份观察记录的版本校验失效：重新审阅变化及其对整套的影响，未变化图片可以保留其真实的旧观察内容，已变化图片必须重新查看。不能仅将新哈希填进去跳过复核。

如用户日后明确改变编号位置或计数方式，应同步更新本次规范和校验器，不直接绕过失败检查或错误宣称通过。
