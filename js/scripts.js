document.getElementById('generate-btn').addEventListener('click', async () => {
    const numKeys = document.getElementById('num-keys').value;
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = 'Generating keys...';

    const response = await fetch('/.netlify/functions/generate-keys', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ num_keys: numKeys })
    });

    const data = await response.json();
    resultDiv.innerHTML = 'Generated Keys:<br>' + data.keys.join('<br>');
});
