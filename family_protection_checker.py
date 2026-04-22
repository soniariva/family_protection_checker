import streamlit as st
import pandas as pd
from datetime import datetime
# ==================== 靜默儲存到 Google Sheets ====================
import requests
import json

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxuoIJBs_MHy7XekB8RiOCtyiyiZghm22wS-8HRBv2IfZ9-dti9-1kMlo3PA0kNG4Ti/exec"   # 改為你嘅 Google Apps Script 網址
SAVE_TO_SHEETS = True   # 是否啟用儲存

def silent_save_to_gs(data):
    if not SAVE_TO_SHEETS or not WEBAPP_URL:
        return
    try:
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": data.get("name", ""),
            "phone": data.get("phone", ""),
            "risk": data.get("risk", ""),
            "budget": data.get("budget", 0),
            "has_medical": data.get("has_medical", ""),
            "company": data.get("company", ""),
            "inpatient_amount": data.get("inpatient_amount", 0),
            "surgery_amount": data.get("surgery_amount", 0),
            "cancer_amount": data.get("cancer_amount", 0),
            "critical_amount": data.get("critical_amount", 0),
            "accident_medical": data.get("accident_medical", 0),
            "accident_death": data.get("accident_death", 0),
            "monthly_expense": data.get("monthly_expense", 0),
            "mortgage": data.get("mortgage", 0),
            "total_income": data.get("annual_income", 0) + data.get("spouse_income", 0)
        }
        requests.post(WEBAPP_URL, json=payload, timeout=5)
    except:
        pass   # 靜默失敗，完全無提示


st.set_page_config(page_title="全方位家庭保障檢視", page_icon="🏠", layout="wide")

st.title("🏠 全方位家庭保障檢視")
st.caption("輸入你嘅家庭同財務資料，系統會自動計算各項保障缺口")

# 初始化 session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "client_data" not in st.session_state:
    st.session_state.client_data = {}

# 進度條
st.progress(st.session_state.step / 5)

# ==================== Step 1: 家庭成員基本資料 ====================
if st.session_state.step == 1:
    st.header("👨‍👩‍👧‍👦 第一步：家庭成員基本資料")
    
    # 主申請人
    st.subheader("主申請人")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("姓名")
    with col2:
        age = st.number_input("年齡", min_value=0, max_value=120, step=1)
    with col3:
        occupation = st.text_input("職業")
    
    # 配偶
    has_spouse = st.radio("有冇配偶？", ["有", "冇"], horizontal=True)
    spouse_name = ""
    spouse_age = 0
    spouse_occ = ""
    if has_spouse == "有":
        col1, col2, col3 = st.columns(3)
        with col1:
            spouse_name = st.text_input("配偶姓名")
        with col2:
            spouse_age = st.number_input("配偶年齡", min_value=0, max_value=120, step=1)
        with col3:
            spouse_occ = st.text_input("配偶職業")
    
    # 子女
    num_children = st.number_input("子女數目", min_value=0, max_value=10, step=1)
    children = []
    for i in range(num_children):
        col1, col2 = st.columns(2)
        with col1:
            child_name = st.text_input(f"子女 {i+1} 姓名", key=f"child_name_{i}")
        with col2:
            child_age = st.number_input(f"子女 {i+1} 年齡", min_value=0, max_value=30, step=1, key=f"child_age_{i}")
        children.append({"name": child_name, "age": child_age})
    
    # 父母（供養）
    num_parents = st.number_input("需要供養嘅父母數目", min_value=0, max_value=4, step=1)
    parents = []
    for i in range(num_parents):
        col1, col2 = st.columns(2)
        with col1:
            parent_name = st.text_input(f"父母 {i+1} 姓名", key=f"parent_name_{i}")
        with col2:
            parent_age = st.number_input(f"父母 {i+1} 年齡", min_value=0, max_value=120, step=1, key=f"parent_age_{i}")
        parents.append({"name": parent_name, "age": parent_age})
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("下一步 →"):
            # 儲存資料
            st.session_state.client_data["name"] = name
            st.session_state.client_data["age"] = age
            st.session_state.client_data["occupation"] = occupation
            st.session_state.client_data["has_spouse"] = has_spouse
            st.session_state.client_data["spouse_name"] = spouse_name
            st.session_state.client_data["spouse_age"] = spouse_age
            st.session_state.client_data["spouse_occ"] = spouse_occ
            st.session_state.client_data["children"] = children
            st.session_state.client_data["parents"] = parents
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("重置全部"):
            st.session_state.client_data = {}
            st.session_state.step = 1
            st.rerun()

