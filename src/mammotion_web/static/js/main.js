// Mammotion Web - Main JavaScript Module

class MammotionWeb {
    constructor() {
        this.wsConnection = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.statusUpdateInterval = null;
        
        this.init();
    }
    
    init() {
        console.log('Mammotion Web initializing...');
        
        // Initialize WebSocket connection
        this.initWebSocket();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start periodic status updates
        this.startStatusUpdates();
        
        // Initialize UI components
        this.initializeUI();
        
        console.log('Mammotion Web initialized successfully');
    }
    
    initWebSocket() {
        if (!window.location.pathname.includes('/devices')) {
            return; // Only connect WebSocket on devices page
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.wsConnection = new WebSocket(wsUrl);
            
            this.wsConnection.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.showConnectionStatus('connected');
            };
            
            this.wsConnection.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.wsConnection.onclose = () => {
                console.log('WebSocket disconnected');
                this.showConnectionStatus('disconnected');
                this.scheduleReconnect();
            };
            
            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'device_status':
                this.updateDeviceStatus(data.device_id, data.status);
                break;
            case 'device_list':
                this.updateDeviceList(data.devices);
                break;
            case 'command_result':
                this.handleCommandResult(data);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.showConnectionStatus('failed');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.initWebSocket();
        }, delay);
    }
    
    showConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;
        
        statusElement.className = `status status-${status}`;
        
        const messages = {
            connected: 'Online',
            disconnected: 'Reconnecting...',
            error: 'Connection Error',
            failed: 'Connection Failed'
        };
        
        statusElement.textContent = messages[status] || status;
    }
    
    setupEventListeners() {
        // Device command buttons
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-command]')) {
                event.preventDefault();
                const deviceId = event.target.dataset.deviceId;
                const command = event.target.dataset.command;
                this.sendDeviceCommand(deviceId, command, event.target);
            }
        });
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-devices');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshDevices();
            });
        }
        
        // Logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (event) => {
                event.preventDefault();
                this.logout();
            });
        }
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (event) => {
                if (event.target.checked) {
                    this.startStatusUpdates();
                } else {
                    this.stopStatusUpdates();
                }
            });
        }
    }
    
    async sendDeviceCommand(deviceId, command, buttonElement) {
        if (!deviceId || !command) {
            console.error('Missing device ID or command');
            return;
        }
        
        // Show loading state
        const originalText = buttonElement.textContent;
        const originalDisabled = buttonElement.disabled;
        
        buttonElement.disabled = true;
        buttonElement.innerHTML = '<span class="loading"></span> Sending...';
        
        try {
            const response = await fetch(`/devices/${deviceId}/commands`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command })
            });
            
            if (response.ok) {
                this.showNotification(`Command "${command}" sent successfully`, 'success');
                // Refresh device status after command
                setTimeout(() => this.refreshDeviceStatus(deviceId), 1000);
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Command failed');
            }
            
        } catch (error) {
            console.error('Command failed:', error);
            this.showNotification(`Command failed: ${error.message}`, 'error');
        } finally {
            // Restore button state
            buttonElement.disabled = originalDisabled;
            buttonElement.textContent = originalText;
        }
    }
    
    async refreshDevices() {
        const refreshBtn = document.getElementById('refresh-devices');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<span class="loading"></span> Refreshing...';
        }
        
        try {
            const response = await fetch('/devices');
            if (response.ok) {
                // Reload the page to get fresh device data
                window.location.reload();
            } else {
                throw new Error('Failed to refresh devices');
            }
        } catch (error) {
            console.error('Refresh failed:', error);
            this.showNotification('Failed to refresh devices', 'error');
        } finally {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = 'Refresh';
            }
        }
    }
    
    async refreshDeviceStatus(deviceId) {
        try {
            const response = await fetch(`/devices/${deviceId}`);
            if (response.ok) {
                const status = await response.json();
                this.updateDeviceStatus(deviceId, status);
            }
        } catch (error) {
            console.error('Failed to refresh device status:', error);
        }
    }
    
    updateDeviceStatus(deviceId, status) {
        const deviceCard = document.querySelector(`[data-device-id="${deviceId}"]`);
        if (!deviceCard) return;
        
        // Update battery level
        const batteryElement = deviceCard.querySelector('.battery-level');
        if (batteryElement && status.battery !== null) {
            batteryElement.textContent = `${status.battery}%`;
            
            const progressBar = deviceCard.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${status.battery}%`;
            }
        }
        
        // Update status
        const statusElement = deviceCard.querySelector('.device-status');
        if (statusElement && status.status) {
            statusElement.textContent = status.status;
            statusElement.className = `status status-${this.getStatusClass(status.status)}`;
        }
        
        // Update last updated time
        const updatedElement = deviceCard.querySelector('.last-updated');
        if (updatedElement) {
            updatedElement.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
        }
        
        // Update online status
        if (status.online !== undefined) {
            const onlineIndicator = deviceCard.querySelector('.online-indicator');
            if (onlineIndicator) {
                onlineIndicator.className = `status ${status.online ? 'status-online' : 'status-offline'}`;
                onlineIndicator.textContent = status.online ? 'Online' : 'Offline';
            }
        }
    }
    
    updateDeviceList(devices) {
        // This would be used for real-time device list updates
        console.log('Device list updated:', devices);
    }
    
    handleCommandResult(data) {
        const message = data.success ? 
            `Command "${data.command}" completed successfully` :
            `Command "${data.command}" failed: ${data.error}`;
        
        this.showNotification(message, data.success ? 'success' : 'error');
    }
    
    getStatusClass(status) {
        const statusMap = {
            'online': 'online',
            'mowing': 'online',
            'charging': 'charging',
            'returning': 'warning',
            'paused': 'warning',
            'offline': 'offline',
            'error': 'error',
            'unknown': 'offline'
        };
        
        return statusMap[status.toLowerCase()] || 'offline';
    }
    
    startStatusUpdates() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        
        // Get update interval from page data or default to 15 seconds
        const pollInterval = parseInt(document.body.dataset.pollInterval || '15') * 1000;
        
        this.statusUpdateInterval = setInterval(() => {
            this.updateAllDeviceStatuses();
        }, pollInterval);
    }
    
    stopStatusUpdates() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
            this.statusUpdateInterval = null;
        }
    }
    
    async updateAllDeviceStatuses() {
        const deviceCards = document.querySelectorAll('[data-device-id]');
        
        for (const card of deviceCards) {
            const deviceId = card.dataset.deviceId;
            if (deviceId) {
                await this.refreshDeviceStatus(deviceId);
            }
        }
    }
    
    initializeUI() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize modals
        this.initModals();
        
        // Initialize form validation
        this.initFormValidation();
        
        // Set initial theme
        this.initTheme();
    }
    
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    }
    
    showTooltip(event) {
        const text = event.target.dataset.tooltip;
        if (!text) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.id = 'active-tooltip';
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
    }
    
    hideTooltip() {
        const tooltip = document.getElementById('active-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
    
    initModals() {
        // Modal functionality would go here
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-modal-trigger]')) {
                const modalId = event.target.dataset.modalTrigger;
                this.openModal(modalId);
            }
            
            if (event.target.matches('.modal-close') || event.target.matches('.modal-backdrop')) {
                this.closeModal();
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeModal();
            }
        });
    }
    
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    closeModal() {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            activeModal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', this.validateForm.bind(this));
        });
    }
    
    validateForm(event) {
        const form = event.target;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        if (!isValid) {
            event.preventDefault();
        }
    }
    
    showFieldError(input, message) {
        input.classList.add('error');
        
        let errorElement = input.parentNode.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            input.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
    }
    
    clearFieldError(input) {
        input.classList.remove('error');
        
        const errorElement = input.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    initTheme() {
        // Theme switching would go here if needed
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // Add to notification container or create one
        let container = document.getElementById('notifications');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications';
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
    
    async logout() {
        try {
            const response = await fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                window.location.href = '/';
            } else {
                throw new Error('Logout failed');
            }
        } catch (error) {
            console.error('Logout error:', error);
            this.showNotification('Logout failed', 'error');
        }
    }
    
    // Cleanup method
    destroy() {
        if (this.wsConnection) {
            this.wsConnection.close();
        }
        
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        
        // Remove event listeners
        document.removeEventListener('click', this.handleClick);
        document.removeEventListener('keydown', this.handleKeydown);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mammotionWeb = new MammotionWeb();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.mammotionWeb) {
        window.mammotionWeb.destroy();
    }
});
