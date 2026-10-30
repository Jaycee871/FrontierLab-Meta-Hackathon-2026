# 研究操作介面（Research Operating Interface）— 繁體中文說明與示意概念

本文是 [Research Operating Interface](RESEARCH_OPERATING_INTERFACE.md) 的繁體中文說明版，由 Pack Kwan Low / Jaycee871 的簡報內容整理而成。英文版記錄的是 FrontierLab 目前的模組狀態與實測指標；本文則說明這個構想從哪裡來、想解決什麼問題，以及哪些部分只是示意。

兩份文件內容有重疊，但**不互相取代**。如果兩者對 FrontierLab 現況的描述有出入，以英文版與程式碼為準。

## 閱讀前：三種說法的標記方式

這份文件混合了三種性質不同的說法。為了不讓它們混在一起，每一節標題下方都會標出它屬於哪一種：

| 標記 | 意思 | 不代表什麼 |
| --- | --- | --- |
| **【文獻】** | 來自引用的文獻，例如 Paper2Agent 及其列出的相關方法。這是作者簡報中對文獻的摘要，本文沒有重新逐字核對原文。 | 不代表 FrontierLab 已經做到。 |
| **【作者前瞻】** | 原始文獻作者提出的前瞻主張（forward-looking proposal）。 | **不是**已公布的政策、期刊規定或既有制度。 |
| **【延伸觀點】** | Jaycee 從資訊管理（Information Management）角度提出的個人延伸。 | **不是**任何論文驗證過的結論。 |

另外還有一個專門的警示標記：

> **【示意數字】** 這個標記出現的地方，數字只是介面示意圖（mock-up）上的範例，**不是實測結果**。

一節裡如果混有不同性質的內容，會在該段落前個別標出。

---

## 1. 研究成果可以成為可操作的代理

### 1.1 論文不必停在 PDF 與程式碼庫

**【文獻】**

一篇論文不一定只能停在 PDF 檔和一個原始碼庫（source repository）。

這裡的**研究產物（research artefact）**，指的是一篇論文產出的所有東西，包括資料、程式碼和工具，而不只是文字。Paper2Agent 這類工作的重點是：這些研究產物現在可以被「操作」，也就是讓人透過一個互動代理（agent）直接使用論文裡的方法。

### 1.2 自動驗證是可信 Paper Agent 的核心

**【文獻】**

**自動驗證（automatic validation）**是可信的論文代理（Paper Agent）的核心。

它和**可重現性（reproducibility）**密切相關。可重現性的意思是：別人在相同條件下重做一次，會得到相同的結果，就像同一份食譜應該做出同一道菜。

### 1.3 代理可用性（Agent Availability）聲明

**【作者前瞻】** — 這是原始文獻作者的前瞻主張，**不是已公布的政策**。

跨論文的代理，可能形成一種新的研究協作模式。

現在很多期刊會要求「資料可用性（data availability）」和「程式碼可用性（code availability）」聲明。作者的設想是，未來可能再多一項**代理可用性（Agent Availability）**聲明，說明這篇論文有沒有可以互動的代理。

目前沒有任何期刊把它列為必要項目。本文只把它當作一個值得討論的方向。FrontierLab 另外寫了一份格式草案，見 [Agent Availability statement proposal](AGENT_AVAILABILITY_STATEMENT.md)，那份草案同樣只是提案。

---

## 2. 三個資訊管理面向

**【延伸觀點】** — 以下三點是 Jaycee 的個人延伸，**不是論文驗證過的結論**。它們也是他自己在做生醫 AI 治理與系統整合時實際遇到的問題。

### 2.1 可維護性（maintainability）

問題：工具壞掉的時候，系統能不能自己發現，並且自動重建？

舉例來說，某個套件升級之後，系統應該自己跑測試、發現失敗、嘗試修復，而不是等到使用者操作時碰到錯誤才知道。

### 2.2 可追溯性（provenance）

可追溯性是記錄資料、工具和結果的來源歷史。它很像食品產銷履歷：拿起一包菜，可以查到它來自哪個農場、哪一批。

