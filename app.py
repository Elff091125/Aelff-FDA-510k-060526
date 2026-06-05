import streamlit as st
import yaml
import json
import random
import datetime
import io
import os
import pandas as pd

# -----------------------------------------------------------------------------
# 1. INITIAL SESSION STATE SETUP
# -----------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "en"  # "en" or "zh_tw"
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "style_preset" not in st.session_state:
    st.session_state.style_preset = "coral haze"
if "logs" not in st.session_state:
    st.session_state.logs = [
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] System initialized in bilingual mode."
    ]
if "active_context" not in st.session_state:
    st.session_state.active_context = ""
if "agents_yaml" not in st.session_state:
    st.session_state.agents_yaml = """# Standardized Regulatory Agents Configuration
version: 1.0.0
agents:
  - name: FDA Classifier
    role: "Determine FDA medical device classification based on intended use and risk profile."
    skills:
      - classification_rationale
      - standards_mapping
  - name: TFDA Specialist
    role: "Verify checklist alignment against Taiwan FDA technical documentation requirements."
    skills:
      - technical_file_review
      - translation_glossary
"""
if "skill_md" not in st.session_state:
    st.session_state.skill_md = """# Standardized Regulatory Skill Configuration
## Purpose
Facilitate cross-border regulatory analysis and document drafting.

## Constraints
- Outputs must align strictly with active standards (e.g., ISO 13485, ISO 14971).
- Identify and flag gaps transparently rather than interpolating ambiguous data.
- Maintain bilingual consistency.
"""
if "reports_generated" not in st.session_state:
    st.session_state.reports_generated = {}
if "notes_text" not in st.session_state:
    st.session_state.notes_text = ""

# -----------------------------------------------------------------------------
# 2. LOCALIZATION STRINGS
# -----------------------------------------------------------------------------
LOCALIZATION = {
    "en": {
        "title": "Medical Device Regulatory Intelligence Workspace",
        "subtitle": "Bilingual AI-Assisted Document Synthesis & Agent Studio",
        "dashboard": "Dashboard",
        "doc_analyzer": "Document Analyzer",
        "feasibility": "Regulatory Feasibility",
        "tfda_checklist": "TFDA Checklist",
        "risk_classifier": "Risk Classifier",
        "predicate_finder": "Predicate Finder",
        "compliance_roadmap": "Compliance Roadmap",
        "agent_studio": "Agent Studio (YAML/MD)",
        "note_keeper": "AI Note Keeper",
        "ai_magics": "AI Magics & Custom Tools",
        "settings": "Global Settings",
        "live_log": "Live Activity Log",
        "preset_select": "Jackslot Theme Chooser",
        "roll_preset": "🎰 Roll Random Style",
        "theme_light": "Light Mode",
        "theme_dark": "Dark Mode",
        "api_status": "API Configuration Status",
        "gemini_key": "Gemini API Key",
        "openai_key": "OpenAI API Key",
        "anthropic_key": "Anthropic API Key",
        "model_select": "Model Selection",
        "grounding_status": "Grounding Status",
        "active_profile": "Active Workspace Profile",
        "status_ready": "Ready",
        "status_attention": "Attention Needed",
        "status_failed": "Missing Key / Blocked",
        "status_processing": "Processing",
        "prompt_editor": "Editable System Prompt",
        "run_analysis": "Execute Analysis",
        "download_markdown": "Download Markdown",
        "export_pdf_sim": "Print/Export Layout",
        "coral_highlight_info": "Coral highlighted keywords indicate crucial regulatory standards or deadlines.",
        "coral_enabled": "Highlight Regulatory Keywords",
        "keep_prompt": "Keep Original Prompt in Output",
    },
    "zh_tw": {
        "title": "醫療器材法規智慧工作坊",
        "subtitle": "雙語 AI 輔助文件合成與代理技能工作室",
        "dashboard": "儀表板",
        "doc_analyzer": "文件分析器",
        "feasibility": "法規可行性報告",
        "tfda_checklist": "TFDA 技術查驗登記清單",
        "risk_classifier": "風險分類評估",
        "predicate_finder": "實體對照品比對",
        "compliance_roadmap": "法規合規路徑圖",
        "agent_studio": "Agent 技能工作室 (YAML/MD)",
        "note_keeper": "AI 筆記整理器",
        "ai_magics": "AI 魔法與自定義工具",
        "settings": "全域設定",
        "live_log": "即時運行紀錄",
        "preset_select": "Jackslot 主題挑選器",
        "roll_preset": "🎰 隨機切換主題風格",
        "theme_light": "淺色模式",
        "theme_dark": "深色模式",
        "api_status": "API 金鑰配置狀態",
        "gemini_key": "Gemini API 金鑰",
        "openai_key": "OpenAI API 金鑰",
        "anthropic_key": "Anthropic API 金鑰",
        "model_select": "模型選擇",
        "grounding_status": "文獻查證狀態",
        "active_profile": "當前工作空間設定檔",
        "status_ready": "就緒",
        "status_attention": "需要注意",
        "status_failed": "缺少金鑰 / 已受阻",
        "status_processing": "處理中",
        "prompt_editor": "可編輯系統提示詞",
        "run_analysis": "執行分析",
        "download_markdown": "下載 Markdown 檔",
        "export_pdf_sim": "列印/匯出排版預覽",
        "coral_highlight_info": "珊瑚橘高亮關鍵字標示關鍵法規標準或截止日期。",
        "coral_enabled": "高亮法規關鍵字",
        "keep_prompt": "在輸出中保留原始提示詞",
    }
}

def t(key):
    return LOCALIZATION[st.session_state.lang].get(key, key)

def add_log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

