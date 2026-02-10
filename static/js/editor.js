/**
 * 360 Tour Editor JavaScript
 * Manages scene uploads, hotspots, and Pannellum integration
 * Includes solutions for coordinate drift and grey screen issues
 */

class SceneManager {
    constructor(propertyId) {
        this.propertyId = propertyId;
        this.scenes = [];
        this.currentScene = null;
        this.viewer = null;
        this.hotspots = [];
        this.addingHotspot = false;
        this.pendingHotspot = null;
        
        this.init();
    }
    
    init() {
        // Load existing scenes from property data
        if (window.propertyData && window.propertyData.tour && window.propertyData.tour.scenes) {
            this.scenes = window.propertyData.tour.scenes;
            this.hotspots = window.propertyData.tour.hotspots || [];
        }
        
        this.renderSceneList();
        this.setupEventListeners();
        
        // Load first scene if available
        if (this.scenes.length > 0) {
            this.loadScene(this.scenes[0].id);
        }
    }
    
    setupEventListeners() {
        const self = this;
        
        // File input change
        document.getElementById('sceneInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });
        
        // Upload area click
        document.getElementById('uploadArea').addEventListener('click', () => {
            document.getElementById('sceneInput').click();
        });
        
        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragging');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragging');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragging');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });
        
        // Add hotspot button
        document.getElementById('addHotspotBtn').addEventListener('click', () => {
            this.startAddingHotspot();
        });
        
        // Save hotspots button
        document.getElementById('saveHotspotsBtn').addEventListener('click', () => {
            this.saveHotspots();
        });
        
        // Confirm hotspot in modal
        document.getElementById('confirmHotspotBtn').addEventListener('click', () => {
            this.confirmHotspot();
        });
        
        // Publish button
        document.getElementById('publishBtn').addEventListener('click', () => {
            this.publishTour();
        });
        
        // Fix grey screen issue - Re-initialize viewer when modal is shown
        const hotspotModal = document.getElementById('hotspotModal');
        hotspotModal.addEventListener('shown.bs.modal', () => {
            if (this.viewer) {
                // Force viewer resize to prevent grey screen
                setTimeout(() => {
                    if (this.viewer && typeof this.viewer.resize === 'function') {
                        this.viewer.resize();
                    }
                }, 100);
            }
        });
    }
    
    async handleFileSelect(file) {
        // Validate file
        if (!file.type.match('image/jpeg') && !file.type.match('image/jpg') && !file.type.match('image/png')) {
            alert('Sadece JPG ve PNG dosyaları desteklenir.');
            return;
        }
        
        if (file.size > 16 * 1024 * 1024) {
            alert('Dosya boyutu 16MB\'dan büyük olamaz.');
            return;
        }
        
        // Show loading modal
        this.showLoading('Resim işleniyor...');
        this.updateProgress(10);
        
        try {
            // Process image on client-side (compress if needed)
            const processedBlob = await this.processImage(file);
            this.updateProgress(50);
            
            // Get scene name
            const sceneName = prompt('Sahne adı giriniz:', this.generateSceneName());
            if (!sceneName) {
                this.hideLoading();
                return;
            }
            
            // Upload to server
            await this.uploadScene(processedBlob, sceneName);
            this.updateProgress(100);
            
            setTimeout(() => {
                this.hideLoading();
            }, 500);
            
        } catch (error) {
            console.error('File processing error:', error);
            alert('Dosya işlenirken hata oluştu: ' + error.message);
            this.hideLoading();
        }
    }
    
    async processImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = new Image();
                
