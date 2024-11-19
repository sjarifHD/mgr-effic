import streamlit as st
import plotly.express as px
import pandas as pd

# Load the dataset
st.title("Manager Matrix Scores")
st.subheader("Performance Metrics Scoring")

# Read the pre-existing CSV file
file_path = "jira_data.csv"  # Adjust the path if needed
try:
    # Load and display the dataset
    manager_productivity_raw = pd.read_csv(file_path)

    # Display raw dataset
    st.write("Raw Dataset:")
    st.dataframe(manager_productivity_raw)

    # Select only numeric columns for aggregation
    numeric_columns = manager_productivity_raw.select_dtypes(include=['number']).columns
    manager_productivity = manager_productivity_raw.groupby("Manager")[numeric_columns].mean().reset_index()

    # Display grouped dataset
    st.write("Grouped Dataset by Manager:")
    st.dataframe(manager_productivity)

    # Define the scoring function
    def calculate_score(value, values_list, reverse=False):
        sorted_values = sorted(values_list, reverse=reverse)
        return sorted_values.index(value) + 1

    # Map the correct column names for scoring
    updated_columns_to_score = {
        'Avg Mandays/Task (Lower is Better)': False,  # Lower is better
        'Avg Task/Mandays (Higher is Better)': True,   # Higher is better
        'Avg Mandays for Eachday': False,  # Lower is better
        'Avg Task Eachday (Higher is Better)': True,  # Higher is better
        'Avg Task/Day within Mandays (Higher is Better)': True  # Higher is better
    }

    # Ensure all required columns exist in the dataset
    missing_columns = [col for col in updated_columns_to_score.keys() if col not in manager_productivity.columns]
    if missing_columns:
        st.error(f"Missing columns in the dataset: {missing_columns}")
        st.stop()

    # Apply scoring logic for each column
    for col, reverse in updated_columns_to_score.items():
        manager_productivity[f'{col} Score'] = manager_productivity[col].apply(
            lambda x: calculate_score(x, manager_productivity[col].tolist(), reverse=reverse)
        )

    # Summarize the scores for each manager
    manager_matrix_scores_final_corrected = manager_productivity[
        ['Manager'] + [f'{col} Score' for col in updated_columns_to_score]
    ]

    # Display the final results in Streamlit
    st.write(
        "This table displays the scores for managers based on productivity and efficiency across multiple metrics. "
        "Lower scores indicate better performance."
    )
    st.dataframe(manager_matrix_scores_final_corrected)

    # Radar Chart Visualization
    st.subheader("Radar Chart of Manager Scores")
    radar_df = pd.melt(manager_matrix_scores_final_corrected, id_vars='Manager', 
                   var_name='Metric', value_name='Score')
    fig = px.line_polar(radar_df, r='Score', theta='Metric', color='Manager', line_close=True)
    fig.update_traces(fill='toself')
    st.plotly_chart(fig)

except FileNotFoundError:
    st.error(f"File '{file_path}' not found. Please ensure the file exists in the specified location.")