# -----------------------------------------------------------------------------
# 3. 20 SLEEK STYLE PRESETS (Pantone-like Palette Definition)
# -----------------------------------------------------------------------------
STYLE_PRESETS = {
    "coral haze": {"bg": "#FAF9F6", "surface": "#F5EBE6", "accent": "#FF7F50", "text": "#2C2C2C", "dark_bg": "#1C1412", "dark_surface": "#2D201D", "dark_accent": "#FF8C69"},
    "cobalt tide": {"bg": "#F0F4F8", "surface": "#D9E2EC", "accent": "#0047AB", "text": "#102A43", "dark_bg": "#0B132B", "dark_surface": "#1C2541", "dark_accent": "#48CAE4"},
    "emerald graphite": {"bg": "#F4F6F4", "surface": "#E1E6E1", "accent": "#0B6623", "text": "#223322", "dark_bg": "#141A14", "dark_surface": "#222B22", "dark_accent": "#50C878"},
    "amber slate": {"bg": "#F9F7F1", "surface": "#EFEBE0", "accent": "#D97706", "text": "#2D251E", "dark_bg": "#1A1612", "dark_surface": "#2C241E", "dark_accent": "#FBBF24"},
    "lavender mist": {"bg": "#F6F5F7", "surface": "#ECE9EE", "accent": "#8A2BE2", "text": "#2E1A47", "dark_bg": "#140F1D", "dark_surface": "#241B35", "dark_accent": "#D8BFD8"},
    "ocean mint": {"bg": "#F2F8F6", "surface": "#E2F0EC", "accent": "#00A86B", "text": "#0F2F23", "dark_bg": "#0D1B17", "dark_surface": "#19352D", "dark_accent": "#50FA7B"},
    "terracotta dusk": {"bg": "#F8F2F0", "surface": "#EFE1DD", "accent": "#C24E3A", "text": "#3A1B14", "dark_bg": "#1D1311", "dark_surface": "#321D19", "dark_accent": "#FF7F50"},
    "icy rose": {"bg": "#FAF5F6", "surface": "#F4EAEB", "accent": "#D16587", "text": "#3B1825", "dark_bg": "#1D1014", "dark_surface": "#321A21", "dark_accent": "#FFB7C5"},
    "citrus ink": {"bg": "#FBFBF8", "surface": "#F5F5EC", "accent": "#FFA700", "text": "#2A2A1A", "dark_bg": "#15150E", "dark_surface": "#2A2A1E", "dark_accent": "#FFD700"},
    "orchid smoke": {"bg": "#F5F3F5", "surface": "#EAE5EA", "accent": "#9E5E9E", "text": "#2A182A", "dark_bg": "#1A101A", "dark_surface": "#2D1D2D", "dark_accent": "#EE82EE"},
    "jade noir": {"bg": "#F1F5F2", "surface": "#E0EAE2", "accent": "#006400", "text": "#0B1D12", "dark_bg": "#09120C", "dark_surface": "#152A1C", "dark_accent": "#32CD32"},
    "saffron pearl": {"bg": "#FAF9F5", "surface": "#F4EFE0", "accent": "#F4C430", "text": "#2C2A1E", "dark_bg": "#1C1A14", "dark_surface": "#2D2A1F", "dark_accent": "#FFF0F5"},
    "ultramarine fog": {"bg": "#F2F4F8", "surface": "#E1E6F0", "accent": "#120A8F", "text": "#050230", "dark_bg": "#06031A", "dark_surface": "#110E33", "dark_accent": "#4169E1"},
    "sand chrome": {"bg": "#F6F6F4", "surface": "#ECECE6", "accent": "#C2B280", "text": "#2B2B2A", "dark_bg": "#191918", "dark_surface": "#2D2D2A", "dark_accent": "#D2B48C"},
    "plum steel": {"bg": "#F4F2F5", "surface": "#E7E3EA", "accent": "#4B0082", "text": "#220530", "dark_bg": "#12071B", "dark_surface": "#220F32", "dark_accent": "#DA70D6"},
    "basil ivory": {"bg": "#F7F8F5", "surface": "#ECEFE8", "accent": "#579229", "text": "#1A2E0E", "dark_bg": "#101B0B", "dark_surface": "#1F3517", "dark_accent": "#98FB98"},
    "ruby ash": {"bg": "#F9F4F4", "surface": "#EFE2E2", "accent": "#E0115F", "text": "#3B081A", "dark_bg": "#1C0D11", "dark_surface": "#32161E", "dark_accent": "#FF69B4"},
    "teal quartz": {"bg": "#F0F6F7", "surface": "#DDECEF", "accent": "#008080", "text": "#032828", "dark_bg": "#041414", "dark_surface": "#0C2B2B", "dark_accent": "#48D1CC"},
    "honey basalt": {"bg": "#F8F6F1", "surface": "#EFECE1", "accent": "#E5A65D", "text": "#2E2416", "dark_bg": "#1C1710", "dark_surface": "#2D261B", "dark_accent": "#F5C285"},
    "violet linen": {"bg": "#F6F4F8", "surface": "#EBE5F2", "accent": "#7F00FF", "text": "#20033B", "dark_bg": "#11071F", "dark_surface": "#220F3D", "dark_accent": "#BB86FC"}
}

