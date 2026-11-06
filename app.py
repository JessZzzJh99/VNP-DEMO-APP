import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ----------------- CONFIG & CONSTANTS -----------------
st.set_page_config(page_title="Vazyme Demo Request Hub", page_icon="🧬", layout="wide")
CSV_FILE = "vazyme_questionnaire_records.csv"
ADMIN_PASSWORD = "123"

# Initialize workflow count state
if 'workflow_count' not in st.session_state:
    st.session_state.workflow_count = 1

def add_workflow():
    st.session_state.workflow_count += 1

def remove_workflow():
    if st.session_state.workflow_count > 1:
        st.session_state.workflow_count -= 1

# ----------------- SMART MODE SWITCH (HIDDEN ADMIN) -----------------
query_params = st.query_params
is_admin_url = query_params.get("admin") == "true"
app_mode = "Client Questionnaire"

if is_admin_url:
    st.sidebar.title("Management")
    app_mode = st.sidebar.radio("Mode:", ["Client Questionnaire", "Admin Dashboard"])

# ----------------- VIEW 1: CLIENT QUESTIONNAIRE -----------------
if app_mode == "Client Questionnaire":
    st.title("🧬 Vazyme Nucleic Acid Extraction Questionnaire")
    st.markdown("Thank you for your interest in Vazyme Biotech's nucleic acid extraction solutions. Please complete the questionnaire below.")

    with st.form("client_form"):
        # ================= SECTION 1: Contact Information =================
        st.header("Section 1: Contact Information")
        c1, c2, c3 = st.columns(3)
        with c1:
            full_name = st.text_input("1. Full Name *")
            job_title = st.text_input("2. Job Title")
        with c2:
            company_name = st.text_input("3. Company Name *")
            department = st.text_input("4. Department")
        with c3:
            email_address = st.text_input("5. Email Address *")
            
        st.markdown("---")

        # ================= SECTION 2: Current Status & Throughput =================
        st.header("Section 2: Current Status & Throughput")
        
        col_a, col_b = st.columns(2)
        with col_a:
            current_method = st.selectbox("Current method for nucleic acid extraction", ["Manual extraction", "Automated extraction using instrument", "Outsourced to CRO/Service provider", "Other"])
            method_detail = st.text_input("Specify kit name (Cat.No) or instrument brand/model:")
            
            samples_per_month = st.selectbox("Approximately how many samples do you extract per month?", ["< 50", "50-200", "200-500", "> 500"])
            batch_process = st.selectbox("Do you often need to process batches of 8-32 or 96 samples at once?", ["Yes, regularly", "Occasionally", "Rarely", "Never"])
            
        with col_b:
            challenges = st.multiselect("What challenges or issues are you experiencing? (Select all that apply)", ["Low yield", "Poor purity", "RNA degradation", "Long processing time", "Difficult operation", "Poor reproducibility", "Column clogging", "High cost", "Automation compatibility issues", "Other"])
            challenges_other = st.text_input("Specify other challenges (if any):")
            pref_instrument = st.selectbox("Would you prefer a 32-channel (VNP-32P) or a 96-channel instrument (VNP-96P)?", ["32-channel", "96-channel", "Not sure yet depends on use case"])

        st.markdown("---")

        # ================= SECTION 3: Extraction Workflows =================
        st.header("Section 3: Extraction Workflows & Applications")
        st.markdown("Please fill out the details for your extraction workflow below[cite: 1].")

        workflows_data = []

        for i in range(st.session_state.workflow_count):
            st.markdown(f"### 🔹 Workflow {i+1}")
            
            w1, w2, w3 = st.columns(3)
            with w1:
                target_na = st.selectbox(f"Target Nucleic Acid (W{i+1}) *", ["Genomic DNA", "Plasmid DNA", "cfDNA", "Microbial DNA", "Total RNA", "cfRNA", "Microbial RNA", "Microbial DNA & RNA", "miRNA only", "Total gDNA & RNA", "Other"], key=f"target_{i}")
                sample_type = st.selectbox(f"Biological Sample Type (W{i+1}) *", ["Cell", "Tissue", "Microbe: Virus, Fungi, Bacteria", "Plant", "FFPE", "Whole blood", "Plasma", "Serum", "Urine", "Swab", "Stool", "Soil", "Water", "Food", "Other"], key=f"sample_{i}")
                sample_detail = st.text_input(f"Specify Sample Details (W{i+1}):", key=f"s_det_{i}")

            with w2:
                sample_condition = st.selectbox(f"Sample Condition (W{i+1})", ["Fresh", "Frozen", "FFPE", "Other"], key=f"cond_{i}")
                condition_detail = st.text_input(f"If Frozen, specify reagent/buffer (W{i+1}):", key=f"c_det_{i}")
                input_amount_type = st.selectbox(f"Typical Input Unit (W{i+1})", ["Cell number", "Tissue weight", "Sample volume", "Size/Amount", "OD value", "Other"], key=f"in_unit_{i}")
                input_amount_val = st.text_input(f"Specify Input Amount (W{i+1}):", key=f"in_val_{i}")

            with w3:
                downstream = st.multiselect(f"Downstream Applications (W{i+1})", ["RT-qPCR", "PCR / Gel electrophoresis", "Sanger sequencing", "DNA-Seq", "RNA-Seq", "Single-cell sequencing", "Microarray analysis", "Cloning", "Other"], key=f"ds_{i}")
                qc_method = st.multiselect(f"Quality Assessment Method (W{i+1})", ["NanoDrop", "Qubit", "TapeStation", "Gel electrophoresis", "Other"], key=f"qc_{i}")
                requirements = st.multiselect(f"Extraction Requirements (W{i+1})", ["High yield", "High purity", "High integrity", "Specific fragment size range", "Low elution volume", "Other"], key=f"req_{i}")
                req_detail = st.text_input(f"Specify Requirement Details (W{i+1}):", key=f"r_det_{i}")

            workflows_data.append({
                "Workflow": f"W{i+1}", "Target": target_na, "Sample_Type": sample_type,
                "Sample_Detail": sample_detail, "Condition": sample_condition,
                "Condition_Detail": condition_detail, "Input": f"{input_amount_val} ({input_amount_type})",
                "Downstream": ", ".join(downstream), "QC": ", ".join(qc_method),
                "Requirements": ", ".join(requirements), "Req_Details": req_detail
            })
            st.markdown("---")

        submit_btn = st.form_submit_button("🚀 Submit Technical Questionnaire", type="primary")
        
        if submit_btn:
            if not full_name or not company_name or not email_address:
                st.error("⚠️ Please fill in all required Contact Information marked with *.")
            else:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rec = []
                ch = ", ".join(challenges) + (f" (Other: {challenges_other})" if challenges_other else "")
                meth = current_method + (f" - {method_detail}" if method_detail else "")
                
                for wf in workflows_data:
                    rec.append({
                        "Timestamp": ts, "Full_Name": full_name, "Job_Title": job_title,
                        "Company": company_name, "Department": department, "Email": email_address,
                        "Current_Method": meth, "Challenges": ch, "Samples_Per_Month": samples_per_month,
                        "Batch_Processing": batch_process, "Instrument_Preference": pref_instrument,
                        "Workflow_No": wf["Workflow"], "Target_NA": wf["Target"], "Sample_Type": wf["Sample_Type"],
                        "Sample_Detail": wf["Sample_Detail"], "Sample_Condition": wf["Condition"],
                        "Condition_Detail": wf["Condition_Detail"], "Input_Amount": wf["Input"],
                        "Downstream_Apps": wf["Downstream"], "QC_Method": wf["QC"],
                        "Requirements": wf["Requirements"], "Requirement_Details": wf["Req_Details"]
                    })
                
                df_new = pd.DataFrame(rec)
                df_new.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
                st.success(f"✅ Thank you, {full_name}! Your questionnaire has been successfully submitted.")
                st.balloons()

    st.markdown("#### ⚙️ Need to add another extraction workflow?")
    b1, b2, _ = st.columns([1, 1, 3])
    with b1:
        st.button("➕ Add Another Workflow", on_click=add_workflow)
    with b2:
        if st.session_state.workflow_count > 1:
            st.button("➖ Remove Last Workflow", on_click=remove_workflow)

# ----------------- VIEW 2: ADMIN DASHBOARD -----------------
elif app_mode == "Admin Dashboard":
    st.title("📊 Admin Dashboard - Collected Submissions")
    pwd = st.text_input("Enter Admin Password to View Data", type="password")
    
    if pwd != ADMIN_PASSWORD:
        if pwd != "": st.error("Incorrect password.")
        st.info("💡 Protected Area. Please enter the administrator password.")
    else:
        st.success("Access granted!")
        if os.path.exists(CSV_FILE):
            df_records = pd.read_csv(CSV_FILE)
            st.subheader(f"Total Submissions Records: {len(df_records)}")
            sq = st.text_input("🔍 Search records by Company Name or Name:", "")
            if sq:
                mask = df_records.apply(lambda r: r.astype(str).str.contains(sq, case=False, na=False).any(), axis=1)
                df_records = df_records[mask]
            st.dataframe(df_records, use_container_width=True)
            st.download_button("📥 Download All Records as CSV", df_records.to_csv(index=False).encode('utf-8'), "vazyme_client_questionnaires.csv", "text/csv")
        else:
            st.info("ℹ️ No questionnaire records found yet.")