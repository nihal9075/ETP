import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- PDF Generation Class ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        # [cite_start]Title based on source [cite: 1]
        self.cell(0, 10, 'ETP Daily Operation Sheet', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- Main App Logic ---
def main():
    st.title("💧 ETP Operation Log App")
    st.write("You can now enter units like '18 g', '5 kg', or '10 L'.")

    # [cite_start]1. Inputs [cite: 1]
    col1, col2, col3 = st.columns(3)
    with col1:
        op_date = st.date_input("Date", datetime.today())
    with col2:
        shift = st.text_input("Shift", placeholder="Morning")
    with col3:
        operator_name = st.text_input("Operator Name")

    st.divider()

    st.subheader("Operation Data")
    
    # [cite_start]2. Data Table Setup [cite: 2]
    # We use strings ("") for chemicals so you can type "18 g" or "5 kg"
    default_data = pd.DataFrame(
        [{"Sl No.": 1, 
          "Run Hours": 0.0, 
          "Flow Rate (m3/hr)": 0.0, 
          "Anionic Polymer": "0 g",   # Text input allowed
          "Acqalent": "0 ml",         # Text input allowed
          "Water Treated (m3)": 0.0, 
          "Remarks": ""}],
    )

    # Configure columns to allow text for chemicals
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

    # [cite_start]Print Info Header [cite: 1]
    pdf.cell(0, 10, f"Date: {str(op_date)}    Shift: {str(shift)}    Operator: {str(operator_name)}", 0, 1, 'L')
    pdf.ln(5)

    # Table Setup
    pdf.set_font("Arial", 'B', 9)
    # Adjusted widths to fit text inputs
    col_widths = [15, 30, 35, 45, 45, 40, 55] 
    headers = list(df.columns)

    # 1. Print Table Headers
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), 1, 0, 'C')
    pdf.ln()

    # 2. Print Data Rows
    pdf.set_font("Arial", size=9)
    
    for index, row in df.iterrows():
        try:
            pdf.cell(col_widths[0], 10, str(row.iloc[0]), 1, 0, 'C') # Sl No
            pdf.cell(col_widths[1], 10, str(row.iloc[1]), 1, 0, 'C') # Run Hours
            pdf.cell(col_widths[2], 10, str(row.iloc[2]), 1, 0, 'C') # Flow Rate
            
            # These are now text, so they print exactly what you typed (e.g. "18 g")
            pdf.cell(col_widths[3], 10, str(row.iloc[3]), 1, 0, 'C') # Anionic
            pdf.cell(col_widths[4], 10, str(row.iloc[4]), 1, 0, 'C') # Acqalent
            
            pdf.cell(col_widths[5], 10, str(row.iloc[5]), 1, 0, 'C') # Water Treated
            pdf.cell(col_widths[6], 10, str(row.iloc[6]), 1, 0, 'C') # Remarks
            pdf.ln()
        except Exception as e:
            st.error(f"Error printing row {index}: {e}")

    pdf.ln(10)

    # [cite_start]Notes [cite: 3, 4]
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Notes:", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, "1. Anionic Polymer and Acqalent usage recorded with units.", 0, 1)
    pdf.cell(0, 6, "2. Flow rate and water treated recorded as per flow meter.", 0, 1)

    pdf.ln(15)

    # [cite_start]Signature [cite: 5]
    pdf.cell(100, 10, "Checked by: ____________________", 0, 0)
    pdf.cell(100, 10, "Signature: ____________________", 0, 1)

    # Create safe output
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