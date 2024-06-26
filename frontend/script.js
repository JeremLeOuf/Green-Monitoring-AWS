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
            resultsDiv.innerHTML = formatResults(data);

        } catch (error) {
            console.error('Error calling Lambda function:', error);
            resultsDiv.innerHTML = `<div>Error: ${error.message}</div>`;
        }
    });

    function formatResults(data) {
        console.log('Response data:', data); // Log the response for debugging
    
        // Check if data object is defined and contains messages and table_data
        if (data && data.body) {
            const parsedData = JSON.parse(data.body);
    
            // Check if parsedData contains messages and table_data
            if (parsedData.messages && parsedData.table_data) {
                // Construct formatted messages
                let formattedMessages = parsedData.messages.map(message => {
                    // Bold specific value for Kilowatt-Hours (kWh)
                    message = message.replace(/(\d+\.\d+) Kilowatt-Hours:/g, '<b>$1 Kilowatt-Hours:</b>');
    
                    // Bold numerical values followed by % for CPU utilization, including "CPU Utilization"
                    message = message.replace(/(\d+(\.\d+)?)% (CPU Utilization)/g, '<b>$1%</b> <b>$3</b>');
    
                    // Bold numbers followed by " Watt" for Watts
                    message = message.replace(/(\d+\.\d+) Watts/g, '<b>$1 Watts</b>');
    
                    // Bold numbers followed by " gCO2/kWh" for Carbon Intensity
                    message = message.replace(/(\d+\.\d+) gCO2\/kWh/g, '<b>$1 gCO2/kWh</b>');
    
                    return message;
                }).join('<br>');
    
                // Build the first table for min_max data
                let minMaxTableHtml = `<table class="table instance-table">`;
                minMaxTableHtml += `<tr><th>Instance details:</th><th>Value:</th></tr>`;
                for (const row of parsedData.table_data.min_max) {
                    minMaxTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
                }
                minMaxTableHtml += `</table>`;
    
                // Build the second table for avg_watt_hours data
                let avgWattHoursTableHtml = `<table class="table utilization-table">`;
                avgWattHoursTableHtml += `<tr><th>Utilization details:</th><th>Value:</th></tr>`;
                for (const row of parsedData.table_data.avg_watt_hours) {
                    // Bold the specific value for Kilowatt-Hours (kWh) in the table
                    if (row.Metric.includes('Instance power consumption (kWh)')) {
                        avgWattHoursTableHtml += `<tr><td>${row.Metric}</td><td><b>${row.Value}</b></td></tr>`;
                    } else {
                        avgWattHoursTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
                    }
                }
                avgWattHoursTableHtml += `</table>`;
    
                // Return the combined HTML for messages and both tables
                return `
                    <p>${formattedMessages}</p>
                    ${minMaxTableHtml}
                    ${avgWattHoursTableHtml}
                `;
            } else {
                return '<p>No data available.</p>';
            }
        } else {
            return '<p>No data available.</p>';
        }
    }
    
});