# ==================== Step 2: 財務狀況 ====================
elif st.session_state.step == 2:
    st.header("💰 第二步：財務狀況")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("收入")
        annual_income = st.number_input("主申請人年收入 (HK$)", min_value=0, step=50000, value=0)
        spouse_income = 0
        if st.session_state.client_data.get("has_spouse") == "有":
            spouse_income = st.number_input("配偶年收入 (HK$)", min_value=0, step=50000, value=0)
        other_income = st.number_input("其他收入 (租金/投資等)", min_value=0, step=50000, value=0)
        
        st.subheader("資產")
        savings = st.number_input("現金/儲蓄 (HK$)", min_value=0, step=100000, value=0)
        investments = st.number_input("投資 (股票/基金等)", min_value=0, step=100000, value=0)
        property_value = st.number_input("物業價值 (HK$)", min_value=0, step=500000, value=0)
    with col2:
        st.subheader("支出")
        monthly_expense = st.number_input("每月家庭開支 (HK$)", min_value=0, step=5000, value=0)
        annual_expense = monthly_expense * 12
        st.caption(f"每年總支出約: HK$ {annual_expense:,}")
        
        st.subheader("負債")
        mortgage = st.number_input("按揭貸款餘額 (HK$)", min_value=0, step=100000, value=0)
        other_debt = st.number_input("其他債務 (HK$)", min_value=0, step=50000, value=0)
        
        st.subheader("教育目標")
        edu_years = st.number_input("距離子女升大學仲有幾年", min_value=0, step=1, value=10)
        edu_cost = st.number_input("預計每年大學費用 (HK$)", min_value=0, step=50000, value=200000)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("下一步 →"):
            # 儲存財務資料
            st.session_state.client_data["annual_income"] = annual_income
            st.session_state.client_data["spouse_income"] = spouse_income
            st.session_state.client_data["other_income"] = other_income
            st.session_state.client_data["savings"] = savings
            st.session_state.client_data["investments"] = investments
            st.session_state.client_data["property_value"] = property_value
            st.session_state.client_data["monthly_expense"] = monthly_expense
            st.session_state.client_data["mortgage"] = mortgage
            st.session_state.client_data["other_debt"] = other_debt
            st.session_state.client_data["edu_years"] = edu_years
            st.session_state.client_data["edu_cost"] = edu_cost
            st.session_state.step = 3
            st.rerun()

# ==================== Step 3: 現有保障輸入 ====================
elif st.session_state.step == 3:
    st.header("📋 第三步：現有保障（可多項）")
    st.info("請輸入你同家人現有嘅保險賠償額，如果冇該項保障，請填 0")
    
    # 主申請人
    st.subheader("主申請人")
    col1, col2, col3 = st.columns(3)
    with col1:
        medical_inpatient = st.number_input("醫療 - 住院賠償 (每晚)", min_value=0, step=500, value=0)
        medical_surgery = st.number_input("醫療 - 手術賠償 (每次)", min_value=0, step=10000, value=0)
    with col2:
        medical_cancer = st.number_input("醫療 - 癌症治療 (每年)", min_value=0, step=50000, value=0)
        critical = st.number_input("危疾一筆過賠償", min_value=0, step=100000, value=0)
    with col3:
        accident_medical = st.number_input("意外醫療 (每年)", min_value=0, step=10000, value=0)
        accident_death = st.number_input("意外身故/傷殘", min_value=0, step=100000, value=0)
        life = st.number_input("人壽保險賠償額", min_value=0, step=100000, value=0)
    
    # 儲蓄/教育基金
    st.subheader("儲蓄及教育基金")
    savings_insurance = st.number_input("儲蓄保險/基金現有價值", min_value=0, step=50000, value=0)
    edu_fund = st.number_input("已為子女準備嘅教育基金", min_value=0, step=50000, value=0)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("下一步 →"):
            # 儲存保障資料
            st.session_state.client_data["medical_inpatient"] = medical_inpatient
            st.session_state.client_data["medical_surgery"] = medical_surgery
            st.session_state.client_data["medical_cancer"] = medical_cancer
            st.session_state.client_data["critical"] = critical
            st.session_state.client_data["accident_medical"] = accident_medical
            st.session_state.client_data["accident_death"] = accident_death
            st.session_state.client_data["life"] = life
            st.session_state.client_data["savings_insurance"] = savings_insurance
            st.session_state.client_data["edu_fund"] = edu_fund
            st.session_state.step = 4
            st.rerun()

