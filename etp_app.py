import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- PDF Generation Class ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        # Title from source 
        self.cell(0, 10, 'ETP Daily Operation Sheet', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- Main App Logic ---
def main():
    st.title("💧 ETP Operation Log App")
    st.write("Fill in the data below and download your PDF.")

    # 1. Inputs for the Header 
    col1, col2, col3 = st.columns(3)
    with col1:
        op_date = st.date_input("Date", datetime.today())
    with col2:
        shift = st.text_input("Shift", placeholder="e.g., Morning")
    with col3:
        operator_name = st.text_input("Operator Name")

    st.divider()

    # 2. Data Entry Table
    # Based on columns provided in 
    st.subheader("Operation Data")
    
    # Initialize an empty dataframe with the specific columns
    default_data = pd.DataFrame(
        [{"Sl No.": 1, "Machine Running Hours (hr)": 0.0, "Flow Rate (m³/hr)": 0.0, 
          "Anionic Polymer Used (kg)": 0.0, "Acqalent Used (kg/L)": 0.0, 
          "Total Water Treated (m³)": 0.0, "Remarks": ""}],
    )

    # Allow user to add/edit rows
    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    # 3. Generate PDF Button
    if st.button("Generate PDF Report"):
        if not operator_name:
            st.warning("Please enter an Operator Name.")
        else:
            export_pdf(op_date, shift, operator_name, edited_df)

def export_pdf(op_date, shift, operator_name, df):
    pdf = PDF(orientation='L', unit='mm', format='A4') # Landscape for wide tables
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Add Header Info 
    pdf.cell(0, 10, f"Date: {op_date}    Shift: {shift}    Operator Name: {operator_name}", 0, 1, 'L')
    pdf.ln(5)

    # Table Header Settings
    pdf.set_font("Arial", 'B', 9)
    # Column widths based on content 
    # Sl No, Hrs, Flow, Anionic, Acqalent, Total Water, Remarks
    col_widths = [15, 45, 35, 40, 40, 40, 50] 
    headers = df.columns.tolist()

    # Draw Header Row
    for i, header in enumerate(headers):
        # clean up header text for pdf fit
        text = header.replace("(hr)", "").replace("(m³/hr)", "").replace("(kg)", "").replace("(kg/L)", "").replace("(m³)", "")
        pdf.cell(col_widths[i], 10, text, 1, 0, 'C')
    pdf.ln()

    # Draw Data Rows
    pdf.set_font("Arial", size=9)
    for index, row in df.iterrows():
        pdf.cell(col_widths[0], 10, str(row['Sl No.']), 1, 0, 'C')
        pdf.cell(col_widths[1], 10, str(row['Machine Running Hours (hr)']), 1, 0, 'C')
        pdf.cell(col_widths[2], 10, str(row['Flow Rate (m³/hr)']), 1, 0, 'C')
        pdf.cell(col_widths[3], 10, str(row['Anionic Polymer Used (kg)']), 1, 0, 'C')
        pdf.cell(col_widths[4], 10, str(row['Acqalent Used (kg/L)']), 1, 0, 'C')
        pdf.cell(col_widths[5], 10, str(row['Total Water Treated (m³)']), 1, 0, 'C')
        pdf.cell(col_widths[6], 10, str(row['Remarks']), 1, 0, 'C')
        pdf.ln()

    pdf.ln(10)

    # Notes Section 
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Notes:", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, "1. Only Anionic Polymer and its Acqalent are recorded in this sheet.", 0, 1)
    pdf.cell(0, 6, "2. Flow rate and water treated should be recorded as per flow meter reading.", 0, 1)

    pdf.ln(15)

    # Signature Section 
    pdf.cell(100, 10, "Checked by: ____________________", 0, 0)
    pdf.cell(100, 10, "Signature: ____________________", 0, 1)

    # Output
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    st.success("PDF Generated Successfully!")
    st.download_button(
        label="Download PDF Sheet",
        data=pdf_output,
        file_name=f"ETP_Sheet_{op_date}.pdf",
        mime="application/pdf"
    )

if __name__ == "__main__":
    main()