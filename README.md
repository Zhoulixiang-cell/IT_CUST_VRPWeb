# AI Roleplay Chat

> 一个面向“AI 角色扮演 + 语音聊天”的全栈示例工程（前端：React + Vite + Tailwind；后端：FastAPI）。

---

## 一、项目简介

* 目标：允许用户**搜索/选择角色**（如“哈利·波特”“苏格拉底”），并与该角色进行**文本/语音**的自由对话。角色回复由 LLM 生成，语音通过 TTS 输出；用户语音通过 ASR 转为文本输入。

---

## 二、目录结构（建议）

```
ai-roleplay-chat/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   └── roles.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── llm_client.py
│   │   ├── models/
│   │   │   └── role.py
│   │   ├── services/
│   │   │   ├── chat_service.py
│   │   │   ├── asr.py
│   │   │   └── tts.py
│   │   ├── storage/
│   │   │   ├── memory_store.py  # 短/长期记忆实现（Redis / SQLite / Postgres）
│   │   └── utils/
│   │       ├── prompt_templates.py
│   │       └── moderation.py
│   └── requirements.txt
├── frontend/
└── README.md
```

---

## 三、快速启动（开发环境）

**后端**：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**

```bash
cd frontend
npm install
npm run dev
```

---

## 四、后端关键接口（示例）

### 健康检查

`GET /health` -> `{ "status": "ok" }`

### 文本聊天（同步）

`POST /chat/` 请求体：

```json
{ "role": "哈利波特", "message": "你好" }
```

返回：

```json
{ "reply": "..." }
```

### 实时/流式聊天（建议用于语音）

`WS /ws/chat`：

* 建议协议：建立 WebSocket -> 发送 `{"type":"start","role":"苏格拉底","mode":"voice"}` -> 客户端把录音片段以 base64 发送 -> 后端拼接/转写（ASR）-> 调用 LLM -> 将 TTS 音频片段流回客户端。

### 角色管理

`GET /roles/`（搜索/分页）
`POST /roles/`（新增角色）
`GET /roles/{id}`（读取角色详情）

---

## 五、核心后端模块说明（重点）

### 1. `core/llm_client.py`（抽象并多厂商适配）

* 目的：统一调用不同 LLM 的接口（OpenAI / Anthropic / Mistral / 本地模型）。
* 要点：

  * 支持同步与流式调用
  * 支持 prompt-template 注入：role profile + conversation history + system instructions
  * 支持安全检查（moderation）和 token 计数/限额

### 2. `services/chat_service.py`

* 目的：管理一次会话的全部逻辑。
* 职责：

  * 维护会话上下文（短期历史）
  * 与 memory\_store 协作（短期→Redis，长期→Postgres/文件）
  * 拼装 prompt（注入角色 persona、记忆、系统指令）
  * 调用 llm\_client，并在结果上运行后处理（包括敏感内容过滤）

### 3. `services/asr.py` / `services/tts.py`

* ASR：把用户上传的音频或流转为文本（可选：边录边转，或录满 N 秒再转）。
* TTS：把 LLM 回复从文本生成语音，并以小片段或完整音频返回给前端。

### 4. `storage/memory_store.py`

* 用途：实现“短期记忆（conversation window）”和“长期记忆（persona facts）”。
* 推荐：短期使用 Redis（TTL、列表），长期使用 Postgres/SQLite（可按角色做索引）。

### 5. `utils/prompt_templates.py`

* 维护所有角色模板和技能模板（Socratic、讲故事、测验等），以便复用与 A/B 测试。

---

## 六、目标用户 / 痛点 / 用户故事

### 目标用户（示例）

1. **角色扮演爱好者 / 二创作者**：喜欢与虚拟角色互动、写同人、做 cosplay 的人。需求：高拟真、持续对话的角色体验。
2. **语言学习者 / 老师**：需要用虚拟角色做对话练习或模拟场景教学。需求：可控制话风与难度，支持纠错与解释。
3. **内容创作者 / 游戏设计师**：想快速生成对话片段、角色对白、世界观细节。需求：定制化输出与导出功能。
4. **无障碍用户 / 视障者**：依赖语音交互，需要清楚、可控的语音输出与字幕。


