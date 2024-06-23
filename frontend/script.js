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
  
        const data = await response.json();
  
        // Build the table HTML
        let tableHtml = `<table class="table">`;
        tableHtml += `<tr><th>Metric</th><th>Value</th></tr>`;
  
        // Loop through table data and add rows
        for (const row of data.table_data) {
          tableHtml += `<tr><td>${row.Metric}</td><td>${row.Value}</td></tr>`;
        }
  
        tableHtml += `</table>`;
  
        // Display the message and table in the resultsDiv
        resultsDiv.innerHTML = `
          <p>${data.message}</p>
          ${tableHtml}
        `;
      } catch (error) {
        console.error('Error invoking Lambda:', error);
        resultsDiv.innerHTML = `<div>Error: ${error.message}</div>`;
      }
    });
  });
  