放到代理身上，就是每一次執行都要保留：

- 用了哪個工具版本；
- 用了哪些參數；
- 用了哪個資料集；
- 用了哪個模型。

這些紀錄串起來就是一條證據鏈。如果有人引用了代理產出的一張圖，審稿人想要查證時，可以一路追回去。

### 2.3 研究治理（governance）

研究治理是管理權限與責任的規則。例如：

- 一個可以執行程式碼的代理，有沒有權限碰病患資料？
- 哪些工具開放給哪些人使用？
- 出了問題，責任在研究者、研究機構，還是工具開發者？

這些規則需要研究機構事先訂好，而不是出事之後才補。

---

## 3. 研究延伸構想：研究操作介面（DEMO CONCEPT）

**【延伸觀點】** 整節都是示意性概念（demo concept）。

> **【示意數字】** 本節出現的「**12 份來源稽核（source audits）**」和「**98% 追蹤覆蓋率（trace coverage）**」是示意用的數字，**不是實測結果**。它們沒有在任何系統上量測過。

可以把這一節想成建築師的透視圖（architect's rendering）：它讓你看到「如果蓋好了，大概長這樣」，但房子還沒有蓋。

### 3.1 為什麼叫「操作系統」

手機的作業系統（operating system）不是某一個 App，而是管理所有 App、權限，以及資料怎麼流動的那一層。

這裡設想的未來論文代理也一樣。它不是一個單獨的問答工具，而是把論文、程式碼、資料和工具放在同一個地方管理，讓它們**看得見、可稽核、可治理**。

### 3.2 架構：一個 Core 加八個模組

中間是 **Core**，也就是系統的核心引擎。周圍有八個模組，分成三組：

```text
                 研究操作介面（示意）
                         |
       --------------------------------------
       |                 |                  |
    研究材料          MCP 三件組        資訊管理味最重的兩個
 Paper / Code /   MCP Tools /         Evidence Trace
     Data         MCP Resources /     Governance
                  MCP Prompts
       |                 |                  |
       ----------------- Core ---------------
```

**第一組：研究材料**

| 模組 | 角色 |
| --- | --- |
| **Paper** | 文獻輸入與知識來源。 |
| **Code** | 可以執行的分析方法。 |
| **Data** | 資料集、資料庫，或透過 API 取得的外部資料。 |

API（Application Programming Interface，應用程式介面）可以想成餐廳的菜單：系統照著菜單點一道「外部資料庫」的菜，對方就把資料送過來。

**第二組：MCP 三件組**

MCP（Model Context Protocol）可以想成 AI 世界的 USB-C：一個統一的接頭，讓代理接上各種外部能力。

| 模組 | 比喻 |
| --- | --- |
| **MCP Tools**（工具） | 計算機上的按鈕，按下去就執行一個動作。 |
| **MCP Resources**（資源） | 放參考資料的書架。 |
| **MCP Prompts**（提示） | 一張食譜卡，寫好固定的做事步驟。 |

在這個介面裡，三者被放進同一個管理畫面。

**第三組：最有資訊管理味的兩個模組**

| 模組 | 角色 |
| --- | --- |
| **Evidence Trace**（證據追蹤） | 系統說出的每一個結論，都留下它從哪裡來。就像論文的註腳，或是一張之後可以拿來對帳的購物收據。 |
| **Governance**（治理） | 安全、規範與合規：誰可以用哪個工具、能不能碰病患資料、使用某些資料時是否必須留紀錄。 |

### 3.3 一個問題進來之後：Research Workflow 四步驟

研究者問一個沒有標準答案的開放問題，例如：

> 「有什麼證據可以支持某一個生醫研究假說？」

系統不會只回一句話，而是進入**研究流程（Research Workflow）**，分四步：

1. **Interpret Query（解讀問題）**  
   先確認到底在問什麼、範圍多大。例如「生醫研究假說」指的是哪一種疾病、哪一個基因。

