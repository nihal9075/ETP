import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- PDF Generation Class ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'ETP Daily Operation Sheet', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- Main App Logic ---
def main():
    st.title("💧 ETP Operation Log App")
    st.write("Fill data in English/Numbers only (বাংলা পিডিএফ-এ আসবে না).")

    # 1. Header Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        op_date = st.date_input("Date", datetime.today())
    with col2:
        shift = st.text_input("Shift", placeholder="Morning")
    with col3:
        operator_name = st.text_input("Operator Name")

    st.divider()

    # 2. Data Table Setup
    st.subheader("1. Operation Data")
    default_data = pd.DataFrame(
        [{"Sl No.": 1, 
          "Water Treated Hours": 0.0, 
          "Flow Rate (m3/hr)": 0.0, 
          "Anionic Polymer": "0 g",   
          "Acqalent": "0 L",         
          "Water Treated (L)": 0.0, 
          "Remarks": ""}],
    )

    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Anionic Polymer": st.column_config.TextColumn(
                "Anionic Polymer (Qty)",
                help="Enter amount with unit (e.g., 18 g, 5 kg)",
                required=True
            ),
            "Acqalent": st.column_config.TextColumn(
                "Acqalent (Qty)",
                help="Enter amount with unit (e.g., 500 ml, 2 L)",
                required=True
            ),
            "Run Hours": st.column_config.NumberColumn("Run Hours"),
            "Flow Rate (m3/hr)": st.column_config.NumberColumn("Flow Rate (m3/hr)"),
            "Water Treated (m3)": st.column_config.NumberColumn("Water Treated (m3)"),
        }
    )

    st.divider()

    # 3. NEW: Optional Time Log Section
    st.subheader("2. Machine Run Time Log (Optional)")
    add_time_log = st.checkbox("Add Time Log to PDF? (সময় তালিকা যুক্ত করতে চান?)")
    
    time_log_text = ""
    if add_time_log:
        st.info("Write your schedule below clearly.")
        # Default example text based on user request
        default_log = (
            "Water Treated Run - 08.00am\n"
            "Water Treated Off - 01.00pm\n\n"
            "Water Treated Run - 02.00pm\n"
            "Water Treated Off - 07.00pm\n\n"
            "Water Treated Run - 07.20pm\n"
            "Water Treated Off - 11.00pm\n"
            "Total Time: 13.40hr"
        )
        time_log_text = st.text_area("Enter Run/Off Schedule:", value=default_log, height=200)

    st.divider()

    # 4. Operator Notes
    st.subheader("3. Other Observations")
    operator_notes = st.text_area(
        "Write any other special notes here:",
        height=80,
        placeholder="Example: Motor cleaning done."
    )

    st.divider()

    # 5. Generate Button
    if st.button("Generate PDF Report", type="primary"):
        if not operator_name:
            st.warning("Please enter an Operator Name first.")
        else:
            # Pass the new time_log_text to the export function
            export_pdf(op_date, shift, operator_name, edited_df, operator_notes, time_log_text)

def export_pdf(op_date, shift, operator_name, df, notes, time_log):
    # Setup PDF
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Header Info
    pdf.cell(0, 10, f"Date: {str(op_date)}    Shift: {str(shift)}    Operator: {str(operator_name)}", 0, 1, 'L')
    pdf.ln(5)

    # Table Setup
    pdf.set_font("Arial", 'B', 9)
    col_widths = [15, 40, 35, 40, 40, 40, 55] 
    headers = list(df.columns)

    # Print Table Headers
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), 1, 0, 'C')
    pdf.ln()

    # Print Data Rows
    pdf.set_font("Arial", size=9)
    for index, row in df.iterrows():
        try:
            pdf.cell(col_widths[0], 10, str(row.iloc[0]), 1, 0, 'C') 
            pdf.cell(col_widths[1], 10, str(row.iloc[1]), 1, 0, 'C') 
            pdf.cell(col_widths[2], 10, str(row.iloc[2]), 1, 0, 'C') 
            pdf.cell(col_widths[3], 10, str(row.iloc[3]), 1, 0, 'C') 
            pdf.cell(col_widths[4], 10, str(row.iloc[4]), 1, 0, 'C') 
            pdf.cell(col_widths[5], 10, str(row.iloc[5]), 1, 0, 'C') 
            pdf.cell(col_widths[6], 10, str(row.iloc[6]), 1, 0, 'C') 
            pdf.ln()
        except Exception as e:
            st.error(f"Error printing row {index}: {e}")

    pdf.ln(10)

    # --- NEW: Time Log Section (Only prints if user checked the box) ---
    if time_log:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, "Machine Run Time Schedule:", 0, 1)
        pdf.set_font("Arial", size=10)
        # Multi_cell handles the new lines automatically
        pdf.multi_cell(0, 5, time_log)
        pdf.ln(5)

    # Standard Notes
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "Standard Notes:", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "1. Anionic Polymer and Acqalent usage recorded with units.", 0, 1)
    pdf.cell(0, 5, "2. Flow rate and water treated recorded as per flow meter.", 0, 1)

    # Operator Custom Notes
    if notes:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, "Other Observations:", 0, 1)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, notes)

    pdf.ln(15)

    # Signature
    if pdf.get_y() > 170:
        pdf.add_page()
        
    pdf.cell(100, 10, "Checked by: ____________________", 0, 0)
    pdf.cell(100, 10, "Signature: ____________________", 0, 1)

    # Output
    try:
        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
        
        st.success("PDF Generated Successfully!")
        st.download_button(
            label="Download PDF Sheet",
            data=pdf_output,
            file_name=f"ETP_Sheet_{op_date}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Creation Failed: {e}")

if __name__ == "__main__":
    main()