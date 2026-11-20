import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection

# Create App title
st.set_page_config(page_title="Zodiac Maritime Dashboard",layout="wide")
# Create App title
#st.title("Zodiac Maritime — Vessel KPI & Anomaly Triage")
st.markdown(
    """
    <h1 style='text-align: center;'>
        Zodiac Maritime — Vessel KPI & Anomaly Triage
    </h1>
    """,
    unsafe_allow_html=True
)
# Left Side Pane
st.sidebar.header("Data & Audit Controls")
user_id = st.sidebar.text_input("Analyst / User ID",value="ops_analyst@zodiacmaritime.com")

# Read CSV File
df = pd.read_csv("2_vessel_kpi_reports.csv")
#st.write(df.head())
df["To_Timestamp"] = pd.to_datetime(df["To_Timestamp"],errors="coerce")
#st.write(df["To_Timestamp"].dtype)
#st.write(df["Voyage_Type"].unique())
if st.sidebar.button("Reset SQLite DB from CSV"):
    conn = get_connection()
    df.to_sql("reports",conn,if_exists="replace",index=False)
    conn.close()
    st.sidebar.success("Database Reset Complete")

st.sidebar.markdown("---")
st.sidebar.subheader("Planted Data Quality Checks")
duplicate_rows = df[df.duplicated(subset=["Report_ID"],keep=False)]

st.sidebar.write(f"• Duplicate Report_ID rows: {len(duplicate_rows)}")

missing_power_rows = df[(df["KPI"] == "Power") & (df["Power_%"].isna())]
st.sidebar.write(f"• Power rows with null Power_%: {len(missing_power_rows)}")

negative_speed_rows = df[(df["KPI"] == "Speed") & (df["Speed_%"] < 0)]
st.sidebar.write(f"• Speed rows with negative Speed_%: {len(negative_speed_rows)}")

with st.sidebar.expander("Inspect flagged data-quality rows"):
        st.write("duplicate_report_id")
        st.dataframe(duplicate_rows[["Report_ID","Vessel_Name","KPI","Power_%","Speed_%"]])
        st.write("missing_power_pct")
        st.dataframe(missing_power_rows[["Report_ID","Vessel_Name","KPI","Power_%","Speed_%"]])
        st.write("negative_speed_pct")
        st.dataframe(negative_speed_rows[["Report_ID","Vessel_Name","KPI","Power_%","Speed_%"]])