### 用户故事（样例）

* **场景 A（学习）**：王同学想跟“苏格拉底”练习哲学讨论，他要求对方用 Socratic 提问方式，遇到专业术语时给予解释并在会话结束时给出笔记。
* **场景 B（娱乐）**：小李想和“哈利·波特”聊一段原创故事，并要求角色保持自己性格与既有世界观的合理性。
* **场景 C（辅助）**：盲人用户张先生通过语音与“导游”角色交互，角色需要把景点描述成口头导航并提供短链接到导览文本。

---

## 七、功能清单与优先级（开发建议）

> 优先级标识：**H=高（必须） M=中（增强体验） L=低（可选/迭代）**

1. **基础文本聊天（H）**：用户选择角色，文本问答。已实现骨架。
2. **语音输入（ASR）+ 简单 TTS（H）**：实现语音转文本与文本转语音的闭环。
3. **角色管理与搜索（H）**：角色元数据、标签、搜索排序。
4. **会话短期记忆（H）**：保持对话上下文（N-turn sliding window）。
5. **角色长期记忆（M）**：保存用户与角色互动的重要事实（偏好、背景设定）。
6. **角色技能（M）**：以下 3+ 技能（见下一节）
7. **安全/审查 pipeline（H）**：在线内容检测、脱敏策略、日志记录。
8. **流式/低延迟体验（M）**：WebSocket + 分段 ASR/TTS。
9. **多声音色与选项（M）**：用户可选择不同的 TTS 声音或上传自定义声音（合规前提）。
10. **导出/保存对话（L）**：导出为文本/音频/脚本。

---



## 八、后端可补充/强化的部分（着重于后端，建议清单）

> 以下按重要性罗列：

1. **多厂商 LLM 适配层（高）** — `core/llm_client.py`

   * 理由：为未来切换模型、对比性能、做降级容错提供接口。
   * 要点：抽象化 API 调用、增加重试与降级策略、token 计数器。

2. **会话与长期记忆存储（高）** — `storage/memory_store.py`

   * 建议：Redis（短期）+ Postgres（长期），并提供 memory summarization（定期把 long chat 摘要写入长期记忆）。

3. **流式 WebSocket 支持（中）** — `ws/chat_ws.py`

   * 建议实现：单向或双向流（ASR → LLM → TTS 分段流回），并提供心跳与连接恢复机制。

4. **审查与内容策略（高）** — `utils/moderation.py`

   * 必要性：语音/文本可能包含敏感或违法内容，必须在输出前做过滤和脱敏。

5. **角色管理后台（中）** — 增加 admin API、角色导入导出与版本管理。

6. **鉴权/计费与速率限制（中）** — JWT + API Key + rate-limit（Redis）以防滥用。

7. **日志/监控/告警（中）** — structured logging、Prometheus metrics、Sentry 错误收集。

8. **自动化测试（高）** — 单元测试（prompt 模板）、集成测试（API 流程）、端到端测试（emulated voice flow）。

9. **部署脚本（高）** — Dockerfile、docker-compose、Kubernetes manifests 与 CI/CD（GitHub Actions）。

10. **隐私与合规（高）** — 明确语音/文本保存策略、用户授权、数据删除接口。

---

## 九、API 示例（快速参考）

### 文本聊天（POST）

```
POST http://localhost:8000/chat/
Content-Type: application/json

{ "role": "苏格拉底", "message": "什么是美德？" }
```

返回：

```json
{ "reply": "（苏格拉底式回答）..." }
```



## 十、部署建议

* 使用 Docker 打包后端镜像
* 生产环境：Kubernetes + Horizontal Pod Autoscaler（基于 CPU/请求速率）
* 使用负载均衡与 CDN（对 TTS 音频做缓存）
* 将短期交互缓存（Redis）与长期存储（Postgres）分离，便于扩展

---

## 十一、贡献 & 联系

欢迎按 issue/PR 讨论功能改进与 bug 修复。建议先在 `./docs/` 编写 API 扩展说明，再发 PR。

---


<!-- end -->
