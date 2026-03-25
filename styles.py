import streamlit as st

LUCIDE_CDN = "https://unpkg.com/lucide-static@latest/icons"

# Lucide icon SVG paths (inline for speed)
ICONS = {
    "package": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16.5 9.4 7.55 4.24"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" x2="12" y1="22" y2="12"/></svg>',
    "building": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>',
    "truck": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>',
    "package-check": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 2 2 4-4"/><path d="M21 10V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l2-1.14"/><path d="m7.5 4.27 9 5.15"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" x2="12" y1="22" y2="12"/></svg>',
    "warehouse": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 8.35V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.35A2 2 0 0 1 3.26 6.5l8-3.2a2 2 0 0 1 1.48 0l8 3.2A2 2 0 0 1 22 8.35Z"/><path d="M6 18h12"/><path d="M6 14h12"/><rect width="12" height="12" x="6" y="10"/></svg>',
    "history": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>',
    "bar-chart": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    "layout-dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "upload": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    "plus-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>',
    "trash": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>',
    "save": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/></svg>',
    "file-text": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    "send": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/><path d="m21.854 2.147-10.94 10.939"/></svg>',
    "inbox": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>',
    "scale": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>',
    "alert-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>',
    "check-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
    "filter": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg>',
    "edit": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/></svg>',
    "recycle": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.203a1.83 1.83 0 0 0 1.556-.89 1.784 1.784 0 0 0 0-1.775l-1.226-2.12"/><path d="m14 16-3 3 3 3"/><path d="M8.293 13.596 7.196 9.5 3.1 10.598"/><path d="m9.344 5.811 1.093-1.892A1.83 1.83 0 0 1 11.985 3a1.784 1.784 0 0 1 1.546.888l3.943 6.843"/><path d="m13.378 9.633 4.096 1.098 1.097-4.096"/></svg>',
}


def icon(name, size=20, color=None):
    """Return Lucide icon SVG string."""
    svg = ICONS.get(name, "")
    if size != 20:
        svg = svg.replace('width="20"', f'width="{size}"').replace('height="20"', f'height="{size}"')
    if color:
        svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    return svg


def inject_css():
    """Inject custom CSS for a clean, modern look."""
    st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetric"] label {
        font-weight: 500 !important;
        color: #64748b !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.025em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #1e293b !important;
        font-size: 1.8rem !important;
    }

    /* Page title */
    .page-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
        padding-bottom: 16px;
        border-bottom: 2px solid #e2e8f0;
    }
    .page-header svg {
        color: #3b82f6;
    }
    .page-header h1 {
        margin: 0 !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    .page-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: -8px;
        margin-bottom: 24px;
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    .stat-card .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
    }
    .stat-card .stat-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 4px;
        letter-spacing: 0.025em;
    }
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1;
    }

    .stat-blue .stat-icon { background: #dbeafe; color: #2563eb; }
    .stat-green .stat-icon { background: #dcfce7; color: #16a34a; }
    .stat-orange .stat-icon { background: #fed7aa; color: #ea580c; }
    .stat-purple .stat-icon { background: #e9d5ff; color: #9333ea; }
    .stat-red .stat-icon { background: #fecaca; color: #dc2626; }

    /* Info banner */
    .info-banner {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #93c5fd;
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        color: #1e40af;
        font-size: 0.9rem;
    }

    /* Section header */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
        font-weight: 600;
        color: #334155;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #f1f5f9;
    }
    .section-header svg {
        color: #3b82f6;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        padding: 10px 20px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 500 !important;
        border-radius: 10px;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Form */
    .stForm {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
    }

    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        border-radius: 16px;
        padding: 40px;
        color: white;
        margin-bottom: 32px;
    }
    .welcome-card h2 {
        color: white !important;
        font-size: 1.75rem !important;
        margin-bottom: 8px !important;
    }
    .welcome-card p {
        color: #dbeafe;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Feature grid */
    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        transition: all 0.2s ease;
    }
    .feature-card:hover {
        border-color: #93c5fd;
        box-shadow: 0 4px 12px rgba(59,130,246,0.1);
    }
    .feature-card .feature-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
    }
    .feature-card h4 {
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .feature-card p {
        color: #64748b;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* Transaction card */
    .tx-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.15s ease;
    }
    .tx-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .tx-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .tx-badge-chiqim { background: #fef3c7; color: #92400e; }
    .tx-badge-kirim { background: #dcfce7; color: #166534; }
    .tx-badge-sarf { background: #dbeafe; color: #1e40af; }
    .tx-badge-chiqindi { background: #fecaca; color: #991b1b; }
    .tx-badge-tuzatish { background: #e9d5ff; color: #6b21a8; }

    /* Hide default hamburger menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def page_header(title, icon_name, subtitle=""):
    """Render a styled page header with Lucide icon."""
    inject_css()
    svg = icon(icon_name, size=28)
    st.markdown(f"""
    <div class="page-header">
        {svg}
        <h1>{title}</h1>
    </div>
    """, unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def section_header(title, icon_name):
    """Render a styled section header."""
    svg = icon(icon_name, size=18)
    st.markdown(f"""
    <div class="section-header">
        {svg}
        <span>{title}</span>
    </div>
    """, unsafe_allow_html=True)


def stat_card(label, value, icon_name, color="blue"):
    """Render a stat card with icon."""
    svg = icon(icon_name, size=24)
    return f"""
    <div class="stat-card stat-{color}">
        <div class="stat-icon">{svg}</div>
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
    </div>
    """


def info_banner(text, icon_name="alert-circle"):
    """Render an info banner."""
    svg = icon(icon_name, size=18, color="#2563eb")
    st.markdown(f"""
    <div class="info-banner">
        {svg}
        <span>{text}</span>
    </div>
    """, unsafe_allow_html=True)


def tx_badge(tx_type):
    """Return HTML for a transaction type badge."""
    labels = {
        "chiqim": "Chiqim",
        "kirim": "Kirim",
        "sarf": "Sarf",
        "chiqindi": "Chiqindi",
        "tuzatish": "Tuzatish",
    }
    icons_map = {
        "chiqim": "send",
        "kirim": "inbox",
        "sarf": "recycle",
        "chiqindi": "trash",
        "tuzatish": "edit",
    }
    svg = icon(icons_map.get(tx_type, "package"), size=14)
    return f'<span class="tx-badge tx-badge-{tx_type}">{svg} {labels.get(tx_type, tx_type)}</span>'
