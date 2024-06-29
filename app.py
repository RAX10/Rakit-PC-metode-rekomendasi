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
        
        data = read_excel()
        data = normalize_data(data)
        recommendations = recommend_components(budget, allocations, data)

    return render_template('index.html', components=components, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
