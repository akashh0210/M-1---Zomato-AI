document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendation-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    
    const locationSelect = document.getElementById('location');
    
    // Fetch locations
    fetch('/locations')
        .then(res => res.json())
        .then(data => {
            if (data.locations && data.locations.length > 0) {
                locationSelect.innerHTML = '<option value="" disabled selected>Select a locality</option>';
                data.locations.forEach(loc => {
                    const opt = document.createElement('option');
                    opt.value = loc;
                    opt.textContent = loc;
                    locationSelect.appendChild(opt);
                });
            } else {
                locationSelect.innerHTML = '<option value="" disabled selected>No locations found</option>';
            }
        })
        .catch(err => {
            locationSelect.innerHTML = '<option value="" disabled selected>Error loading locations</option>';
        });
    
    const resultsSection = document.getElementById('results-section');
    const messageBanner = document.getElementById('message-banner');
    const cardsContainer = document.getElementById('cards-container');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI loading state
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        
        // Hide previous results
        resultsSection.classList.add('hidden');
        messageBanner.className = 'message-banner'; // reset class
        cardsContainer.innerHTML = '';

        const payload = {
            location: document.getElementById('location').value,
            cuisine: document.getElementById('cuisine').value,
            budget: parseFloat(document.getElementById('budget').value),
            min_rating: parseFloat(document.getElementById('min_rating').value)
        };

        try {
            const response = await fetch('/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail?.message || data.detail || 'An error occurred server-side.');
            }

            renderResults(data);

        } catch (error) {
            messageBanner.textContent = error.message;
            messageBanner.classList.add('error');
            resultsSection.classList.remove('hidden');
        } finally {
            // Restore button state
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    function renderResults(data) {
        // Display message
        if (data.message) {
            messageBanner.textContent = data.message;
            if (data.recommendations && data.recommendations.length === 0) {
                messageBanner.classList.add('error');
            }
        } else {
            messageBanner.textContent = "Here are your recommendations!";
        }

        // Display suggestions (Fallback)
        if (data.suggestions && data.suggestions.length > 0) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.style.textAlign = 'center';
            suggestionsDiv.style.marginBottom = '2rem';
            
            data.suggestions.forEach(suggestion => {
                const pill = document.createElement('span');
                pill.className = 'suggestion-pill';
                pill.textContent = suggestion;
                pill.onclick = () => {
                    // Try to guess if it's a location or cuisine based on the context of the error
                    if(data.message && data.message.toLowerCase().includes('location')) {
                        document.getElementById('location').value = suggestion;
                    } else {
                        document.getElementById('cuisine').value = suggestion;
                    }
                    setTimeout(() => form.dispatchEvent(new Event('submit')), 100);
                };
                suggestionsDiv.appendChild(pill);
            });
            messageBanner.parentElement.insertBefore(suggestionsDiv, cardsContainer);
        } else {
            // cleanup any previous suggestions attached before cardsContainer
            const prev = cardsContainer.previousElementSibling;
            if (prev && prev !== messageBanner) {
                prev.remove();
            }
        }

        // Render cards
        if (data.recommendations) {
            data.recommendations.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = `card stagger-${Math.min(index + 1, 5)}`;
                
                card.innerHTML = `
                    <div class="card-rank">#${item.rank}</div>
                    <h3 class="card-title">${item.restaurant_name}</h3>
                    <div class="card-meta">
                        <span class="badge rating">★ ${item.rating.toFixed(1)}</span>
                        <span class="badge">${item.cuisines.slice(0, 2).join(', ')}</span>
                        <span>₹${item.estimated_cost_for_two} for two</span>
                    </div>
                    <p class="card-explanation">${item.explanation}</p>
                    <div class="card-confidence">AI Confidence: ${Math.round(item.confidence * 100)}%</div>
                `;
                cardsContainer.appendChild(card);
            });
        }

        resultsSection.classList.remove('hidden');
        
        // Scroll into view
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
});
