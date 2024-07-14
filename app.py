import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cosine

# Fungsi untuk membaca file Excel
def read_excel():
    data = pd.read_excel('sparepart dataset.xlsx')
    return data

# Normalisasi harga untuk setiap komponen
def normalize_data(data):
    scaler = MinMaxScaler()
    data['Normalized_Price'] = scaler.fit_transform(data[['Price']])
    return data

# Rekomendasi komponen berdasarkan cosine similarity
def recommend_components(budget, allocations, data):
    components = ['Processor', 'Motherboard', 'RAM', 'SSD', 'VGA', 'PSU', 'Casing']
    component_data = {comp: data[data['Tipe'] == comp] for comp in components}
    
    recommended_components = {}
    for comp, percentage in allocations.items():
        allocated_budget = budget * percentage
        suitable_parts = component_data[comp][component_data[comp]['Price'] <= allocated_budget]
        
        if suitable_parts.empty:
            continue
        
        distances = suitable_parts['Normalized_Price'].apply(lambda x: cosine([x], [allocated_budget / budget]))
        best_part_index = distances.idxmin()
        best_part = suitable_parts.loc[best_part_index]
        
        recommended_components[comp] = best_part
    return recommended_components

st.title('PC Recommendation')

components = ['Processor', 'Motherboard', 'RAM', 'SSD', 'VGA', 'PSU', 'Casing']
recommendations = None

with st.form(key='pc_form'):
    budget = st.number_input('Total Budget:', min_value=0, step=100, format="%d")
    allocations = {}
    total_allocation = 0

    for component in components:
        allocation = st.number_input(f'{component} Allocation (%):', min_value=0, max_value=100, step=1, format="%d")
        allocations[component] = allocation / 100
        total_allocation += allocation

    sisa_alokasi = 100 - total_allocation
    st.markdown(f'**Sisa Alokasi (%): {sisa_alokasi}**')

    kebutuhan = st.radio('Kebutuhan Utama:', ['Gaming', 'Rendering/Editing Video', 'Desain Grafis', 'Programming/Coding', 'Streaming', 'Office Work'])
    submit_button = st.form_submit_button(label='Get Recommendations')

if submit_button:
    if kebutuhan == 'Gaming':
        allocations['VGA'] += 0.15
        allocations['Processor'] += 0.10
        allocations['RAM'] += 0.05

    elif kebutuhan == 'Rendering/Editing Video':
        allocations['Processor'] += 0.15
        allocations['RAM'] += 0.20
        allocations['SSD'] += 0.05

    elif kebutuhan == 'Desain Grafis':
        allocations['VGA'] += 0.15
        allocations['Processor'] += 0.05
        allocations['Monitor'] = 0.10

    elif kebutuhan == 'Programming/Coding':
        allocations['Processor'] += 0.10
        allocations['SSD'] += 0.05
        allocations['Monitor'] = 0.05

    elif kebutuhan == 'Streaming':
        allocations['Processor'] += 0.10
        allocations['VGA'] += 0.10
        allocations['RAM'] += 0.05

    elif kebutuhan == 'Office Work':
        allocations['Processor'] -= 0.05
        allocations['VGA'] -= 0.05
        allocations['SSD'] += 0.10

    total_allocation = sum(allocations.values())
    allocations = {comp: allocation / total_allocation for comp, allocation in allocations.items()}

    data = read_excel()
    data = normalize_data(data)
    recommendations = recommend_components(budget, allocations, data)

    st.subheader('Recommended Components')
    if recommendations:
        # Membuat DataFrame dari rekomendasi
        recommended_df = pd.DataFrame([
            {
                'Type': comp,
                'Brand': part['Brand'],
                'Specifications': part['Specifications'],
                'Price': part['Price']
            } for comp, part in recommendations.items()
        ])
        
        # Menampilkan DataFrame dalam bentuk tabel
        st.table(recommended_df)
    else:
        st.write("No suitable components found within the given budget and allocations.")
