# PlotFunction.py
# Unified Streamlit App: 2D/3D Plotting + Story-Based Math Solver (Bilingual)

import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG + LANGUAGE SYSTEM
# =========================================================
st.set_page_config(page_title="StoryMathPro", layout="wide", initial_sidebar_state="expanded")

# Inisialisasi session state untuk tema dan fitur baru
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Light'
if 'mobile_opt_active' not in st.session_state:
    st.session_state['mobile_opt_active'] = True
if 'additional_opt_active' not in st.session_state:
    st.session_state['additional_opt_active'] = False

# LANGUAGE SYSTEM
lang = st.sidebar.selectbox("🌐 Language / Bahasa", ["Indonesia", "English"])

def tr(idn, en):
    return idn if lang == "Indonesia" else en

# =========================================================
# THEME CONFIGURATION (Dynamic CSS)
# =========================================================

# Tentukan warna berdasarkan tema yang dipilih
if st.session_state['theme'] == 'Light':
    BG_MAIN = 'linear-gradient(135deg, #f6f3ff 0%, #f3fbff 100%)'
    BG_CARD = 'rgba(255,255,255,0.95)'
    COLOR_TEXT = '#0f172a'
    COLOR_HEADER = '#1e3a8a'
    BG_PREMIUM_HEADER = '#e0f2fe'
    BORDER_ACCENT = '#005A9C'
else: # Dark Theme
    BG_MAIN = '#111827'
    BG_CARD = '#1f2937'
    COLOR_TEXT = '#f9fafb'
    COLOR_HEADER = '#93c5fd'
    BG_PREMIUM_HEADER = '#1f2937'
    BORDER_ACCENT = '#3b82f6'


st.markdown(
    f"""
    <style>
    /* Main App Background and Font */
    .stApp {{
        background: {BG_MAIN};
        color: {COLOR_TEXT};
        font-family: "Segoe UI", Roboto, Arial;
    }}
    
    /* Card/Content Box Style (similar to the white box in the image) */
    .card {{
        background: {BG_CARD};
        color: {COLOR_TEXT};
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px rgba(15,23,42,0.1);
        border-left: 5px solid {BORDER_ACCENT};
    }}

    /* Sidebar Styling */
    .stSidebar {{
        background-color: #e5e7eb;
        padding-top: 20px;
    }}
    
    /* Headers Styling */
    h1, h2, h3, .stMarkdown > h1, .stMarkdown > h2, .stMarkdown > h3 {{
        color: {COLOR_HEADER};
    }}
    
    /* Custom Styling for the premium title area */
    .premium-header {{
        background-color: {BG_PREMIUM_HEADER};
        border-radius: 10px;
        padding: 15px 25px;
        margin-bottom: 30px;
        border-bottom: 3px solid {BORDER_ACCENT};
    }}
    
    /* Override input/text area color for dark theme readability */
    {'div[data-testid="stTextInput"] > div > input, div[data-testid="stNumberInput"] > div > input { color: #f9fafb; }' if st.session_state['theme'] == 'Dark' else ''}

    </style>
    """,
    unsafe_allow_html=True,
)