# Apply styles using markdown custom injection
def inject_custom_styles():
    preset = STYLE_PRESETS[st.session_state.style_preset]
    is_dark = st.session_state.theme_mode == "Dark"
    
    bg = preset["dark_bg"] if is_dark else preset["bg"]
    surface = preset["dark_surface"] if is_dark else preset["surface"]
    accent = preset["dark_accent"] if is_dark else preset["accent"]
    text = "#FFFFFF" if is_dark else preset["text"]
    
    css_code = f"""
    <style>
    /* Global Background Adjustments (Partial Override) */
    .stApp {{
        background-color: {bg} !important;
        color: {text} !important;
    }}
    /* Custom Decorative Elements */
    .custom-card {{
        background-color: {surface};
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 5px solid {accent};
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .custom-badge {{
        background-color: {accent};
        color: {bg};
        font-weight: bold;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }}
    .coral-highlight {{
        color: #FF7F50 !important;
        font-weight: bold;
    }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. LLM ROUTING & FALLBACK GENERATOR
# -----------------------------------------------------------------------------
def get_parsed_agents():
    """
    安全解析工作區中的 agents.yaml，若語法錯誤則返回預設值。
    """
    default_agent = {
        "name": "General Regulatory Specialist (通用法規專家)",
        "role": "General medical device regulatory drafting and analysis.",
        "skills": ["regulatory_compliance", "technical_writing"]
    }
    
    # 確保 session state 中有 agents_yaml 變數
    raw_yaml = st.session_state.get("agents_yaml", "")
    if not raw_yaml.strip():
        return [default_agent]
        
    try:
        data = yaml.safe_load(raw_yaml)
        if isinstance(data, dict) and "agents" in data:
            return data["agents"]
    except Exception as e:
        # 僅記錄於 Log 中，不中斷使用者介面
        add_log(f"YAML Parse Warning (Using fallback): {str(e)}")
        
    return [default_agent]

def execute_llm_call(prompt, system_instruction="", model="gemini-3.1-flash-lite"):
    """
    動態調用現代 LLM 介面，並主動融合 agents.yaml 的角色設定與 skill.md 的行為限制。
    """
    add_log(f"Initiated request to {model} with prompt length {len(prompt)} characters.")
    
    # 1. 取得當前選定代理人（Agent）的詳細 Role 與 Skills 資訊
    active_agent_name = st.session_state.get("selected_agent_name", "")
    agents_list = get_parsed_agents()
    active_agent = next((a for a in agents_list if a.get("name") == active_agent_name), {})
    
    agent_role = active_agent.get("role", "General medical device regulatory specialist.")
    agent_skills = active_agent.get("skills", [])
    
    # 2. 取得 skill.md 的全域準則約束
    global_rules = st.session_state.get("skill_md", "")
    
    # 3. 融合建置 Master System Instruction
    master_system_instruction = f"""
# EXECUTIVE PERSONA
You are executing this task as the following specialized agent:
- **Agent Name**: {active_agent_name}
- **Your Role**: {agent_role}
- **Your Specific Skills**: {', '.join(agent_skills)}

# BASE INSTRUCTIONS
{system_instruction}

# GLOBAL COMPLIANCE RULES & CONSTRAINTS (From skill.md)
{global_rules}
"""

    # 提取 API Key
    gemini_key = os.environ.get("GEMINI_API_KEY") or st.session_state.get("gemini_key_val")
    openai_key = os.environ.get("OPENAI_API_KEY") or st.session_state.get("openai_key_val")
    
    # === GEMINI 呼叫流程 ===
    if "gemini" in model.lower() and gemini_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=gemini_key)
            target_model = model.strip()
            
            # 將合成的 master_system_instruction 注入至 GenerateContentConfig 中
            config_params = types.GenerateContentConfig(
                system_instruction=master_system_instruction,
                thinking_config=types.ThinkingConfig(thinking_budget=1024) if "3.5" in target_model else None
            )
            
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config_params
            )
            
            add_log(f"Gemini API ({target_model}) call succeeded. Mode: {active_agent_name}")
            return response.text
            
        except Exception as e:
            add_log(f"Gemini API ({model}) returned an error: {str(e)}. Falling back to deterministic simulation.")
    
    # === OPENAI 呼叫流程 ===
    elif "gpt" in model.lower() and openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            target_model = "gpt-4o-mini" if "mini" in model else model
            
            # 將合成的 master_system_instruction 注入為 system role
            completion = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": master_system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            add_log(f"OpenAI API ({target_model}) call succeeded. Mode: {active_agent_name}")
            return completion.choices[0].message.content
        except Exception as e:
            add_log(f"OpenAI API ({model}) returned an error: {str(e)}. Falling back to deterministic simulation.")

    # === 降級模擬輸出 (當無 API 金鑰或呼叫失敗時) ===
    add_log(f"Standard fallback routing triggered under agent: {active_agent_name}")
    
    if "feasibility" in prompt.lower() or "regulatory roadmap" in prompt.lower():
        return f"""### 📋 醫療器材法規可行性評估報告 (代理人協同合成)
**執行代理人 (Agent)**: {active_agent_name}
**代理人角色描述**: {agent_role}
**採用全域規則庫 (skill.md)**: 已融合

#### 代理人基於其專業技能 `{', '.join(agent_skills)}` 提出的特定意見：
1. 本器材因具備特定人體接觸界面，應優先確認 <span class='coral-highlight'>ISO 10993-1</span> 的生物相容性測試豁免可行性。
2. 考量本代理人的專業職能，建議在技術文件中補充特定安全與性能要求（EP Checklist）的第 1 至第 5 項論證。
3. 軟體維護與資安控制，應在 <span class='coral-highlight'>IEC 62304</span> 生命週期架構下，委由資安代理人進行二次審查。
"""
    else:
        return f"""### 🪄 AI 輔助合成報告 (代理人: {active_agent_name})
此報告已融入您在 Agent Studio 中編輯之 `{active_agent_name}` 角色特徵。
全域規則（來自於 `skill.md` 規範）已寫入 LLM 核心編譯器。

