document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('metrics-form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission

        // Fetch form values
        const instanceType = document.getElementById('instance_type').value;
        const region = document.getElementById('region').value;
        const period = document.getElementById('period').value;

        // Construct payload for Lambda function
        const payload = {
            instance_type: instanceType,
            region: region,
            period: parseInt(period) // Ensure period is parsed as integer
        };

        try {
            const response = await fetch('<your_lambda_endpoint>', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            // Display results in the resultsDiv
            resultsDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } catch (error) {
            console.error('Error invoking Lambda:', error);
            resultsDiv.innerHTML = `<div>Error: ${error.message}</div>`;
        }
    });
});
