// Ads Genius AI - Main JavaScript

document.addEventListener('DOMContentLoaded', async () => {
    let markedReady = false;

    // Function to load script and wait for it to be ready
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    try {
        // Load marked library first
        await loadScript('https://cdn.jsdelivr.net/npm/marked/marked.min.js');
        console.log('Marked library loaded');

        // Configure marked
        marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: false,
            mangle: false
        });
        markedReady = true;

        // Then load DOMPurify
        await loadScript('https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.9/purify.min.js');
        console.log('DOMPurify loaded');
    } catch (error) {
        console.error('Failed to load required libraries:', error);
    }

    // DOM Elements
    const inputText = document.getElementById('input-text');
    const temperatureInput = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    const maxTokensInput = document.getElementById('max-tokens');
    const generateBtn = document.getElementById('generate-btn');
    const resultsDiv = document.getElementById('results');
    const completionsList = document.getElementById('completions-list');
    const loadingDiv = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const charCounter = document.getElementById('char-counter');
    const themeToggle = document.getElementById('theme-toggle');
    const historyDiv = document.getElementById('history');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history');
    const topPInput = document.getElementById('top-p');
    const topPValue = document.getElementById('top-p-value');
    const topKInput = document.getElementById('top-k');
    const repetitionPenaltyInput = document.getElementById('repetition-penalty');
    const repetitionPenaltyValue = document.getElementById('repetition-penalty-value');
    const processingTime = document.getElementById('processing-time');
    const inputTokens = document.getElementById('input-tokens');
    const generatedTokens = document.getElementById('generated-tokens');
    const totalTokens = document.getElementById('total-tokens');
    const toggleAdvanced = document.getElementById('toggle-advanced');
    const advancedSettings = document.getElementById('advanced-settings');

    // Toggle advanced settings
    toggleAdvanced.addEventListener('click', () => {
        advancedSettings.classList.toggle('hidden');
        const isHidden = advancedSettings.classList.contains('hidden');
        toggleAdvanced.innerHTML = isHidden
            ? 'Show <i class="fas fa-chevron-down ml-1"></i>'
            : 'Hide <i class="fas fa-chevron-up ml-1"></i>';
    });

    // Theme handling
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    }

    themeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        localStorage.theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });

    // Character counter
    inputText.addEventListener('input', () => {
        const length = inputText.value.length;
        charCounter.textContent = `${length}/500`;
        if (length > 500) {
            charCounter.classList.add('text-red-500');
            inputText.value = inputText.value.slice(0, 500);
        } else {
            charCounter.classList.remove('text-red-500');
        }
    });

    temperatureInput.addEventListener('input', (e) => {
        temperatureValue.textContent = e.target.value;
    });

    topPInput.addEventListener('input', (e) => {
        topPValue.textContent = e.target.value;
    });

    repetitionPenaltyInput.addEventListener('input', (e) => {
        repetitionPenaltyValue.textContent = e.target.value;
    });

    function createCompletionCard(completion, isHistory = false) {
        if (!completion) {
            console.error("Received empty completion");
            return null;
        }

        console.log("Creating card for completion:", completion);

        const div = document.createElement('div');
        div.className = 'p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 relative group';

        const copyBtn = document.createElement('button');
        copyBtn.className = 'absolute top-2 right-2 p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 opacity-0 group-hover:opacity-100 transition-opacity duration-200';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.addEventListener('click', async () => {
            await navigator.clipboard.writeText(completion);
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });

        const textDiv = document.createElement('div');
        textDiv.className = 'pr-8 text-slate-900 dark:text-slate-100 completion-content';

        // Convert markdown to HTML using marked only if it's loaded
        if (markedReady) {
            // Clean up the text before converting to markdown
            const cleanedText = completion
                // Replace literal '\n' with actual newlines
                .replace(/\\n/g, '\n')
                // Replace multiple newlines with double newlines
                .replace(/\n{3,}/g, '\n\n')
                // Split into lines and process each
                .split('\n')
                .map(line => line.trim())  // Trim each line
                .filter(line => line.length > 0)  // Remove empty lines
                .join('\n');  // Join back with newlines

            // Convert single newlines to markdown line breaks
            const markdownText = cleanedText
                .replace(/(?<!\n)\n(?!\n)/g, '  \n');  // Add markdown line breaks for single newlines

            try {
                textDiv.innerHTML = DOMPurify.sanitize(marked.parse(markdownText));
            } catch (error) {
                console.error("Error parsing markdown:", error);
                textDiv.textContent = cleanedText;
            }
        } else {
            // Fallback to plain text if marked is not loaded
            textDiv.textContent = completion.replace(/\\n/g, '\n');
        }

        // Add some basic styling for markdown content
        const style = document.createElement('style');
        if (!document.querySelector('#completion-styles')) {
            style.id = 'completion-styles';
            style.textContent = `
                .completion-content p {
                    margin-bottom: 1rem;
                }
                .completion-content h1, .completion-content h2, .completion-content h3 {
                    margin-top: 1.5rem;
                    margin-bottom: 1rem;
                    font-weight: bold;
                }
                .completion-content ul, .completion-content ol {
                    margin-left: 1.5rem;
                    margin-bottom: 1rem;
                }
                .completion-content li {
                    margin-bottom: 0.5rem;
                }
                .completion-content strong {
                    font-weight: bold;
                }
                .completion-content em {
                    font-style: italic;
                }
                .completion-content code {
                    background-color: rgba(0, 0, 0, 0.05);
                    padding: 0.2em 0.4em;
                    border-radius: 3px;
                    font-family: monospace;
                }
                .completion-content pre code {
                    display: block;
                    padding: 1em;
                    overflow-x: auto;
                }
                #history-list {
                    max-height: 400px;
                    overflow-y: auto;
                    scrollbar-width: thin;
                    scrollbar-color: rgba(14, 165, 233, 0.5) transparent;
                }
                #history-list::-webkit-scrollbar {
                    width: 6px;
                }
                #history-list::-webkit-scrollbar-track {
                    background: transparent;
                }
                #history-list::-webkit-scrollbar-thumb {
                    background-color: rgba(14, 165, 233, 0.5);
                    border-radius: 3px;
                }
                #history-list::-webkit-scrollbar-thumb:hover {
                    background-color: rgba(14, 165, 233, 0.7);
                }
                .dark #history-list::-webkit-scrollbar-thumb {
                    background-color: rgba(14, 165, 233, 0.3);
                }
                .dark #history-list::-webkit-scrollbar-thumb:hover {
                    background-color: rgba(14, 165, 233, 0.5);
                }
            `;
            document.head.appendChild(style);
        }

        div.appendChild(copyBtn);
        div.appendChild(textDiv);
        return div;
    }

    // Function to safely parse JSON from localStorage
    function safeJSONParse(str, fallback = []) {
        try {
            const parsed = JSON.parse(str);
            return Array.isArray(parsed) ? parsed : fallback;
        } catch (e) {
            console.error("Error parsing JSON from localStorage:", e);
            return fallback;
        }
    }

    // Initialize completion history with safety check
    let completionHistory = safeJSONParse(localStorage.getItem('completionHistory'), []);
    if (!completionHistory) completionHistory = [];
    console.log("Initial history from localStorage:", completionHistory);

    function updateHistory() {
        // Ensure completionHistory is always an array
        if (!Array.isArray(completionHistory)) {
            console.error("Invalid completion history, resetting to empty array");
            completionHistory = [];
        }

        if (completionHistory.length > 0) {
            historyDiv.classList.remove('hidden');
            historyList.innerHTML = '';
            console.log("Updating history with:", completionHistory.slice(0, 5));
            completionHistory.slice(0, 5).forEach(completion => {
                const card = createCompletionCard(completion, true);
                if (card) {
                    historyList.appendChild(card);
                }
            });
        } else {
            historyDiv.classList.add('hidden');
        }
    }

    // Clear history functionality
    clearHistoryBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear your ad copy history?')) {
            completionHistory = [];
            localStorage.removeItem('completionHistory');
            historyDiv.classList.add('hidden');
            historyList.innerHTML = '';
        }
    });

    generateBtn.addEventListener('click', async () => {
        if (!inputText.value.trim()) {
            errorMessage.textContent = 'Please describe your product or service';
            errorMessage.classList.remove('hidden');
            return;
        }

        errorMessage.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        generateBtn.disabled = true;
        generateBtn.classList.add('opacity-50');

        const startTime = performance.now();

        // Get selected tone checkboxes
        const tones = [];
        document.querySelectorAll('input[id^="tone-"]:checked').forEach(checkbox => {
            tones.push(checkbox.id.replace('tone-', ''));
        });

        try {
            const response = await fetch('/api/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: inputText.value,
                    temperature: parseFloat(temperatureInput.value),
                    max_new_tokens: parseInt(maxTokensInput.value),
                    top_p: parseFloat(topPInput.value),
                    top_k: parseInt(topKInput.value),
                    repetition_penalty: parseFloat(repetitionPenaltyInput.value),
                    tones: tones
                }),
            });

            if (!response.ok) {
                throw new Error('Server responded with an error');
            }

            const data = await response.json();
            console.log("Raw API response:", data);
            const endTime = performance.now();

            completionsList.innerHTML = '';

            // Check if data is properly structured
            if (Array.isArray(data.completions) && data.completions.length > 0) {
                console.log("Completions array:", data.completions);
                data.completions.forEach(completion => {
                    if (completion) {
                        console.log("Individual completion:", completion);
                        const card = createCompletionCard(completion);
                        if (card) {
                            completionsList.appendChild(card);
                            // Ensure completionHistory is an array before unshift
                            if (!Array.isArray(completionHistory)) completionHistory = [];
                            completionHistory.unshift(completion);
                        }
                    }
                });
            } else if (typeof data.completions === 'string' && data.completions.trim()) {
                // Handle single completion
                const card = createCompletionCard(data.completions);
                if (card) {
                    completionsList.appendChild(card);
                    // Ensure completionHistory is an array before unshift
                    if (!Array.isArray(completionHistory)) completionHistory = [];
                    completionHistory.unshift(data.completions);
                }
            } else {
                throw new Error('Invalid response format or empty completion');
            }

            // Ensure completionHistory is an array before slice
            if (!Array.isArray(completionHistory)) completionHistory = [];
            completionHistory = completionHistory.slice(0, 10);

            // Store completions in localStorage with safety checks
            try {
                if (!Array.isArray(completionHistory)) completionHistory = [];
                localStorage.setItem('completionHistory', JSON.stringify(completionHistory));
            } catch (e) {
                console.error("Error storing completions in localStorage:", e);
                // If localStorage fails, try with a smaller history
                try {
                    const smallerHistory = completionHistory.slice(0, 3);
                    localStorage.setItem('completionHistory', JSON.stringify(smallerHistory));
                } catch (e2) {
                    console.error("Still failed with smaller history:", e2);
                    // Reset history if all else fails
                    completionHistory = [];
                    localStorage.removeItem('completionHistory');
                }
            }

            // Update metadata - handle both object and direct property formats
            processingTime.textContent = `${((endTime - startTime) / 1000).toFixed(2)}s`;
            const metadata = data.metadata || data;
            inputTokens.textContent = metadata.input_tokens || 'N/A';
            generatedTokens.textContent = metadata.output_tokens || 'N/A';
            totalTokens.textContent = (metadata.input_tokens && metadata.output_tokens)
                ? (metadata.input_tokens + metadata.output_tokens)
                : 'N/A';

            updateHistory();

            resultsDiv.classList.remove('hidden');
        } catch (error) {
            errorMessage.textContent = 'An error occurred while generating ad copy. Please try again.';
            errorMessage.classList.remove('hidden');
            console.error('Error:', error);
        } finally {
            loadingDiv.classList.add('hidden');
            generateBtn.disabled = false;
            generateBtn.classList.remove('opacity-50');
        }
    });

    // Initialize history on load
    updateHistory();
}); 