2. **Search & Retrieve（搜尋與擷取）**  
   從多個來源找證據。示意畫面上的 **Active Sources** 列出 PubMed（生醫文獻資料庫）、arXiv（預印本平台）、IEEE（電機電子與工程領域文獻）和 Nature，後面還有另外三個。  
   這就是**多來源（multi-source）**：不只依賴單一資料庫，就像做調查不會只問一個人。

3. **Analyze & Synthesize（分析與整合）**  
   把不同來源的內容整合起來，使用**證據圖譜（Evidence Graph）**。證據圖譜是一張關係圖：每個結論是一個節點，連到支持它的論文和資料。如果兩篇論文的結論互相衝突，在圖上也看得出來。

4. **Generate Output（產生輸出）**  
   產出一份結構化報告，每一個重要主張都附上引用來源。

### 3.4 介面上的狀態讀數

**System Status（系統狀態）**  
右上角的系統狀態像飛機的儀表板，告訴你研究代理準備好了沒、證據圖譜是不是正在運作。

**Source Audit（來源稽核）**  
像會計的對帳：確認引用的來源真的存在，而且真的說了報告裡宣稱它說的話。

> **【示意數字】** 示意畫面上的「12 份來源稽核」是範例數字，不是實測結果。

**Trace Coverage（追蹤覆蓋率）**  
報告裡的主張中，有多少比例可以一路追回原始來源。以 98% 為例，意思是每 100 個重要結論裡，有 98 個找得到出處。

> **【示意數字】** 「98% 追蹤覆蓋率」只是用來解釋這個指標的範例，**不是任何系統量測出來的數字**。FrontierLab 實際量到的數值見第 5 節，兩者無關。

**底部狀態列：Current Activity、Active Sources、Agent Reasoning**

這三格回答的其實是同一件事：

- 代理現在正在做什麼；
- 它用了哪些來源；
- 它走到了哪一步。

示意畫面顯示的是第 2 步：正在搜尋生醫文獻。

重點是：未來重要的不只是模型答對了沒有，還有**它是怎麼得出答案的，以及這個過程能不能被檢查**。

---

## 4. 五個值得研究的方向

**【延伸觀點】** — 以下五個方向是 Jaycee 從資訊管理角度提出的個人看法，**不是論文驗證過的結論**。

| 方向 | 要回答的問題 |
| --- | --- |
| **系統整合（system integration）** | 怎麼把論文、程式碼、資料庫和各種 MCP 工具接在一起？例如把研究機構內部的資料系統接上外部文獻資料庫。 |
| **流程治理（workflow governance）** | 在四步驟流程裡，誰負責、誰核准、哪一步需要人來看？ |
| **來源稽核（source auditing）** | 能不能自動檢查引用是不是真的存在、是不是最新的？ |
| **證據追蹤（evidence traceability）** | 每一個結論能不能追回原始論文或資料？ |
| **人機協作（human-in-the-loop）** | AI 提出十種驗證策略，由研究者挑一種；關鍵決定留在人手上。 |

如果這幾件事做得好，代理就不只是一個回答問題的工具，而會更接近一個真正支援研究工作的作業系統。

---

## 5. 對照：FrontierLab 現在做到哪裡

本節只寫在程式碼裡查得到的東西。FrontierLab 的自主程度定位不變：它是 **Level 1 Assisted Pipeline（輔助式流程）**，模型負責固定角色，階段之間的推進由程式和研究者控制，見 [agentic-AI landscape and self-assessment](AGENTIC_AI_LANDSCAPE.md)。下表把第 4 節的五個方向對到目前的實作，不代表任何一個方向已經解決。

