document.getElementById('metrics-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const instanceType = document.getElementById('instance_type').value;
    const region = document.getElementById('region').value;
    const period = document.getElementById('period').value;

    const response = await fetch('https://8f72pd0xpd.execute-api.eu-north-1.amazonaws.com/test/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ instance_type: instanceType, region: region, period: period })
    });

    const result = await response.json();
    document.getElementById('results').innerText = JSON.stringify(result, null, 2);
});
