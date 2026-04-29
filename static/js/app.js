const UPDATE_INTERVAL = document.body.dataset.updateInterval * 1000 || 5000;

async function updateStats() {
    try {
        const [cpuRes, ramRes] = await Promise.all([
            fetch('/api/hardware/cpu/usage'),
            fetch('/api/hardware/ram/usage')
        ]);

        const cpuData = await cpuRes.json();
        const ramData = await ramRes.json();

        updateDial('CPU', cpuData.usage);
        updateDial('RAM', ramData.usage);
    } catch(err) {
        console.error('Error updating statistics:', err);
    }
}

function updateDial(title, percentage) {
    const cards = document.querySelectorAll('.stat-card');
    cards.forEach(card => {
        if(card.querySelector('.stat-title').textContent === title) {
            const circle = card.querySelector('.progress-value');
            const dot = card.querySelector('.progress-dot');
            const text = card.querySelector('.progress-text');

            const radius = 45;
            const circumference = 282.74;
            const offset = circumference - (circumference * percentage / 100);

            circle.style.strokeDashoffset = offset;
            dot.style.transform = `rotate(${percentage * 3.6}deg) translate(45px)`;
            text.textContent = Math.round(percentage) + '%';
        }
    });
}

setInterval(updateStats, UPDATE_INTERVAL);
updateStats();
