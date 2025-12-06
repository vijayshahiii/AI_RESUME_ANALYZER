// Analyze resume
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }

    const formData = new FormData();
    formData.append('resume', selectedFile);

    loadingState.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log(data); // just to check
    } catch (error) {
        console.error(error);
        alert('Error analyzing resume');
    }
});
