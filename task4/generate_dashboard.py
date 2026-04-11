import json

def generate_dashboard():
    with open('results.json', 'r') as f:
        data = json.load(f)
        
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BI Analytics Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --surface-color: #1e293b;
            --primary: #8b5cf6;
            --primary-hover: #7c3aed;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #10b981;
            --border: #334155;
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            min-height: 100vh;
            background-image: 
                radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.1) 0px, transparent 50%);
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }}
        
        h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .tabs {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .tab-btn {{
            background: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .tab-btn:hover {{
            background: var(--surface-color);
            color: var(--text-main);
        }}
        
        .tab-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.4s ease forwards;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 1.5rem;
        }}
        
        .card {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        .stat-card {{
            grid-column: span 3;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        @media (max-width: 1024px) {{
            .stat-card {{ grid-column: span 6; }}
        }}
        
        @media (max-width: 640px) {{
            .stat-card {{ grid-column: span 12; }}
        }}
        
        .chart-card {{
            grid-column: span 8;
        }}
        
        .table-card {{
            grid-column: span 4;
        }}
        
        @media (max-width: 1024px) {{
            .chart-card, .table-card {{ grid-column: span 12; }}
        }}
        
        .card-title {{
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .card-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-main);
        }}
        
        .card-value.highlight {{
            color: var(--accent);
        }}
        
        .chart-container {{
            width: 100%;
            height: auto;
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            object-fit: contain;
        }}
        
        .list-group {{
            list-style: none;
            margin-top: 1rem;
        }}
        
        .list-item {{
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .list-item:last-child {{
            border-bottom: none;
        }}
        
        .list-item-rank {{
            background: var(--surface-color);
            color: var(--text-muted);
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            margin-right: 0.5rem;
        }}
        
        .badge {{
            background: rgba(139, 92, 246, 0.2);
            color: #c4b5fd;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }}
        
        .author-name {{
            display: inline-block;
            margin: 0.2rem;
            background: rgba(16, 185, 129, 0.1);
            color: #6ee7b7;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            font-size: 0.875rem;
        }}
        
        .buyer-ids {{
            font-family: monospace;
            background: #0f172a;
            padding: 0.75rem;
            border-radius: 8px;
            word-break: break-all;
            color: #cbd5e1;
            font-size: 0.85rem;
            border: 1px solid var(--border);
            margin-top: 0.5rem;
            max-height: 150px;
            overflow-y: auto;
        }}

        /* Scrollbar styles for buyer-ids */
        .buyer-ids::-webkit-scrollbar {{
            width: 6px;
        }}
        .buyer-ids::-webkit-scrollbar-track {{
            background: #0f172a;
        }}
        .buyer-ids::-webkit-scrollbar-thumb {{
            background: #475569;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ITransition Data Dashboard</h1>
            <div>
                <span class="badge">Static BI</span>
            </div>
        </header>
        
        <div class="tabs">
"""
    # Create Tab buttons
    for i, dataset in enumerate(data.keys()):
        active_class = "active" if i == 0 else ""
        html += f'            <button class="tab-btn {active_class}" onclick="openTab(event, \'{dataset}\')">{dataset}</button>\n'
        
    html += "        </div>\n\n"
    
    # Create Tab Contents
    for i, (dataset, stats) in enumerate(data.items()):
        active_class = "active" if i == 0 else ""
        
        top_author_html = ""
        for author in stats['top_author']:
            top_author_html += f'<span class="author-name">{author}</span>'
        if not top_author_html:
            top_author_html = '<span class="text-muted">None Found</span>'
            
        buyer_ids_json = json.dumps(stats['best_buyer'])
        
        top_days_html = ""
        for rank, day in enumerate(stats['top_5_days'], 1):
            top_days_html += f"""
                            <li class="list-item">
                                <div>
                                    <span class="list-item-rank">{rank}</span>
                                    <span>{day}</span>
                                </div>
                                <span class="badge">Top Revenue</span>
                            </li>"""
        
        html += f"""        <div id="{dataset}" class="tab-content {active_class}">
            <div class="dashboard-grid">
                
                <!-- Stat Cards -->
                <div class="card stat-card">
                    <div class="card-title">Unique Users</div>
                    <div class="card-value highlight">{stats['unique_users']:,}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">After fuzzy reconciliation</div>
                </div>
                
                <div class="card stat-card">
                    <div class="card-title">Unique Author Sets</div>
                    <div class="card-value">{stats['unique_authors']:,}</div>
                </div>
                
                <div class="card stat-card" style="grid-column: span 6;">
                    <div class="card-title">Most Popular Author Set</div>
                    <div style="margin-top: 0.5rem;">
                        {top_author_html}
                    </div>
                </div>
                
                <!-- Main Chart -->
                <div class="card chart-card">
                    <div class="card-title">Daily Revenue Overview</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{stats['chart']}" alt="Daily Revenue Chart">
                    </div>
                </div>
                
                <!-- Top Days Table -->
                <div class="card table-card">
                    <div class="card-title">Top 5 Days by Revenue</div>
                    <ul class="list-group">
                        {top_days_html}
                    </ul>
                </div>
                
                <!-- Best Customer -->
                <div class="card" style="grid-column: span 12;">
                    <div class="card-title">Top Customer Identity Clusters (Array of IDs)</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
                        This customer generated the highest total spending across all paired identity profiles.
                    </div>
                    <div class="buyer-ids">
                        {buyer_ids_json}
                    </div>
                </div>
                
            </div>
        </div>
"""

    html += """
    </div>

    <script>
        function openTab(evt, tabName) {
            // Hide all tab contents
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].className = tabcontent[i].className.replace(" active", "");
            }
            
            // Remove active class from all buttons
            tablinks = document.getElementsByClassName("tab-btn");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            
            // Show the current tab and add active class to button
            document.getElementById(tabName).className += " active";
            evt.currentTarget.className += " active";
        }
    </script>
</body>
</html>
"""
    
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Dashboard generated successfully as `dashboard.html`")

if __name__ == '__main__':
    generate_dashboard()
