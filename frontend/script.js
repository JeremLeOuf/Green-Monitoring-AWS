document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('metrics-form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission

        // Fetch form values
        const instanceType = document.getElementById('instance_type').value;
        const period = document.getElementById('period').value;
        const vcpuUtilization = document.getElementById('vcpu_utilization').value;
        const region = document.getElementById('region').value;

        // Construct payload for Lambda function
        const payload = {
            instance_type: instanceType,
            period: parseInt(period),
            vcpu_utilization: parseFloat(vcpuUtilization),
            region: region
        };

        try {
            const response = await fetch('https://gqupth3jnl.execute-api.eu-north-1.amazonaws.com/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Lambda function executed successfully:', data);

            // Display results in the resultsDiv
            resultsDiv.innerHTML = formatResults(data, instanceType, period, region);

        } catch (error) {
            console.error('Error calling Lambda function:', error);
            resultsDiv.innerHTML = `<div>Error: ${error.message}</div>`;
        }
    });

    function formatResults(data, instanceType, period, region) {
        console.log('Response data:', data); // Log the response for debugging

        // Check if data object is defined and contains messages and table_data
        if (data && data.body) {
            const parsedData = JSON.parse(data.body);

            // Check if parsedData contains messages and table_data
            if (parsedData.messages && parsedData.table_data) {
                    // Construct formatted messages
                    let formattedMessages = parsedData.messages.map(message => {

                    // Format instance type as bold
                    message = message.replace(instanceType, `<b>${instanceType}</b>`);

                    // Bold numerical values followed by % for CPU utilization, including "CPU Utilization"
                    message = message.replace(/(\d+(\.\d+)?)% (CPU Utilization)/g, '<b>$1%</b> <b>$3</b>');

                    // Bold the number of hours/days/weeks/months dynamically
                    message = message.replace(/(\d+\s(hours?|days?|weeks?|months?|years?))/g, '<b>$1</b>');

                    // Bold numbers followed by " Watts" and the "(W)"
                    message = message.replace(/(\d+\.\d+) Watts\s?\(W\)/g, '<b>$1 Watts</b> <b>(W)</b>');
                    
                    // Bold specific value for Kilowatt-Hours (kWh)
                    message = message.replace(/(\d+\.\d+) Kilowatt-Hours:/g, '<b>$1 Kilowatt-Hours:</b>');

                    // Bold numbers followed by " gCO2/kWh" for Carbon Intensity and round the number
                    message = message.replace(/(\d+\.\d+) gCO2\/kWh/g, (_, value) => `<b>${Math.round(value)} gCO2/kWh</b>`);

                    // Include the region name with bold formatting
                    message = message.replace(/The carbon intensity for your region is/, `The carbon intensity for your region <b>(${region})</b> is`);

                    return message;
                }).join('<br>');

                // Build the first table for instance details data
                let minMaxTableHtml = `<table class="table instance-table">`;
                minMaxTableHtml += `<tr><th>${instanceType} Details:</th><th>Value:</th></tr>`;
                for (const row of parsedData.table_data.min_max) {
                    minMaxTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
                }
                minMaxTableHtml += `</table>`;

                // Build the second table for the utilization data
                let avgWattHoursTableHtml = `<table class="table utilization-table">`;
                avgWattHoursTableHtml += `<tr><th>Utilization Details:</th><th>Value:</th></tr>`;
                for (const row of parsedData.table_data.avg_watt_hours) {
                    // Bold the specific value for Kilowatt-Hours (kWh) in the table
                    if (row.Metric.includes('Instance Power Consumption (kWh)')) {
                        avgWattHoursTableHtml += `<tr><td>${row.Metric}</td><td><b>${row.Value}</b></td></tr>`;
                    } else {
                        avgWattHoursTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
                    }
                }
                avgWattHoursTableHtml += `</table>`;

                // Build the third table for the carbon intensity data
                let carbonIntensityTableHtml = `<table class="table carbon-intensity-table">`;
                carbonIntensityTableHtml += `<tr><th>Region Details:</th><th>Value:</th></tr>`;
                for (const row of parsedData.table_data.carbon_intensity) {
                    carbonIntensityTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
                }
                carbonIntensityTableHtml += `</table>`;

                // Return the combined HTML for messages and all tables
                return `
                    <p>${formattedMessages}</p>
                    ${minMaxTableHtml}
                    ${avgWattHoursTableHtml}
                    ${carbonIntensityTableHtml}
                `;
            } else {
                return '<p>No data available.</p>';
            }
        } else {
            return '<p>No data available.</p>';
        }
    }
});
