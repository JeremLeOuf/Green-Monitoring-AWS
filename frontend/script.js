document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('metrics-form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission

        // Fetch form values
        const instanceType = document.getElementById('instance_type').value;
        const period = document.getElementById('period').value;
        const vcpuUtilization = document.getElementById('vcpu_utilization').value;

        // Construct payload for Lambda function
        const payload = {
            instance_type: instanceType,
            period: parseInt(period),
            vcpu_utilization: parseFloat(vcpuUtilization)
        };

        try {
            const response = await fetch('https://8f72pd0xpd.execute-api.eu-north-1.amazonaws.com/test/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            let data = await response.json();

            // Parse the body from the response if it is a string
            if (typeof data.body === 'string') {
                data = JSON.parse(data.body);
            }

            // Ensure data.messages is defined
            if (!data.messages) {
                throw new Error("Messages data is undefined");
            }

            // Format and display results
            resultsDiv.innerHTML = formatResults(data);
        } catch (error) {
            console.error('Error invoking Lambda:', error);
            resultsDiv.innerHTML = `<div>Error: ${error.message}</div>`;
        }
    });

    function formatResults(data) {
        // Combine all messages into a single string with line breaks and formatting
        let formattedMessages = data.messages.map(message => {
            // Bold numerical values followed by % for CPU utilization, including "CPU Utilization"
            message = message.replace(/(\d+(\.\d+)?)% (CPU Utilization)/g, '<b>$1%</b> <b>$3</b>');
            
            // Bold numbers followed by "hour(s)"
            message = message.replace(/(\d+) (hour\(s\))/g, '<b>$1</b> <b>$2</b>');
            
            // Bold numerical values followed by " Watts" for Watts
            message = message.replace(/(\d+\.\d+) Watts/g, '<b>$1</b> Watts');
            
            // Bold numerical values followed by " Watt-Hours" for Watt-Hours
            message = message.replace(/(\d+\.\d+) Watt-Hours/g, '<b>$1</b> Watt-Hours');
    
            // Replace inline code with <code> tags
            message = message.replace(/`(.*?)`/g, '<code>$1</code>');
    
            return message;
        }).join('<br>');

        // Build the "Instance details" table
        let instanceTableHtml = `<table class="table">`;
        instanceTableHtml += `<tr><th>Instance details:</th><th>Value:</th></tr>`;

        // Filter data for instance details and add rows
        for (const row of data.table_data) {
            if (row.Metric.includes('Watts')) {
                instanceTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
            }
        }

        instanceTableHtml += `</table>`;

        // Build the "Utilization details" table
        let utilizationTableHtml = `<table class="table">`;
        utilizationTableHtml += `<tr><th>Utilization details:</th><th>Value:</th></tr>`;

        // Filter data for utilization details and add rows
        for (const row of data.table_data) {
            if (!row.Metric.includes('Watts')) {
                utilizationTableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
            }
        }

        utilizationTableHtml += `</table>`;

        // Return the combined HTML for messages and both tables
        return `
            <p>${formattedMessages}</p>
            ${instanceTableHtml}
            ${utilizationTableHtml}
        `;
    }
});
