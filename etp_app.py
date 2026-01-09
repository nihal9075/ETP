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

    # 1. Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        op_date = st.date_input("Date", datetime.today())
    with col2:
        shift = st.text_input("Shift", placeholder="Morning")
    with col3:
        operator_name = st.text_input("Operator Name")

    st.divider()

    st.subheader("Operation Data")
    
    # 2. Data Table (Renamed columns to remove special symbols)
    # Using 'm3' instead of the symbol ensures it prints correctly.
    default_data = pd.DataFrame(
        [{"Sl No.": 1, 
          "Machine Running Hours ": 0.0, 
          "Flow Rate (m3/hr)": 0.0, 
          "Anionic Poly (kg)": 0.0, 
          "Acqalent (kg/L)": 0.0, 
          "Water Treated (m3)": 0.0, 
          "Remarks": ""}],
    )

    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    if st.button("Generate PDF Report"):
        if not operator_name:
            st.warning("Please enter an Operator Name.")
        else:
            export_pdf(op_date, shift, operator_name, edited_df)

def export_pdf(op_date, shift, operator_name, df):
    # Setup PDF
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Print Info Header
    # Force all text to string to prevent errors
    pdf.cell(0, 10, f"Date: {str(op_date)}    Shift: {str(shift)}    Operator: {str(operator_name)}", 0, 1, 'L')
    pdf.ln(5)

    # Table Setup
    pdf.set_font("Arial", 'B', 9)
    col_widths = [15, 30, 40, 40, 40, 40, 60] 
    headers = list(df.columns)

    # 1. Print Table Headers
    for i, header in enumerate(headers):
        # We assume the user creates ASCII headers or uses the defaults
        pdf.cell(col_widths[i], 10, str(header), 1, 0, 'C')
    pdf.ln()

    # 2. Print Data Rows
    pdf.set_font("Arial", size=9)
    
    # Using iloc to get data by position (safer than by name)
    for index, row in df.iterrows():
        try:
            # We loop through columns by index 0 to 6
            pdf.cell(col_widths[0], 10, str(row.iloc[0]), 1, 0, 'C') # Sl No
            pdf.cell(col_widths[1], 10, str(row.iloc[1]), 1, 0, 'C') # Run Hours
            pdf.cell(col_widths[2], 10, str(row.iloc[2]), 1, 0, 'C') # Flow Rate
            pdf.cell(col_widths[3], 10, str(row.iloc[3]), 1, 0, 'C') # Anionic
            pdf.cell(col_widths[4], 10, str(row.iloc[4]), 1, 0, 'C') # Acqalent
            pdf.cell(col_widths[5], 10, str(row.iloc[5]), 1, 0, 'C') # Water Treated
            pdf.cell(col_widths[6], 10, str(row.iloc[6]), 1, 0, 'C') # Remarks
            pdf.ln()
        except Exception as e:
            st.error(f"Error printing row {index}: {e}")

    pdf.ln(10)

    # Notes
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Notes:", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, "1. Only Anionic Polymer and Acqalent are recorded.", 0, 1)
    pdf.cell(0, 6, "2. Flow rate and water treated recorded as per flow meter.", 0, 1)

    pdf.ln(15)

    # Signature
    pdf.cell(100, 10, "Checked by: ____________________", 0, 0)
    pdf.cell(100, 10, "Signature: ____________________", 0, 1)

    # Create safe output
    # 'latin-1' encoding handles standard English text and numbers well
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
        st.error(f"PDF Creation Failed: {e}. Please ensure you are not using Bengali characters.")

if __name__ == "__main__":
    main()