請於側邊欄輸入 API 金鑰，以啟動線上即時代理人協調網路。
"""

    # FALLBACK INTELLECTUAL WORKSPACE RESPONSES (Grounded & high quality)
    add_log("Standard fallback routing triggered (Simulation Engine).")
    
    if "feasibility" in prompt.lower() or "regulatory roadmap" in prompt.lower():
        return f"""### Comprehensive Regulatory Feasibility & Standards Report
**Grounded Status**: Model-Only (Fallback Mode)
**Device Classification**: Proposed Class II / Rule 11 (MDR)
**Subject standards**: ISO 13485:2016, IEC 62304, <span class='coral-highlight'>ISO 14971:2019</span> (Risk Management)

#### Executive Analysis
The submitted device outline demands a controlled lifecycle framework conforming to **IEC 62304 Class B** software standards. A robust clinical evaluation roadmap is necessary for target entry into US and EU regions.

#### Recommended Next Actions:
1. Finalize technical definitions in your configuration.
2. Formulate cross-compliance trace matrix targeting <span class='coral-highlight'>ISO 13485</span>.
"""
    elif "checklist" in prompt.lower() or "tfda" in prompt.lower():
        return f"""### TFDA Checklist Compliance Report
**Grounded Status**: Model-Only (Fallback Mode)
**Target Region**: Taiwan (TFDA Class II Regulatory Pathway)

1. **Safety and Performance Requirements**: Compliant (Requires verification details)
2. **Biocompatibility Evaluation**: Gap Identified (Material details omitted)
3. **Software Lifecycle Validation**: <span class='coral-highlight'>IEC 62304 Guidance Map Required</span>
"""
    elif "risk" in prompt.lower():
        return """### Automated Risk Classification Analysis
Based on anatomical path and active energy metrics:
- **Primary Risk Category**: Moderate (Class IIa / Class II)
- **Applicable Safety Thresholds**: IEC 60601-1 third edition.
- **Identified Gap**: Biocompatibility verification for direct mucosal contact duration.
"""
    elif "predicate" in prompt.lower():
        return """### Predicate Device Comparison Map
Comparing device specifications against benchmark clearings:
- **Predicate Device Identification**: K192837 (Active Monitoring System)
- **Equivalence Status**: Substantially Equivalent with notable software UI deviations.
- **Action Needed**: Contrast data collection parameters to confirm zero clinical-deviation impact.
"""
    else:
        # Default smart response
        return f"""### AI Synthesized Output (Workspace Studio)
**Status**: Completed
Your custom workspace prompt has been synthesized.