# TEXTS (UPDATED)
T = {
    "title_main": tr("StoryMathPro", "StoryMathPro"),
    "version_tag": tr("Versi Super dengan Fitur Lengkap!", "Super Version with Full Features!"),
    "tab_func": tr("Fungsi & Turunan", "Function & Derivative"),
    "tab_3d": tr("Grafik 3D", "3D Graph"),
    "tab_story": tr("Optimasi (Input F(x))", "Optimization (F(x) Input)"),
    "tab_problem_solver": tr("Asisten Soal Cerita", "Word Problem Assistant"), # NEW
    "solver_title": tr("Solver Optimasi Dinamis Premium", "Premium Dynamic Optimization Solver"),
    "story_example_intro": tr(
        "Pilih jenis masalah optimasi di bawah ini dan **masukkan fungsi satu variabel** yang ingin Anda optimalkan menggunakan turunan. Gunakan 'x' sebagai variabel.",
        "Select the type of optimization problem below and **enter the single-variable function** you wish to optimize using derivatives. Use 'x' as the variable."
    ),
    "input_func": tr("Masukkan fungsi f(x):", "Enter function f(x):"),
    "xmin": "x-min",
    "xmax": "x-max",
    "samples": tr("Jumlah sampel", "Number of samples"),
    "sym_deriv": tr("Turunan Simbolik", "Symbolic Derivative"),
    "category": tr("Pilih Jenis Soal Optimasi", "Select Optimization Problem Type"),
    "summary": tr("📌 Ringkasan", "📌 Summary"),
    "optimization_area": tr("Optimasi Luas & Keliling (Perimeter)", "Area & Perimeter Optimization"),
    "optimization_volume": tr("Optimasi Volume", "Volume Optimization"),
    "optimization_profit": tr("Optimasi Keuntungan (Profit)", "Profit Optimization"),
    "opt_setup": tr("Pengaturan Masalah", "Problem Setup"),
    "opt_solution": tr("Penyelesaian Optimasi Langkah-per-Langkah", "Step-by-Step Optimization Solution"),
    # NEW PROBLEM SOLVER TEXTS
    "problem_input": tr("Soal Cerita / Deskripsi Masalah:", "Word Problem / Problem Description:"),
    "solution_type": tr("Pilih Kategori Penyelesaian", "Select Solution Category"),
    "formula_list": tr("📚 Daftar Rumus Terkait", "📚 List of Related Formulas"),
    "step_by_step": tr("Penyelesaian Rinci Langkah-per-Langkah", "Detailed Step-by-Step Solution"),
    "integral_setup": tr("Masukkan fungsi f(x) dan batas integral [a, b]:", "Enter function f(x) and integration bounds [a, b]:"),
    "integral_a": "Batas Bawah (a)",
    "integral_b": "Batas Atas (b)",
}

# Optimization Problem Choices
OPTS_CHOICES = {
    T["optimization_area"]: "AREA",
    T["optimization_volume"]: "VOLUME",
    T["optimization_profit"]: "PROFIT",
}

# SymPy Symbols
x, r, h, P, K = sp.symbols('x r h P K', real=True, positive=True)

# =========================================================
# CORE FUNCTIONS
# =========================================================

# =========================================================
# NEW CORE FUNCTION: SOLVER RESULT PLOTTING
# =========================================================

def plot_solver_result(f_sym, x_min, x_max, plot_type="function", a=None, b=None):
    x_sym = sp.Symbol('x')
    f_lambdified = sp.lambdify(x_sym, f_sym, "numpy")
    
    # Gunakan rentang yang lebih luas untuk plot optimasi
    if plot_type == "optimization":
        x_range = 10
        # Coba mencari titik kritis untuk menentukan rentang plot yang relevan
        try:
            df_dx = sp.diff(f_sym, x_sym)
            critical_points = sp.solve(df_dx, x_sym)
            if critical_points:
                x_opt_val = float(critical_points[0].evalf())
                x_min, x_max = x_opt_val - x_range, x_opt_val + x_range
        except:
            x_min, x_max = -x_range, x_range
            
    
    xs = np.linspace(x_min, x_max, 400)
    ys = f_lambdified(xs)

    plt.style.use('dark_background' if st.session_state['theme'] == 'Dark' else 'default')
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.plot(xs, ys, label=f'{plot_type}', color=BORDER_ACCENT)
    
    # Logika untuk Integral (arsiran)
    if plot_type == "integral" and a is not None and b is not None:
        x_fill = np.linspace(a, b, 100)
        y_fill = f_lambdified(x_fill)
        ax.fill_between(x_fill, y_fill, color='crimson', alpha=0.3, label=tr('Area Integral', 'Integral Area'))
        ax.set_title(tr(f'Grafik Fungsi dan Area Integral [{a}, {b}]', f'Function Graph and Integral Area [{a}, {b}]'), color=COLOR_TEXT)
        
    # Logika untuk Optimasi (menandai titik kritis)
    elif plot_type == "optimization":
        try:
            df_dx = sp.diff(f_sym, x_sym)
            critical_points = sp.solve(df_dx, x_sym)
            for crit in critical_points:
                if crit.is_real and x_min <= crit <= x_max:
                    x_crit = float(crit.evalf())
                    y_crit = float(f_sym.subs(x_sym, crit).evalf())
                    ax.plot(x_crit, y_crit, 'o', color='gold', markersize=8, 
                            label=tr(f"Titik Kritis ({x_crit:.2f}, {y_crit:.2f})", 
                                    f"Critical Point ({x_crit:.2f}, {y_crit:.2f})"))
        except:
            pass
        ax.set_title(tr('Grafik Fungsi Optimasi', 'Optimization Function Graph'), color=COLOR_TEXT)
        
    else:
        ax.set_title(tr(f'Grafik Fungsi {plot_type}', f'Function Graph {plot_type}'), color=COLOR_TEXT)
        
    ax.axhline(0, color='grey', linestyle='--', alpha=0.5)
    ax.axvline(0, color='grey', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.5)
    ax.legend()
    
    # Custom colors for ticks and borders (Theme support)
    text_color = COLOR_TEXT if st.session_state['theme'] == 'Dark' else '#333333'
    for axis in [ax.xaxis, ax.yaxis]:
        axis.tick_params(colors=text_color)
    
    st.pyplot(fig, use_container_width=True)

