from flask import Flask, render_template_string, request, jsonify
import random
import httpx
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WARP+ Key Generator</title>
    <link rel="icon" href="https://www.cloudflare.com/favicon.ico" type="image/x-icon">
    <style>
        body {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #161b22;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            max-width: 500px;
            width: 100%;
            box-sizing: border-box;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
        }
        form {
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="number"] {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #30363d;
            background-color: #0d1117;
            color: #c9d1d9;
            font-size: 16px;
            box-sizing: border-box;
            -moz-appearance: textfield;
        }
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        button {
            background-color: #58a6ff;
            color: #0d1117;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            display: block;
            width: 100%;
            box-sizing: border-box;
            transition: background-color 0.3s;
        }
        button:disabled {
            background-color: #1f6feb;
            cursor: not-allowed;
        }
        #typingText {
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: bold;
            display: none;
        }
        #keyList {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .key-container {
            background-color: #0d1117;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
            width: 100%;
            box-sizing: border-box;
            cursor: pointer;
        }
        .key-info {
            white-space: pre-wrap;
            font-family: 'Courier New', Courier, monospace;
        }
        .data-allocated {
            font-weight: bold;
            color: #58a6ff;
        }
        .key {
            font-weight: bold;
            color: #c9d1d9;
        }
        .typing-animation {
            white-space: pre-wrap;
            display: inline-block;
            border-right: 2px solid #c9d1d9;
            overflow: hidden;
            animation: blink-caret 0.75s step-end infinite;
        }
        @keyframes blink-caret {
            from { border-color: transparent; }
            to { border-color: #c9d1d9; }
        }
        #copyNotification {
            display: none;
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #161b22;
            color: #58a6ff;
            padding: 10px 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            font-size: 16px;
            font-weight: bold;
            z-index: 1000;
            transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
        }
        #copyNotification.show {
            display: block;
            opacity: 1;
            transform: translate(-50%, 0);
        }
        @keyframes fade-in-out {
            0% {
                opacity: 0;
                transform: translate(-50%, -20px);
            }
            50% {
                opacity: 1;
                transform: translate(-50%, 0);
            }
            100% {
                opacity: 0;
                transform: translate(-50%, -20px);
            }
        }
        .fade-in-out {
            animation: fade-in-out 2s ease-in-out;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; color: #c9d1d9;">WARP+ Key Generator</h1>

        <form id="keyForm">
            <div class="form-group">
                <label for="num_keys">Enter the desired number of keys:</label>
                <input type="number" id="num_keys" name="num_keys" required>
            </div>
            <button type="submit">Generate</button>
        </form>
        <div id="typingText" class="typing-animation"></div>
        <ul id="keyList"></ul>
    </div>
    <div id="copyNotification">Key copied!</div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const typingTextElement = document.getElementById('typingText');
            const generateButton = document.querySelector('button[type="submit"]');

            const typeText = (text, element, delay = 100) => {
                element.textContent = '';
                let index = 0;
                return new Promise(resolve => {
                    const interval = setInterval(() => {
                        element.textContent += text[index];
                        index++;
                        if (index === text.length) {
                            clearInterval(interval);
                            resolve();
                        }
                    }, delay);
                });
            };

            document.getElementById('keyForm').addEventListener('submit', async (event) => {
                event.preventDefault();
                const numKeys = parseInt(document.getElementById('num_keys').value);
                const keyList = document.getElementById('keyList');
                const copyNotification = document.getElementById('copyNotification');

                keyList.innerHTML = '';
                generateButton.disabled = true;
                typingTextElement.style.display = 'inline-block';

                await typeText('Generating keys...', typingTextElement, 100);

                try {
                    const response = await fetch('/api/generate_keys', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ num_keys: numKeys })
                    });

                    const data = await response.json();

                    data.gkeys.forEach((keyInfo, index) => {
                        setTimeout(() => {
                            const listItem = document.createElement('li');
                            listItem.className = 'key-container';

                            const keyInfoElement = document.createElement('div');
                            keyInfoElement.className = 'key-info';
                            const text = `Data Allocated: ${keyInfo.referral_count} GB\nKey: ${keyInfo.license}`;

                            keyInfoElement.classList.add('typing-animation');
                            listItem.appendChild(keyInfoElement);

                            const typeTextKey = async (text, element, delay = 0.05) => {
                                return new Promise(resolve => {
                                    let index = 0;
                                    const interval = setInterval(() => {
                                        element.textContent += text[index];
                                        index++;
                                        if (index === text.length) {
                                            clearInterval(interval);
                                            element.classList.remove('typing-animation');
                                            resolve();
                                        }
                                    }, delay * 1000);
                                });
                            };

                            typeTextKey(text, keyInfoElement).then(() => {
                                listItem.addEventListener('click', () => {
                                    const tempInput = document.createElement('input');
                                    tempInput.value = keyInfo.license;
                                    document.body.appendChild(tempInput);
                                    tempInput.select();
                                    document.execCommand('copy');
                                    document.body.removeChild(tempInput);
                                    copyNotification.classList.add('show', 'fade-in-out');
                                    setTimeout(() => {
                                        copyNotification.classList.remove('show', 'fade-in-out');
                                    }, 2000);
                                });
                            });

                            keyList.appendChild(listItem);
                        }, index * 500);
                    });
                } catch (error) {
                    console.error('Error:', error);
                } finally {
                    typingTextElement.style.display = 'none';
                    generateButton.disabled = false;
                }
            });
        });
    </script>
