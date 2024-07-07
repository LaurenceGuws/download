let eventSource;

export function initializeProgressEventSource() {
    if (eventSource) {
        eventSource.close();
    }
    eventSource = new EventSource('/download_progress');
    eventSource.onmessage = function(event) {
        const progresses = JSON.parse(event.data);
        updateProgressCards(progresses);
    };
}

function updateProgressCards(progresses) {
    for (const [id, progress] of Object.entries(progresses)) {
        let progressBar = document.getElementById(`${id}_progress`);
        let percentageText = document.getElementById(`${id}_percentage`);
        
        if (!progressBar) {
            // Create new progress card if it doesn't exist
            createProgressCard(id);
            progressBar = document.getElementById(`${id}_progress`);
            percentageText = document.getElementById(`${id}_percentage`);
        }

        if (progressBar && percentageText) {
            progressBar.style.width = `${progress}%`;
            percentageText.textContent = `${progress.toFixed(1)}%`;
        }
    }
}

function createProgressCard(id) {
    const progressCards = document.getElementById('progressCards');
    const progressCard = document.createElement('div');
    
    progressCard.classList.add('bg-light-purple', 'p-6', 'rounded-lg', 'shadow-md', 'neon-border', 'mb-4');
    progressCard.innerHTML = `
        <div class="text-sm font-medium text-gray-300 mb-1">Downloading: ${id}</div>
        <div class="w-full bg-gray-700 rounded-full h-2.5 mb-2">
            <div id="${id}_progress" class="bg-neon-purple h-2.5 rounded-full" style="width: 0%"></div>
        </div>
        <div id="${id}_percentage" class="text-xs font-medium text-gray-300">0%</div>
    `;

    progressCards.appendChild(progressCard);
}