# =========================================================

def solve_generic_optimization(func_str):
    x_sym = sp.Symbol('x', real=True, positive=True)
    try:
        f = sp.sympify(func_str)
        df_dx = sp.diff(f, x_sym)
        
        critical_points = sp.solve(df_dx, x_sym)
        positive_crits = [p for p in critical_points if p.is_real and p > 0]
        
        if not positive_crits:
            return f, df_dx, None, None, tr("Tidak ditemukan titik kritis positif atau real.", "No positive or real critical points found.")

        results = {}
        for crit in positive_crits:
            results[crit] = f.subs(x_sym, crit)
            
        x_opt = max(results, key=results.get)
        f_max = results[x_opt]
            
        return f, df_dx, x_opt, f_max, None
    
    except Exception as e:
        return None, None, None, None, f"Error SymPy: {e}"

def plot_optimization(f_sym, x_opt, f_max, label='Fungsi Optimasi'):
    x_sym = sp.Symbol('x')
    f_lambdified = sp.lambdify(x_sym, f_sym, "numpy")
    
    if x_opt is None:
        x_start, x_end = 0.1, 10
    else:
        x_val = float(x_opt.evalf())
        x_range_min = max(0.1, x_val - 5 * x_val / 4)
        x_range_max = x_val + 5 * x_val / 4

        x_start = x_range_min
        x_end = x_range_max
        
    xs = np.linspace(x_start, x_end, 500)
    
    try:
        ys = f_lambdified(xs)
    except Exception:
        xs = np.linspace(0.1, x_val * 2 if x_val else 10, 500)
        ys = f_lambdified(xs)


    plt.style.use('dark_background' if st.session_state['theme'] == 'Dark' else 'default')
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.plot(xs, ys, label=label, color=BORDER_ACCENT)
    
    if x_opt is not None:
        x_opt_float = float(x_opt.evalf())
        f_max_float = float(f_max.evalf())
        ax.plot(x_opt_float, f_max_float, 'o', color='crimson', markersize=8, 
                label=tr(f"Maksimum: ({x_opt_float:.2f}, {f_max_float:.2f})", 
                         f"Maximum: ({x_opt_float:.2f}, {f_max_float:.2f})"))
        
        ax.axvline(x_opt_float, color='grey', linestyle='--', alpha=0.5)
        ax.axhline(f_max_float, color='grey', linestyle='--', alpha=0.5)


    ax.set_title(tr(f'Grafik {label}', f'{label} Graph'), color=COLOR_TEXT)
    ax.set_xlabel('x', color=COLOR_TEXT)
    ax.set_ylabel(label.split(' ')[-1], color=COLOR_TEXT)
    ax.grid(True, alpha=0.5)
    ax.legend()
    
    for axis in [ax.xaxis, ax.yaxis]:
        axis.tick_params(colors=COLOR_TEXT)
    ax.spines['left'].set_color(COLOR_TEXT)
    ax.spines['bottom'].set_color(COLOR_TEXT)
        
    if st.session_state['mobile_opt_active']:
        st.pyplot(fig, use_container_width=True) 
    else:
        st.pyplot(fig)