</body>
</html>
"""

def load_keys():
    if os.path.exists('base.txt'):
        with open('base.txt', 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def save_keys(new_keys):
    keys = load_keys()
    with open('base.txt', 'a') as f:
        for key in new_keys:
            f.write(f"\n{key}")

    if len(keys) + len(new_keys) > 100:
        keys.extend(new_keys)
        with open('base.txt', 'w') as f:
            for key in keys[-100:]: 
                f.write(f"\n{key}")

def generate_keys(num_keys):
    headers = {
        "CF-Client-Version": "a-6.11-2223",
        "Host": "api.cloudflareclient.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.12.1",
    }
    
    keys = load_keys()
    new_keys = []
    gkeys = []

    for _ in range(num_keys):
        try:
            with httpx.Client(base_url="https://api.cloudflareclient.com/v0a2223", headers=headers, timeout=30.0) as client:
                r = client.post("/reg")
                id = r.json()["id"]
                license = r.json()["account"]["license"]
                token = r.json()["token"]

                r = client.post("/reg")
                id2 = r.json()["id"]
                token2 = r.json()["token"]

                headers_get = {"Authorization": f"Bearer {token}"}
                headers_get2 = {"Authorization": f"Bearer {token2}"}
                headers_post = {"Content-Type": "application/json; charset=UTF-8", "Authorization": f"Bearer {token}"}

                json = {"referrer": f"{id2}"}
                client.patch(f"/reg/{id}", headers=headers_post, json=json)
                client.delete(f"/reg/{id2}", headers=headers_get2)

                key = random.choice(keys)
                json = {"license": f"{key}"}
                client.put(f"/reg/{id}/account", headers=headers_post, json=json)
                json = {"license": f"{license}"}
                client.put(f"/reg/{id}/account", headers=headers_post, json=json)

                r = client.get(f"/reg/{id}/account", headers=headers_get)
                referral_count = r.json()["referral_count"]
                license = r.json()["license"]

                client.delete(f"/reg/{id}", headers=headers_get)

                new_key_info = {
                    'referral_count': referral_count,
                    'license': license
                }
                gkeys.append(new_key_info)
                new_keys.append(license)
                print(f"Generated key: {license}")
                print(f"Data Allocated: {referral_count} GB")

        except Exception as e:
            print(f"Error generating key: {e}")

    save_keys(new_keys)
    return gkeys

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate_keys', methods=['POST'])
def api_generate_keys():
    num_keys = int(request.json.get('num_keys', 0))
    gkeys = generate_keys(num_keys)
    return jsonify({'gkeys': gkeys})

if __name__ == '__main__':
    app.run(debug=True)
