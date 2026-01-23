
function showSection(sectionId) {
    document.getElementById('dashboard-section').classList.add('hidden-section');
    document.getElementById('purchases-section').classList.add('hidden-section');
    document.getElementById('products-section').classList.add('hidden-section');
   
    document.getElementById(`${sectionId}-section`).classList.remove('hidden-section');
   
    if(sectionId === 'purchases') loadPurchases();
    if(sectionId === 'products') loadProducts();
}


document.addEventListener('DOMContentLoaded', () => {
    // Load Dashboard Data
    fetch('http://127.0.0.1:5000/api/dashboard')
        .then(res => res.json())
        .then(data => {
            document.getElementById('kpi-products').innerText = data.products;
            document.getElementById('kpi-revenue').innerText = `₹${data.revenue.toLocaleString('en-IN')}`;
            document.getElementById('kpi-stock').innerText = data.stock;
            document.getElementById('kpi-oos').innerText = data.oos;


            // Scrollable Tables
            const expTable = document.getElementById('expiring-table');
            data.expiring.forEach(item => {
                expTable.innerHTML += `<tr class="border-b last:border-0 hover:bg-slate-50 transition">
                    <td class="py-4 font-bold text-slate-700">${item.name}</td>
                    <td class="py-4 text-slate-400">${new Date(item.expiry_date).toLocaleDateString()}</td>
                    <td class="py-4 text-right font-mono text-cyan-600">${item.stock_quantity}</td>
                </tr>`;
            });


            const ordTable = document.getElementById('orders-table');
            data.recent_orders.forEach(item => {
                ordTable.innerHTML += `<tr class="border-b last:border-0 hover:bg-slate-50 transition">
                    <td class="py-4 font-bold text-slate-700">${item.customer_name}</td>
                    <td class="py-4 text-right font-black text-teal-600">₹${item.total_amount}</td>
                </tr>`;
            });


            // Sales Chart (Bar + Line Hybrid)
            const ctxSales = document.getElementById('salesChart').getContext('2d');
            new Chart(ctxSales, {
                type: 'line',
                data: {
                    labels: data.monthly_sales.map(m => m.month),
                    datasets: [{
                        label: 'Revenue',
                        data: data.monthly_sales.map(m => m.amount),
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3
                    }]
                }
            });


            // Doughnut Chart (Stock by Category)
            const ctxDonut = document.getElementById('donutChart').getContext('2d');
            new Chart(ctxDonut, {
                type: 'doughnut',
                data: {
                    labels: data.category_dist.map(c => c.category),
                    datasets: [{
                        data: data.category_dist.map(c => c.value),
                        backgroundColor: ['#06b6d4', '#14b8a6', '#6366f1', '#f43f5e', '#f59e0b']
                    }]
                },
                options: { cutout: '75%', plugins: { legend: { position: 'bottom' } } }
            });
        });
});


function loadPurchases() {
    fetch('http://127.0.0.1:5000/api/purchases')
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById('full-purchases-table');
            table.innerHTML = '';
            data.forEach(p => {
                table.innerHTML += `<tr class="border-b hover:bg-slate-50">
                    <td class="p-5 font-mono text-xs text-slate-400">#${p.id}</td>
                    <td class="p-5 font-bold">${p.customer_name}</td>
                    <td class="p-5">${p.medicine}</td>
                    <td class="p-5">${p.quantity}</td>
                    <td class="p-5 font-bold text-teal-600">₹${p.total_amount}</td>
                    <td class="p-5 text-slate-400">${new Date(p.order_date).toLocaleString()}</td>
                </tr>`;
            });
        });
}


function loadProducts() {
    fetch('http://127.0.0.1:5000/api/products')
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById('full-products-table');
            table.innerHTML = '';
            data.forEach(p => {
                const badgeColor = p.stock_quantity > 0 ? 'bg-teal-100 text-teal-700' : 'bg-rose-100 text-rose-700';
                table.innerHTML += `<tr class="border-b hover:bg-slate-50">
                    <td class="p-5 font-bold">${p.name}</td>
                    <td class="p-5 text-slate-500">${p.category}</td>
                    <td class="p-5 font-mono">₹${p.price}</td>
                    <td class="p-5 font-bold">${p.stock_quantity}</td>
                    <td class="p-5"><span class="${badgeColor} px-3 py-1 rounded-full text-[10px] font-black uppercase">${p.status}</span></td>
                </tr>`;
            });
        });
}

