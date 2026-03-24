// Search Buses
document.getElementById('searchForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const from = document.getElementById('from').value.trim();
    const to = document.getElementById('to').value.trim();
    const maxFare = document.getElementById('maxFare').value.trim();

    const params = new URLSearchParams({
        from_district: from,
        to_district: to
    });

    if (maxFare !== "") params.append('max_fare', maxFare);

    const response = await fetch('/api/search?' + params.toString());
    const data = await response.json();

    document.getElementById('searchResults').innerHTML =
        `<pre>${JSON.stringify(data.results, null, 2)}</pre>`;
});


// Book Bus Ticket
document.getElementById('bookForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const payload = {
        passenger_name: document.getElementById('passenger_name').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        from_district: document.getElementById('b_from').value.trim(),
        to_district: document.getElementById('b_to').value.trim(),
        dropping_point: document.getElementById('b_dp').value.trim(),
        fare: parseInt(document.getElementById('b_fare').value.trim()),
        travel_date: document.getElementById('b_date').value.trim()
    };

    const response = await fetch('/api/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    document.getElementById('bookResult').innerHTML =
        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
});


// RAG Query
document.getElementById('ragForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const query = document.getElementById('q').value.trim();
    const response = await fetch('/api/rag?q=' + encodeURIComponent(query));
    const data = await response.json();

    document.getElementById('ragAnswer').innerHTML =
        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
});
