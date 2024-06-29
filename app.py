from flask import Flask, render_template, request
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cosine

app = Flask(__name__, static_url_path='/static', static_folder='static')

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

@app.route('/', methods=['GET', 'POST'])
def index():
    components = ['Processor', 'Motherboard', 'RAM', 'SSD', 'VGA', 'PSU', 'Casing']
    recommendations = None

    if request.method == 'POST':
        budget = float(request.form['budget'])
        allocations = {comp: float(request.form[comp]) / 100 for comp in components}
        kebutuhan = request.form.get('kebutuhan')

        # Sesuaikan alokasi berdasarkan kebutuhan (contoh)
        if kebutuhan == 'Gaming':
            allocations['VGA'] += 0.15  # Tambah alokasi VGA untuk gaming (15%)
            allocations['Processor'] += 0.10  # Tambah alokasi CPU untuk gaming (10%)
            allocations['RAM'] += 0.05  # Tambah sedikit alokasi RAM untuk gaming (5%)

        elif kebutuhan == 'Rendering/Editing Video':
            allocations['Processor'] += 0.15  # Tambah alokasi CPU untuk rendering (15%)
            allocations['RAM'] += 0.20  # Tambah alokasi RAM untuk rendering (20%)
            allocations['SSD'] += 0.05  # Tambah sedikit alokasi SSD untuk penyimpanan file (5%)

        elif kebutuhan == 'Desain Grafis':
            allocations['VGA'] += 0.15  # Tambah alokasi VGA untuk desain grafis (15%)
            allocations['Processor'] += 0.05  # Tambah sedikit alokasi CPU untuk desain grafis (5%)
            allocations['Monitor'] = 0.10  # Alokasikan budget untuk monitor (10%)

        elif kebutuhan == 'Programming/Coding':
            allocations['Processor'] += 0.10  # Tambah alokasi CPU untuk programming (10%)
            allocations['SSD'] += 0.05  # Tambah sedikit alokasi SSD untuk kecepatan (5%)
            allocations['Monitor'] = 0.05  # Alokasikan sedikit budget untuk monitor (5%)

        elif kebutuhan == 'Streaming':
            allocations['Processor'] += 0.10  # Tambah alokasi CPU untuk streaming (10%)
            allocations['VGA'] += 0.10  # Tambah alokasi VGA untuk streaming (10%)
            allocations['RAM'] += 0.05  # Tambah sedikit alokasi RAM untuk streaming (5%)

        elif kebutuhan == 'Office Work':
            allocations['Processor'] -= 0.05  # Kurangi alokasi CPU untuk office (5%)
            allocations['VGA'] -= 0.05  # Kurangi alokasi VGA untuk office (5%)
            allocations['SSD'] += 0.10  # Tambah alokasi SSD untuk office (10%)

        # Normalisasi alokasi agar totalnya tetap 100%
        total_allocation = sum(allocations.values())
        allocations = {comp: allocation / total_allocation for comp, allocation in allocations.items()}

        # ... (hitung rekomendasi) ...
        
        data = read_excel()
        data = normalize_data(data)
        recommendations = recommend_components(budget, allocations, data)

    return render_template('index.html', components=components, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
