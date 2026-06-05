醫療器材法規智慧工作坊技術規格書
Medical Device Regulatory Intelligence Workspace: Technical Specification
1. 執行摘要與系統概述 (Executive Summary & System Overview)
本技術規格書定義了「醫療器材法規智慧工作坊 (Medical Device Regulatory Intelligence Workspace)」的架構、模組與功能規範。這是一個專為醫療器材法規專員 (RA)、品質管理主管 (QA) 以及醫材軟體 (SaMD) 開發團隊設計的智慧型協同撰寫、自動合規對照與法規路徑分析系統。

本系統聚焦於美國食品藥物管理局 (FDA) 與台灣衛生福利部食品藥物管理署 (TFDA) 的雙規跨境申報（主要為 FDA 510(k) 與 TFDA 查驗登記門檻等同性證明），並完美支援 2026 年最新技術與資訊標準。

1.1 核心設計原則
事實查證為本 (Grounded and Truthful)：系統輸出具有極高的可信賴度，全面對齊所載入的產品規格、技術文檔及官方查驗登記指引（台灣衛福部《醫療器材管理法》指引與美國 FDA guidance），全面杜絕大語言模型 (LLM) 產生的幻覺 (Hallucination)。

多代理人協調 (Multi-Agent Orchestration)：利用 agents.yaml 作為核心控制配置文件，解耦不同合規任務。系統會讀取 skill.md 獲取通用行為限制、特定專用術語和格式約束，以此動態拼裝成 Master System Instruction 調用 API。

雙語無縫整合 (Seamless Bilingual Experience)：本系統不只在介面上具備一鍵雙語切換（繁體中文 / 英文），其輸出的所有報告、對照表和句式轉換均能完美體現中英法規術語的精確映射（如「Substantial Equivalence」對譯「實體等同性」）。

低摩擦部署 (Zero-Config Portability)：採用輕量化、敏捷的 Web App 容器架構部署於宿主環境，即便在無外部 API Key 的極限斷網情況下，亦能依靠強大的「本地法規模擬引擎 (Local Regulatory Fallback Engine)」和預設快取範本正常顯示與運作，確保不會造成介面崩潰或資料丟失。

2. 系統邏輯架構 (System Architecture & Logical Layers)
系統劃分為四大邏輯層，將 UI 呈現、任務編排、AI 推論與靜態資產徹底解耦，以提升維護性：

code
Code
+-----------------------------------------------------------------------------------+
|                            呈現層 (Presentation Layer)                            |
|       Streamlit UI / 雙語切換 / 主題預設 (20 款 Pantone 系列) / 即時運行紀錄 (Log)     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            編排層 (Orchestration Layer)                           |
|   Session State 狀態管理器 / 代理人選擇器 (YAML 解析) / 6000字雙語上下文切片引擎   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            智能層 (Intelligence Layer)                            |
|    Gemini 3.5 (google-genai SDK) / OpenAI GPT-4o / 5項經典魔法與6項客製化 WOW 功能 |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            資產與IO層 (Data & Asset Layer)                        |
| agents.yaml / skill.md / utf-8-sig CSV 匯入匯出 / 系統與使用者 Session 臨時快取   |
+-----------------------------------------------------------------------------------+
2.1 數據流生命週期 (Data Flow Lifecycle)
上傳與字數截斷：用戶將非結構化的設計說明書或臨床文字黏貼，系統將其處理為全域作用中上下文（active_context）。若英文超過 6,000 單字、中文超過 6,000 字元，發出前台警示，但在 Session State 中保留完整無損文本供 API 推論。

載入代理人設定與行為約束：系統解析 agents.yaml 以提供動態代理人角色選擇，並導入 skill.md 全域限制。

編譯 Master System Instruction：動態將當前 Agent 的 role、skills 與 skill.md 行為準則拼裝成系統指令，以此發起模型推論。

執行與本地合成降級防衛：調用 API 推論。若偵測到金鑰缺失或限流報錯，即刻啟用 Simulated Engine 根據內置專家模板進行語意合成。

資料輸出與高亮：渲染 Markdown，利用 CSS 高亮核心條目，並可一鍵導出帶有 utf-8-sig 的 Excel 相容 CSV、JSON 或 DHF 電子簽章。

3. 部署環境與關鍵依賴 (Deployment & Dependency Specifications)
本系統與部署容器環境高度適配，並遵循 2026 年最新 Python 生態相容性規範。

3.1 關鍵依賴套件 (requirements.txt / package.json)
code
Text
streamlit>=1.30.0
pyyaml>=6.0
pandas>=2.0.0
openai>=1.10.0
google-genai>=2.4.0
(注意：嚴格淘汰 legacy google-generativeai 舊版 SDK，使用全新原生 google-genai SDK 作為 Gemini 3.5 推論標準)

3.2 Session State 關鍵狀態樹
狀態鍵名 (Key)	資料類型 (Type)	預設值 (Default)	職責與用途 (Description)
lang	str	"en"	目前介面語系（en / zh_tw）
theme_mode	str	"Light"	亮色與暗色模式狀態（Light / Dark）
style_preset	str	"coral haze"	20 款精細 Pantone 風格主題名稱
logs	list	[timestamp + init_msg]	即時日誌隊列，僅保留最新 10 筆
active_context	str	""	當前作用中的產品設計規格與背景文檔
agents_yaml	str	(內置 YAML 字串)	可編輯的代理人角色設定
skill_md	str	(內置 Markdown 字串)	全域合規約束指南
tfda_checklist_df	pd.DataFrame	(5筆符合性預設欄位)	查驗登記符合性清單互動編輯器的 DataFrame 綁定
reports_generated	dict	{}	快取各功能模組已生成的歷史報告快照
4. WOW 視覺體驗與全域 UI 設計 (WOW User Experience & Styling)
4.1 20 款 Pantone 精緻風格預設 (The 20 Style Presets)
本系統內置 20 款細心揉合的專業 Pantone Style 預設：

