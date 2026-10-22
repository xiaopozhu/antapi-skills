# AntAPI Skills

[English](README.md) | [简体中文](README.zh-CN.md)

所有 AntAPI 官方产品 Skills 的集中仓库。每个 Skill 支持单独安装，通过官方 CLI 调用同一套平台 API、AK 和 Credits。

## 当前状态

已实现首个候选 Skill `skills/antapi-whois`，支持域名注册信息和 TLD 覆盖查询，依赖官方 CLI
`>=0.1.0 <1.0.0` 与公开 API v1。Skill 和引用面向全球用户使用英文；仓库工程文档使用中文。
候选版本为 `0.1.0`，尚未正式发布。CI 与本地格式检查通过不表示生产调用已验收。默认 README 使用英文，并提供本中文版。

## 使用 npx skills 安装

在项目目录运行：

```bash
npx skills add xiaopozhu/antapi-skills --skill antapi-whois
```

安装器会让你选择 Agent；加 `-g` 可全局安装，加 `--agent codex` 可指定 Codex。仅列出可用 Skill：

```bash
npx skills add xiaopozhu/antapi-skills --list
```

这是通过 npm 分发的 [skills 安装器](https://github.com/vercel-labs/skills) 从 GitHub 获取 Skill，
无需将本仓库另行发布到 npm registry。Node.js 版本要求以安装器的官方说明为准。

以上命令跟随仓库默认分支，当前用于安装开发候选版，不代表正式产品发布。正式安装入口将固定到
已验证的 tag/commit 或 Release archive。Skill 需要本地配置的 Gateway、凭据与稳定 CLI
`>=0.1.0 <1.0.0`；首个 CLI 稳定版尚未发布，`dev` 构建会被版本检查拒绝。
安装 Skill 不会安装 CLI 或配置 AK，凭据按 CLI README 在本机配置，不放入聊天。

## 本地检查

结构与打包检查依赖 Python 3.9+ 和 Make；官方格式校验需要 Python 3.11+ 的独立工具环境：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-tools.txt
make verify SKILLS_REF=.venv/bin/skills-ref
```

官方 [skills-ref](https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref)
固定到 `69ef37e9424c0a7ea9dd2293b559e43ec8176379`，由 CI 与工具依赖共同记录；不会用自制检查器冒充官方格式验证。

基础检查可单独运行：

```bash
make check
make test
```

`scripts/check_structure.py` 检查目录命名、非空 `SKILL.md`、普通文件、禁止符号链接，以及 Markdown/HTML 本地引用必须存在并留在单个 Skill 内；不解析 YAML，也不验证触发效果。
`make verify` 在结构及脚本测试后调用官方校验器；零 Skill 时明确显示未进行格式校验。`tests/whois-scenarios.json` 是无真实 AK 的行为验收输入与准则，存在场景文件不表示验收已执行。

检查器仍允许初始化 fixture 的 `skills/` 为空并明确打印 `nothing installable`；正式发布前运行
`make check-release SKILLS_REF=.venv/bin/skills-ref`，空仓库必须失败。发布还必须完成 CLI 联合测试与真实 Agent 任务验收。
场景及实际执行证据边界见 [验收说明](tests/README.md)。

## 候选包

```bash
python3 scripts/package_skills.py --output /tmp/antapi-skill-packages
```

打包器拒绝空仓库、符号链接、特殊文件、越界引用和位于 `skills/` 内的输出目录。每个 Skill 生成
`<skill>-<version>.tar.gz`，同时生成 `SHA256SUMS` 与 `manifest.json`。归档仅包含该 Skill 的目录，
条目按路径排序并固定时间、权限及属主；相同内容产生相同字节。版本默认读取 `VERSION`，可显式传入
`--version`；`--commit` 仅接受完整 SHA，未提供时明确记为 `uncommitted`，不冒充实际 tag 或发布记录。
打包不会安装 Skill、提交代码或发布稳定版本。

## 内容组织

```text
skills/
  antapi-<product>/
    SKILL.md
    references/
    scripts/
```

Skill 围绕用户任务和产品划分，不为每个 endpoint 单独创建 Skill。命名和 frontmatter 遵循 [Agent Skills 规范](https://agentskills.io/specification)。每个目录可独立分发，引用不能依赖其他 Skill 或仓库外部相对路径。

`SKILL.md` 说明触发条件、CLI 依赖、流程、数量上限、错误恢复和凭据使用方式。HTTP、认证和重试能力由官方 CLI 提供，只有任务编排需要时才增加薄脚本。

## 协同发布

仓库整体使用一个 tag，不给每个 Skill 维护独立发布流水线。稳定安装入口固定到已验证的 tag/commit。
尚未正式发布时不提供稳定 tag 安装命令。开发预览使用上方默认分支安装入口。
本地验收可执行 `npx skills add /absolute/path/to/antapi-skills --skill antapi-whois`，或将完整
`skills/antapi-whois/` 复制至隔离 Agent 的 Skill 目录，保留 bundled references；不依赖仓库其他位置。
候选 archive 仅含同名单个根目录，手动解压前先核对 `SHA256SUMS`。

正式发布由 [antapi](https://github.com/xiaopozhu/antapi) 总入口发起，顺序为 API/Gateway 验收 → CLI → Skills → 官网。每批次明确 CLI 与 Skills 的版本组合，没有变化的组件沿用旧版本。

- [三仓库协同发布设计](https://github.com/xiaopozhu/antapi/blob/main/docs/design/coordinated-product-release.md)
- [实施计划](https://github.com/xiaopozhu/antapi/blob/main/docs/superpowers/plans/2026-10-22-coordinated-product-release.md)