# ==================== Step 4: 分析缺口 ====================
elif st.session_state.step == 4:
    st.header("📊 第四步：保障缺口分析")
    data = st.session_state.client_data
    
    # 市場參考值
    market = {
        "住院": 1200,
        "手術": 40000,
        "癌症": 720000,
        "危疾": 1000000,
        "意外醫療": 50000,
        "意外身故": 1000000,
    }
    
    # 人壽建議額 = 10年家庭支出 + 子女教育金 + 房貸餘額
    annual_expense = data.get("monthly_expense", 0) * 12
    edu_needed = data.get("edu_years", 0) * data.get("edu_cost", 0)
    mortgage = data.get("mortgage", 0)
    recommended_life = annual_expense * 10 + edu_needed + mortgage
    
    # 計算各項缺口
    inpatient_gap = max(0, market["住院"] - data["medical_inpatient"])
    surgery_gap = max(0, market["手術"] - data["medical_surgery"])
    cancer_gap = max(0, market["癌症"] - data["medical_cancer"])
    critical_gap = max(0, market["危疾"] - data["critical"])
    accident_med_gap = max(0, market["意外醫療"] - data["accident_medical"])
    accident_death_gap = max(0, market["意外身故"] - data["accident_death"])
    life_gap = max(0, recommended_life - data["life"])
    
    # 教育基金缺口
    edu_gap = max(0, edu_needed - data["edu_fund"])
    
    # 顯示對比表格
    st.markdown("### 市場建議 vs 你現有保障")
    compare_df = pd.DataFrame({
        "保障項目": ["醫療 - 住院 (每晚)", "醫療 - 手術 (每次)", "醫療 - 癌症 (每年)", 
                     "危疾 (一筆過)", "意外醫療 (每年)", "意外身故/傷殘", "人壽保障", "教育基金"],
        "市場/建議水平": [f"${market['住院']:,}", f"${market['手術']:,}", f"${market['癌症']:,}",
                          f"${market['危疾']:,}", f"${market['意外醫療']:,}", f"${market['意外身故']:,}",
                          f"${recommended_life:,.0f}", f"${edu_needed:,.0f}"],
        "你現有": [f"${data['medical_inpatient']:,}", f"${data['medical_surgery']:,}", f"${data['medical_cancer']:,}",
                   f"${data['critical']:,}", f"${data['accident_medical']:,}", f"${data['accident_death']:,}",
                   f"${data['life']:,}", f"${data['edu_fund']:,}"],
        "差額 (不足)": [f"${inpatient_gap:,}", f"${surgery_gap:,}", f"${cancer_gap:,}",
                        f"${critical_gap:,}", f"${accident_med_gap:,}", f"${accident_death_gap:,}",
                        f"${life_gap:,.0f}", f"${edu_gap:,.0f}"]
    })
    st.dataframe(compare_df, use_container_width=True)
    
    # 主要缺口總結
    st.divider()
    st.subheader("🔍 主要保障缺口")
    gaps = []
    if inpatient_gap > 0:
        gaps.append(f"醫療住院不足，每晚差額 ${inpatient_gap:,}")
    if surgery_gap > 0:
        gaps.append(f"醫療手術不足，每次差額 ${surgery_gap:,}")
    if cancer_gap > 0:
        gaps.append(f"癌症治療保障不足，每年差額 ${cancer_gap:,}")
    if critical_gap > 0:
        gaps.append(f"危疾保障不足，差額 ${critical_gap:,}")
    if accident_med_gap > 0:
        gaps.append(f"意外醫療不足，每年差額 ${accident_med_gap:,}")
    if accident_death_gap > 0:
        gaps.append(f"意外身故保障不足，差額 ${accident_death_gap:,}")
    if life_gap > 0:
        gaps.append(f"人壽保障不足，差額 ${life_gap:,.0f}")
    if edu_gap > 0:
        gaps.append(f"教育基金不足，差額 ${edu_gap:,.0f}")
    
    if gaps:
        for g in gaps:
            st.error(f"⚠️ {g}")
    else:
        st.success("✅ 各項保障均達到建議水平，無明顯缺口")
    
    # 建議行動
    st.subheader("💡 建議行動")
    recs = []
    if data["medical_inpatient"] == 0 and data["medical_surgery"] == 0 and data["medical_cancer"] == 0:
        recs.append("完全沒有醫療保險，建議立即配置自願醫保靈活計劃")
    else:
        if inpatient_gap > 0 or surgery_gap > 0 or cancer_gap > 0:
            recs.append("升級醫療保險，提高住院、手術及癌症治療賠償額")
    if data["critical"] == 0:
        recs.append("完全沒有危疾保險，建議添置，保額最少 $1,000,000")
    elif critical_gap > 0:
        recs.append("增加危疾保額至 $1,000,000 或以上")
    if data["accident_medical"] == 0 and data["accident_death"] == 0:
        recs.append("完全沒有意外保險，建議添置")
    else:
        if accident_med_gap > 0 or accident_death_gap > 0:
            recs.append("加強意外保險，提高醫療及身故賠償")
    if data["life"] == 0:
        recs.append("沒有人壽保險，建議按家庭責任配置定期人壽")
    elif life_gap > 0:
        recs.append(f"增加人壽保額至 ${recommended_life:,.0f}，保障家人生活")
    if edu_gap > 0:
        recs.append(f"教育基金不足，建議每月儲蓄或購買教育儲蓄保險")
    
    for rec in recs:
        st.info(f"📌 {rec}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回修改"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("生成報告 →"):
            st.session_state.step = 5
            st.rerun()

# ==================== Step 5: 生成專業報告 ====================
elif st.session_state.step == 5:
    st.header("📄 第五步：全方位家庭保障報告")
    data = st.session_state.client_data

    # 計算建議值（與你原有報告一致）
    annual_expense = data.get("monthly_expense", 0) * 12
    edu_needed = data.get("edu_years", 0) * data.get("edu_cost", 0)
    mortgage = data.get("mortgage", 0)
    recommended_life = annual_expense * 10 + edu_needed + mortgage

    # 顯示報告內容（保持原有樣式）
    st.markdown(f"**客人姓名**：{data['name']}  &nbsp;&nbsp; **檢視日期**：{data['date']}")
    st.markdown("---")

    st.markdown("### 👨‍👩‍👧‍👦 家庭狀況")
    st.markdown(f"- 主申請人：{data['name']}，{data['age']}歲，{data['occupation']}")
    if data.get("has_spouse") == "有":
        st.markdown(f"- 配偶：{data['spouse_name']}，{data['spouse_age']}歲，{data['spouse_occ']}")
    for i, child in enumerate(data.get("children", [])):
        st.markdown(f"- 子女 {i+1}：{child['name']}，{child['age']}歲")
    for i, parent in enumerate(data.get("parents", [])):
        st.markdown(f"- 供養父母 {i+1}：{parent['name']}，{parent['age']}歲")

    st.markdown("### 💰 財務概況")
    total_income = data.get("annual_income", 0) + data.get("spouse_income", 0) + data.get("other_income", 0)
    st.markdown(f"- 家庭年收入：HK$ {total_income:,}")
    st.markdown(f"- 每月家庭開支：HK$ {data.get('monthly_expense', 0):,}")
    st.markdown(f"- 資產總值：HK$ {data.get('savings',0)+data.get('investments',0)+data.get('property_value',0):,}")
    st.markdown(f"- 負債總額：HK$ {data.get('mortgage',0)+data.get('other_debt',0):,}")

    st.markdown("### 📋 保障缺口分析")
    # 醫療缺口
    inpatient_gap = max(0, 1200 - data.get("medical_inpatient", 0))
    surgery_gap = max(0, 40000 - data.get("medical_surgery", 0))
    cancer_gap = max(0, 720000 - data.get("medical_cancer", 0))
    critical_gap = max(0, 1000000 - data.get("critical", 0))
    accident_med_gap = max(0, 50000 - data.get("accident_medical", 0))
    accident_death_gap = max(0, 1000000 - data.get("accident_death", 0))
    life_gap = max(0, recommended_life - data.get("life", 0))
    edu_gap = max(0, edu_needed - data.get("edu_fund", 0))

    st.markdown(f"- 醫療住院：現有 HK$ {data.get('medical_inpatient',0):,}/晚，建議 HK$ 1,200，差額 HK$ {inpatient_gap:,}")
    st.markdown(f"- 醫療手術：現有 HK$ {data.get('medical_surgery',0):,}/次，建議 HK$ 40,000，差額 HK$ {surgery_gap:,}")
    st.markdown(f"- 癌症治療：現有 HK$ {data.get('medical_cancer',0):,}/年，建議 HK$ 720,000，差額 HK$ {cancer_gap:,}")
    st.markdown(f"- 危疾：現有 HK$ {data.get('critical',0):,}，建議 HK$ 1,000,000，差額 HK$ {critical_gap:,}")
    st.markdown(f"- 意外醫療：現有 HK$ {data.get('accident_medical',0):,}/年，建議 HK$ 50,000，差額 HK$ {accident_med_gap:,}")
    st.markdown(f"- 意外身故：現有 HK$ {data.get('accident_death',0):,}，建議 HK$ 1,000,000，差額 HK$ {accident_death_gap:,}")
    st.markdown(f"- 人壽：現有 HK$ {data.get('life',0):,}，建議 HK$ {recommended_life:,.0f}，差額 HK$ {life_gap:,.0f}")
    st.markdown(f"- 教育基金：已準備 HK$ {data.get('edu_fund',0):,}，目標 HK$ {edu_needed:,.0f}，差額 HK$ {edu_gap:,.0f}")

    st.markdown("---")
    st.markdown("*無壓力・唔使買・純粹幫你睇*")
    st.caption("顧問：Sonia")

    # 準備報告文字（用於下載）
    report_text = f"""
全方位家庭保障檢視報告
客人：{data['name']}
日期：{data['date']}

家庭狀況
- 主申請人：{data['name']}，{data['age']}歲，{data['occupation']}
- 配偶：{data['spouse_name'] if data.get('has_spouse')=='有' else '無'}
- 子女數目：{len(data.get('children', []))}
- 供養父母數目：{len(data.get('parents', []))}

財務概況
- 家庭年收入：HK$ {total_income:,}
- 每月開支：HK$ {data.get('monthly_expense',0):,}
- 資產總值：HK$ {data.get('savings',0)+data.get('investments',0)+data.get('property_value',0):,}
- 負債總額：HK$ {data.get('mortgage',0)+data.get('other_debt',0):,}

保障缺口
- 醫療住院：現有 HK$ {data.get('medical_inpatient',0):,}/晚，建議 HK$ 1,200，差額 HK$ {inpatient_gap:,}
- 醫療手術：現有 HK$ {data.get('medical_surgery',0):,}/次，建議 HK$ 40,000，差額 HK$ {surgery_gap:,}
- 癌症治療：現有 HK$ {data.get('medical_cancer',0):,}/年，建議 HK$ 720,000，差額 HK$ {cancer_gap:,}
- 危疾：現有 HK$ {data.get('critical',0):,}，建議 HK$ 1,000,000，差額 HK$ {critical_gap:,}
- 意外醫療：現有 HK$ {data.get('accident_medical',0):,}/年，建議 HK$ 50,000，差額 HK$ {accident_med_gap:,}
- 意外身故：現有 HK$ {data.get('accident_death',0):,}，建議 HK$ 1,000,000，差額 HK$ {accident_death_gap:,}
- 人壽：現有 HK$ {data.get('life',0):,}，建議 HK$ {recommended_life:,.0f}，差額 HK$ {life_gap:,.0f}
- 教育基金：已準備 HK$ {data.get('edu_fund',0):,}，目標 HK$ {edu_needed:,.0f}，差額 HK$ {edu_gap:,.0f}

---
無壓力・唔使買・純粹幫你睇
顧問：Sonia
    """

    # 只有一個按鈕：儲蓄記錄（點擊後下載 + 靜默儲存）
    if st.button("💾 儲蓄記錄"):
        # 1. 靜默儲存到 Google Sheets
        silent_save_to_gs(data)
        # 2. 觸發下載（使用 st.download_button 但放在 button 內，需要特殊處理）
        # Streamlit 唔允許喺 button 內再放 download_button，所以改為用 st.markdown 提供 data URI 下載連結
        b64 = base64.b64encode(report_text.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="保險報告_{data["name"]}.txt">📥 按此下載報告</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("報告已儲存記錄，多謝使用！")   # 只顯示呢一句，唔提 Sonia 跟進

    if st.button("← 開始新檢視"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
