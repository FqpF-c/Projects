// static/js/dressing-room.js
document.addEventListener('DOMContentLoaded', function() {
    // Store selected items with position, scale, and rotation information
    const selectedItems = {
        tops: null,
        bottoms: null,
        outerwear: null,
        accessories: []
    };

    // Track active (currently being manipulated) item
    let activeItem = null;

    // Initial UI setup
    setupUI();

    // Handle clothing item selection
    const clothingItems = document.querySelectorAll('.clothing-item');
    clothingItems.forEach(item => {
        item.addEventListener('click', function() {
            const itemId = this.dataset.id;
            const category = this.dataset.category;
            const imageUrl = this.dataset.image;
            
            // Visual feedback on click
            animateClick(this);
            
            // Handle selection logic based on category
            if (category === 'accessories') {
                // Accessories: multiple selection allowed
                if (this.classList.contains('selected')) {
                    // Deselect
                    this.classList.remove('selected');
                    const index = selectedItems.accessories.findIndex(item => item.id === itemId);
                    if (index !== -1) {
                        selectedItems.accessories.splice(index, 1);
                        // Remove the corresponding element from DOM
                        const layerToRemove = document.querySelector(`.clothing-layer[data-id="${itemId}"]`);
                        if (layerToRemove) {
                            layerToRemove.remove();
                        }
                    }
                } else {
                    // Select
                    this.classList.add('selected');
                    
                    // Default positions and scales for accessories
                    let defaultPosition = { x: 50, y: 30 }; // Default position
                    let defaultScale = 0.5; // Smaller for accessories
                    
                    // Specific positioning based on accessory ID
                    if (itemId === 'a1') { // Hat
                        defaultPosition = { x: 50, y: 12 }; // Position at the top of head
                        defaultScale = 0.4;
                    } else if (itemId === 'a2') { // Scarf
                        defaultPosition = { x: 50, y: 28 }; // Position at neck level
                        defaultScale = 0.5;
                    } else if (itemId === 'a3') { // Glasses
                        defaultPosition = { x: 50, y: 18 }; // Position at eye level
                        defaultScale = 0.3;
                    }
                    
                    selectedItems.accessories.push({
                        id: itemId,
                        imageUrl: imageUrl,
                        position: defaultPosition,
                        scale: defaultScale,
                        rotation: 0
                    });
                }
            } else {
                // Other categories: single selection
                const categoryItems = document.querySelectorAll(`.clothing-item[data-category="${category}"]`);
                categoryItems.forEach(categoryItem => {
                    categoryItem.classList.remove('selected');
                });
                
                // If clicking the same item, deselect it
                if (selectedItems[category] && selectedItems[category].id === itemId) {
                    selectedItems[category] = null;
                    // Remove the corresponding element from DOM
                    const layerToRemove = document.querySelector(`.clothing-layer[data-category="${category}"]`);
                    if (layerToRemove) {
                        layerToRemove.remove();
                    }
                } else {
                    this.classList.add('selected');
                    
                    // Default positions for different categories
                    let defaultPosition = { x: 50, y: 50 }; // Center
                    
                    if (category === 'tops') {
                        defaultPosition = { x: 50, y: 25 }; // Upper body - positioned higher
                    } else if (category === 'bottoms') {
                        defaultPosition = { x: 50, y: 65 }; // Lower body - adjusted for better fit
                    } else if (category === 'outerwear') {
                        defaultPosition = { x: 50, y: 30 }; // Upper body, over tops
                    }
                    
                    // Default scales for different categories
                    let defaultScale = 1;
                    if (category === 'tops') {
                        defaultScale = 0.8; // Slightly smaller for tops
                    } else if (category === 'bottoms') {
                        defaultScale = 0.75; // Smaller for bottoms
                    } else if (category === 'outerwear') {
                        defaultScale = 0.9; // Larger for outerwear
                    } else if (category === 'accessories') {
                        defaultScale = 0.5; // Much smaller for accessories
                    }
                    
                    selectedItems[category] = {
                        id: itemId,
                        imageUrl: imageUrl,
                        position: defaultPosition,
                        scale: defaultScale,
                        rotation: 0
                    };
                }
            }
            
            // Update the model visualization
            updateVisualization();
        });
    });

    // Reset outfit button
    document.getElementById('reset-outfit').addEventListener('click', function() {
        // Visual feedback
        animateClick(this);
        
        // Clear all selections
        clothingItems.forEach(item => {
            item.classList.remove('selected');
        });
        
        // Reset selected items
        selectedItems.tops = null;
        selectedItems.bottoms = null;
        selectedItems.outerwear = null;
        selectedItems.accessories = [];
        
        // Reset active item
        activeItem = null;
        
        // Clear the clothing overlay
        const clothingOverlay = document.getElementById('clothing-overlay');
        clothingOverlay.innerHTML = '';
        
        // Add back the control buttons
        addControlButtons();
        
        // Show feedback
        showNotification('Outfit has been reset', 'info');
    });

    // Save outfit button
    document.getElementById('save-outfit-confirm').addEventListener('click', function() {
        const outfitName = document.getElementById('outfit-name').value || 'My Outfit';
        
        // Validate - if no items selected, show error
        const hasItems = selectedItems.tops || selectedItems.bottoms || 
                         selectedItems.outerwear || selectedItems.accessories.length > 0;
        
        if (!hasItems) {
            showNotification('Please select at least one clothing item', 'danger');
            return;
        }
        
        // Show loading state
        document.getElementById('loading-overlay').classList.remove('d-none');
        
        // Prepare selected items for saving
        const outfitItems = [];
        if (selectedItems.tops) outfitItems.push(selectedItems.tops.id);
        if (selectedItems.bottoms) outfitItems.push(selectedItems.bottoms.id);
        if (selectedItems.outerwear) outfitItems.push(selectedItems.outerwear.id);
        selectedItems.accessories.forEach(item => outfitItems.push(item.id));
        
        // Send data to server
        fetch('/save_outfit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                outfit_name: outfitName,
                selected_items: outfitItems
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading state
            document.getElementById('loading-overlay').classList.add('d-none');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('saveOutfitModal'));
            modal.hide();
            
            // Show success alert
            showNotification(data.message, 'success');
            
            // Reset form
            document.getElementById('outfit-name').value = '';
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide loading state
            document.getElementById('loading-overlay').classList.add('d-none');
            
            // Show error alert
            showNotification('Error saving outfit. Please try again.', 'danger');
        });
    });

    // Add control buttons to the overlay
    function addControlButtons() {
        const overlayContainer = document.getElementById('clothing-overlay');
        
        // Add clothing controls
        const controlDiv = document.createElement('div');
        controlDiv.className = 'clothing-control';
        controlDiv.innerHTML = `
            <button class="control-btn" id="rotate-left" title="Rotate Left"><i class="fas fa-undo"></i></button>
            <button class="control-btn" id="rotate-right" title="Rotate Right"><i class="fas fa-redo"></i></button>
            <button class="control-btn" id="scale-up" title="Scale Up"><i class="fas fa-search-plus"></i></button>
            <button class="control-btn" id="scale-down" title="Scale Down"><i class="fas fa-search-minus"></i></button>
        `;
        overlayContainer.appendChild(controlDiv);
        
        // Set up control buttons
        setupControlButtons();
    }

    // Function to update visualization
    function updateVisualization() {
        const overlayContainer = document.getElementById('clothing-overlay');
        overlayContainer.innerHTML = '';
        
        // Add control buttons
        addControlButtons();
        
        // Add bottoms (lowest layer)
        if (selectedItems.bottoms) {
            addClothingLayer(selectedItems.bottoms, 'bottoms');
        }
        
        // Add tops
        if (selectedItems.tops) {
            addClothingLayer(selectedItems.tops, 'tops');
        }
        
        // Add outerwear
        if (selectedItems.outerwear) {
            addClothingLayer(selectedItems.outerwear, 'outerwear');
        }
        
        // Add accessories (top layer)
        selectedItems.accessories.forEach(item => {
            addClothingLayer(item, 'accessories');
        });
    }
    
    // Function to add a clothing layer
    function addClothingLayer(item, category) {
        const layerDiv = document.createElement('div');
        layerDiv.className = `clothing-layer ${category}-layer`;
        layerDiv.dataset.id = item.id;
        layerDiv.dataset.category = category;
        
        // Set position
        layerDiv.style.left = '0';
        layerDiv.style.top = '0';
        
        const img = document.createElement('img');
        img.src = item.imageUrl;
        img.alt = category;
        img.draggable = false; // Prevent default drag behavior
        
        // Apply position and transformation using a container
        const imgContainer = document.createElement('div');
        imgContainer.className = 'image-container';
        imgContainer.style.position = 'absolute';
        imgContainer.style.left = item.position.x + '%';
        imgContainer.style.top = item.position.y + '%';
        imgContainer.style.transform = `translate(-50%, -50%) scale(${item.scale}) rotate(${item.rotation}deg)`;
        imgContainer.appendChild(img);
        
        layerDiv.appendChild(imgContainer);
        document.getElementById('clothing-overlay').appendChild(layerDiv);
        
        // Add drag functionality
        makeDraggable(imgContainer, item, category);
        
        // Add click to select functionality
        imgContainer.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Deactivate all items
            document.querySelectorAll('.image-container').forEach(container => {
                container.classList.remove('active');
            });
            
            // Activate this item
            imgContainer.classList.add('active');
            
            // Provide visual feedback that item is selected
            const currentTransform = imgContainer.style.transform;
            imgContainer.style.transition = 'all 0.2s ease';
            const scaleFactor = item.scale * 1.05;
            imgContainer.style.transform = `translate(-50%, -50%) scale(${scaleFactor}) rotate(${item.rotation}deg)`;
            setTimeout(() => {
                imgContainer.style.transform = currentTransform;
            }, 200);
            
            // Set as active item
            if (category === 'accessories') {
                activeItem = {
                    item: item,
                    element: imgContainer,
                    category: category,
                    index: selectedItems.accessories.findIndex(accessory => accessory.id === item.id)
                };
            } else {
                activeItem = {
                    item: item,
                    element: imgContainer,
                    category: category
                };
            }
        });
    }
    
    // Function to make an element draggable
    function makeDraggable(element, item, category) {
        let isDragging = false;
        let startX, startY;
        let startLeft, startTop;
        
        // Touch events for mobile support
        element.addEventListener('touchstart', handleStart, { passive: false });
        document.addEventListener('touchmove', handleMove, { passive: false });
        document.addEventListener('touchend', handleEnd);
        
        // Mouse events for desktop
        element.addEventListener('mousedown', handleStart);
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        
        function handleStart(e) {
            e.preventDefault();
            
            // Get event position (touch or mouse)
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            
            isDragging = true;
            startX = clientX;
            startY = clientY;
            startLeft = parseFloat(element.style.left);
            startTop = parseFloat(element.style.top);
            
            // Add dragging class for visual feedback
            element.classList.add('dragging');
            
            // Set z-index higher during drag
            const parentLayer = element.closest('.clothing-layer');
            if (parentLayer) {
                parentLayer.style.zIndex = '100';
            }
            
            // Set this as the active item
            if (category === 'accessories') {
                activeItem = {
                    item: item,
                    element: element,
                    category: category,
                    index: selectedItems.accessories.findIndex(accessory => accessory.id === item.id)
                };
            } else {
                activeItem = {
                    item: item,
                    element: element,
                    category: category
                };
            }
            
            // Deactivate all items
            document.querySelectorAll('.image-container').forEach(container => {
                container.classList.remove('active');
            });
            
            // Activate this item
            element.classList.add('active');
        }
        
        function handleMove(e) {
            if (!isDragging) return;
            
            // Prevent default behavior like scrolling on mobile
            if (e.touches) e.preventDefault();
            
            // Get event position (touch or mouse)
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            
            // Calculate the model container boundaries
            const container = document.getElementById('model-container');
            const containerRect = container.getBoundingClientRect();
            
            // Calculate new position in percentage
            const deltaX = clientX - startX;
            const deltaY = clientY - startY;
            const newLeft = startLeft + (deltaX / containerRect.width) * 100;
            const newTop = startTop + (deltaY / containerRect.height) * 100;
            
            // Update element position
            element.style.left = newLeft + '%';
            element.style.top = newTop + '%';
            
            // Update item data
            item.position.x = newLeft;
            item.position.y = newTop;
            
            // Update the stored item data
            if (category === 'accessories') {
                const index = selectedItems.accessories.findIndex(accessory => accessory.id === item.id);
                if (index !== -1) {
                    selectedItems.accessories[index].position = item.position;
                }
            } else {
                selectedItems[category].position = item.position;
            }
        }
        
        function handleEnd() {
            if (isDragging) {
                isDragging = false;
                element.classList.remove('dragging');
                
                // Reset z-index
                const parentLayer = element.closest('.clothing-layer');
                if (parentLayer) {
                    parentLayer.style.zIndex = '';
                }
            }
        }
    }
    
    // Set up control buttons for rotation and scaling
    function setupControlButtons() {
        // Rotate left
        document.getElementById('rotate-left').addEventListener('click', function() {
            if (!activeItem) {
                showNotification('Please select an item first', 'info');
                return;
            }
            
            // Update rotation
            activeItem.item.rotation -= 15;
            
            // Update the visual element
            updateActiveItemStyle();
            
            // Update stored data
            updateStoredItemData();
        });
        
        // Rotate right
        document.getElementById('rotate-right').addEventListener('click', function() {
            if (!activeItem) {
                showNotification('Please select an item first', 'info');
                return;
            }
            
            // Update rotation
            activeItem.item.rotation += 15;
            
            // Update the visual element
            updateActiveItemStyle();
            
            // Update stored data
            updateStoredItemData();
        });
        
        // Scale up
        document.getElementById('scale-up').addEventListener('click', function() {
            if (!activeItem) {
                showNotification('Please select an item first', 'info');
                return;
            }
            
            // Update scale (max 2.0)
            activeItem.item.scale = Math.min(activeItem.item.scale + 0.1, 2.0);
            
            // Update the visual element
            updateActiveItemStyle();
            
            // Update stored data
            updateStoredItemData();
        });
        
        // Scale down
        document.getElementById('scale-down').addEventListener('click', function() {
            if (!activeItem) {
                showNotification('Please select an item first', 'info');
                return;
            }
            
            // Update scale (min 0.5)
            activeItem.item.scale = Math.max(activeItem.item.scale - 0.1, 0.5);
            
            // Update the visual element
            updateActiveItemStyle();
            
            // Update stored data
            updateStoredItemData();
        });
    }
    
    // Function to update the active item's visual style
    function updateActiveItemStyle() {
        if (activeItem && activeItem.element) {
            activeItem.element.style.transform = `translate(-50%, -50%) scale(${activeItem.item.scale}) rotate(${activeItem.item.rotation}deg)`;
        }
    }
    
    // Function to update the stored item data
    function updateStoredItemData() {
        if (activeItem) {
            if (activeItem.category === 'accessories') {
                selectedItems.accessories[activeItem.index] = activeItem.item;
            } else {
                selectedItems[activeItem.category] = activeItem.item;
            }
        }
    }
    
    // Deselect active item when clicking on the model container background
    document.getElementById('model-container').addEventListener('click', function(e) {
        // Only if clicking directly on the container, not on a clothing item
        if (e.target === this || e.target.id === 'model-container' || e.target.classList.contains('model-image')) {
            activeItem = null;
            document.querySelectorAll('.image-container').forEach(container => {
                container.classList.remove('active');
            });
        }
    });
    
    // Helper functions
    
    // Setup initial UI
    function setupUI() {
        // Ensure the outfit name field is cleared when modal is opened
        const saveOutfitModal = document.getElementById('saveOutfitModal');
        if (saveOutfitModal) {
            saveOutfitModal.addEventListener('show.bs.modal', function() {
                document.getElementById('outfit-name').value = '';
            });
        }
        
        // Initialize tooltips
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }
    
    // Show notification/alert
    function showNotification(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'danger') icon = 'exclamation-triangle';
        
        alertDiv.innerHTML = `
            <i class="fas fa-${icon} me-2"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 150);
            }
        }, 5000);
    }
    
    // Animate click effect
    function animateClick(element) {
        element.style.transition = 'transform 0.1s ease';
        element.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 100);
    }
});