                img.onload = () => {
                    try {
                        // Max dimension 8192px (for 360 images)
                        const maxDimension = 8192;
                        let width = img.width;
                        let height = img.height;
                        
                        // Calculate new dimensions if needed
                        if (width > maxDimension || height > maxDimension) {
                            if (width > height) {
                                height = Math.round(height * (maxDimension / width));
                                width = maxDimension;
                            } else {
                                width = Math.round(width * (maxDimension / height));
                                height = maxDimension;
                            }
                        }
                        
                        // Create canvas
                        const canvas = document.createElement('canvas');
                        canvas.width = width;
                        canvas.height = height;
                        
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, width, height);
                        
                        // Convert to blob with compression
                        canvas.toBlob((blob) => {
                            if (blob) {
                                resolve(blob);
                            } else {
                                reject(new Error('Canvas to blob conversion failed'));
                            }
                        }, 'image/jpeg', 0.9);
                        
                    } catch (error) {
                        reject(error);
                    }
                };
                
                img.onerror = () => {
                    reject(new Error('Image load failed'));
                };
                
                img.src = e.target.result;
            };
            
            reader.onerror = () => {
                reject(new Error('File read failed'));
            };
            
            reader.readAsDataURL(file);
        });
    }
    
    async uploadScene(blob, sceneName) {
        const formData = new FormData();
        formData.append('image', blob, 'scene.jpg');
        formData.append('name', sceneName);
        
        try {
            const response = await fetch(`/tour/api/upload-scene/${this.propertyId}`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.scenes.push(result.scene);
                this.renderSceneList();
                this.loadScene(result.scene.id);
                
                // Show success message
                this.showToast('Sahne başarıyla yüklendi!', 'success');
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            throw error;
        }
    }
    
    renderSceneList() {
        const sceneList = document.getElementById('sceneList');
        const sceneCount = document.getElementById('sceneCount');
        const noScenesAlert = document.getElementById('noScenesAlert');
        
        sceneCount.textContent = this.scenes.length;
        
        if (this.scenes.length === 0) {
            sceneList.innerHTML = '';
            noScenesAlert.style.display = 'block';
            return;
        }
        
        noScenesAlert.style.display = 'none';
        
        sceneList.innerHTML = this.scenes.map(scene => `
            <div class="scene-item ${this.currentScene && this.currentScene.id === scene.id ? 'active' : ''}" 
                 data-scene-id="${scene.id}"
                 onclick="sceneManager.loadScene('${scene.id}')">
                <img src="/static/uploads/tours/${this.propertyId}/${scene.thumbnail}" 
                     class="scene-thumbnail" 
                     alt="${scene.name}">
                <div class="d-flex justify-content-between align-items-center">
                    <strong class="small">${scene.name}</strong>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="event.stopPropagation(); sceneManager.deleteScene('${scene.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <small class="text-muted">${this.formatFileSize(scene.size)}</small>
            </div>
        `).join('');
    }
    
    loadScene(sceneId) {
        const scene = this.scenes.find(s => s.id === sceneId);
        if (!scene) return;
        
        this.currentScene = scene;
        
        // Update UI
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('viewerSection').style.display = 'block';
        document.getElementById('currentSceneName').textContent = scene.name;
        document.getElementById('currentSceneSize').textContent = 
            `${scene.width}x${scene.height} (${this.formatFileSize(scene.size)})`;
        
        // Update scene list active state
        document.querySelectorAll('.scene-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-scene-id="${sceneId}"]`)?.classList.add('active');
        
        // Initialize or update Pannellum viewer
        this.initViewer(scene);
    }
    
    initViewer(scene) {
        const container = document.getElementById('pannellum-container');
        
        // Destroy existing viewer
        if (this.viewer) {
            try {
                this.viewer.destroy();
            } catch (e) {
                console.warn('Error destroying viewer:', e);
            }
        }
        
        // Get hotspots for this scene
        const sceneHotspots = this.hotspots.filter(h => h.sceneId === scene.id);
        
        // Initialize Pannellum
        this.viewer = pannellum.viewer(container, {
            type: 'equirectangular',
            panorama: `/static/uploads/tours/${this.propertyId}/${scene.filename}`,
            autoLoad: true,
            showControls: true,
            mouseZoom: true,
            hotSpots: sceneHotspots.map(h => ({
                pitch: h.pitch,
                yaw: h.yaw,
                type: 'scene',
                text: h.text,
                sceneId: h.targetSceneId,
                cssClass: 'custom-hotspot'
            }))
        });
        
        // Add click handler for adding hotspots - FIX for coordinate drift
        this.viewer.on('mousedown', (event) => {
            if (this.addingHotspot && event) {
                // Use mouseEventToCoords to fix coordinate drift issue
                const coords = this.viewer.mouseEventToCoords(event);
                this.pendingHotspot = {
                    pitch: coords[0],
                    yaw: coords[1]
                };
                
                // Show hotspot modal
                this.showHotspotModal();
                this.addingHotspot = false;
                
                // Update button state
                document.getElementById('addHotspotBtn').classList.remove('active');
            }
        });
    }
    
    startAddingHotspot() {
        if (!this.currentScene) {
            alert('Önce bir sahne seçiniz.');
            return;
        }
        
        this.addingHotspot = true;
        document.getElementById('addHotspotBtn').classList.add('active');
        
        alert('360° görüntüde hotspot eklemek istediğiniz noktaya tıklayın.');
    }
    
    showHotspotModal() {
        // Populate target scene options
        const select = document.getElementById('hotspotTargetScene');
        select.innerHTML = '<option value="">Sahne seçiniz...</option>' + 
            this.scenes
                .filter(s => s.id !== this.currentScene.id)
                .map(s => `<option value="${s.id}">${s.name}</option>`)
                .join('');
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('hotspotModal'));
        modal.show();
    }
    
    confirmHotspot() {
        const targetSceneId = document.getElementById('hotspotTargetScene').value;
        const text = document.getElementById('hotspotText').value;
        
        if (!targetSceneId) {
            alert('Lütfen hedef sahne seçiniz.');
            return;
        }
        
        const targetScene = this.scenes.find(s => s.id === targetSceneId);
        
        // Add hotspot
        const hotspot = {
            id: this.generateId(),
            sceneId: this.currentScene.id,
            targetSceneId: targetSceneId,
            pitch: this.pendingHotspot.pitch,
            yaw: this.pendingHotspot.yaw,
            text: text || targetScene.name
        };
        
        this.hotspots.push(hotspot);
        
        // Reload viewer to show new hotspot
        this.loadScene(this.currentScene.id);
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('hotspotModal')).hide();
        
        // Clear inputs
        document.getElementById('hotspotTargetScene').value = '';
        document.getElementById('hotspotText').value = '';
        
        this.showToast('Hotspot eklendi. Kaydetmeyi unutmayın!', 'info');
    }
    
    async saveHotspots() {
        if (this.hotspots.length === 0) {
            alert('Kaydedilecek hotspot bulunmamaktadır.');
            return;
        }
        
        try {
            const response = await fetch(`/tour/api/save-hotspots/${this.propertyId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.hotspots)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Hotspotlar kaydedildi!', 'success');
            } else {
                alert('Hotspot kaydetme hatası: ' + result.error);
            }
        } catch (error) {
            console.error('Save hotspots error:', error);
            alert('Hotspot kaydetme hatası: ' + error.message);
        }
    }
    
    async deleteScene(sceneId) {
        if (!confirm('Bu sahneyi silmek istediğinizden emin misiniz?')) {
            return;
        }
        
        try {
            const response = await fetch(`/tour/api/delete-scene/${this.propertyId}/${sceneId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Remove scene from list
                this.scenes = this.scenes.filter(s => s.id !== sceneId);
                
                // Remove hotspots related to this scene
                this.hotspots = this.hotspots.filter(h => 
                    h.sceneId !== sceneId && h.targetSceneId !== sceneId
                );
                
                // Update UI
                this.renderSceneList();
                
                if (this.currentScene && this.currentScene.id === sceneId) {
                    if (this.scenes.length > 0) {
                        this.loadScene(this.scenes[0].id);
                    } else {
                        document.getElementById('viewerSection').style.display = 'none';
                        document.getElementById('uploadArea').style.display = 'block';
                        this.currentScene = null;
                    }
                }
                
                this.showToast('Sahne silindi', 'success');
            } else {
                alert('Sahne silme hatası: ' + result.error);
            }
        } catch (error) {
            console.error('Delete scene error:', error);
            alert('Sahne silme hatası: ' + error.message);
        }
    }
    
    async publishTour() {
        if (this.scenes.length === 0) {
            alert('Yayınlamak için en az 1 sahne eklemelisiniz.');
            return;
        }
        
        if (!confirm('İlanı yayınlamak istediğinizden emin misiniz?')) {
            return;
        }
        
        try {
            const response = await fetch(`/tour/api/publish/${this.propertyId}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('İlan başarıyla yayınlandı!');
                if (result.redirect) {
                    window.location.href = result.redirect;
                }
            } else {
                alert('Yayınlama hatası: ' + result.error);
            }
        } catch (error) {
            console.error('Publish error:', error);
            alert('Yayınlama hatası: ' + error.message);
        }
    }
    
    // Helper functions
    generateSceneName() {
        const defaultNames = ['Salon', 'Yatak Odası', 'Mutfak', 'Banyo', 'Balkon', 'Koridor'];
        const usedNames = this.scenes.map(s => s.name);
        
        for (const name of defaultNames) {
            if (!usedNames.includes(name)) {
                return name;
            }
        }
        
        return `Sahne ${this.scenes.length + 1}`;
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    showLoading(message) {
        document.getElementById('loadingMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }
    
    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }
    
    updateProgress(percent) {
        const progressBar = document.getElementById('uploadProgress');
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
    }
    
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize SceneManager when DOM is ready
let sceneManager;
document.addEventListener('DOMContentLoaded', () => {
    const propertyId = document.getElementById('propertyId').value;
    sceneManager = new SceneManager(propertyId);
});