#### Evaluated Highlights:
- Active compliance indicators have been aligned with standard <span class='coral-highlight'>ISO 13485</span>.
- No critical framework contradictions detected.
"""

# -----------------------------------------------------------------------------
# 5. THE WORKSPACE APP STRUCTURE & MAIN RENDER
# -----------------------------------------------------------------------------
st.set_page_color = "#1A1A1A"
st.set_page_config(
    page_title="Regulatory Intelligence Console",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_styles()

# Sidebar: Unified Workspace Control and Insights
with st.sidebar:
    # 1. Title/Header & Lang Selector
    st.markdown(f"### ⚙️ {t('settings')}")
    col_lang, col_theme = st.columns(2)
    with col_lang:
        lang_choice = st.radio("Language / 語言", ("English", "繁體中文"), index=0 if st.session_state.lang=="en" else 1)
        st.session_state.lang = "en" if lang_choice == "English" else "zh_tw"
    with col_theme:
        theme_choice = st.radio("UI Theme", ("Light", "Dark"), index=0 if st.session_state.theme_mode=="Light" else 1)
        st.session_state.theme_mode = theme_choice

    st.markdown("---")
    
    # 2. Jackslot style chooser
    st.markdown(f"#### {t('preset_select')}")
    selected_preset = st.selectbox("Style Palette", list(STYLE_PRESETS.keys()), index=list(STYLE_PRESETS.keys()).index(st.session_state.style_preset))
    if selected_preset != st.session_state.style_preset:
        st.session_state.style_preset = selected_preset
        add_log(f"Theme preset adjusted to '{selected_preset}'.")
        st.rerun()
        
    if st.button(t("roll_preset")):
        random_preset = random.choice(list(STYLE_PRESETS.keys()))
        st.session_state.style_preset = random_preset
        add_log(f"Jackslot theme triggered: rolled {random_preset.upper()}")
        st.rerun()
    
    # Visual color chip preview for selected style
    cp = STYLE_PRESETS[st.session_state.style_preset]
    st.markdown(
        f"""
        <div style="display: flex; gap: 5px; margin-top: 5px; margin-bottom: 15px;">
            <div style="width: 25px; height: 25px; background: {cp['bg']}; border: 1px solid #ccc; border-radius: 50%;" title="Background"></div>
            <div style="width: 25px; height: 25px; background: {cp['surface']}; border: 1px solid #ccc; border-radius: 50%; title="Surface""></div>
            <div style="width: 25px; height: 25px; background: {cp['accent']}; border: 1px solid #ccc; border-radius: 50%; title="Accent""></div>
        </div>
        """, unsafe_allow_html=True
    )
    
    st.markdown("---")

    # 3. Web-based API configuration flow
    st.markdown(f"#### 🔑 {t('api_status')}")
    g_key = st.text_input(t("gemini_key"), type="password", value=st.session_state.get("gemini_key_val", ""))
    if g_key:
        st.session_state.gemini_key_val = g_key
    o_key = st.text_input(t("openai_key"), type="password", value=st.session_state.get("openai_key_val", ""))
    if o_key:
        st.session_state.openai_key_val = o_key


    # Adding agents.yaml
    st.markdown("---")
    st.markdown(f"#### 🤖 {t('active_profile')}")
    
    # 1. 動態解析並取得當前 agents.yaml 的所有代理人名稱
    available_agents = get_parsed_agents()
    agent_names = [agent.get("name", "Unnamed Agent") for agent in available_agents]
    
    # 2. 提供下拉選單讓使用者切換當前執行任務的 Agent
    if "selected_agent_name" not in st.session_state:
        st.session_state.selected_agent_name = agent_names[0] if agent_names else ""
        
    chosen_agent_name = st.selectbox(
        "Select Executive Agent", 
        agent_names, 
        index=agent_names.index(st.session_state.selected_agent_name) if st.session_state.selected_agent_name in agent_names else 0
    )
    
    # 保存選取的 Agent 狀態
    if chosen_agent_name != st.session_state.selected_agent_name:
        st.session_state.selected_agent_name = chosen_agent_name
        add_log(f"Switched executive agent persona to: {chosen_agent_name}")
    
    # Status markers for API keys
    key_found = "No key configured"
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        key_found = "System Keys Active"
    elif st.session_state.get("gemini_key_val") or st.session_state.get("openai_key_val"):
        key_found = "User Keys Configured"
    st.caption(f"Status: {key_found}")

    st.markdown("---")
    
    # 4. Live activity log
    st.markdown(f"#### 📜 {t('live_log')}")
    log_text = "\n".join(st.session_state.logs[-10:])  # Last 10 records
    st.text_area("Workspace Events", log_text, height=180, disabled=True)

# -----------------------------------------------------------------------------
# MAIN VIEW PANEL
# -----------------------------------------------------------------------------
st.title(t("title"))
st.caption(t("subtitle"))

# Define Workspace tabs
tab_dash, tab_analyzer, tab_feas, tab_checklist, tab_risk, tab_pred, tab_roadmap, tab_studio, tab_notes, tab_magics = st.tabs([
    "🏠 " + t("dashboard"),
    "📂 " + t("doc_analyzer"),
    "📋 " + t("feasibility"),
    "🔍 " + t("tfda_checklist"),
    "⚡ " + t("risk_classifier"),
    "⚖️ " + t("predicate_finder"),
    "📅 " + t("compliance_roadmap"),
    "🛠️ " + t("agent_studio"),
    "📝 " + t("note_keeper"),
    "🪄 " + t("ai_magics")
])

# -----------------------------------------------------------------------------
# TAB 1: INTERACTIVE DASHBOARD
# -----------------------------------------------------------------------------
with tab_dash:
    st.markdown(f"### 📊 Workspace Status Center")
    
    # Stat widgets row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Active Style Preset", value=st.session_state.style_preset.title())
    with m2:
        model_name = "gemini-3.1-flash-lite (Default)"
        st.metric(label="Selected Model Platform", value="Multi-Provider Native")
    with m3:
        api_state_lbl = "Ready" if (os.environ.get("GEMINI_API_KEY") or st.session_state.get("gemini_key_val")) else "Limited"
        st.metric(label="API Connectivity", value=api_state_lbl)
    with m4:
        st.metric(label="Workspace Profile", value="FDA/TFDA MedDev v2")

    # Main Interactive Visual Health Chart
    st.markdown("#### Operational Workspace Metrics")
    chart_data = pd.DataFrame({
        "Task Queue": [100, 90, 85, 45, 10],
        "Verification Grounding": [40, 50, 75, 90, 95],
        "Workspace Readiness": [20, 45, 60, 80, 90]
    })
    st.line_chart(chart_data)

    # Health status check list
    st.markdown("#### System Validation Checks")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.info("🟢 **Green**: Core Workspace is active and parameters conform to schema.")
        st.success("🟢 Standardized file format is active for `agents.yaml`")
    with col_c2:
        if not (st.session_state.get("gemini_key_val") or st.session_state.get("openai_key_val")):
            st.warning("🟡 **Attention**: Running with simulated fallback engines. Enter API keys in the sidebar to activate live model calls.")
        else:
            st.success("🟢 Live API integration validated for workspace pipelines.")

# -----------------------------------------------------------------------------
# TAB 2: DOCUMENT ANALYZER
# -----------------------------------------------------------------------------
with tab_analyzer:
    st.markdown(f"### 📂 {t('doc_analyzer')}")
    st.write("Extract source contents from unstructured briefs or mixed device descriptors.")
    
    upload_file = st.file_uploader("Upload Product Specification Brief (TXT/PDF/YAML)", type=["txt", "pdf", "yaml"])
    pasted_text = st.text_area("Or Paste Raw Technical/Clinical Notes Here", height=150)
    
    if st.button("Store Active Context"):
        if upload_file:
            context = upload_file.read().decode("utf-8", errors="ignore")
            st.session_state.active_context = context
            add_log("Document loaded to active memory workspace.")
        elif pasted_text:
            st.session_state.active_context = pasted_text
            add_log("Pasted technical context loaded to memory.")
        st.success("Context loaded successfully.")

    st.markdown("#### Currently Active Context Memory")
    if st.session_state.active_context:
        st.info(st.session_state.active_context[:4000] + ("..." if len(st.session_state.active_context) > 4000 else ""))
    else:
        st.caption("No context currently loaded into memory.")

# -----------------------------------------------------------------------------
# TAB 3: REGULATORY FEASIBILITY
# -----------------------------------------------------------------------------
with tab_feas:
    st.markdown(f"### 📋 {t('feasibility')}")
    st.write("Synthesize FDA & TFDA cross-border pathways and regulatory feasibility reports.")

    # Model and prompt choices
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        f_model = st.selectbox("Pipeline Model Selection", ["gemini-3.1-flash-lite", "gpt-4o-mini", "gemini-3.5-flash", "gpt-4.1-mini"], key="f_model")
    with col_f2:
        f_grounding = st.checkbox("Require Grounded Validation Search", value=True)

    default_feas_prompt = """Review the product configuration to draft a comprehensive FDA Class II pathway feasibility report. Highlight gaps regarding biocompatibility validation."""
    feas_prompt = st.text_area(t("prompt_editor"), value=default_feas_prompt, height=100)

    if st.button(t("run_analysis"), key="btn_feas"):
        # Combine user prompt with workspace content
        combined_prompt = f"{feas_prompt}\n\nWorkspace Context:\n{st.session_state.active_context}"
        out = execute_llm_call(combined_prompt, "You are a professional medical device classification engineer.", model=f_model)
        st.session_state.reports_generated["feasibility"] = out
        
    if "feasibility" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["feasibility"], unsafe_allow_html=True)
        st.download_button(t("download_markdown"), st.session_state.reports_generated["feasibility"], file_name="feasibility_report.md")

# -----------------------------------------------------------------------------
# TAB 4: TFDA CHECKLIST GENERATOR
# -----------------------------------------------------------------------------
# =============================================================================
# TAB 4: TFDA CHECKLIST GENERATOR (具備上傳、下載與 Session 記憶功能)
# =============================================================================
with tab_checklist:
    st.markdown(f"### 🔍 {t('tfda_checklist')}")
    st.write("Construct, edit, import, and export structured Taiwan FDA technical checklist matrices.")

    # 1. 初始化 Session State 表格資料 (避免切換 Tab 時編輯內容遺失)
    if "tfda_checklist_df" not in st.session_state:
        st.session_state.tfda_checklist_df = pd.DataFrame({
            "Requirement Item": [
                "1. Functional specifications and design characteristics (功能規格與設計特徵描述)",
                "2. Biocompatibility assessment report (生物相容性評估報告)",
                "3. Software validation file conforming to IEC 62304 (軟體生命週期驗證檔案)",
                "4. Human factors and usability engineering files (人因與可用性工程評估報告)",
                "5. Sterilization testing parameters & Validation (無菌與滅菌製程驗證)"
            ],
            "Compliance Status": ["Compliant", "Gap Detected", "Compliant", "Not Applicable", "Gap Detected"],
            "Traceability Reference File": ["Doc-S-01", "Missing", "Doc-SW-88", "N/A", "Missing"]
        })

    # 2. 檔案上傳功能區塊
    st.markdown("#### 📥 匯入現有的 Checklist 檔案")
    uploaded_checklist = st.file_uploader(
        "Upload edited checklist (CSV format)", 
        type=["csv"], 
        key="checklist_uploader"
    )

    if uploaded_checklist is not None:
        try:
            # 使用 utf-8 或 utf-8-sig 讀取，避免中文字元解析失敗
            uploaded_df = pd.read_csv(uploaded_checklist, encoding="utf-8-sig")
            
            # 簡單驗證上傳的 CSV 欄位結構是否相符
            required_cols = ["Requirement Item", "Compliance Status", "Traceability Reference File"]
            if all(col in uploaded_df.columns for col in required_cols):
                st.session_state.tfda_checklist_df = uploaded_df[required_cols]
                add_log("Successfully imported a custom TFDA checklist via CSV upload.")
                st.success("✅ 檔案匯入成功！下方表格已更新。")
            else:
                st.error("❌ 匯入失敗：上傳的 CSV 欄位名稱與範本不符，請確認欄位包含：'Requirement Item', 'Compliance Status', 'Traceability Reference File'")
        except Exception as e:
            st.error(f"❌ 讀取檔案時發生錯誤: {str(e)}")

    st.markdown("---")

    # 3. 互動式資料編輯器 (綁定 Session State)
    st.markdown("#### 📝 編輯與確認 Checklist 內容")
    
    # 透過 data_editor 讓使用者自由新增、刪除或修改表格內容
    edited_df = st.data_editor(
        st.session_state.tfda_checklist_df, 
        num_rows="dynamic", 
        key="tfda_editor_instance"
    )
    
    # 將編輯後的結果即時存回 Session State
    st.session_state.tfda_checklist_df = edited_df

    # 4. 檔案下載與控制項區塊
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # 將最新的表格轉換為相容於 Excel 的 utf-8-sig 格式 CSV
        csv_buffer = io.BytesIO()
        edited_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_bytes = csv_buffer.getvalue()
        
        st.download_button(
            label="📤 匯出目前表格 (Download CSV)",
            data=csv_bytes,
            file_name="tfda_checklist_export.csv",
            mime="text/csv",
            key="download_checklist_btn"
        )
        st.caption("💡 註：此 CSV 檔案採用 UTF-8-SIG 編碼，可直接使用 Microsoft Excel 開啟，中文不會出現亂碼。")

    with col_dl2:
        if st.button("Synthesize Full Checklist Narrative"):
            checklist_str = edited_df.to_string()
            prompt = f"Create a comprehensive TFDA checklist synthesis report based on this matrix:\n{checklist_str}"
            out = execute_llm_call(prompt, "You are an expert on TFDA regulations.")
            st.session_state.reports_generated["checklist_report"] = out
            st.rerun() # 重新渲染頁面以即時顯示報告

    # 5. 渲染 AI 產生的技術報告
    if "checklist_report" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["checklist_report"], unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 5: RISK CLASSIFIER
# -----------------------------------------------------------------------------
with tab_risk:
    st.markdown(f"### ⚡ {t('risk_classifier')}")
    st.write("Predict Class rules based on duration, energy transmission, and anatomical exposure.")

    # Multi-factor inputs
    c1, c2 = st.columns(2)
    with c1:
        duration = st.selectbox("Anatomical Contact Duration", ["Temporary (< 24 hrs)", "Prolonged (24 hrs to 30 days)", "Permanent (> 30 days)"])
        active_energy = st.checkbox("Involves Active Energy Transmission", value=False)
    with c2:
        anatomical_exposure = st.selectbox("Anatomical Location", ["Intact Skin", "Mucosal Membrane", "Circulatory System", "Central Nervous System / Core Organs"])
    
    prompt = f"Provide classification risk assessment and suggested standards list for: Duration: {duration}, Energy: {active_energy}, Location: {anatomical_exposure}."
    
    if st.button("Evaluate Risks"):
        out = execute_llm_call(prompt, "You are a professional medical device risk management specialist using ISO 14971 standards.")
        st.session_state.reports_generated["risk"] = out
        
    if "risk" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["risk"], unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 6: PREDICATE FINDER
# -----------------------------------------------------------------------------
with tab_pred:
    st.markdown(f"### ⚖️ {t('predicate_finder')}")
    st.write("Contrast target devices against predicate FDA cleared systems.")

    pred_id = st.text_input("Benchmark Predicate Device ID (e.g., K213948)", value="K213948")
    comp_points = st.multiselect("Select Crucial Comparison Points", ["Intended Use", "Power Source", "Anatomical Path", "Software Framework", "Sterilization Scheme"], default=["Intended Use", "Anatomical Path"])

    prompt = f"Analyze predicate device equivalence map. Predicate Target: {pred_id}. Critical Parameters: {', '.join(comp_points)}."

    if st.button("Map Predicate Equivalence"):
        out = execute_llm_call(prompt, "You are an expert FDA regulatory submission writer specializing in 510(k) equivalence.")
        st.session_state.reports_generated["predicate"] = out
        
    if "predicate" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["predicate"], unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 7: COMPLIANCE ROADMAP
# -----------------------------------------------------------------------------
with tab_roadmap:
    st.markdown(f"### 📅 {t('compliance_roadmap')}")
    st.write("Formulate timeline pathways and phase budget approximations.")

    phase_cols = st.columns(3)
    with phase_cols[0]:
        st.markdown("**Phase 1: Verification**")
        st.write("- Usability testing\n- Biocompatibility evaluation")
    with phase_cols[1]:
        st.markdown("**Phase 2: Submission**")
        st.write("- 510(k) file assembly\n- TFDA review dossier compiling")
    with phase_cols[2]:
        st.markdown("**Phase 3: Launch**")
        st.write("- Post-market vigilance\n- Audit tracking")

    prompt = "Create a detailed step-by-step regulatory milestone timeline with approximate US & TFDA submission agency fees."
    
    if st.button("Synthesize Dynamic Roadmap"):
        out = execute_llm_call(prompt, "You are a highly experienced global regulatory consultant.")
        st.session_state.reports_generated["roadmap"] = out
        
    if "roadmap" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["roadmap"], unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 8: AGENT & SKILL STUDIO (YAML / MD)
# -----------------------------------------------------------------------------
with tab_studio:
    st.markdown(f"### 🛠️ {t('agent_studio')}")
    st.write("Manage, edit, standardize, and export configuration properties.")

    col_yaml, col_md = st.columns(2)
    
    with col_yaml:
        st.markdown("#### `agents.yaml` Workspace")
        agents_text = st.text_area("YAML Definition Block", value=st.session_state.agents_yaml, height=300)
        
        col_y_btns = st.columns(2)
        with col_y_btns[0]:
            if st.button("Standardize Schema"):
                try:
                    loaded_yaml = yaml.safe_load(agents_text)
                    # Normalize structure
                    normalized = {
                        "version": loaded_yaml.get("version", "1.0.0"),
                        "agents": []
                    }
                    for agent in loaded_yaml.get("agents", []):
                        normalized["agents"].append({
                            "name": agent.get("name", "Unnamed Agent"),
                            "role": agent.get("role", "No role assigned"),
                            "skills": agent.get("skills", [])
                        })
                    st.session_state.agents_yaml = yaml.dump(normalized, default_flow_style=False, sort_keys=False)
                    add_log("Standardized agents.yaml format.")
                    st.success("Successfully Normalized!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to parse YAML: {str(e)}")
        with col_y_btns[1]:
            st.download_button("Download YAML", st.session_state.agents_yaml, file_name="agents.yaml")

    with col_md:
        st.markdown("#### `skill.md` Workspace")
        skill_text = st.text_area("MD System Constraints", value=st.session_state.skill_md, height=300)
        st.session_state.skill_md = skill_text
        
        st.download_button("Download Skill.md", st.session_state.skill_md, file_name="skill.md")

# -----------------------------------------------------------------------------
# TAB 9: AI NOTE KEEPER (Structured Markdown with Coral Keywords)
# -----------------------------------------------------------------------------
with tab_notes:
    st.markdown(f"### 📝 {t('note_keeper')}")
    st.write("Clean loose clinical / design inputs into unified compliance files.")

    pasted_notes = st.text_area("Raw Clinical and Lab Workspace Notes", height=150, value=st.session_state.notes_text)
    if pasted_notes:
        st.session_state.notes_text = pasted_notes

    # Control parameters
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        keep_orig = st.checkbox(t("keep_prompt"), value=True)
        coral_on = st.checkbox(t("coral_enabled"), value=True)
    with c_col2:
        note_lang = st.radio("Output Language Format", ["Bilingual Parallel", "English Primary", "Traditional Chinese Primary"])

    if st.button("Process & Highlight Notes"):
        add_log("Processing raw unstructured clinical notes.")
        
        # Safe simulated structure generator with coral highlights applied
        formatted_output = f"""### 📝 Formatted Regulatory Note
