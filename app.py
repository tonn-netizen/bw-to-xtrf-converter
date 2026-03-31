import streamlit as st
import pandas as pd
import csv
from io import StringIO

# --- UI Setup ---
st.set_page_config(page_title="BW > XTRF Converter by tnk", page_icon="🔄")
st.title("🔄 Bureau Works > XTRF Converter by tnk")
st.write("Lae üles Bureau Works Logfile (CSV) konvertimaks see XTRFi jaoks söödavasse formaati.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Lae üles Bureau Works CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the file. sep=None allows pandas to auto-detect commas vs semicolons!
        bw_df = pd.read_csv(uploaded_file, sep=None, engine='python', header=1)
        
        # --- Conversion Logic ---
        row1 = ["", "", "", "Context Match", "", "", "", "Repetitions", "", "", "", "100%", "", "", "", "95% - 99%", "", "", "", "85% - 94%", "", "", "", "75% - 84%", "", "", "", "50% - 74%", "", "", "", "No Match", "", "", "", "Total"]
        row2 = ["File", "Tagging Errors", "Chars/Word"]
        for _ in range(8):
            row2.extend(["Segments", "Words", "Placeables", "Percent"])
        row2.extend(["Segments", "Words", "Placeables", "Characters"])
        
        output_rows = []
        for _, row in bw_df.iterrows():
            filename = str(row.iloc[0])
            if "Summary [" in filename:
                continue
                
            src, tgt = str(row.iloc[1]), str(row.iloc[2])
            tot_s, tot_w, tot_c = float(row.iloc[3]), float(row.iloc[4]), float(row.iloc[5])
            
            nt_s, nt_w = float(row.iloc[6]), float(row.iloc[7])
            rep_s, rep_w = float(row.iloc[9]), float(row.iloc[10])
            nm_s, nm_w = float(row.iloc[12]), float(row.iloc[13])
            p50_s, p50_w = float(row.iloc[15]), float(row.iloc[16])
            p75_s, p75_w = float(row.iloc[18]), float(row.iloc[19])
            p85_s, p85_w = float(row.iloc[21]), float(row.iloc[22])
            p95_s, p95_w = float(row.iloc[24]), float(row.iloc[25])
            p100_s, p100_w = float(row.iloc[27]), float(row.iloc[28])
            cm_s, cm_w = float(row.iloc[30]), float(row.iloc[31])
            
            nm_s += nt_s
            nm_w += nt_w
            
            chars_per_word = round(tot_c / tot_w, 2) if tot_w > 0 else 0
            def pct(w): return round((w / tot_w) * 100, 2) if tot_w > 0 else 0

            out_row = [
                f"{filename} | {src}>{tgt}", 0, chars_per_word,
                int(cm_s), int(cm_w), 0, pct(cm_w),
                int(rep_s), int(rep_w), 0, pct(rep_w),
                int(p100_s), int(p100_w), 0, pct(p100_w),
                int(p95_s), int(p95_w), 0, pct(p95_w),
                int(p85_s), int(p85_w), 0, pct(p85_w),
                int(p75_s), int(p75_w), 0, pct(p75_w),
                int(p50_s), int(p50_w), 0, pct(p50_w),
                int(nm_s), int(nm_w), 0, pct(nm_w),
                int(tot_s), int(tot_w), 0, int(tot_c)
            ]
            output_rows.append(out_row)

        # --- Generate Output CSV in Memory ---
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(row1)
        writer.writerow(row2)
        for r in output_rows:
            writer.writerow(r)
            
        st.success("✅ File converted successfully!")
        
        # --- Download Button ---
        st.download_button(
            label="⬇️ Download Converted XTRF File",
            data=output.getvalue().encode("utf-8-sig"), # utf-8-sig ensures Excel/XTRF reads special characters correctly
            file_name="Converted_XTRF_Analysis.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}. Please ensure it is a valid Bureau Works logfile.")