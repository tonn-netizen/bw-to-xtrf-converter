import streamlit as st
import csv

# --- UI Setup ---
st.set_page_config(page_title="BW>XTRF Conv 0.3 by tnk", page_icon="🔄")
st.title("🔄 Bureau Works > XTRF Converter")
st.write("Lae üles mitmekeelne BW logifail. Jagan selle iga sihtkeele jaoks eraldi XTRF-ühilduvateks failideks.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Bureau Works CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the raw string data
        string_data = uploaded_file.getvalue().decode("utf-8")
        lines = string_data.splitlines()
        
        # Auto-detect delimiter based on the first line
        delimiter = ';' if ';' in lines[0] else ','
        
        # Parse the CSV manually for maximum resilience against bad headers
        reader = csv.reader(lines, delimiter=delimiter)
        rows = list(reader)
        
        # Find the actual header row dynamically
        header_idx = -1
        for i, row in enumerate(rows):
            if len(row) > 0 and row[0].strip() == 'File':
                header_idx = i
                break
                
        if header_idx == -1:
            st.error("Could not find a valid header row starting with 'File'.")
            st.stop()
            
        # Prepare output headers
        row1 = ["", "", "", "Context Match", "", "", "", "Repetitions", "", "", "", "100%", "", "", "", "95% - 99%", "", "", "", "85% - 94%", "", "", "", "75% - 84%", "", "", "", "50% - 74%", "", "", "", "No Match", "", "", "", "Total"]
        row2 = ["File", "Tagging Errors", "Chars/Word"]
        for _ in range(8):
            row2.extend(["Segments", "Words", "Placeables", "Percent"])
        row2.extend(["Segments", "Words", "Placeables", "Characters"])
        
        header_string = ";".join(row1) + "\n" + ";".join(row2) + "\n"
        
        # Dictionary to store rows separated by Target Language
        language_files = {}
        
        # Process every row under the header
        for row in rows[header_idx + 1:]:
            if len(row) < 33: # Skip broken/empty rows
                continue
            
            filename = row[0].strip()
            # Skip empty rows and summary rows
            if not filename or "Summary [" in filename:
                continue
                
            src = row[1].strip()
            tgt = row[2].strip()
            
            # Format language codes from et_ee to et-ee
            src_clean = src.replace('_', '-')
            tgt_clean = tgt.replace('_', '-')
            
            # Safe float conversion
            def to_float(val):
                try: return float(val)
                except: return 0.0
                
            tot_s, tot_w, tot_c = to_float(row[3]), to_float(row[4]), to_float(row[5])
            nt_s, nt_w = to_float(row[6]), to_float(row[7])
            rep_s, rep_w = to_float(row[9]), to_float(row[10])
            nm_s, nm_w = to_float(row[12]), to_float(row[13])
            p50_s, p50_w = to_float(row[15]), to_float(row[16])
            p75_s, p75_w = to_float(row[18]), to_float(row[19])
            p85_s, p85_w = to_float(row[21]), to_float(row[22])
            p95_s, p95_w = to_float(row[24]), to_float(row[25])
            p100_s, p100_w = to_float(row[27]), to_float(row[28])
            cm_s, cm_w = to_float(row[30]), to_float(row[31])
            
            # Combine non-translatables and 0-49%
            nm_s += nt_s
            nm_w += nt_w
            
            chars_per_word = round(tot_c / tot_w, 2) if tot_w > 0 else 0
            def pct(w): return round((w / tot_w) * 100, 2) if tot_w > 0 else 0
            def fmt(val): return f"{val:g}" # Cleans up numbers
            
            # Explicitly force quotes around the filename just like Memsource
            file_lang_str = f'"{filename} | {src_clean}>{tgt_clean}"'
            
            out_row = [
                file_lang_str, 0, fmt(chars_per_word),
                int(cm_s), int(cm_w), 0, fmt(pct(cm_w)),
                int(rep_s), int(rep_w), 0, fmt(pct(rep_w)),
                int(p100_s), int(p100_w), 0, fmt(pct(p100_w)),
                int(p95_s), int(p95_w), 0, fmt(pct(p95_w)),
                int(p85_s), int(p85_w), 0, fmt(pct(p85_w)),
                int(p75_s), int(p75_w), 0, fmt(pct(p75_w)),
                int(p50_s), int(p50_w), 0, fmt(pct(p50_w)),
                int(nm_s), int(nm_w), 0, fmt(pct(nm_w)),
                int(tot_s), int(tot_w), 0, int(tot_c)
            ]
            
            # Add the formatted row to the correct target language group
            if tgt_clean not in language_files:
                language_files[tgt_clean] = []
                
            language_files[tgt_clean].append(";".join(str(x) for x in out_row))

        # --- UI Output ---
        st.success(f"✅ File successfully split into {len(language_files)} languages!")
        st.markdown("### Download Individual Language Files")
        
        # Create a download button for each target language found
        for lang, rows in language_files.items():
            final_csv_string = header_string + "\n".join(rows) + "\n"
            
            st.download_button(
                label=f"⬇️ Download {lang.upper()}",
                data=final_csv_string.encode("utf-8-sig"),
                file_name=f"XTRF_Analysis_{lang}.csv", # Includes the language code!
                mime="text/csv",
                key=lang # Streamlit needs unique keys for dynamically generated buttons
            )
        
    except Exception as e:
        st.error(f"An error occurred: {e}. Please ensure it is a valid Bureau Works logfile.")