| 方向 | FrontierLab 已有的部分 | 還沒有的部分 |
| --- | --- | --- |
| 系統整合 | 文獻來源接了 Europe PMC，以及 Springer Nature Meta API、Open Access API（`frontierlab/discovery.py`）；多來源合併用 DOI 去重（`frontierlab/multisource.py`）。 | 第 3 節示意畫面上的 PubMed、arXiv、IEEE 並沒有直接接上。沒有機構內部資料系統的整合，也沒有一般性的 MCP 工具管理。 |
| 流程治理 | 人工主張審查、研究者選擇方法、明確核准第 5 階段（Planning）、逐步核准計畫步驟、模型呼叫次數上限。 | 沒有機構層級的角色權限控管（RBAC），也沒有病患資料存取政策的強制執行。 |
| 來源稽核 | 主張必須引用已知來源 ID，引文必須能在原始摘要裡定位到（fail-closed，找不到就擋下）。`frontierlab/traceability.py` 提供 `source_audit_summary`。 | 不檢查引用是不是「最新的」。EXTRACTED 只證明那段文字存在，**不證明主張真的從那段文字推得出來**。 |
| 證據追蹤 | 證據圖譜（`frontierlab/evidence_graph.py`，schema `frontierlab.evidence-graph.v2`）：Paper ← Passage ← Claim ← Hypothesis ← PlanStep，每條邊標 EXTRACTED / INFERRED / AMBIGUOUS；主張、假說和計畫步驟節點的 ID 由內容雜湊（SHA-256）產生；每個 Paper 帶 `source_fingerprint`；核准紀錄帶 `approval_digest`；`load_graph()` 檢查不通過就拒絕載入。 | `graph.json` 沒有簽章；一個把所有雜湊都重算過的偽造檔，只有拿可信的 run 比對（`expected_fingerprints`）時才擋得住。 |
| 人機協作 | `step_gate()` 只在路徑全部是 EXTRACTED、而且所有引用來源都追得到時才允許核准；`approve_plan_step()` 要求審查者姓名和至少 8 個字元的理由。 | 核准紀錄沒有數位簽章。 |

**追蹤覆蓋率的實測值（和第 3 節的 98% 無關）**

FrontierLab 已經在 `frontierlab/traceability.py` 實作了兩個追蹤指標。在已審查的 M2 紀錄上量到：

- Source Trace Coverage（來源可追溯比例）：4 / 4 = **100%**；
- Strict Extracted Coverage（全程 EXTRACTED 比例）：2 / 4 = **50%**。

這是在 4 個項目上量到的值，樣本非常小，而且衡量的是來源可追溯性，**不是模型準確度或科學正確性**。詳見 [Trace Coverage](TRACE_COVERAGE.md)。

**可維護性（對應第 2.1 節）**

目前有排程執行的 Maintenance Canary（`frontierlab/maintenance.py`、`.github/workflows/maintenance-canary.yml`）：記錄套件版本與相依指紋，跑完整回歸測試，失敗時標成 `QUARANTINE_REQUIRED`。

第 2.1 節設想的「自動修復、自動重建」**沒有實作**。程式碼裡 `automatic_repair_enabled` 和 `automatic_environment_rebuild_enabled` 都是 `False`，修復必須由人核准。詳見 [Maintenance canary](MAINTENANCE_CANARY.md)。

---

## 參考資料與討論

**【文獻】**

### DOI 是什麼

**DOI（Digital Object Identifier，數位物件識別碼）**可以想成一篇論文的身分證字號。就算期刊網站每年搬家，只要用 doi.org 加上那串號碼，還是找得到同一篇論文。

### 相關方法

簡報中列出三篇相關方法論文：

- **AlphaGenome**（Nature 2026）
- **Scanpy**（Genome Biology 2018）
- **TISSUE**（Nature Methods 2024）

### 程式碼與部署

- **Paper2Agent** 的程式碼公開在 GitHub。
- AlphaGenome、Scanpy 和 TISSUE 的代理都部署在 Hugging Face。

以上依簡報原文列出，本文沒有另外查證。

> **待補：** 上面三篇論文的完整書目資料（作者、卷期、頁碼、DOI）和各代理的網址還沒有填入。本文刻意不自行補上，避免寫出錯的引用。Paper2Agent 本身的書目見 [Information Management extension](INFORMATION_MANAGEMENT_EXTENSION.md#references)。