code
Python
STYLE_PRESETS = {
    "coral haze": {"bg": "#FAF9F6", "surface": "#F5EBE6", "accent": "#FF7F50", "text": "#2C2C2C"},
    "cobalt tide": {"bg": "#F0F4F8", "surface": "#D9E2EC", "accent": "#0047AB", "text": "#102A43"},
    "emerald graphite": {"bg": "#F4F6F4", "surface": "#E1E6E1", "accent": "#0B6623", "text": "#223322"},
    "amber slate": {"bg": "#F9F7F1", "surface": "#EFEBE0", "accent": "#D97706", "text": "#2D251E"},
    "lavender mist": {"bg": "#F6F5F7", "surface": "#ECE9EE", "accent": "#8A2BE2", "text": "#2E1A47"},
    "ocean mint": {"bg": "#F2F8F6", "surface": "#E2F0EC", "accent": "#00A86B", "text": "#0F2F23"},
    "terracotta dusk": {"bg": "#F8F2F0", "surface": "#EFE1DD", "accent": "#C24E3A", "text": "#3A1B14"},
    "icy rose": {"bg": "#FAF5F6", "surface": "#F4EAEB", "accent": "#D16587", "text": "#3B1825"},
    "citrus ink": {"bg": "#FBFBF8", "surface": "#F5F5EC", "accent": "#FFA700", "text": "#2A2A1A"},
    "orchid smoke": {"bg": "#F5F3F5", "surface": "#EAE5EA", "accent": "#9E5E9E", "text": "#2A182A"},
    "jade noir": {"bg": "#F1F5F2", "surface": "#E0EAE2", "accent": "#006400", "text": "#0B1D12"},
    "saffron pearl": {"bg": "#FAF9F5", "surface": "#F4EFE0", "accent": "#F4C430", "text": "#2C2A1E"},
    "ultramarine fog": {"bg": "#F2F4F8", "surface": "#E1E6F0", "accent": "#120A8F", "text": "#050230"},
    "sand chrome": {"bg": "#F6F6F4", "surface": "#ECECE6", "accent": "#C2B280", "text": "#2B2B2A"},
    "plum steel": {"bg": "#F4F2F5", "surface": "#E7E3EA", "accent": "#4B0082", "text": "#220530"},
    "basil ivory": {"bg": "#F7F8F5", "surface": "#ECEFE8", "accent": "#579229", "text": "#1A2E0E"},
    "ruby ash": {"bg": "#F9F4F4", "surface": "#EFE2E2", "accent": "#E0115F", "text": "#3B081A"},
    "teal quartz": {"bg": "#F0F6F7", "surface": "#DDECEF", "accent": "#008080", "text": "#032828"},
    "honey basalt": {"bg": "#F8F6F1", "surface": "#EFECE1", "accent": "#E5A65D", "text": "#2E2416"},
    "violet linen": {"bg": "#F6F4F8", "surface": "#EBE5F2", "accent": "#7F00FF", "text": "#20033B"}
}
4.2 Jackslot 隨機主題切換器與 CSS 注入
在側邊欄提供一個下拉式選單與一鍵「🎰 隨機切換主題風格」按鈕。一旦觸發，系統會自動在 st.session_state.style_preset 中變更選取的色調，並利用 st.markdown(unsafe_allow_html=True) 注入客製化的 CSS 屬性，全面覆寫 Streamlit 的卡片、按鈕與文字標籤背景：

