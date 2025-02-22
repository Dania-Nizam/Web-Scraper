import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set page title and layout
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("📊 Data Sweeper")

# Custom CSS for better UI
st.markdown(
    """
    <style>
    .stApp { background-color: #1E1E1E; color: white; }
    .stFileUploader { 
        border: 2px solid #4CAF50; 
        border-radius: 10px; 
        padding: 10px; 
        background-color: #2E2E2E; 
    }
    .stButton > button, .stDownloadButton > button { 
        border-radius: 8px; 
    }
    h1, h2, h3, h4, h5, h6, label { 
        color: #FFFFFF !important;  /* White color for better visibility */
        font-weight: bold;  /* Make text bold */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# File uploader
uploaded_files = st.file_uploader("📤 Upload your files (CSV or Excel only):", 
                                  type=["csv", "xlsx"], 
                                  accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            # Read file based on extension
            if file_ext == ".csv":
                df = pd.read_csv(file, encoding="utf-8")
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue

            # File details
            st.write(f"**📄 File Name:** {file.name}")
            st.write(f"**📦 File Size:** {file.size / 1024:.2f} KB")

            # Display preview
            st.subheader(f"🔍 Preview of {file.name}")
            st.dataframe(df.head())

            # Data Cleaning Options
            st.subheader("🧹 Data Cleaning Options")
            if st.checkbox(f"Clean Data for {file.name}", key=f"clean_{file.name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"🗑 Remove Duplicates - {file.name}", key=f"dup_{file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.success("✅ Duplicates removed!")

                with col2:
                    if st.button(f"📊 Fill Missing Values - {file.name}", key=f"fillna_{file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing values filled!")

            # Column Selection
            st.subheader("📌 Select Columns to Keep")
            selected_columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns, key=f"columns_{file.name}")
            df = df[selected_columns]

            # Data Visualization
            st.subheader("📊 Data Visualization")
            numeric_columns = df.select_dtypes(include="number").columns.tolist()
            if numeric_columns:
                selected_chart_column = st.selectbox("Select a column for the bar chart", numeric_columns, key=f"chart_col_{file.name}")
                st.bar_chart(df[[selected_chart_column]])
            else:
                st.warning("⚠ No numeric columns available for visualization.")

            # Conversion Options
            st.subheader("🔄 Conversion Options")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")

            if st.button(f"📥 Convert & Download {file.name}", key=f"download_{file.name}"):
                buffer = BytesIO()
                
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name="Sheet1")
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                buffer.seek(0)
                st.download_button(
                    label=f"📩 Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
        
        except Exception as e:
            st.error(f"❌ Error processing {file.name}: {e}")

# Fix the success message issue
if uploaded_files:
    st.success("🎉 All files processed successfully!")