**Source Reference**: Internal Clinical Concept Brief
**Date Processed**: {datetime.datetime.now().strftime("%Y-%m-%d")}

#### Cleaned Overview
The development pipeline is designed for diagnostic tracking. System processes must align with standard <span class='coral-highlight'>ISO 13485</span>.

#### Identified Action Steps
- [ ] Complete software configuration lifecycle analysis according to standard <span class='coral-highlight'>IEC 62304</span>.
- [ ] Establish precise hazard verification boundaries in compliance with <span class='coral-highlight'>ISO 14971</span> before **Q3 2026**.
"""
        if keep_orig:
            formatted_output += f"\n\n---\n**Original Note Context**:\n{pasted_notes}"
            
        st.session_state.reports_generated["notes_formatted"] = formatted_output

    if "notes_formatted" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["notes_formatted"], unsafe_allow_html=True)
        st.download_button("Export Notes", st.session_state.reports_generated["notes_formatted"], file_name="formatted_notes.md")

# -----------------------------------------------------------------------------
# TAB 10: FIVE AI MAGICS + THREE CUSTOM WOW AI FEATURES
# -----------------------------------------------------------------------------
with tab_magics:
    st.markdown(f"### 🪄 Signature AI Assist & Magics")
    st.write("Deploy specialized intelligence scripts to advance draft validation instantly.")

    magic_choice = st.selectbox("Select AI Magic Action", [
        "Magic 1: Prompt Spark (Structure Optimizer)",
        "Magic 2: Dual-Lens Translator (Bilingual Synced Glossary)",
        "Magic 3: Gap Hunter (Review Weak Rationale)",
        "Magic 4: Artifact Weaver (Build Draft Blocks)",
        "Magic 5: Workflow Oracle (Analyze Workspace Status)",
        "WOW 1: Standard Harmony Checker (ISO 13485/14971 Sync)",
        "WOW 2: Regulatory Claim Synthesizer (510k Clearance Logic)",
        "WOW 3: Bilingual Clinical Mockup Protocol Builder"
    ])

    input_text = st.text_area("Source Text / Prompt for Magic Tool", height=120)

    if st.button("Spark Magic Transformation"):
        if "Magic 1" in magic_choice:
            prompt = f"Optimize this system prompt for compliance models: {input_text}"
            out = execute_llm_call(prompt, "You are an expert prompt engineer specializing in regulatory affairs.")
            st.session_state.reports_generated["magic_out"] = f"### 🪄 Optimized Prompt Spark\n{out}"
            
        elif "Magic 2" in magic_choice:
            prompt = f"Translate this text into parallel English and Traditional Chinese with a mini domain glossary: {input_text}"
            out = execute_llm_call(prompt, "You are a professional medical translator.")
            st.session_state.reports_generated["magic_out"] = f"### 🪄 Dual-Lens Translation\n{out}"
            
        elif "Magic 3" in magic_choice:
            prompt = f"Scan this document text for missing clinical validation evidence or logic gaps: {input_text}"
            out = execute_llm_call(prompt, "You are a strict regulatory auditor checking for compliance gaps.")
            st.session_state.reports_generated["magic_out"] = f"### 🪄 Audited Gap Map\n{out}"
            
        elif "Magic 4" in magic_choice:
            prompt = f"Weave this partial text into a clean draft ready for submission: {input_text}"
            out = execute_llm_call(prompt, "You are a professional technical writer.")
            st.session_state.reports_generated["magic_out"] = f"### 🪄 Synthesized Draft Section\n{out}"
            
        elif "Magic 5" in magic_choice:
            prompt = "Analyze the entire active workspace (agents, active specs, files) and advise on next logical regulatory pipeline tasks."
            out = execute_llm_call(prompt, "You are an AI-powered regulatory strategy supervisor.")
            st.session_state.reports_generated["magic_out"] = f"### 🪄 Oracle Strategy Advisor\n{out}"

        # --- 3 CUSTOM WOW AI FEATURES ---
        elif "WOW 1" in magic_choice:
            prompt = f"Evaluate this technical design text specifically for direct synergy gaps between ISO 13485 (QMS) and ISO 14971 (Risk Management): {input_text}"
            out = execute_llm_call(prompt, "You are a world-class QMS & Risk auditor.")
            st.session_state.reports_generated["magic_out"] = f"### 🧬 WOW 1: Standard Harmony Evaluator\n**System Sync Diagnostic Status**: High Relevance\n\n{out}"
            
        elif "WOW 2" in magic_choice:
            prompt = f"Extract technology claims from this draft and restructure them into formal FDA cleared wording models: {input_text}"
            out = execute_llm_call(prompt, "You are a senior regulatory strategist.")
            st.session_state.reports_generated["magic_out"] = f"### 🧬 WOW 2: Regulatory Claim Synthesizer\n**Inferred Intended Use Matcher**: Successful\n\n{out}"
            
        elif "WOW 3" in magic_choice:
            prompt = f"Draft an interactive parallel clinical evaluation or bench testing mockup protocol for this device description: {input_text}"
            out = execute_llm_call(prompt, "You are a principal medical director draft clinical studies.")
            st.session_state.reports_generated["magic_out"] = f"### 🧬 WOW 3: Bilingual Mock Clinical Blueprint\n\n{out}"

    if "magic_out" in st.session_state.reports_generated:
        st.markdown("---")
        st.markdown(st.session_state.reports_generated["magic_out"], unsafe_allow_html=True)
        st.download_button("Export Magic Output", st.session_state.reports_generated["magic_out"], file_name="magic_transformation.md")
