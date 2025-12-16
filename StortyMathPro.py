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
    "area_setup": tr("Masukkan dimensi (misal: panjang (p) dan lebar (l), pisahkan dengan koma):", "Enter dimensions (e.g.: length (l) and width (w), separate by comma):"),
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
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.markdown("## ⚙️ KONFIGURASI PREMIUM")

# --- FITUR CONTENT THEME ---
selected_theme = st.sidebar.radio(
    tr("Content Theme", "Content Theme"), 
    ["Light", "Dark"], 
    index=0 if st.session_state['theme'] == 'Light' else 1
)

if selected_theme != st.session_state['theme']:
    st.session_state['theme'] = selected_theme
    st.rerun() 
# --- AKHIR FITUR CONTENT THEME ---

## fi
# NEW TAB INCLUSION
selected_tab_title = st.sidebar.radio("Pilih Modul", [T["tab_func"], T["tab_3d"], T["tab_story"], T["tab_problem_solver"]], index=3)


# =========================================================
# MAIN HEADER
# =========================================================
with st.container():
    st.markdown('<div class="premium-header">', unsafe_allow_html=True)
    st.markdown(f'<h1 style="text-align: center; color: {COLOR_HEADER};">{T["title_main"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: {BORDER_ACCENT}; font-size: 1.1em;">{T["version_tag"]}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# CONTENT TABS 
# =========================================================

# Tab 1: Function & Derivative (2D) 
if selected_tab_title == T["tab_func"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(T["tab_func"])
    
    func_input = st.text_input(T["input_func"], "sin(x)")
    col1, col2, col3 = st.columns(3)
    with col1:
        x_min = st.number_input(T["xmin"], value=-10.0)
    with col2:
        x_max = st.number_input(T["xmax"], value=10.0)
    with col3:
        n = st.number_input(T["samples"], value=400)

    x_sym = sp.Symbol('x')
    try:
        f = sp.sympify(func_input)
        df = sp.diff(f, x_sym)

        st.subheader(T["sym_deriv"])
        st.latex(sp.latex(df))

        xs = np.linspace(x_min, x_max, int(n))
        f_l = sp.lambdify(x_sym, f, "numpy")
        df_l = sp.lambdify(x_sym, df, "numpy")

        ys = f_l(xs)
        dys = df_l(xs)

        plt.style.use('dark_background' if st.session_state['theme'] == 'Dark' else 'default')
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        
        ax[0].plot(xs, ys, color=BORDER_ACCENT)
        ax[0].set_title("f(x)", color=COLOR_TEXT)
        ax[0].grid(True, alpha=0.5)

        ax[1].plot(xs, dys, color="crimson")
        ax[1].set_title("f'(x)", color=COLOR_TEXT)
        ax[1].grid(True, alpha=0.5)
        
        for axis in ax:
            axis.tick_params(colors=COLOR_TEXT)
            axis.spines['left'].set_color(COLOR_TEXT)
            axis.spines['bottom'].set_color(COLOR_TEXT)
            axis.xaxis.label.set_color(COLOR_TEXT)
            axis.yaxis.label.set_color(COLOR_TEXT)
            
        if st.session_state['mobile_opt_active']:
            st.pyplot(fig, use_container_width=True) 
        else:
            st.pyplot(fig) 

    except Exception as e:
        st.error(tr(f"Kesalahan: {e}", f"Error: {e}"))

    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: 3D Surface Plot 
elif selected_tab_title == T["tab_3d"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(T["tab_3d"])
    
    z_input = st.text_input(
        tr("Masukkan z = f(x, y)", "Enter z = f(x, y)"),
        "sin(sqrt(x**2+y**2))/sqrt(x**2+y**2)"
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        xmin = st.number_input("x-min", -6.0)
    with col2:
        xmax = st.number_input("x-max", 6.0)
    with col3:
        ymin = st.number_input("y-min", -6.0)
    with col4:
        ymax = st.number_input("y-max", 6.0)

    samples = st.slider(T["samples"], 20, 100, 50)

    x, y = sp.symbols('x y')
    try:
        z = sp.sympify(z_input)
        z_l = sp.lambdify((x, y), z, "numpy")

        X = np.linspace(xmin, xmax, samples)
        Y = np.linspace(ymin, ymax, samples)
        Xg, Yg = np.meshgrid(X, Y)
        Zg = z_l(Xg, Yg)

        template = 'plotly_dark' if st.session_state['theme'] == 'Dark' else 'plotly_white'
        
        fig = go.Figure(data=[go.Surface(x=Xg, y=Yg, z=Zg)])
        fig.update_layout(height=600, template=template)

        if st.session_state['mobile_opt_active']:
            st.plotly_chart(fig, use_container_width=True, key='3d_plot_active')
        else:
            st.plotly_chart(fig, width=700, key='3d_plot_fixed') 

    except Exception as e:
        st.error(tr(f"Kesalahan: {e}", f"Error: {e}"))
    st.markdown('</div>', unsafe_allow_html=True)


# Tab 3: Story-Based Solver (Optimasi F(x) Input)
elif selected_tab_title == T["tab_story"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(T["solver_title"])
    st.write(T["story_example_intro"])

    st.markdown("---")
    
    # --- Pilihan Jenis Soal Optimasi ---
    problem_type = st.radio(
        T["category"],
        list(OPTS_CHOICES.keys()),
        key="opt_category_radio"
    )
    
    selected_key = OPTS_CHOICES[problem_type]
    
    st.markdown(f'<h3>{problem_type}</h3>', unsafe_allow_html=True)
    
    # --- AREA Optimization Solver (Generalized Input) ---
    if selected_key == "AREA":
        st.markdown(tr(
            "Soal Contoh: Maksimalkan luas $A(x)$ dengan fungsi batasan yang telah disubstitusikan (misal: $A(x) = 60x - 2x^2$ dari masalah pagar). **Gunakan 'x' sebagai variabel.**", 
            "Example Problem: Maximize area $A(x)$ with the substituted constraint function (e.g.: $A(x) = 60x - 2x^2$ from the fence problem). **Use 'x' as the variable.**"
        ))
        
        A_func_str = st.text_input(
            tr("Masukkan Fungsi Luas A(x) yang Dioptimalkan:", "Enter the Optimized Area Function A(x):"), 
            value="60*x - 2*x**2", key="A_input"
        )
        
        if st.button(tr("ANALISIS AREA PREMIUM", "ANALYZE AREA PREMIUM"), use_container_width=True, key="solve_area_button"):
            A, dA_dx, x_opt, A_max, error = solve_generic_optimization(A_func_str)

            st.markdown("---")
            st.markdown(f'<h3>{T["opt_solution"]}</h3>', unsafe_allow_html=True)
            
            if error:
                st.error(error)
            elif x_opt is not None:
                st.markdown('**1. Tentukan Fungsi Objektif (Fungsi yang Dioptimalkan):**')
                st.latex(f"A(x) = {sp.latex(A)}")

                st.markdown('**2. Cari Turunan Pertama $A\'(x)$ dan Samakan dengan Nol:**')
                st.latex(f"A'(x) = {sp.latex(dA_dx)} = 0")

                st.markdown('**3. Selesaikan untuk Titik Kritis (Nilai x Optimal):**')
                st.latex(f"x = {sp.latex(x_opt)}")
                
                st.markdown("---")
                st.subheader(tr("Visualisasi Optimasi", "Optimization Visualization"))
                plot_optimization(A, x_opt, A_max, label=tr('Fungsi Luas A(x)', 'Area Function A(x)'))

                st.info(
                    tr(
                        f"Luas maksimum $A_{{max}}$ adalah **{A_max}**.",
                        f"The maximum area $A_{{max}}$ is **{A_max}**."
                    )
                )
            else:
                st.warning(tr("Tidak ditemukan solusi optimal. Pastikan fungsi menggunakan variabel 'x' dan memiliki solusi positif.", "No optimal solution found. Ensure the function uses variable 'x' and has a positive solution."))


    # --- VOLUME Optimization Solver (Generalized Input) ---
    elif selected_key == "VOLUME":
        st.markdown(tr(
            "Soal Contoh: Maksimalkan Volume $V(x)$ dengan fungsi batasan yang telah disubstitusikan (misal: $V(x) = (96x - x^3) / 4$ dari masalah kotak). **Gunakan 'x' sebagai variabel.**", 
            "Example Problem: Maximize Volume $V(x)$ with the substituted constraint function (e.g.: $V(x) = (96x - x^3) / 4$ from the box problem). **Use 'x' as the variable.**"
        ))
        
        V_func_str = st.text_input(
            tr("Masukkan Fungsi Volume V(x) yang Dioptimalkan:", "Enter the Optimized Volume Function V(x):"), 
            value="(96*x - x**3) / 4", key="V_input"
        )
        
        if st.button(tr("ANALISIS VOLUME PREMIUM", "ANALYZE VOLUME PREMIUM"), use_container_width=True, key="solve_volume_button"):
            V, dV_dx, x_opt, V_max, error = solve_generic_optimization(V_func_str)

            st.markdown("---")
            st.markdown(f'<h3>{T["opt_solution"]}</h3>', unsafe_allow_html=True)
            
            if error:
                st.error(error)
            elif x_opt is not None:
                st.markdown('**1. Tentukan Fungsi Objektif (Fungsi yang Dioptimalkan):**')
                st.latex(f"V(x) = {sp.latex(V)}")

                st.markdown('**2. Cari Turunan Pertama $V\'(x)$ dan Samakan dengan Nol:**')
                st.latex(f"V'(x) = {sp.latex(dV_dx)} = 0")
                
                st.markdown('**3. Selesaikan untuk Titik Kritis (Nilai x Optimal):**')
                st.latex(f"x = {sp.latex(x_opt)}")

                st.markdown("---")
                st.subheader(tr("Visualisasi Optimasi", "Optimization Visualization"))
                plot_optimization(V, x_opt, V_max, label=tr('Fungsi Volume V(x)', 'Volume Function V(x)'))
                
                st.info(
                    tr(
                        f"Volume maksimum $V_{{max}}$ adalah **{V_max}**.",
                        f"The maximum volume $V_{{max}}$ is **{V_max}**."
                    )
                )
            else:
                st.warning(tr("Tidak ditemukan solusi optimal. Pastikan fungsi menggunakan variabel 'x' dan memiliki solusi positif.", "No optimal solution found. Ensure the function uses variable 'x' and has a positive solution."))


    # --- PROFIT Optimization Solver (Cost/Price Input) ---
    elif selected_key == "PROFIT":
        st.markdown(tr(
            "Soal Contoh: Maksimalkan Keuntungan $P(x)$ dari penjualan $x$ unit. Masukkan fungsi Biaya Total $C(x)$ dan Harga Jual per unit $p(x)$ (di mana $P(x) = x \cdot p(x) - C(x)$). **Gunakan 'x' sebagai variabel.**", 
            "Example Problem: Maximize Profit $P(x)$ from selling $x$ units. Enter the Total Cost function $C(x)$ and Selling Price per unit $p(x)$ (where $P(x) = x \cdot p(x) - C(x)$). **Use 'x' as the variable.**"
        ))
        
        x_sym = sp.Symbol('x', real=True, positive=True)
        C_default = "1000 + 10 * x**2"
        p_default = "500 - 5 * x"

        st.markdown(f'**{T["opt_setup"]}**')
        col_c, col_p = st.columns(2)
        with col_c:
             C_func_str = st.text_input(tr("Fungsi Biaya Total C(x):", "Total Cost Function C(x):"), 
                                        value=C_default, key="C_input")
        with col_p:
             p_func_str = st.text_input(tr("Fungsi Harga Jual per unit p(x):", "Selling Price Function p(x):"), 
                                        value=p_default, key="p_input")

        if st.button(tr("ANALISIS PROFIT PREMIUM", "ANALYZE PROFIT PREMIUM"), use_container_width=True, key="solve_profit_button"):
            try:
                C_sym = sp.sympify(C_func_str)
                p_sym = sp.sympify(p_func_str)
                R_sym = x_sym * p_sym 
                Profit_sym = R_sym - C_sym

                Profit, dProfit_dx, x_opt, Profit_max, error = solve_generic_optimization(str(Profit_sym))

                st.markdown("---")
                st.markdown(f'<h3>{T["opt_solution"]}</h3>', unsafe_allow_html=True)
                
                if error:
                    st.error(error)
                elif x_opt is not None:
                    st.markdown('**1. Tentukan Fungsi Objektif (Keuntungan):**')
                    st.latex(f"P(x) = {sp.latex(Profit_sym)}")
        
                    st.markdown('**2. Cari Turunan Pertama $P\'(x)$ dan Samakan dengan Nol:**')
                    st.latex(f"P'(x) = {sp.latex(dProfit_dx)} = 0")
                    
                    st.markdown('**3. Selesaikan untuk Titik Kritis (Kuantitas Optimal):**')
                    st.latex(f"x = {sp.latex(x_opt)}")

                    st.markdown("---")
                    st.subheader(tr("Visualisasi Optimasi", "Optimization Visualization"))
                    plot_optimization(Profit, x_opt, Profit_max, label=tr('Fungsi Keuntungan P(x)', 'Profit Function P(x)'))
                        
                    st.info(
                        tr(
                            f"Keuntungan maksimum $P_{{max}}$ adalah **{Profit_max}** pada kuantitas **{x_opt}** unit.",
                            f"The maximum profit $P_{{max}}$ is **{Profit_max}** at a quantity of **{x_opt}** units."
                        )
                    )
                else:
                    st.warning(tr("Tidak ditemukan kuantitas optimal positif. Periksa fungsi input.", "No positive optimal quantity found. Check input functions."))

            except Exception as e:
                st.error(tr(f"Kesalahan dalam memproses fungsi: {e}", f"Error processing function: {e}"))

    st.markdown('</div>', unsafe_allow_html=True)

# Tab 4: Word Problem Assistant (NEW)
elif selected_tab_title == T["tab_problem_solver"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(T["tab_problem_solver"])
    
    # --- Input Masalah dan Kategori ---
    problem_text = st.text_area(T["problem_input"], 
                                tr("Sebuah wadah berbentuk balok memiliki panjang 10, lebar 5, dan tinggi 3. Hitunglah volumenya.", 
                                   "A box shaped as a cuboid has a length of 10, width of 5, and height of 3. Calculate its volume."))
    
    category_options = {
        "FUNGSI & TURUNAN": "FUNGSI_DASAR",
        "LUAS PERMUKAAN & KELILING": "LUAS_BIDANG",
        "VOLUME BANGUN RUANG": "VOLUME",
        "OPTIMASI (Nilai Maks/Min)": "OPTIMASI",
        "INTEGRAL (Luas/Volume Rotasi)": "INTEGRAL",
    }
    
    selected_category_name = st.selectbox(T["solution_type"], list(category_options.keys()))
    selected_category_key = category_options[selected_category_name]
    
    st.markdown("---")
    
    # --- Input Spesifik Sesuai Kategori ---
    input_data = None
    input_valid = False
    
    st.subheader(tr("📝 Input Data Kunci", "📝 Key Data Input"))
    
    if selected_category_key == "INTEGRAL":
        col_f, col_a, col_b = st.columns([2, 1, 1])
        with col_f:
            f_str = st.text_input(T["input_func"], "x**2", key="integral_func_input")
        with col_a:
            a = st.number_input(T["integral_a"], value=0, key="integral_a_input")
        with col_b:
            b = st.number_input(T["integral_b"], value=2, key="integral_b_input")
        input_data = (f_str, a, b)
        input_valid = True
        
    elif selected_category_key == "LUAS_BIDANG":
        input_data = st.text_input(T["area_setup"], "10, 5", key="area_input")
        input_valid = True
        
    elif selected_category_key == "VOLUME":
        input_data = st.text_input(tr("Masukkan dimensi (panjang, lebar, tinggi), pisahkan dengan koma:", "Enter dimensions (length, width, height), separate by comma:"), "10, 5, 3", key="volume_input")
        input_valid = True

    elif selected_category_key == "FUNGSI_DASAR":
        input_data = st.text_input(tr("Masukkan Fungsi f(x) (untuk dicari turunan/propertinya):", "Enter Function f(x) (to find derivative/properties):"), "3*x**2 + 5*x - 7", key="func_basic_input")
        input_valid = True
        
    elif selected_category_key == "OPTIMASI":
        input_data = st.text_input(tr("Masukkan Fungsi f(x) yang dioptimasi (misal: 60*x - 2*x**2):", "Enter the function f(x) to be optimized (e.g.: 60*x - 2*x**2):"), "60*x - 2*x**2", key="opt_solver_input")
        input_valid = True


    if st.button(tr("SOLVE SOAL CERITA PREMIUM", "SOLVE PREMIUM WORD PROBLEM"), use_container_width=True, key="solve_word_problem_button"):
        if input_valid:
            # Panggil Solver
            steps, summary_text, success = solve_word_problem(selected_category_key, input_data)
            
            st.markdown("---")
            
            # --- Tampilkan Rumus Terkait ---
            st.subheader(T["formula_list"])
            formulas = get_related_formulas(selected_category_key)
            if formulas:
                st.markdown(tr("**Beberapa Rumus yang Relevan dengan Kategori ini:**", "**Some Formulas Relevant to this Category:**"))
                for formula in formulas:
                    st.latex(formula)
            else:
                st.info(tr("Tidak ada rumus spesifik yang terdaftar untuk kategori ini.", "No specific formulas listed for this category."))

            st.markdown("---")
            
            # --- Tampilkan Langkah Penyelesaian ---
            st.subheader(T["step_by_step"])
            for step in steps:
                st.markdown(step)
                
            st.markdown("---")
            
            # --- Ringkasan Akhir ---
            st.subheader(T["summary"])
            if success:
                st.success(summary_text)
            else:
                st.error(summary_text)

        else:
            st.warning(tr("Mohon masukkan data input kunci yang valid untuk kategori yang dipilih.", "Please enter valid key input data for the selected category."))

    st.markdown('</div>', unsafe_allow_html=True)
# --- Akhir Tab 4 ---