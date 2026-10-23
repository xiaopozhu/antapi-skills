# AntAPI Skills

[English](README.md) | [简体中文](README.zh-CN.md)

所有 AntAPI 官方产品 Skills 的集中仓库。每个 Skill 支持单独安装，由 Agent 使用项目 Key 和 Credits 直接调用对应 HTTP API。AntAPI CLI 是独立、可选的接入方式。

## 当前状态

已实现首个候选 Skill `skills/antapi-whois`，支持域名注册信息和 TLD 覆盖查询，使用 Python 3.9+ 与公开 API v1，不依赖 CLI。
仓库当前保持私有，由所有者决定正式公开。Skill 和引用面向全球用户使用英文；仓库工程文档使用中文。
候选版本为 `0.1.0`，尚未正式发布。CI 与本地格式检查通过不表示生产调用已验收。默认 README 使用英文，并提供本中文版。

## 单独安装 Skill

从经过验证的归档或有权访问的源码中取得完整 `skills/antapi-whois/`，放入 Agent 的 Skills 目录并保留 scripts 与 references，无需安装 CLI。已有本地源码时，也可运行：

```bash
npx skills add /absolute/path/to/antapi-skills --skill antapi-whois
```

安装器会让你选择 Agent；加 `-g` 可全局安装，加 `--agent codex` 可指定 Codex。仅列出可用 Skill：

```bash
npx skills add /absolute/path/to/antapi-skills --list
```

这是通过 npm 分发的 [skills 安装器](https://github.com/vercel-labs/skills) 从 GitHub 获取 Skill，
无需将本仓库另行发布到 npm registry。Node.js 版本要求以安装器的官方说明为准。

本地源码或候选归档不代表正式产品发布。正式安装入口固定到已验证的 tag/commit 或 Release archive。
在 Agent 的执行环境中私下配置 `ANTAPI_KEY` 即可，Skill 默认调用 `https://api.antapi.dev`。仅在明确使用测试或开发环境时，通过可选的 `ANTAPI_GATEWAY_URL` 覆盖地址。
Skill 与 HTTP 示例使用 `ANTAPI_KEY`；可选 CLI 使用 `ANTAPI_API_KEY`，两者没有安装依赖。
不要把真实凭据放入聊天或命令参数。安装 Skill 不会创建 API key；手动复制目录不需要 Node.js。

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
`make check-release SKILLS_REF=.venv/bin/skills-ref`，空仓库必须失败。发布还必须完成独立 HTTP 联合测试与真实 Agent 任务验收。
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

`SKILL.md` 说明触发条件、API 与运行要求、流程、数量上限、错误恢复和凭据使用方式。WHOIS 随包 HTTP helper 每次只发一个请求，30 秒超时、1 MiB 响应上限，不跟随跳转、不自动重试、不默认持久化正文。

## 发布范围

本仓库仅分发面向调用方的产品 Skill。内部发布、运维和管理员 Skill 放在私有 AntAPI 项目中，不进入本仓库、安装列表或分发归档。

所有产品 Skill 使用仓库级版本/tag，与 API、CLI 独立版本。每个 Skill 声明公开 API 主版本和真实运行要求；稳定安装固定到已验证的 tag/commit 或归档。本地安装候选不会发布任何内容。CI 只验证，不在 push/tag 时自动发布。
