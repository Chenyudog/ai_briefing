---
name: AI 大事
description: 前沿 AI 与机器人研究简报的中文科技期刊视觉系统
colors:
  accent: "#a52e17"
  accent-hover: "#84240f"
  accent-wash: "#eddace"
  paper: "#f6f2e9"
  surface: "#fffdf7"
  ink: "#211d18"
  muted: "#635a4e"
  line: "#c9c0b1"
  field-line: "#9a8d80"
  white: white
  draft: "#764709"
  success-surface: "#e4eddb"
  error-ink: "#842d25"
  error-surface: "#f2ded7"
typography:
  display:
    fontFamily: '"Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", Georgia, serif'
    fontSize: "clamp(53px, 8.4vw, 96px)"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-.038em"
  headline:
    fontFamily: '"Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", Georgia, serif'
    fontSize: "clamp(28px, 3.65vw, 53px)"
    fontWeight: 800
    lineHeight: 1.19
    letterSpacing: "-.025em"
  article-title:
    fontFamily: '"Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", Georgia, serif'
    fontSize: "clamp(31px, 5vw, 58px)"
    fontWeight: 800
    lineHeight: 1.23
    letterSpacing: "-.025em"
  title:
    fontFamily: '"Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", Georgia, serif'
    fontSize: "clamp(19px, 2.25vw, 25px)"
    fontWeight: 800
    lineHeight: 1.4
  body:
    fontFamily: '"Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif'
    fontSize: "16px"
    lineHeight: 1.7
  label:
    fontFamily: '"Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif'
    fontSize: "12px"
    fontWeight: 750
    lineHeight: 1.7
rounded:
  control: "3px"
spacing:
  form-gap: "14px"
  field-section-gap: "15px"
  layout-gap: "24px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    rounded: "{rounded.control}"
    padding: "8px 15px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 15px"
  button-secondary-hover:
    backgroundColor: "{colors.accent-wash}"
  text-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 10px"
  story-tag:
    textColor: "{colors.accent}"
    typography: "{typography.label}"
  draft-tag:
    textColor: "{colors.draft}"
    typography: "{typography.label}"
  login-panel:
    backgroundColor: "{colors.surface}"
    padding: "25px 30px"
---

# Design System: AI 大事

## Overview

**Creative North Star: "中文科技期刊"**

暖纸底、墨黑刊头和砖红强调色构成简报的视觉语言。宋体标题与版面横线划分阅读层次。左文右图的头条用一张横幅插图提供视觉重心，后续条目用对齐的日期和标题方便快速浏览。

新闻正文用窄栏呈现摘要、研究事实和段落，保留醒目的原文入口。编辑界面沿用纸底和横线，用清楚的字段标签和按钮区分日常编务操作。

**Key Characteristics:**

- 暖纸底与墨色标题
- 砖红标示链接、当前频道和主要动作
- 刊头、头条、按日期排列的新闻列表
- 窄栏阅读和实用的原生表单

## Colors

### Primary

- **砖红**用于页面顶边、刊名字标方点、当前频道下划线、文章类型、链接和主按钮。
- **深砖红**用于主按钮悬停。**浅砖红**用于次按钮悬停。

### Neutral

- **暖纸**是页面底色。**浅纸**用于登录面板、表单字段和次按钮。
- **墨黑**用于刊名、标题、正文和主要横线。**灰褐**用于摘要、时间、来源和辅助说明。
- **纸灰线**分开归档行、研究事实和面板边界。**深纸灰线**勾勒表单字段。**白字**用于砖红实底按钮。
- **琥珀棕**用于草稿文字标签。浅绿色用于保存反馈，浅红底和深红字用于错误信息。

## Typography

- **刊头**用 Noto Serif CJK SC 优先的宋体栈，重字重和紧字距使「AI 大事」成为阅读入口。
- **标题**沿用宋体栈。头条与文章标题采用流动字号，归档标题以较小字号维持扫读节奏。后台页面标题沿用宋体，新闻列表中的后台标题沿用无衬线正文栈。
- **正文**用 Noto Sans CJK SC 优先的无衬线栈（16px，行高 1.7）。文章段落行高为 1.85，摘要为 20px。
- **信息标签**用无衬线，新闻类型用 12px 强调色。来源和同行元数据为 13px，日期启用等宽数字。

## Layout

- 页面最大宽度为 1216px。常规两侧留 56px，视口不超过 900px 时收为 32px，不超过 650px 时收为 17px。
- 桌面顶栏将频道放在居中的列中。首页刊头把大标题和刊物说明放在同一横排，头条按 `.92fr 1.08fr` 分配文字和封面两列，归档行依次安排日期、内容、箭头。
- 不超过 650px 时，频道移至顶栏下一行，刊头和头条纵向排列，日期独占归档行首行，编辑表单的并列字段改为单列。封面裁成较宽的横幅（1.95）。
- 阅读页和后台工作区最宽 800px。正文段落区最宽 36em，登录面板最宽 440px。

## Elevation & Depth

版面采用平面层次。墨色线用于刊头、头条与页脚的主要分区，细纸灰线用于归档、研究事实和后台列表。浅纸面板与页面暖纸底形成轻微色差，登录面板用墨色上边界固定视觉层次。

## Shapes

封面、面板与版面横线保留直角。按钮、输入框和反馈条使用 3px 微圆角。刊名字标的砖红方点随字号缩放，新闻类型和稿件状态以文字标签呈现。

## Components

### Navigation

频道链接以灰褐为默认状态，悬停和当前频道用砖红。当前频道保留 2px 下划线和 `aria-current`。首个键盘焦点可显示「跳到主要内容」，可交互组件用 2px 砖红描边标示可见焦点，描边偏移 4px。

### Cover and archive rows

头条封面是版面插图，页脚显示「封面为生成插图」。桌面封面宽高比为 1.72，以 `object-fit: cover` 裁切。移动端按更宽的比例调整裁切位置。头条及归档行可通过标题链接进入详情，链接的点击区域覆盖整行。系统允许动效时，封面执行 .62s 的裁切展开，归档箭头悬停右移 4px。

### Reading

文章以返回频道链接开头，紧接新闻类型、来源、发布日期和宋体标题。论文状态与评测方式出现时放入带细边线的事实行。「发生了什么」与「为什么值得关注」各有一个可扫读的段落标题。原文入口使用主按钮。

### Buttons and fields

主要动作使用砖红实底按钮。退出和存草稿使用浅纸底次按钮，边框用纸灰线。按钮和字段最小高度 44px。输入框、下拉框和文本区共享浅纸底、深纸灰边框以及砖红输入光标。按钮悬停在允许动效时上移 2px，按下时下移 1px。

### Editorial panels

登录使用带墨色上边线的浅纸面板。编辑列表每行用纸灰线划分，稿件状态用文字标明。保存反馈使用浅绿色横条，校验错误使用浅红底及深红字。

## Do's and Don'ts

- **Do** 让纸色、宋体标题和细横线维持刊物的阅读层次。
- **Do** 保持原文日期和来源的位置稳定，方便在列表中比较。
- **Do** 用文字呈现稿件状态和表单反馈，并保留可见的键盘焦点。
- **Don't** 为归档行添加独立卡片底色或投影。
