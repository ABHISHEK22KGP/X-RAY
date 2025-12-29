"""
server.py - Dashboard for X-Ray traces
The UI part that shows you what's actually happening inside your code
"""

import json
import os
import html
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime

class DashboardHandler(BaseHTTPRequestHandler):
    """Handles the dashboard requests"""
    
    def do_GET(self):
        """GET requests - serve page or API data"""
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/':
            self._show_dashboard()
        elif path == '/api/traces':
            self._send_trace_list()
        elif path.startswith('/api/trace/'):
            trace_id = path.split('/')[-1]
            self._send_single_trace(trace_id)
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        """POST requests - for saving new traces"""
        if self.path == '/api/traces':
            self._save_new_trace()
        else:
            self.send_error(404)
    
    def _show_dashboard(self):
        """Show the main dashboard page"""
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>X-Ray Debug Dashboard</title>
    <style>
        /* Basic reset */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.5;
        }
        
        /* Header */
        .header {
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 0.95rem;
        }
        
        /* Main layout */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .dashboard {
            display: flex;
            gap: 2rem;
            margin-top: 2rem;
            min-height: 600px;
        }
        
        /* Sidebar */
        .sidebar {
            width: 320px;
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .search {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
        
        .search:focus {
            outline: none;
            border-color: #4f46e5;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-box {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 0.75rem;
            text-align: center;
        }
        
        .stat-number {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1f2937;
        }
        
        .stat-label {
            font-size: 0.75rem;
            color: #6b7280;
            text-transform: uppercase;
            margin-top: 0.25rem;
        }
        
        /* Trace list */
        .trace-list {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
        }
        
        .trace-item {
            padding: 1rem;
            border-bottom: 1px solid #e5e7eb;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .trace-item:hover {
            background: #f3f4f6;
        }
        
        .trace-item.selected {
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
        }
        
        .trace-name {
            font-weight: 500;
            color: #1f2937;
            margin-bottom: 0.25rem;
        }
        
        .trace-id {
            font-family: monospace;
            font-size: 0.8rem;
            color: #6b7280;
            background: #f3f4f6;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 0.5rem;
        }
        
        .trace-info {
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
            color: #6b7280;
        }
        
        /* Main content */
        .main {
            flex: 1;
        }
        
        .trace-details {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .details-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .back-btn {
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            color: #4b5563;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .back-btn:hover {
            background: #e5e7eb;
        }
        
        /* Steps */
        .steps {
            margin-top: 1rem;
        }
        
        .step {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        .step-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .step-title {
            font-weight: 500;
            color: #1f2937;
            font-size: 1.1rem;
        }
        
        .step-type {
            background: #dbeafe;
            color: #1d4ed8;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .step-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .info-box {
            background: #f8fafc;
            padding: 0.75rem;
            border-radius: 6px;
        }
        
        .info-label {
            font-size: 0.75rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .info-value {
            font-size: 0.95rem;
            font-weight: 500;
            color: #1f2937;
            margin-top: 0.25rem;
        }
        
        .status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .status-pass {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-fail {
            background: #fee2e2;
            color: #991b1b;
        }
        
        /* Reasoning box */
        .reasoning {
            background: #f0f9ff;
            border-left: 3px solid #0ea5e9;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 6px 6px 0;
        }
        
        .reasoning strong {
            color: #0369a1;
        }
        
        /* I/O section */
        .io-toggle {
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            color: #4b5563;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .io-content {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 1rem;
            margin-top: 0.5rem;
            display: none;
        }
        
        .io-content.show {
            display: block;
        }
        
        .io-section {
            margin-bottom: 1rem;
        }
        
        pre {
            background: #1f2937;
            color: #e5e7eb;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 0.85rem;
            font-family: 'SF Mono', Monaco, Consolas, monospace;
        }
        
        /* Empty state */
        .empty {
            text-align: center;
            padding: 3rem 1rem;
            color: #6b7280;
        }
        
        .empty h3 {
            margin-bottom: 0.5rem;
            color: #4b5563;
        }
        
        /* Auto-refresh note */
        .refresh-note {
            text-align: center;
            font-size: 0.85rem;
            color: #6b7280;
            margin-top: 1rem;
            padding: 0.5rem;
            background: #f8fafc;
            border-radius: 6px;
        }
        
        /* Last updated */
        .last-updated {
            font-size: 0.85rem;
            color: #6b7280;
            margin-top: 1rem;
        }
        
        /* Check and cross icons */
        .check-icon:before {
            content: "✓";
            margin-right: 4px;
        }
        
        .cross-icon:before {
            content: "✗";
            margin-right: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>X-Ray Debug Dashboard</h1>
            <p>See what's really happening inside your multi-step algorithms</p>
        </div>
    </div>
    
    <div class="container">
        <div class="dashboard">
            <!-- Sidebar -->
            <div class="sidebar">
                <input type="text" class="search" placeholder="Search traces..." 
                       onkeyup="searchTraces(this.value)">
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number" id="total-traces">0</div>
                        <div class="stat-label">Traces</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="avg-time">0ms</div>
                        <div class="stat-label">Avg Time</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="avg-steps">0</div>
                        <div class="stat-label">Avg Steps</div>
                    </div>
                </div>
                
                <div class="trace-list" id="trace-list">
                    <div class="empty">
                        <p>Loading traces...</p>
                    </div>
                </div>
                
                <div class="last-updated" id="last-updated">
                    Last updated: --
                </div>
            </div>
            
            <!-- Main content -->
            <div class="main" id="main-content">
                <div class="empty" id="empty-state">
                    <h3>No trace selected</h3>
                    <p>Click on a trace from the left to see details</p>
                </div>
                
                <div class="trace-details" id="trace-details" style="display: none;">
                    <div class="details-header">
                        <h2 id="trace-title">Trace Details</h2>
                        <button class="back-btn" onclick="goBack()">&larr; Back to list</button>
                    </div>
                    
                    <div id="steps-container">
                        <!-- Steps go here -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let traces = [];
        let currentTrace = null;
        
        // Load traces
        async function loadTraces() {
            try {
                const res = await fetch('/api/traces');
                traces = await res.json();
                
                // Newest first
                traces.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
                
                updateTraceList();
                updateStats();
                updateTime();
                
                // Show first trace if nothing selected
                if (traces.length > 0 && !currentTrace) {
                    showTrace(traces[0].id);
                }
                
            } catch (err) {
                console.error('Failed to load traces:', err);
                document.getElementById('trace-list').innerHTML = 
                    '<div class="empty"><p>Error loading traces</p></div>';
            }
        }
        
        // Update trace list
        function updateTraceList() {
            const list = document.getElementById('trace-list');
            
            if (traces.length === 0) {
                list.innerHTML = '<div class="empty"><p>No traces found</p></div>';
                return;
            }
            
            list.innerHTML = traces.map(trace => `
                <div class="trace-item ${currentTrace?.id === trace.id ? 'selected' : ''}" 
                     onclick="showTrace('${trace.id}')">
                    <div class="trace-id">${trace.id}</div>
                    <div class="trace-name">${escape(trace.name || 'Untitled Trace')}</div>
                    <div class="trace-info">
                        <span>${trace.total_steps || 0} steps</span>
                        <span>${trace.total_duration_ms || 0}ms</span>
                    </div>
                </div>
            `).join('');
        }
        
        // Show a specific trace
        async function showTrace(traceId) {
            try {
                const res = await fetch('/api/trace/' + traceId);
                currentTrace = await res.json();
                
                // Update UI
                document.getElementById('empty-state').style.display = 'none';
                document.getElementById('trace-details').style.display = 'block';
                
                // Update list selection
                document.querySelectorAll('.trace-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                const selectedItem = Array.from(document.querySelectorAll('.trace-item')).find(item => 
                    item.querySelector('.trace-id').textContent === traceId
                );
                if (selectedItem) {
                    selectedItem.classList.add('selected');
                }
                
                // Set title
                document.getElementById('trace-title').textContent = 
                    currentTrace.name || currentTrace.id;
                
                // Show steps
                showSteps(currentTrace);
                
            } catch (err) {
                console.error('Failed to load trace:', err);
                alert('Could not load trace details');
            }
        }
        
        // Show steps for trace
        function showSteps(trace) {
            const container = document.getElementById('steps-container');
            
            if (!trace.steps || trace.steps.length === 0) {
                container.innerHTML = '<p>No steps recorded</p>';
                return;
            }
            
            const stepsHtml = trace.steps.map(step => `
                <div class="step">
                    <div class="step-header">
                        <div class="step-title">${step.name}</div>
                        <div class="step-type">${step.step_type}</div>
                    </div>
                    
                    <div class="step-info">
                        <div class="info-box">
                            <div class="info-label">Status</div>
                            <div class="status ${step.success ? 'status-pass' : 'status-fail'}">
                                ${step.success ? 'Pass' : 'Fail'}
                                <span class="${step.success ? 'check-icon' : 'cross-icon'}"></span>
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Duration</div>
                            <div class="info-value">${step.duration_ms || 0}ms</div>
                        </div>
                    </div>
                    
                    ${step.reasoning ? `
                        <div class="reasoning">
                            <strong>Why:</strong> ${step.reasoning}
                        </div>
                    ` : ''}
                    
                    <button class="io-toggle" onclick="toggleIO(this)">
                        Show Input/Output
                    </button>
                    
                    <div class="io-content">
                        <div class="io-section">
                            <div class="info-label">Input</div>
                            <pre>${escape(JSON.stringify(step.input || {}, null, 2))}</pre>
                        </div>
                        
                        ${step.output ? `
                        <div class="io-section">
                            <div class="info-label">Output</div>
                            <pre>${escape(JSON.stringify(step.output || {}, null, 2))}</pre>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <strong>${trace.total_steps} steps • ${trace.total_duration_ms || 0}ms total</strong>
                </div>
                ${stepsHtml}
            `;
        }
        
        // Go back to list
        function goBack() {
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('trace-details').style.display = 'none';
            currentTrace = null;
            
            // Clear selection
            document.querySelectorAll('.trace-item').forEach(item => {
                item.classList.remove('selected');
            });
        }
        
        // Search traces
        function searchTraces(query) {
            if (!query.trim()) {
                updateTraceList();
                return;
            }
            
            const filtered = traces.filter(trace => 
                trace.name?.toLowerCase().includes(query.toLowerCase()) ||
                trace.id.toLowerCase().includes(query.toLowerCase())
            );
            
            const list = document.getElementById('trace-list');
            
            if (filtered.length === 0) {
                list.innerHTML = '<div class="empty"><p>No matches found</p></div>';
                return;
            }
            
            list.innerHTML = filtered.map(trace => `
                <div class="trace-item" onclick="showTrace('${trace.id}')">
                    <div class="trace-id">${trace.id}</div>
                    <div class="trace-name">${escape(trace.name || 'Untitled Trace')}</div>
                    <div class="trace-info">
                        <span>${trace.total_steps || 0} steps</span>
                        <span>${trace.total_duration_ms || 0}ms</span>
                    </div>
                </div>
            `).join('');
        }
        
        // Toggle I/O visibility
        function toggleIO(button) {
            const content = button.nextElementSibling;
            content.classList.toggle('show');
            button.textContent = content.classList.contains('show') 
                ? 'Hide Input/Output' 
                : 'Show Input/Output';
        }
        
        // Update stats
        function updateStats() {
            if (traces.length === 0) {
                document.getElementById('total-traces').textContent = '0';
                document.getElementById('avg-time').textContent = '0ms';
                document.getElementById('avg-steps').textContent = '0';
                return;
            }
            
            document.getElementById('total-traces').textContent = traces.length;
            
            const totalTime = traces.reduce((sum, trace) => sum + (trace.total_duration_ms || 0), 0);
            const avgTime = Math.round(totalTime / traces.length);
            document.getElementById('avg-time').textContent = avgTime + 'ms';
            
            const totalSteps = traces.reduce((sum, trace) => sum + (trace.total_steps || 0), 0);
            const avgSteps = Math.round(totalSteps / traces.length);
            document.getElementById('avg-steps').textContent = avgSteps;
        }
        
        // Update time
        function updateTime() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const dateStr = now.toLocaleDateString();
            document.getElementById('last-updated').textContent = 
                `Last updated: ${dateStr} ${timeStr}`;
        }
        
        // Refresh just the list
        async function refreshList() {
            if (currentTrace) return; // Don't refresh if viewing a trace
            
            try {
                const res = await fetch('/api/traces');
                const newTraces = await res.json();
                newTraces.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
                
                traces = newTraces;
                updateTraceList();
                updateStats();
                updateTime();
            } catch (err) {
                console.error('Refresh failed:', err);
            }
        }
        
        // Escape HTML
        function escape(text) {
            if (!text) return '';
            return text.toString()
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
        
        // Auto-refresh every 10s
        setInterval(refreshList, 10000);
        
        // Initial load
        loadTraces();
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def _send_trace_list(self):
        """Send list of all traces"""
        trace_files = []
        
        # Look for trace files
        for file in os.listdir('.'):
            if file.startswith('trace_') and file.endswith('.json'):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        trace_files.append({
                            "id": data.get("id", file.replace('trace_', '').replace('.json', '')),
                            "name": data.get("name", "Trace"),
                            "start_time": data.get("start_time", ""),
                            "total_steps": data.get("total_steps", 0),
                            "total_duration_ms": data.get("total_duration_ms", 0)
                        })
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
        
        # Sort by time
        trace_files.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        
        self._send_json_response(trace_files)
    
    def _send_single_trace(self, trace_id):
        """Send one trace's details"""
        file_name = f"trace_{trace_id}.json"
        
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                trace_data = json.load(f)
            self._send_json_response(trace_data)
        else:
            self.send_error(404, f"Trace {trace_id} not found")
    
    def _save_new_trace(self):
        """Save a trace from POST"""
        try:
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            trace = json.loads(data)
            
            file_name = f"trace_{trace['id']}.json"
            with open(file_name, 'w') as f:
                json.dump(trace, f, indent=2)
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True,
                "id": trace['id']
            }).encode())
            
        except Exception as e:
            self.send_error(500, f"Save failed: {str(e)}")
    
    def _send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def log_message(self, format, *args):
        """Quiet logging"""
        pass

def start_server(port=8000):
    """Start the dashboard server"""
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print(f"""
    X-Ray Dashboard
    {'=' * 40}
    
    Running at: http://localhost:{port}
    
    Trace files are in: {os.getcwd()}
    
    Auto-refresh: Every 10 seconds (when not viewing trace)
    
    Press Ctrl+C to stop
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.server_close()

if __name__ == '__main__':
    start_server()