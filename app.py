
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load Data
df_sankey = pd.read_csv("df_sankey.csv")
df_2015_scaled = pd.read_csv("df_2015_scaled.csv")
df_2019_scaled = pd.read_csv("df_2019_scaled.csv")

# Streamlit Dashboard
st.set_page_config(layout="wide")
st.title("🌍 Global Happiness Clustering Dashboard")
st.subheader("Explore Socio-Economic Clusters from the World Happiness Report (2015 & 2019)")
st.write("Version 1")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Cluster-wise World Map", "Radar Chart – Cluster Profile", 
    "Cluster Evaluation Sankey Diagram", 
    "Box Plot Score By Cluster", "Bar Plot – Mean Score by Cluster"
])

with tab1:
    st.markdown("### Choropleth Map of Country Clusters")
    year = st.radio("Select Year", [2015, 2019], horizontal=True)
    col = f"Cluster_{year}"
    fig = px.choropleth(
        df_sankey,
        locations="ISO_Code",
        color=col,
        hover_name="Country",
        color_continuous_scale=px.colors.qualitative.Set2,
        title=f"Cluster-wise Country Distribution - {year}"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Radar Charts – Cluster Profiles")
    year = st.radio("Select Year for Radar Chart", [2015, 2019], key="radar_year", horizontal=True)
    df = df_2015_scaled.copy() if year == 2015 else df_2019_scaled.copy()
    features = [
        'Score', 'GDP per capita', 'Social support',
        'Healthy life expectancy', 'Freedom to make life choices',
        'Generosity', 'Perceptions of corruption'
    ]
    fig = go.Figure()
    for cluster, group in df.groupby('Cluster'):
        avg = [group[feat].mean() for feat in features]
        fig.add_trace(go.Scatterpolar(
            r=avg + [avg[0]],
            theta=features + [features[0]],
            fill='toself',
            name=f'{year}_Cluster_{cluster}'
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title=f'Radar Chart – Cluster Profiles ({year})'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Sankey Diagram – Cluster Transitions from 2015 to 2019")
    from collections import defaultdict
    import plotly.graph_objects as go

    sankey_data = df_sankey.groupby(['Cluster_2015', 'Cluster_2019']).size().reset_index(name='count')
    all_labels = sorted(set(sankey_data['Cluster_2015']).union(sankey_data['Cluster_2019']))
    label_dict = {v: i for i, v in enumerate(all_labels)}

    sankey_fig = go.Figure(data=[go.Sankey(
        node=dict(label=[f'2015_{i}' for i in sorted(sankey_data["Cluster_2015"].unique())] +
                         [f'2019_{i}' for i in sorted(sankey_data["Cluster_2019"].unique())],
                  pad=15, thickness=20),
        link=dict(
            source=sankey_data['Cluster_2015'].map(lambda x: label_dict[x]),
            target=sankey_data['Cluster_2019'].map(lambda x: label_dict[x] + len(sankey_data["Cluster_2015"].unique())),
            value=sankey_data['count']
        )
    )])
    sankey_fig.update_layout(title_text="Cluster Membership Transition: 2015 to 2019", font_size=12)
    st.plotly_chart(sankey_fig, use_container_width=True)

with tab4:
    st.markdown("### Boxplot of Happiness Scores by Cluster")
    fig_box_2015 = px.box(
        df_sankey, x='Cluster_2015', y='Score_2015',
        title="Score Distribution by Cluster (2015)",
        labels={'Cluster_2015': 'Cluster', 'Score_2015': 'Score'}
    )
    fig_box_2019 = px.box(
        df_sankey, x='Cluster_2019', y='Score_2019',
        title="Score Distribution by Cluster (2019)",
        labels={'Cluster_2019': 'Cluster', 'Score_2019': 'Score'}
    )
    st.plotly_chart(fig_box_2015, use_container_width=True)
    st.plotly_chart(fig_box_2019, use_container_width=True)

with tab5:
    st.markdown("### Mean Score Comparison by Cluster")
    mean_2015 = df_sankey.groupby('Cluster_2015')['Score_2015'].mean().reset_index()
    mean_2019 = df_sankey.groupby('Cluster_2019')['Score_2019'].mean().reset_index()

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=mean_2015['Cluster_2015'], y=mean_2015['Score_2015'], name='2015'))
    fig_bar.add_trace(go.Bar(x=mean_2019['Cluster_2019'], y=mean_2019['Score_2019'], name='2019'))
    fig_bar.update_layout(
        title='Mean Happiness Score by Cluster (2015 vs 2019)',
        xaxis_title='Cluster',
        yaxis_title='Average Score',
        barmode='group'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown(
    """
    <hr style="margin-top: 50px;">
    <div style='text-align: center; font-size: 14px;'>
        🔍 K-Means Clustering Code available on 
        <a href='https://github.com/fouzul-hassan/happiness-score-analysis-2015-and-2019' target='_blank'>
            GitHub
        </a>
        <br>
        Made by Fouzul Hassan
    </div>
    """,
    unsafe_allow_html=True
)