# Create Vessel Filter
st.subheader("1. Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    vessel = st.selectbox("Vessel",["All"] + list(df["Vessel_Name"].unique()))

with col2:
    voyage = st.selectbox("Voyage Type",["All"] + list(df["Voyage_Type"].unique()))

with col3:
    kpi = st.selectbox("KPI",["Both", "Power", "Speed"])

with col4:
    start_date = df["To_Timestamp"].min().date()
    end_date = df["To_Timestamp"].max().date()
    date_range = st.date_input("Date Range",(start_date, end_date))

filtered_df = df.copy()

if vessel != "All":
    filtered_df = filtered_df[filtered_df["Vessel_Name"] == vessel]

if voyage != "All":
    filtered_df = filtered_df[filtered_df["Voyage_Type"] == voyage]

if kpi != "Both":
    filtered_df = filtered_df[filtered_df["KPI"] == kpi]

if len(date_range) == 2:
    start, end = date_range
    filtered_df = filtered_df[(filtered_df["To_Timestamp"] >= pd.Timestamp(start))&(filtered_df["To_Timestamp"] <= pd.Timestamp(end))]

# Add Power chart
power_df = filtered_df[filtered_df["KPI"] == "Power"]

fig = px.scatter(
                    power_df,
                    x = "To_Timestamp",
                    y = "Power_%",
                    color = "Power_Filter_Flag",
                    title = "Power % Trend",
                    color_discrete_map = {
                                            "No": "#1f77b4",      # Blue
                                            "Yes": "#FFBF00"      # Amber
                                         }
                )
fig.update_layout(height=350,yaxis=dict(range=[80, 210]))
fig.update_traces(marker=dict(size=6))
fig.update_xaxes(tickformat="%b %Y")
#st.plotly_chart(fig, use_container_width=True)

# Add Speed chart
speed_df = filtered_df[filtered_df["KPI"] == "Speed"]

fig2 = px.scatter(
                    speed_df,
                    x = "To_Timestamp",
                    y = "Speed_%",
                    color = "Speed_Filter",
                    title = "Speed % Trend",
                    color_discrete_map = {
                                            "No": "#1f77b4",      # Blue
                                            "Yes": "#FFBF00"      # Amber
                                        }
                 )
fig2.update_layout(height=350,yaxis=dict(range=[20, 100]))
fig2.update_traces(marker=dict(size=6))
fig2.update_xaxes(tickformat="%b %Y")
#st.plotly_chart(fig2, use_container_width=True)

power_selection = None
speed_selection = None
st.subheader("2. KPI Scatter Charts (Box / Lasso / Click to Select)")

# Show both charts
if kpi == "Both":
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        power_selection = st.plotly_chart(fig,use_container_width=True,key="power_chart",on_select="rerun",
                                          config={"displaylogo": False,"modeBarButtonsToRemove": [],"responsive": True})
        #st.write(power_selection)
    with chart_col2:
        speed_selection = st.plotly_chart(fig2,use_container_width=True,key="speed_chart",on_select="rerun",
                                          config={"displaylogo": False,"modeBarButtonsToRemove": [],"responsive": True})

# Show only Power chart
elif kpi == "Power":
    st.plotly_chart(fig,use_container_width=True,key="power_chart_full")

# Show only Speed chart
elif kpi == "Speed":
    st.plotly_chart(fig2,use_container_width=True,key="speed_chart_full")
# # Add Data Quality Checks
# ''' The exercise specifically asks you to notice:
#     1.duplicate Report_ID
#     2.missing Power %
#     3.negative Speed % '''

# st.subheader("Data Quality Checks")

# duplicate_count = df.duplicated(subset=["Report_ID"]).sum()

# missing_power = ((df["KPI"] == "Power") &(df["Power_%"].isna())).sum()

# negative_speed = (df["Speed_%"] < 0).sum()

# col1,col2,col3 = st.columns(3)

# col1.metric("Duplicate Report IDs",duplicate_count)
# col2.metric("Missing Power %",missing_power)
# col3.metric("Negative Speed %",negative_speed)
st.subheader("3. Report Detail Table & Inline Correction")

selected_rows = filtered_df.copy()

# Power chart selection
if (power_selection and "selection" in power_selection and len(power_selection["selection"]["points"]) > 0):
    selected_indices = power_selection["selection"]["point_indices"]
    selected_rows = power_df.iloc[selected_indices]
    #st.write("Power Rows Selected:", len(selected_rows))
    #selected_timestamps = [point["x"] for point in power_selection["selection"]["points"]]
    #selected_dates = pd.to_datetime(selected_timestamps,errors="coerce")
    #selected_rows = filtered_df[filtered_df["To_Timestamp"].dt.floor("D").isin(selected_dates.floor("D"))]
    # # DEBUG
    # st.write("Selected:", selected_timestamps[:3])
    # st.write("Dataframe:",filtered_df["To_Timestamp"].astype(str).head(3).tolist())
    #selected_rows = filtered_df[filtered_df["To_Timestamp"].astype(str).isin(selected_timestamps)]

# Speed chart selection
elif (speed_selection and "selection" in speed_selection and len(speed_selection["selection"]["points"]) > 0):
    selected_indices = speed_selection["selection"]["point_indices"]
    selected_rows = speed_df.iloc[selected_indices]
    #st.write("Speed Rows Selected:", len(selected_rows))
    #selected_timestamps = [point["x"] for point in speed_selection["selection"]["points"]]
    #selected_dates = pd.to_datetime(selected_timestamps,errors="coerce")
    #selected_rows = filtered_df[filtered_df["To_Timestamp"].dt.floor("D").isin(selected_dates.floor("D"))]
    # # DEBUG
    # st.write("Selected:", selected_timestamps[:3])
    # st.write("Dataframe:",filtered_df["To_Timestamp"].astype(str).head(3).tolist())
    #selected_rows = filtered_df[filtered_df["To_Timestamp"].astype(str).isin(selected_timestamps)]

# Show status AFTER selection logic
if len(selected_rows) != len(filtered_df):
    st.success(f"{len(selected_rows)} rows selected from chart.")
else:
    st.info(f"No chart points selected. Showing all {len(filtered_df)} filtered rows.")

with st.expander("Deviation Conditional Formatting View (Negative Deviations Highlighted Red)"):
    def highlight_negative(val):
        try:
            if pd.notna(val) and float(val) < 0:
                return "background-color: #ffcccc; color: red;"
        except:
            pass
        return ""
    st.dataframe(selected_rows.style.map(highlight_negative,subset=["Power_Deviation","Speed_Deviation"]),use_container_width=True)

st.subheader("Inline Editable Reports")

original_df = selected_rows.copy()

edited_df = st.data_editor(selected_rows,use_container_width=True,key="vessel_editor")

# Save Button
if st.button("Submit Changes"):
    validation_errors = []
    audit_records = []

    # Validate ONLY edited cells
    for idx in edited_df.index:
        for col in edited_df.columns:
            old_value = original_df.loc[idx, col]
            new_value = edited_df.loc[idx, col]
            if str(old_value) != str(new_value):
                # Validate edited values only
                if col == "Power_%" and pd.notna(new_value):
                    if not (0 <= float(new_value) <= 300):
                        validation_errors.append(f"Report ID {edited_df.loc[idx,'Report_ID']} - Power_% must be between 0 and 300")

                elif col == "Power_Deviation" and pd.notna(new_value):
                    if not (0 <= float(new_value) <= 200):
                        validation_errors.append(f"Report ID {edited_df.loc[idx,'Report_ID']} - Power_Deviation must be between -200 and 200")

                elif col == "Speed_%" and pd.notna(new_value):
                    if not (0 <= float(new_value) <= 200):
                        validation_errors.append(f"Report ID {edited_df.loc[idx,'Report_ID']} - Speed_% must be between 0 and 200")

                elif col == "Speed_Deviation" and pd.notna(new_value):
                    if not (0 <= float(new_value) <= 200):
                        validation_errors.append(f"Report ID {edited_df.loc[idx,'Report_ID']} - Speed_Deviation must be between -200 and 200")

                audit_records.append({
                                        "Report_ID": edited_df.loc[idx, "Report_ID"],
                                        "Field": col,
                                        "Old_Value": old_value,
                                        "New_Value": new_value
                                     })

    # Stop if validation fails
    if validation_errors:
        st.error("Validation Failed")
        for error in validation_errors:
            st.write(error)
    else:
        conn = get_connection()
        # Audit Table
        conn.execute("""
                            CREATE TABLE IF NOT EXISTS audit_log
                            (
                                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                report_id TEXT,
                                field TEXT,
                                old_value TEXT,
                                new_value TEXT,
                                user TEXT,
                                timestamp TEXT
                            )
                    """)

        # Insert audit records
        for record in audit_records:

            conn.execute("""
                            INSERT INTO audit_log
                            (
                                report_id,
                                field,
                                old_value,
                                new_value,
                                user,
                                timestamp
                            )
                            VALUES
                            (
                                ?, ?, ?, ?, ?, datetime('now')
                            )
                        """,
                            (
                                str(record["Report_ID"]),
                                str(record["Field"]),
                                str(record["Old_Value"]),
                                str(record["New_Value"]),
                                user_id
                            ))

        # Save latest report data
        edited_df.to_sql("reports",conn,if_exists="replace",index=False)
        conn.commit()
        st.success("Changes saved successfully!")
        # Updated records
        if len(audit_records) > 0:
            audit_df = pd.DataFrame(audit_records)
            st.subheader("Updated Records")
            st.dataframe(audit_df,use_container_width=True)
        else:
            st.info("No changes detected.")
        # Audit Log
        audit_history = pd.read_sql("""
                                        SELECT audit_id,
                                               report_id,
                                               field,
                                               old_value,
                                               new_value,
                                               user,
                                               timestamp
                                          FROM audit_log
                                          ORDER BY audit_id DESC
                                    """,conn)

        st.markdown("## Audit Log (`audit_log`)")
        st.dataframe(audit_history,use_container_width=True,hide_index=True)
        conn.close()
        
