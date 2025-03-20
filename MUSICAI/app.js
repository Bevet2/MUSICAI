document.addEventListener('DOMContentLoaded', () => {
    // Initialize navigation
    const navButtons = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetPage = button.dataset.page;
            
            // Update button states
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update page visibility
            pages.forEach(page => {
                if (page.id === `${targetPage}Page`) {
                    page.classList.add('active');
                } else {
                    page.classList.remove('active');
                }
            });
        });
    });

    // Remix page functionality
    class RemixPage {
        constructor() {
            this.selectedTrack = null;
            this.selectedGenre = null;
            this.wavesurfer = null;
            this.currentAudioUrl = null;
            
            // Initialize elements
            this.elements = {
                searchInput: document.getElementById('searchInput'),
                searchResults: document.getElementById('searchResults'),
                genreButtons: document.querySelectorAll('.genre-btn'),
                remixButton: document.getElementById('remixButton'),
                remixWaveform: document.getElementById('remixWaveform'),
                loadingOverlay: document.getElementById('loadingOverlay')
            };
            
            this.initWaveSurfer();
            this.bindEvents();
        }
        
        initWaveSurfer() {
            this.wavesurfer = WaveSurfer.create({
                container: this.elements.remixWaveform,
                waveColor: '#818cf8',
                progressColor: '#4f46e5',
                cursorColor: '#6366f1',
                barWidth: 2,
                barRadius: 3,
                cursorWidth: 1,
                height: 100,
                barGap: 3
            });
        }
        
        bindEvents() {
            // Search with debounce
            let debounceTimeout;
            this.elements.searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimeout);
                debounceTimeout = setTimeout(() => this.handleSearch(), 500);
            });
            
            // Genre selection
            this.elements.genreButtons.forEach(button => {
                button.addEventListener('click', () => {
                    this.elements.genreButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    this.selectedGenre = button.dataset.genre;
                    this.updateRemixButton();
                });
            });
            
            // Remix button
            this.elements.remixButton.addEventListener('click', () => this.handleRemix());
            
            // Waveform controls
            const playButton = this.elements.remixWaveform.parentElement.querySelector('.play-button');
            const downloadButton = this.elements.remixWaveform.parentElement.querySelector('.download-button');
            
            playButton.addEventListener('click', () => {
                this.wavesurfer.playPause();
                playButton.textContent = this.wavesurfer.isPlaying() ? '⏸️' : '▶️';
            });
            
            downloadButton.addEventListener('click', () => {
                if (this.currentAudioUrl) {
                    const link = document.createElement('a');
                    link.href = this.currentAudioUrl;
                    link.download = 'remix.mp3';
                    link.click();
                }
            });
        }
        
        async handleSearch() {
            const query = this.elements.searchInput.value.trim();
            if (!query) {
                this.elements.searchResults.innerHTML = '';
                return;
            }
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, max_results: 5 })
                });
                
                const data = await response.json();
                this.displaySearchResults(data.results);
            } catch (error) {
                console.error('Search error:', error);
            }
        }
        
        displaySearchResults(results) {
            this.elements.searchResults.innerHTML = results.map(video => `
                <div class="search-result" data-video-id="${video.id}">
                    <img src="${video.thumbnail}" alt="${video.title}">
                    <div class="result-info">
                        <h3>${video.title}</h3>
                        <p>${video.channel}</p>
                    </div>
                </div>
            `).join('');
            
            // Add click handlers
            this.elements.searchResults.querySelectorAll('.search-result').forEach(result => {
                result.addEventListener('click', () => {
                    this.selectedTrack = result.dataset.videoId;
                    // Highlight selected
                    this.elements.searchResults.querySelectorAll('.search-result').forEach(r => 
                        r.classList.toggle('selected', r === result));
                    this.updateRemixButton();
                });
            });
        }
        
        updateRemixButton() {
            this.elements.remixButton.disabled = !(this.selectedTrack && this.selectedGenre);
        }
        
        async handleRemix() {
            if (!this.selectedTrack || !this.selectedGenre) return;
            
            this.elements.loadingOverlay.classList.add('active');
            
            try {
                const response = await fetch('/api/remix', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        video_id: this.selectedTrack,
                        genre: this.selectedGenre
                    })
                });
                
                const data = await response.json();
                this.currentAudioUrl = data.url;
                
                // Load and display waveform
                await this.wavesurfer.load(this.currentAudioUrl);
                this.elements.remixWaveform.parentElement.style.display = 'block';
                
            } catch (error) {
                console.error('Remix error:', error);
                alert('Failed to create remix. Please try again.');
            } finally {
                this.elements.loadingOverlay.classList.remove('active');
            }
        }
    }

    // Create page functionality
    class CreatePage {
        constructor() {
            this.uploadedFiles = [];
            this.wavesurfer = null;
            this.currentAudioUrl = null;
            
            this.elements = {
                fileInput: document.getElementById('fileInput'),
                uploadContainer: document.getElementById('uploadContainer'),
                uploadedFiles: document.getElementById('uploadedFiles'),
                mixSliders: document.getElementById('mixSliders'),
                lyricsInput: document.getElementById('lyricsInput'),
                voiceSelect: document.getElementById('voiceSelect'),
                createButton: document.getElementById('createButton'),
                createWaveform: document.getElementById('createWaveform')
            };
            
            this.initWaveSurfer();
            this.bindEvents();
        }
        
        initWaveSurfer() {
            this.wavesurfer = WaveSurfer.create({
                container: this.elements.createWaveform,
                waveColor: '#818cf8',
                progressColor: '#4f46e5',
                cursorColor: '#6366f1',
                barWidth: 2,
                barRadius: 3,
                cursorWidth: 1,
                height: 100,
                barGap: 3
            });
        }
        
        bindEvents() {
            // File upload
            this.elements.fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));
            
            // Drag and drop
            this.elements.uploadContainer.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.elements.uploadContainer.classList.add('dragover');
            });
            
            this.elements.uploadContainer.addEventListener('dragleave', () => {
                this.elements.uploadContainer.classList.remove('dragover');
            });
            
            this.elements.uploadContainer.addEventListener('drop', (e) => {
                e.preventDefault();
                this.elements.uploadContainer.classList.remove('dragover');
                this.handleFileUpload(e.dataTransfer.files);
            });
            
            // Create button
            this.elements.createButton.addEventListener('click', () => this.handleCreate());
            
            // Waveform controls
            const playButton = this.elements.createWaveform.parentElement.querySelector('.play-button');
            const downloadButton = this.elements.createWaveform.parentElement.querySelector('.download-button');
            
            playButton.addEventListener('click', () => {
                this.wavesurfer.playPause();
                playButton.textContent = this.wavesurfer.isPlaying() ? '⏸️' : '▶️';
            });
            
            downloadButton.addEventListener('click', () => {
                if (this.currentAudioUrl) {
                    const link = document.createElement('a');
                    link.href = this.currentAudioUrl;
                    link.download = 'creation.mp3';
                    link.click();
                }
            });
        }
        
        handleFileUpload(files) {
            Array.from(files).forEach(file => {
                if (file.type.startsWith('audio/')) {
                    this.uploadedFiles.push(file);
                }
            });
            
            this.updateUploadedFiles();
            this.updateMixControls();
            this.updateCreateButton();
        }
        
        updateUploadedFiles() {
            this.elements.uploadedFiles.innerHTML = this.uploadedFiles.map((file, index) => `
                <div class="uploaded-file">
                    <span>🎵 ${file.name}</span>
                    <button class="remove-file" data-index="${index}">✕</button>
                </div>
            `).join('');
            
            // Add remove handlers
            this.elements.uploadedFiles.querySelectorAll('.remove-file').forEach(button => {
                button.addEventListener('click', () => {
                    this.uploadedFiles.splice(button.dataset.index, 1);
                    this.updateUploadedFiles();
                    this.updateMixControls();
                    this.updateCreateButton();
                });
            });
        }
        
        updateMixControls() {
            this.elements.mixSliders.innerHTML = this.uploadedFiles.map((file, index) => `
                <div class="mix-slider">
                    <label>${file.name}</label>
                    <input type="range" min="0" max="100" value="50" class="track-volume" data-index="${index}">
                </div>
            `).join('');
        }
        
        updateCreateButton() {
            this.elements.createButton.disabled = this.uploadedFiles.length === 0;
        }
        
        async handleCreate() {
            if (this.uploadedFiles.length === 0) return;
            
            this.elements.loadingOverlay.classList.add('active');
            
            try {
                const formData = new FormData();
                this.uploadedFiles.forEach(file => formData.append('files', file));
                
                // Add mix ratios
                const mixRatios = Array.from(this.elements.mixSliders.querySelectorAll('.track-volume'))
                    .map(slider => parseInt(slider.value) / 100);
                formData.append('mix_ratios', JSON.stringify(mixRatios));
                
                // Add lyrics and voice style if provided
                const lyrics = this.elements.lyricsInput.value.trim();
                const voiceStyle = this.elements.voiceSelect.value;
                
                if (lyrics) {
                    formData.append('lyrics', lyrics);
                    formData.append('voice_style', voiceStyle);
                }
                
                const response = await fetch('/api/create', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                this.currentAudioUrl = data.url;
                
                // Load and display waveform
                await this.wavesurfer.load(this.currentAudioUrl);
                this.elements.createWaveform.parentElement.style.display = 'block';
                
            } catch (error) {
                console.error('Creation error:', error);
                alert('Failed to create track. Please try again.');
            } finally {
                this.elements.loadingOverlay.classList.remove('active');
            }
        }
    }

    // Initialize both pages
    const remixPage = new RemixPage();
    const createPage = new CreatePage();
});