# =========================================================
# NEW FUNCTIONS FOR WORD PROBLEM SOLVER
# =========================================================

def get_related_formulas(category_key):
    formulas = {
        "FUNGSI_DASAR": [r"f'(x) = \frac{d}{dx} f(x)"],
        "LUAS_BIDANG": [r"A = l \times w", r"P = 2(l + w)"],
        "VOLUME": [r"V = l \times w \times h"],
        "OPTIMASI": [r"f'(x) = 0"],
        "INTEGRAL": [r"\int_a^b f(x) \, dx"],
    }
    return formulas.get(category_key, [])

def solve_word_problem(category_key, input_data):
    steps = []
    summary_text = ""
    success = False
    x_sym = sp.Symbol('x')
    
    if category_key == "FUNGSI_DASAR":
        f_str = input_data
        try:
            f = sp.sympify(f_str)
            df = sp.diff(f, x_sym)
            steps.append(tr("**1. Fungsi yang diberikan:**", "**1. Given function:**"))
            steps.append(f"$f(x) = {sp.latex(f)}$")
            steps.append(tr("**2. Turunan pertama:**", "**2. First derivative:**"))
            steps.append(f"$f'(x) = {sp.latex(df)}$")
            summary_text = tr(f"Turunan dari f(x) adalah {sp.latex(df)}", f"The derivative of f(x) is {sp.latex(df)}")
            success = True
        except Exception as e:
            summary_text = f"Error: {e}"
    
    elif category_key == "LUAS_BIDANG":
        dims = input_data.split(',')
        if len(dims) == 2:
            try:
                l, w = map(float, dims)
                area = l * w
                peri = 2 * (l + w)
                steps.append(tr("**1. Dimensi yang diberikan:**", "**1. Given dimensions:**"))
                steps.append(tr(f"Panjang = {l}, Lebar = {w}", f"Length = {l}, Width = {w}"))
                steps.append(tr("**2. Luas:**", "**2. Area:**"))
                steps.append(f"$A = {l} \\times {w} = {area}$")
                steps.append(tr("**3. Keliling:**", "**3. Perimeter:**"))
                steps.append(f"$P = 2({l} + {w}) = {peri}$")
                summary_text = tr(f"Luas = {area}, Keliling = {peri}", f"Area = {area}, Perimeter = {peri}")
                success = True
            except ValueError:
                summary_text = tr("Input tidak valid. Masukkan dua angka dipisah koma.", "Invalid input. Enter two numbers separated by comma.")
        else:
            summary_text = tr("Input tidak valid. Masukkan dua dimensi dipisah koma.", "Invalid input. Enter two dimensions separated by comma.")
    
    elif category_key == "VOLUME":
        dims = input_data.split(',')
        if len(dims) == 3:
            try:
                l, w, h = map(float, dims)
                vol = l * w * h
                steps.append(tr("**1. Dimensi yang diberikan:**", "**1. Given dimensions:**"))
                steps.append(tr(f"Panjang = {l}, Lebar = {w}, Tinggi = {h}", f"Length = {l}, Width = {w}, Height = {h}"))
                steps.append(tr("**2. Volume:**", "**2. Volume:**"))
                steps.append(f"$V = {l} \\times {w} \\times {h} = {vol}$")
                summary_text = tr(f"Volume = {vol}", f"Volume = {vol}")
                success = True
            except ValueError:
                summary_text = tr("Input tidak valid. Masukkan tiga angka dipisah koma.", "Invalid input. Enter three numbers separated by comma.")
        else:
            summary_text = tr("Input tidak valid. Masukkan tiga dimensi dipisah koma.", "Invalid input. Enter three dimensions separated by comma.")
    
    elif category_key == "OPTIMASI":
        f_str = input_data
        try:
            f, df_dx, x_opt, f_max, error = solve_generic_optimization(f_str)
            if error:
                summary_text = error
            else:
                steps.append(tr("**1. Fungsi yang dioptimalkan:**", "**1. Function to optimize:**"))
                steps.append(f"$f(x) = {sp.latex(f)}$")
                steps.append(tr("**2. Turunan pertama:**", "**2. First derivative:**"))
                steps.append(f"$
