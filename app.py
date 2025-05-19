import re
from flask import Flask, request, render_template_string

app = Flask(__name__)

def preprocess(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return " ".join(words)

def lcs(text1, text2):
    n, m = len(text1), len(text2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    lcs_str = []
    i, j = n, m
    while i > 0 and j > 0:
        if text1[i-1] == text2[j-1]:
            lcs_str.append(text1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    return dp[n][m], "".join(reversed(lcs_str))

def similarity_score(text1, text2):
    lcs_len, lcs_str = lcs(text1, text2)
    avg_len = (len(text1) + len(text2)) / 2
    score = (lcs_len / avg_len) * 100 if avg_len > 0 else 0
    return lcs_len, lcs_str, score

# Updated HTML template with Tailwind CSS and enhanced UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plagiarism Detection Tool</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            background-image: url('https://images.unsplash.com/photo-1557683316-973673baf926?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }
        .error-message { display: none; color: #ef4444; }
        .card { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="w-full max-w-3xl mx-auto p-6">
        <div class="card rounded-xl shadow-xl p-8 border border-gray-200">
            <h1 class="text-3xl font-bold text-center text-white mb-6">Plagiarism Detection Tool</h1>
            <form id="plagiarismForm" method="POST" class="space-y-4">
                <div>
                    <label for="text1" class="block text-sm font-medium text-white">Text 1</label>
                    <textarea id="text1" name="text1" class="mt-1 w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none resize-y" rows="4" placeholder="Enter first text" required>{{ text1 }}</textarea>
                    <p id="text1Error" class="error-message text-sm mt-1">Please enter text for Text 1</p>
                </div>
                <div>
                    <label for="text2" class="block text-sm font-medium text-white">Text 2</label>
                    <textarea id="text2" name="text2" class="mt-1 w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none resize-y" rows="4" placeholder="Enter second text" required>{{ text2 }}</textarea>
                    <p id="text2Error" class="error-message text-sm mt-1">Please enter text for Text 2</p>
                </div>
                <div class="flex space-x-4">
                    <button type="submit" class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 hover:scale-105 transition transform duration-200">Compare</button>
                    <button type="button" onclick="resetForm()" class="w-full bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 hover:scale-105 transition transform duration-200">Clear</button>
                </div>
            </form>
            {% if result %}
            <div class="mt-6 p-6 bg-white rounded-lg shadow-md">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Results</h2>
                <p class="text-gray-700"><strong>LCS Length:</strong> {{ result.lcs_len }}</p>
                <p class="text-gray-700"><strong>LCS:</strong> {{ result.lcs_str }}</p>
                <p class="text-gray-700"><strong>Similarity Score:</strong> {{ result.score|round(2) }}%</p>
            </div>
            {% endif %}
        </div>
    </div>
    <script>
        const form = document.getElementById('plagiarismForm');
        const text1 = document.getElementById('text1');
        const text2 = document.getElementById('text2');
        const text1Error = document.getElementById('text1Error');
        const text2Error = document.getElementById('text2Error');

        form.addEventListener('submit', (e) => {
            let valid = true;
            text1Error.style.display = 'none';
            text2Error.style.display = 'none';

            if (!text1.value.trim()) {
                text1Error.style.display = 'block';
                valid = false;
            }
            if (!text2.value.trim()) {
                text2Error.style.display = 'block';
                valid = false;
            }
            if (!valid) e.preventDefault();
        });

        function resetForm() {
            form.reset();
            text1Error.style.display = 'none';
            text2Error.style.display = 'none';
            window.location.href = '/';
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    text1 = text2 = ''
    result = None
    if request.method == 'POST':
        text1 = request.form['text1']
        text2 = request.form['text2']
        if text1.strip() and text2.strip():  # Server-side validation
            text1, text2 = preprocess(text1), preprocess(text2)
            lcs_len, lcs_str, score = similarity_score(text1, text2)
            result = {'lcs_len': lcs_len, 'lcs_str': lcs_str, 'score': score}
    return render_template_string(HTML_TEMPLATE, text1=text1, text2=text2, result=result)

if __name__ == '__main__':
    app.run(debug=True)