code
CSS
<style>
:root {
    --bg-color: {preset_bg};
    --surface-color: {preset_surface};
    --accent-color: {preset_accent};
    --text-color: {preset_text};
}
.stApp {
    background-color: var(--bg-color) !important;
    color: var(--text-color) !important;
}
.custom-card {
    background-color: var(--surface-color);
    border-radius: 10px;
    padding: 1.25rem;
    border-left: 5px solid var(--accent-color);
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.coral-highlight {
    color: #FF7F50 !important;
    font-weight: bold;
    background-color: rgba(255, 127, 80, 0.1);
    padding: 1px 4px;
    border-radius: 3px;
}
</style>
4.3 即時日誌控管中心 (Live Activity Log)
側邊欄的最下方設有「即時運行紀錄」文字框。每當使用者執行資料載入、主動切換 Agent 角色、導出報告或 API 連線失敗時，系統會立即生成帶有秒級時戳（例如 [10:15:32]）的 Log 並追加入狀態隊列中，供使用者進行除錯與流程審計。

5. 互動式狀態儀表板 (State Monitoring Dashboard)
儀表板是系統的首頁，可實時反饋整個工作坊的配置健康度，分為以下幾個子系統：

核心指標列 (Metric Grid)：橫向展示「選取的主題預設」、「當下調用模型 (Gemini 3.5 Flash 預設)」、「API 連線完整度」以及「作用中上下文狀態」。

運行健康診斷表 (Validation Checklists)：

若 agents.yaml 語法解析完全正確：顯示 🟢 agents.yaml Validated

若 skill.md 關鍵標籤完整：顯示 🟢 skill.md Integrated

若未檢測到線上 API Key：顯示 🟡 Attention: Offline Fallback Active (提示系統已切換至無金鑰模擬模式，防止輸入丟失)。

分析與指標趨勢圖 (Analytical Trends)：展示模擬數據（如：文獻查證接地率 98%、條款等同性比對一致度、TFDA 合規項佔比等）之變化趨勢。

6. 核心功能模組技術規格 (Core Functional Modules)
6.1 檔案與上下文分析器 (Document Analyzer)
職責：接收 unstructured、不規則之設計檔案或臨床筆記，並建立全域統一的「作用中上下文 (Active Context)」。

字數控制規格：

英文：以 text.split() 計算單字量，超過 6,000 單字時，前台預覽會利用 join() 截斷展示，並在 UI 發出醒目的黃色警告。

中文：直接計算字元長度 (Characters)，超過 6,000 字元時自動截斷展示。

儲存：完整的 6,000 字/字元以上內容，會 100% 留存在 Session 內，確保調用 API 時技術細節不會遺失。

6.2 法規可行性分析報告 (Regulatory Feasibility Report)
職責：分析目標產品在美台雙邊合規框架下的可行性路徑與差距。

輸出架構：

雙規路徑診斷（FDA 510(k) vs. TFDA 查驗登記門檻）

臨床與非臨床評估差異

實體等同性核心等同性 / 差異分析 (Substantial Equivalence analysis)

缺失缺口與補測清單 (Gap Matrix) - 與後端時程及 TFDA Checklist 自動關聯。

6.3 TFDA 查驗登記符合性清單 (TFDA Checklist Generator)
與 Feasibility 自動關聯機制：此為系統的一大提升點。當 Feasibility 分析完成後，系統會主動提取報告中的 「關鍵缺失 / 補測清單 (Gap Matrix)」，並依此自動初始化並產出對應台灣 TFDA 醫療器材查驗登記 標準模態的符合性查核條目（而非隨機的空表格）。

資料交互架構：採用 st.data_editor 渲染，表格內容與 st.session_state.tfda_checklist_df 即時綁定，支援行列的動態增加與刪除。

數據匯入 (Upload)：支援 CSV 檔案上傳。系統會自動利用 Pandas 讀取上傳內容，並比對欄位名稱是否包含 "Requirement Item", "Compliance Status", "Traceability Reference File"，驗證通過後覆寫至 Session State。

數據匯出 (Download)：點擊導出按鈕後，會將 Pandas DataFrame 轉換為帶有 utf-8-sig（帶有 BOM 的 UTF-8 格式）的 CSV 字串。這確保使用者下載後直接使用 Microsoft Excel 開啟時，繁體中文字元能被正確渲染而不產生亂碼。

6.4 風險評估分類器 (Risk Classifier)
輸入指標：接觸性質（時間、途徑、主動/防護/被動能量傳輸）與解剖路徑。

輸出指標：推測最可能之安全分級（Class I/II/III）及對應法規依據（如 ISO 14971），並列出必須補充的生物學或電氣安全測試建議。

6.5 實體等同性比對 (Predicate Finder)
功能：對比目標產品與已上市對照產品 (Predicate Device) 在核心技術參數（主要原理、電氣特性、軟體演算法、材料等）與預期用途上的一致度。

輸出樣式：自動產出 3x3 對照矩陣，並挑出其非實質等同 (Non-SE) 的核心技術不一致因素。

6.6 合規時程路徑圖 (Compliance Roadmap)
自動衍生時程邏輯：系統在生成 Roadmap 時，會動態掃描 Feasibility 生產出的 Gap 嚴重程度。例如，判定若缺少「電氣安全暨電磁相容 (IEC 60601-1 / 60601-1-2) 報告」，便會自動將時程中的 Verification 階段時間拉長 3-6 個月，並在預算項目中主動加上第三方檢測實驗室規費。

三大階段分期規則：

Verification (驗證階段)：實驗室測試（安全、生物相容性）、軟體確效（IEC 62304）。

Submission (申報審查階段)：文件彙整、規費（FDA eSTAR 規費、TFDA 規費）、回覆官方補件說明（AI 模擬 Q-Submission）。

Launch (上市後追蹤階段)：UDI (唯一器材識別) 設定、MDR/MPS 申報機制建立。

預算與規費精準估算：結合 GHTF 指引與最新規費，並給出台幣與美金雙幣動態計算。

7. 代理人與行為準則工作室 (Agent & Skill Studio)
此模組是實現「人機協同合規設計」的核心樞紐。

7.1 代理人定義檔 (agents.yaml) 規格
提供程式碼編輯器編輯 YAML。當呼叫 API 時會動態利用下方的解析邏輯提取最新變更：

code
Yaml
version: 1.2.0
agents:
  - name: "FDA 510(k) 實體等同性分析官"
    role: "評估申報器材與已上市對照品在預期用途上的等同性，並撰寫實體等同性論證報告。"
    skills: [ "對照品比對", "510(k) 申報文件生成", "FDA eSTAR 對齊" ]
  - name: "TFDA 查驗登記輔導大師"
    role: "專攻台灣醫療器材管理法，輔導廠商準備說明書、結構規格、功能測試及臨床評估報告。"
    skills: [ "TFDA符合性查核", "中英文醫療名詞精準翻譯", "國內外法規對比" ]
7.2 行為準則約束檔 (skill.md) 規格
使用者可以自由在 Studio 中修訂 skill.md。此檔案會定義全局的合規約束，例如限制模型絕對不可無據捏造 (No Hallucination)、強制在輸出中將特定台灣醫材用語（如「實體等同性」非「實質等同性」）翻譯校正，並規定型號與標準名稱必須以珊瑚橘 (<span class='coral-highlight'>) 包裹。

7.3 多代理人動態路由與 Master System Instruction 融合演算法
當用戶點擊任何核心模組的「自動生成」按鈕時，系統會在後端運行以下融合演算法：

抓取用戶在 UI 下拉選單中選取之當前 Agent 名。

開發 Python 解析器解析當前的 agents.yaml 文字檔，抓取對應 Agent 的 role、skills 列表。

抓取 st.session_state.skill_md 中的最新文本，並將其合併為 Master System Instruction：

code
Markdown
# EXECUTIVE PERSONA
You are executing this task as the following specialized agent:
- **Agent Name**: {active_agent_name}
- **Your Role**: {agent_role}
- **Your Specific Skills**: {', '.join(agent_skills)}

# BASE INSTRUCTIONS
{system_instruction}

# GLOBAL COMPLIANCE RULES & CONSTRAINTS (From skill.md)
{global_rules}
將編譯完成的 Master System Instruction 傳遞給 google-genai SDK，使最終的回答格式、法規邊際界線、名詞術語嚴格受到 skill.md 與 agents.yaml 的精確約束。

8. 智慧特色功能 (The Five AI Magics & Six WOW AI Features)
為了大幅深化工作坊的「WOW 驚艷感」與「極致的實用價值」，系統提供 5 個標準魔法工具與 全新擴充之 6 個客製化 AI 功能：

8.1 五大標準 AI 魔法 (The 5 AI Magics)
Magic 1: Prompt Spark (結構優化器)
原理：將法規初學者隨意填寫、語意含糊的提示句，通過精心設計的 Prompt Engineering，重新改寫為具有 Context/Goal/Constraint 三段式、語意清晰、無幻覺、符合美國 FDA 審查委員語氣的結構化 Prompt。

Magic 2: Dual-Lens Translator (雙鏡翻譯與對譯詞彙表)
原理：不只對整段法規進行中英翻譯，且在翻譯輸出後，自動在下方以 Table 列出該段落涉及的「美台官方醫材名詞映射表」，確保對照百分之百契合官方文件。

Magic 3: Gap Hunter (漏洞獵手)
原理：自動掃描上傳之產品說明或軟體架構圖文字。若軟體中含有藍牙功能卻絕口不提 Cyber Security 保障機制，或提及黏膜接觸卻無生物相容性宣告，本工具會以珊瑚橘高亮直接列出技術缺失，防止送件後直接遭到 FDA RTA (Refuse to Accept) 駁回。

Magic 4: Artifact Weaver (草案編織者)
原理：將不完整的、隨手紀錄的實驗筆記或研發規格代號等破碎數據，自動整理、展開並編織為符合 IMDRF STED (Summary Technical Documentation) 架構的正式技術章節。

Magic 5: Workflow Oracle (工作流神諭)
原理：根據當前 Session State 中的 Active Context 完善度、Checklist 被判定為 "Compliant" 的百分比，自動給出下一步的最優執行決策（例如：「Checklist 尚未完成 50% 且缺漏檢磁測試資料，建議您先使用 Gap Hunter 漏洞獵手，或點擊 WOW 1 進行標準協調一致性評估。」）。

8.2 六大客製化 WOW AI 功能 (Six Custom WOW AI Features)
本系統內置 6 個領先行業的高級醫材 AI 合規決策與輔助功能，覆蓋研發、安全性、臨床、軟體資安與數據防偽全流程：

WOW AI Feature 1: Standard Harmony Evaluator (標準協同一致性評估器)
功能核心：評估技術設計在「質量管理體系（ISO 13485）」與「風險管理（ISO 14971）」這兩大醫材支柱標準之間的交叉一致性。

數據流與輸入：

輸入：產品設計規格（Active Context）與用戶提供的風險危害分析表（Risk File/Hazard List）。

處理規則：AI 提取風險矩陣中定義的「設計緩解措施 (Risk Mitigations)」，交叉核對設計管制程序（Design Controls）中是否有相應的「設計輸入 (Design Input)」和「設計驗證 (Design Verification)」來落實該緩解措施。

推論流程：掃描風險矩陣 -> 判定緩解措施關鍵字 -> 搜尋 Active Context 是否涵蓋該具體測試/功能規格 -> 標記未鏈接的「孤立風險項目」。

輸出架構：提供「ISO 13485 (QMS) - ISO 14971 (Risk) 一致性追溯分析表」與不對等警告點。

WOW AI Feature 2: Regulatory Claim Synthesizer (法規宣稱句式合成器)
功能核心：將研發或行銷部分草擬的「誇大、缺乏科學支撐且易招致監管駁回」之市場字句，重新譯編為完全符合 FDA 510(k) 實體等同性 (Substantial Equivalence) 論證安全語氣的「正式合規宣稱」。

數據流與輸入：

輸入：非技術宣傳詞（例如：「本產品為全球最精準且能 100% 預測心律不整的 SaMD。」）。

處理規則：去除絕對字詞（例如：Best, Perfect, Guarantee、100%），代之以經過實體等對照證明的相對條件、臨床效能信賴區間語句。

推論流程：識別行銷誇大詞 -> 自動匹配 Predicate Device 適用之標準法規句式（Clearance Rationale 範式） -> 結合臨床效能數據進行合成。

輸出架構：[原始宣稱 / Marketing Claim]、[合規修改建议 / Regulatory Refined Claim]、[FDA/TFDA 被接受機率評估] 三對照。

WOW AI Feature 3: Bilingual Mock Clinical Blueprint (雙語模擬臨床試驗藍圖)
功能核心：當醫材被判定為中高風險 (Class II / Class III) 或缺乏 SE 對照物，AI 依其適應症及設計特點，自動編製一套高質量的模擬臨床試驗/前瞻性台美雙語大綱。

數據流與輸入：

輸入：器材預期用途 (Intended Use)、目標病患人群 (Target Population)、Class 判定與 GAP 報告。

處理規則：基於 ISO 14155（醫療器材臨床研究規範）或 GCP 指引，合理推估樣本量，設計主要與次要終點。

推論流程：評估器材風險點 -> 定位主要安全性終點（Primary Safety Endpoint）與療效終點（Primary Efficacy Endpoint） -> 生成統計估算架構與多中心受試者排除標準。

輸出架構：中英對照的專利/臨床評估協議草案、樣本量說明、安全性防護措施及倫理（IRB）符合性指南。

WOW AI Feature 4: SaMD Material Vulnerability Sentinel (軟體安全與物料評估哨兵)
功能核心：專攻 SaMD 軟體物料清單 (SBOM) 檢視，依據 U.S. FDA 2023/2024 最新網路安全指引（Cybersecurity in Medical Devices）解析開源與商業組件的安全漏洞風險（Vulnerabilities）。

數據流與輸入：

輸入：軟體設計文件 (SDD) 或 SBOM CSV/Text。

處理規則：辨識 SBOM 中列出的作業系統、開源庫、框架與版本，自動匹配常見的 CVE 安全威脅模型，判定是否需要「網路安全補丁（Security Patches）」或「安全日誌監視」。

推論流程：提取軟體元件與版本 -> 映射其威脅層面 -> 生成威脅緩解計畫 (Cybersecurity Management Plan) 大綱。

輸出架構：軟體脆弱性感知清單，與 FDA 12 大 Cybersecurity 送件文件所需之 SBOM 段落草案。

WOW AI Feature 5: Adaptive Multi-Country Pathway Bridge (跨國多地區申報路徑適配橋接器)
功能核心：在 IMDRF (國際醫療器材法規論壇) 架構下，提供歐盟 (CE MDR)、美國 (FDA 510k/De Novo)、台灣 (TFDA 查驗登記) 三地申報路徑的一鍵轉換與橋接。

數據流與輸入：

輸入：已備妥之單一地區技術資料 (如已擁有的 TFDA 核准函或 510k 摘要)。

處理規則：自動對比目的地國與原國度的「分類原則差異（e.g., EU Annex VIII rules vs FDA 21 CFR panel rules）」與技術規格缺口。

推論流程：分析既有憑證 -> 檢索目的地國家特有合規要求 (e.g., TFDA 雙國認證簡化路徑、EU MCS 臨床數據門檻) -> 重組轉換要點。

輸出架構：跨國申報差異差異報告與一鍵出口適配分析。

WOW AI Feature 6: Electronic Signature Fingerprint Seal (電子文檔防偽與 DHF 電子簽章印章)
功能核心：為符合 U.S. FDA 21 CFR Part 11 等電子簽章合規性，當用戶導出本工作坊生成的 PDF/Markdown/CSV 報告時，系統自動生成一組唯一的加密 SHA-256 指紋印章附加於文件最尾端。

數據流與輸入：

輸入：已生成的文件本文、當前選用之 Active Agent 名稱、用戶隨機雜湊。

處理規則：將文件內容、時間戳、Agent 屬性、及用戶 Session Hash 進行串接，透過 Python 加密庫進行 SHA-256 單向雜湊，生成一個 64 字元的「數位防偽指紋印章」。

推論流程：獲取導出字串 -> 計算 MD5 與 SHA-256 -> 拼接電子簽章聲明 -> 自適應附著於文檔末。

輸出架構：可驗證的電子簽章證書區塊，展示於 Markdown 的底端卡片中。

9. 資料隱私、安全性與退回防禦設計 (Security & Fallback Engineering)
醫療器材數據涉及高度國家監管、商業私密性與專利敏感性，系統在架構與工程設計上，不移餘力地保障用戶隱私與系統的高容錯性：

9.1 API Key 絕不外洩與遮罩機制
系統級環境變數優先：系統加載時，優先從後台安全環境裝載 GEMINI_API_KEY 與 OPENAI_API_KEY。若有，前台介面完全不向使用者顯示這兩個敏感變數，亦不回顯。

本地 Session 隔離：若無環境變數，允許用戶在前台側邊欄輸入 Key，金鑰採用密碼框處理（type="password"）。此金鑰僅保留在該特定的瀏覽器 Session 內存空間中。一旦使用者關閉頁面、重新整理或 Session 超時，內存垃圾回收 (GC) 會即刻徹底抹除金鑰，絕不將任何個人 Key 保存於伺服器、數據庫或本地磁碟中。

安全防護日誌：系統的所有即時日誌（Live Activity Logs）均經過嚴密過濾，禁止打印出 API Key 的任意子陣列（即使是開頭與結尾字元）。

9.2 退回防禦與提示詞衝突檢測 (Error & Fallback Handling)
無金鑰安全降級模式 (Simulated Fallback Mode)：當用戶未使用 API Key，或者當前發生 API 限流、網路中斷等物理故障時，系統絕不崩潰，而會將控制流主動交還給「本地法規模擬引擎」。引擎會根據用戶上傳的 Context 與特定核心模組目的，合成本地高質量的專家合規框架模版，並在前台明顯高亮：⚠️ [Fallback Mode: Simulated Output Active - Please provide your API Key for live clinical reasoning]。

矛盾輸入退回機制：若上傳之設計背景中含有嚴重實體矛盾（例如：標明該產品為免申報免檢 Class I 器材，卻在其他位置要求編製 Class III 的三類主動植入物合規路徑），AI Agent 會即刻中斷自動推論，並在前台顯示紅色警示：🛑 [Regulatory Conflict Detected: Class I declaration contradicts Class III implant paths. Worklow suspended.]。

10. 針對 20 個綜合性後續思考與優化問題之系統性深度解答 (Detailed Architecture Solutions to the 20 Core Engine & Edge Cases Questions)
以下針對系統的 20 個關鍵合規、工程、性能與安全 edge cases（邊界案例），提供全面一體化、代碼級邏輯與架構解讀，這也是本系統最深度的技術骨架。

Q1: SaMD 軟體物料清單 (SBOM) 整合：如何設計 agents.yaml 與 skill.md 自動對接 SBOM 分析漏洞？
系統實現設計：

在 agents.yaml 中新增 SaMD 資安與 SBOM 審查官 角色，具備 SBOM 解析 與 CVE 漏洞危害度分析 技能。

在 skill.md 中嵌入專用指令規則，載入 U.S. FDA《Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions》最新指引。

設計一個 Python 中介層，提取 SBOM 的 CSV 中列出的 Third-party Software Component (含開源庫名、版本號)。當調用 API 時，將組件指紋傳遞給 google-genai，並在系統指令中明確約束：「請模型針對上述元件之版本，對照已知常見 CVE 漏洞數據庫特徵，評估在該 SaMD 特定臨床場景下（如：是否聯網、是否擁有實體防護），該漏洞是否可被利用，並給出危害控制緩解措施。」

Q2: 多文檔平行對照 (Multi-doc Parallel Alignment)：多個不同檔案如何進行交叉語意索引與融合同步？
系統實現設計：
本工作坊設計了專屬的 多重檔案加載與關聯表 (Context Alignment Mapping Table)。

當用戶上傳「硬體規格書」、「臨床評價報告」與「風險分析表」時，Document Analyzer 會利用元數據標籤（Metadata Tags）為每個檔案的段落打上標籤（例如：[HW-Specs], [Clinical-Evaluation], [Risk-Matrix]）。

系統建立一個語意交叉矩陣資料結構（Semantic Matrix DF），存檔於 Session State 中。

AI 代理人在進行對照時，採用 Pivot-and-Search 演算法：例如掃描到 [Risk-Matrix] 中的電氣火災危害，會自動用語意關聯（Cosine Similarity 相似度匹配）提取 [HW-Specs] 中是否有保險絲或過載保護閥的硬體規格。若檢索值低於閥值 0.65，則在 Gap 漏洞分析中報出不對等缺口。

Q3: 動態 RAG 知識庫配置：如何在 skill.md 注入條件使模型動態調用特定國家官方資料庫（如 TFDA 許可證查詢網）進行接地查證？
系統實現設計：
在 Master System Instruction 編譯階段，系統注入以下動態查證協定（Grounded Search Protocol）：

當辨識到用戶輸入含有特殊高風險器材（如：人工水晶體 "Intraocular Lens"）時，激活 RAG 調用條件。

依循 google-genai 的 google_search 網路接地檢索（Google Search Grounding）功能，在調用配置中啟用 tools=[{"google_search": {}}]。

同時，在 skill.md 的行為規範中強制加入 URL Constraints：「請優先檢索 "https://law.mohw.gov.tw" (台灣衛福部法規網) 與 "fda.gov" (美國 FDA) 的專利、指引與許可證許可字號。任何生成的申報成功案例或基準，其指引版本或醫療器材許可證字號必須為真實存在（例如：衛部醫器輸字第 XXXXXX 號），嚴禁模型自行想像拼湊。」

Q4: 與 FDA eSTAR 申報格式相容：本工作坊產出的 Markdown 與 CSV 如何與 eSTAR 的 XML Schema 無損轉換？
系統實現設計：

美國 FDA 的 eSTAR 本質上是一個帶有固定 schema 表格的 PDF/XML 格式。本系統在 reports_generated 中輸出的內容結構，其 JSON 的鍵值（Key-Value）完全採用 eSTAR Schema 命名法（例如：intended_use_statement, device_description, software_level_of_concern, biocompatibility_endpoints）。

開發 XML 導出橋接器。當用戶一鍵下載電子申報檔時，系統利用 Python xml.etree.ElementTree 模組，將 Session State 中暫存的合規矩陣編碼轉換為完全匹配 eSTAR XML Schema 的節點結構。用戶只需將此 XML 導入其本機的 eSTAR 容器中，即可實現自動填充。

Q5: 人因測試與可用性危害溯源：如何從使用誤差數據反向勾勒 UI 修改規格並新增行為限制？
系統實現設計：

輸入與解析：當用戶將可用性測試（Usability Testing）期間的使用誤差數據（Use Errors, 如「使用者常誤觸泵浦啟動鈕導致未校正即注藥」）貼入 Document Analyzer時。

溯源映射：Gap Hunter 利用內置的可用性原則（IEC 62366-1 危害溯源演算法），將此使用誤差（Usability Hazard）映射至 UI 設計的缺陷上（如：按鈕未設置防呆機制、背景對比不足）。

自動限制：系統隨後會將此缺陷反向產生一條全新的行為約束，動態注入到當前的 skill.md 結尾（並寫入系統運行的臨時日誌中）。當下次模型生成「產品宣稱」或「申報說明書草案」時，會被強制要求加入「安全注意事項警告」，且在介面規格描述中補入「加入實體雙擊確認機制」的設計要求，徹底完成「危害-設計緩解-說明書警告」的逆向合規閉環。

Q6: 多代理人投票共識機制 (Agent Voting Consensus)：多個 Agent 對變更評估不一致時，如何設計投票調解機制？
系統實現設計：

當有重大醫材變動（例如：硬體晶片變更，變更申報比對路徑）時，系統併行開闢三個 LLM Chat Sessions：ISO 14971風控專家、FDA 510(k)申報專家、和TFDA法規專員。

第一階段（獨立判定）：三名 Agent 分別根據 agents.yaml 之獨立人設對變更進行評估，產出帶有理由與決策標籤（APPROVED / REJECTED / ACTION_REQUIRED）的獨立合規意見書。

第二階段（調解共識）：系統啟動 Orchestration Moderator（調解 Agent），讀取上述三份報告，並採用「少數服從多數 + 危害嚴重優先原則」。若風控專家投出 REJECTED 而其他兩名投 APPROVED，調解 Agent 根據醫材安全優先性，判定風控票擁有一票否決權 (Veto Power)。

輸出：給出調解中間過程，包含代理人爭論日誌，最後輸出一個融合了妥協修改案的「最終共識變更評估報告」。

Q7: BOM 材表化學風險分析：skill.md 如何引導模型自動評估化學表徵豁免（ISO 10993-18）？
系統實現設計：
在 skill.md 中寫入一組 ISO 10993-18 (化學表徵) 的專家排除法邏輯鏈 (Exemption Decision Tree)：

系統檢索 active_context 中的 BOM 材表。

若模型發現在材表中，器材與人體接觸的性質為「小於 24 小時的暫時接觸 (Transient / Limited contact)」，且接觸組織不含骨骼或血液系統。

skill.md 強制要求模型輸出符合 ISO 10993-1 / ISO 10993-18 指引的豁免聲明（Exemption Rationale Justification）起草架構。

判定是否有高分子添加劑（如 DEHP 塑化劑），若有則自動生成對等毒理學限值 (TTC, Threshold of Toxicological Concern) 與耐受暴露量 (TI, Tolerable Intake) 的計算表框架，供實驗室直接填寫。

Q8: 跨 Space 安全通訊：如何在不透露 API Key 的前提下，實現去識別化資料共享與聯合訓練？
系統實現設計：
當多個科室分別在獨立的容器 Space 下運行此應用時：

無 Key 隔離設計：每台機器利用 Local State 保存自己的專利或患者機密資料，不輸出。

抽象層對接：當需要實現「聯合評估」時，各 Space 只導出包含 去識別化技術特徵 (De-identified Tech Features) 與 合規判定標記 (Boolean Labels) 的 CSV/JSON 描述符。

檔案傳輸接口採用安全 Token 代理機制（OAuth Gateway），不向外發送任何實際 Key。只傳輸梯度差（Gradient Difference）或模型生成的合規概率矩陣，從而在外部統一匯集成綜合的「跨境合規判定預測模型」，完全遵守美國 HIPAA 與台灣個資法對醫材和患者隱私的物理阻斷原則。

Q9: 臨床試驗不良事件 (SAE) 動態預判：WOW 3 中如何配置一組「SAE 預判分類邏輯」並防止試驗非預期危害？
系統實現設計：

在 Bilingual Mock Clinical Blueprint (WOW 3) 的推論邏輯中，強制注入「安全性與預警危害分類引擎」。

依據大眾化不良事件模型（MAUDE 數據庫常見故障），AI 自動在臨床試驗藍圖中嵌入一個 SAE Event Classifier API (假想)。此 API 在試驗設計中規定：一旦受試者生理變數（如血液氧飽度）偏離基線值 > 15%，或器材本身發生數據連線中斷超過 30 秒，該臨床系統必須被強制設計為「進入安全停機降級狀態，並在 24 小時內自動產生 FDA MedWatch Form 3500A 電子申報草案」。

此外，AI 還會主動在臨床方案末端撰寫「臨床非預期危害應變 SOP」，設定臨床叫停準則（Trial Suspension Rules）以規避審查官對臨床安全防範不力的質疑。

Q10: 大語言模型思考過程（Thinking Process）之視覺化：啟用 thinking_config 後，如何在 Streamlit 上優雅展示而不影響打印排版？
系統實現設計：

在調用全新 google-genai 的 gemini-3.5-flash模型時，若設置 thinking_config={'thinking_budget': 1024}，API 會在生成回覆中分開吐出思考過程段落與最終文本段落。

UI 雙層渲染：在 Streamlit 畫面上，系統將思考過程（Reasoning Steps）動態填充進側邊欄或前台主區塊的 st.expander("👁️ 代理人內在法規思考軌跡 (Agent Reasoning Trace - IEC/FDA Linkages)") 內。這利用了折疊面板。

列印排版隔離：當用戶點擊「下載 PDF / Markdown 報告」或呼叫瀏覽器列印時，CSS 覆寫樣式表將排版排除：

code
CSS
@media print {
    .stExpander, .st-expanderHeader, div[data-testid="stExpander"] {
        display: none !important;
    }
}
這確保了最終打印或導出的 PDF 技術報告中，只有格式嚴整的正式法規章節，徹底免去任何調試蹤跡和 AI 碎碎唸發言。

Q11: 與 GitHub / GitLab CI-CD 整合：SaMD 代碼與文檔託管，如何設計 Webhook API 在 Git Push 時自動合規掃描？
系統實現設計：
本工作坊設計了專屬的 API 端點，以整合研發 CI-CD 工作流：

在 Express 服務器中增設 API 路由：POST /api/webhook/git-scan。

當研發 Git Push 時，Git 倉庫觸發 Webhook，將提交的代碼更新差分（Code Diff）與 DHF (Design History File) Markdown 文件以 JSON 的形式 POST 至該路由。

服務器中的 AI 引擎自動加載 agents.yaml 以 SaMD 品質保證專員 身分執行推論，對 Diff 進行掃描。

若 Diff 中修改了關鍵計量代碼（如「輸液泵速率控制」由 2.0 升級到 5.0 ml/hr），但 DHF 文件中缺漏了危害風險重新確認，API 將回傳狀態碼 400 Bad Request，附帶 AI Gap 分析，並發布 commit status 為 failure，從而在 CI-CD 流程中自動阻斷未經風險評估的程式碼合併。

Q12: TFDA 查驗登記之簡化路徑判定：Oracle 智慧工作流 如何判讀前置條件以智慧修訂 Roadmaps？
系統實現設計：

系統檢索 active_context 或用戶提供的註冊聲明。

當 Workflow Oracle 識別到器材符合以下前置證書條件（Prerequisite Certificates）之一：

美國 FDA 510(k) 已核准

歐洲 CE MDR 證書已取得

AI 自動更新申報策略為 「雙國認證簡化路徑 (Dual-country Clearance Route)」。

隨後，系統自動在 Compliance Roadmap 模組中，將原本長達 18 個月、成本 30 萬的 TFDA 查驗登記時程，自動縮減至 8-10 個月，並將臨床與技術文件比對工作（CER）替換為「實體對照品資料簡化報告說明書」，同時在預算規費部分自動調低審查規費為簡化版收費標準。

Q13: 多租戶隔離與內存管理 (Multi-tenant GC)：高並行數十人載入超大文本時，如何防止 CPU/Memory 溢出？
系統實現設計：

輕量儲存：絕不在 Streamlit 後台代碼中使用全域級（Global Module Scope）的變量來動態累加用戶資料。所有暫存資料全部限制在 st.session_state（獨立的瀏覽器會話空間）中，會話關閉即自動釋放。

內存大數據塊清除 (GC Force)：當用戶重新上傳、或在 Document Analyzer 切換新文檔時，系統調用 Python 的垃圾回收模組：

code
Python
if "active_context" in st.session_state:
    st.session_state.active_context = ""
import gc
gc.collect()
限制歷史紀錄大小：Live Activity Log 採用滑動窗口機制（Sliding Window），只保留最新 10 筆，其餘過期 Log 歷史主動 pop(0) 丟棄，防止 Session 數據堆積造成 OOM (Out Of Memory)。

Q14: 法規變更新舊標準衝擊分析 (Gap Impact Analysis)：新舊標準改版，如何定位 Context 的需要補測項目？
系統實現設計：

當用戶點擊「新舊版衝擊分析」時（例如 ISO 14971 從 2012 版升級到 2019 版），系統載入 Legacy-to-Current Standard Gap Mapping DB。

系統獲知 2019 版的新增要求（例如：增加了上市後資訊反饋與主動危害識別程序的要求）。

AI 代理人（品質管理專員）對 6,000 字的 Context DHF 文件執行 「語意指向搜尋 (Targeted Semantic Search)」。

回答輸出時，AI 會以珊瑚橘高亮列出所有受到衝擊的既有程序文件（例如：既存的上市後監管程序缺漏了與設計變更的反饋閉環），並列出必須補充的「差異補測行動計畫與補件時間表 (Actionable Delta Remediation Plan)」。

Q15: 珊瑚橘高亮精準度與 CSS 相容度：Markdown 套用 HTML <span> 標籤如何確保不產生解析錯誤或漏掉閉合？
系統實現設計：

為防止 <span> 標籤破損導致整頁 HTML 樣式崩壞（例如文字全部變為珊瑚橘色），系統採取 Markdown Regular Expression Sandbox (規則表達式沙箱機制) 進行嚴格包裝。

系統設置一個安全的包裝函數：

code
Python
def safe_coral_highlight(text: str) -> str:
    # 強制防範漏掉<span>閉合標籤，將包含標籤的敏感字符包裹在嚴格字串範圍
    clean_text = text.replace("<span", " ").replace("</span>", " ")
    return f"<span class='coral-highlight'>{clean_text}</span>"
在 google-genai 的 System Instruction 中寫入極其嚴厲的代碼控制指示：「任何在 Markdown 中嘗試套用珊瑚橘色高亮的行為，必須嚴格且僅能使用單一正則表達式能匹配的規範：<span class='coral-highlight'>目標重要單詞</span>。此標籤必須在同一行內起迄閉合，嚴禁跨越段落、代碼塊、或大於符號，否則在前端流式輸出中會直接被網頁編譯器攔截剔除。」。

Q16: Excel 的 UDI-DI 數據格式預防變形：在匯出 CSV 時，如何預防長數字被 Excel 自動轉為科學記號？
系統實現設計：

此為法規申報表導出的經典工程 Edge Case（如 UDI-DI 碼為一串長達 14 碼的純數字：00812345678901，直接被 Excel 轉為 8.12E+11 並且抹除前導零）。

系統解決解法：在下載 CSV 的 Pandas 導出管道（Export Pipeline）中，系統會對檢測到符合 UDI、Permit Number 或任何高精度序號的純長數字欄位，強制在數值的前後包裹 Excel 字串定位限定符 (Excel String Literal Qualifier)。

實作公式：將 00812345678901 改寫成 "\t00812345678901" 或 ='00812345678901'。最優解是在導出 CSV 的 Pandas 轉換引擎中，將該列數值包裝：

code
Python
df["UDI-DI"] = df["UDI-DI"].apply(lambda x: f'="{x}"' if str(x).isdigit() and len(str(x)) > 10 else x)
這樣導出的 CSV 檔案在 Microsoft Excel 中被雙擊直接開啟時，Excel 會將其識別為恆定公式字串，強退數字科學計算，百分之百保留原有的前導零與完整數位不變形、不失真。

Q17: 臨床文獻檢索偏誤排除 (Bias Mitigation in CER)：如何透過 skill.md 強制模型在文獻綜述中加入非利益相關研究？
系統實現設計：

在 skill.md 中寫入歐盟 MDR MEDDEV 2.7/1 Rev 4（臨床評價指南）的非偏誤文獻篩選原則（Sifting Principles）。

當臨床研究 Agent 產出文獻綜述草案時，其 prompt 融合了以下黃金標準約束：「請模型在制定臨床搜尋策略時，除了輸入產品相關關鍵字外，必須提供最少兩個 獨立外部對照組 (Independent, Non-sponsored Studies)。搜尋關鍵字串必須公開包括 'Negative results' 與 'Adverse events'。」

在輸出的文獻列表中，AI 被強制標示每個文獻的贊助狀態（如：Academic Independent 或 Industry Sponsored），並對比兩者文獻中的副作用率偏離程度。若有明顯數據偏差（偏差率 > 25%），則在 CER 風險提示區塊顯著回報，藉此符合最挑剔的審查專員（Notified Bodies）的「無偏向文獻檢索」合規宣告。

Q18: 無菌包裝加速老化之極端溫度警告：產品含溫感塗層，如何自動警示並修正加速老化時間估算？
系統實現設計：

當用戶在 Compliance Roadmap 或設計文件中提到醫材包裝使用了加速老化（Accelerated Aging, ASTM F1980），且產品本身含有生物活性聚合物或藥物塗層。

智慧預警邏輯：AI 代理人會自動讀取產品材料，如果辨識到 "Polymer", "Gel", "Coating", "Drug" 等熱敏感關鍵字。

系統自動覆載安全警示，拒絕使用常見的 60°C 加速老化試驗高溫（這會造成材料物理形變或藥物失效，導致測試白費）。

AI 將在時程表中主動將建議老化測試溫度調降至 45°C 或 50°C，並依據 阿瑞尼斯方程式 (Arrhenius Equation Q10 = 2) 自動重算其加速週期時間：將原本在 60°C 僅需 30 天的老化，主動修正為在 45°C 下需要 85 天，重新估算測試時程，避免在合規計畫中出現常識性技術失誤。

Q19: 本地模擬降級機制之數據庫更新：在無網路連線時，本地「法規模擬合成引擎」如何做到不需更新程式即可複覆寫更新？
系統實現設計：

本地引擎快取化：本地法規模擬引擎（Local Regulatory Fallback Engine）所使用的申報大綱、TFDA 符合性條目與 FDA 510k 範本庫，全部不寫死（Hardcode）在 Streamlit 主程式碼內。

靜態文檔覆載機制：系統在 assets/.aistudio/ 或項目根目錄儲存一個輕量、版本化的 JSON 數據包（稱為 local_fallback_templates.json）。

當法規官方發布最新指引（如：TFDA 2026 最新查驗登記法規改版）而此時系統斷網或無 API Key 時，系統在啟動時會主動檢測本機目錄中是否存在該 JSON。

只要使用者將最新法規條目以 UTF-8 格式放入此 JSON，本地引擎會在啟動時自動加載並覆寫舊有模型預期輸出。無需重構或重新編譯 Python 容器，便能實現離線 RAG 可行性比對數據包的一秒升級。

Q20: DHF 技術設計歷史檔案之數位簽章：如何生成結合「Agent」、「用戶雜湊」與「文件指紋」的電子 SHA-256 簽名？
系統實現設計：
為完全滿足 FDA 21 CFR Part 11 的設計控制電子記錄可追溯性，系統在下載輸出（Download Pipeline）中集成了一個數位簽章特徵引擎：

獲取雜湊元數據：當用戶準備下載 CSV Checklist 或 Markdown 報告時，系統聚合以下維度：

doc_body: 該文檔的完整字串本文。

user_session_hash: 用戶瀏覽器的 Session ID 經 SHA-1 雜湊得到的 Unique Code。

agent_identity: 執行該任務的 Agent 完整大名與 YAML 屬性。

local_time: 當下印製的標準 UTC 時間戳。

SHA-256 指紋印章计算：
利用 Python 內建的 hashlib。

code
Python
import hashlib
import json

sign_payload = {
    "document_content_hash": hashlib.sha256(doc_body.encode('utf-8')).hexdigest(),
    "esignature_author": agent_identity,
    "esignature_timestamp": local_time,
    "user_hash": user_session_hash
}
# 編譯為最終合規電子防護指紋印章 (64字符)
seal_hash = hashlib.sha256(json.dumps(sign_payload, sort_keys=True).encode('utf-8')).hexdigest()
自動附加輸出：系統會在 Markdown 報告底端或 CSV 尾部生成一個名名為 [21 CFR Part 11 - DHF Electronic Compliance Seal] 的嚴整證書斑馬卡片，其中清晰展示：

Signatory Agent: {Agent Name}

Audit Timestamp: {local_time} UTC

System Certification Hash: SHA256:: {seal_hash}
透過這項機制，該檔案一旦在導出後遭到任何人為惡意篡改、或漏掉合規條目，只要將其內容重新代入計算指紋，便會因雜湊不一致而直接宣告失效，提供醫材 DHF 檔案無可匹敵的防偽、防篡保證與全週期的可信賴審查能力。
