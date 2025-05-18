/**
 * TagTrack - Unified Status Management Script
 * 
 * This file centralizes all status-related functionality for the List Tagged Items feature:
 * - Standard status definitions and display
 * - Item filtering logic
 * - Status updates and UI management
 */

// Immediately-Invoked Function Expression to avoid global scope pollution
(function() {
  console.log("Unified Status Management script loaded");
  
  // ===== STATUS DEFINITIONS =====
  
  // Define standard status types and their display properties
  const STATUS_TYPES = {
    REGISTERED: {
      value: 'Registered',
      label: 'Needs Review',
      icon: '🔒',
      colorClass: 'bg-blue-100 text-blue-800',
      buttonClass: 'bg-blue-600 hover:bg-blue-700'
    },
    APPROVED: {
      value: 'Approved',
      label: 'Awaiting QR Code',
      icon: '⏳',
      colorClass: 'bg-amber-100 text-amber-800',
      buttonClass: 'bg-amber-500 hover:bg-amber-600'
    },
    COMPLETED: {
      value: 'Completed',
      label: 'Tagged',
      icon: '✅',
      colorClass: 'bg-green-100 text-green-800',
      buttonClass: 'bg-green-600 hover:bg-green-700'
    },
    UNCLAIMED: {
      value: 'Unclaimed',
      label: 'Unclaimed',
      icon: '❌',
      colorClass: 'bg-amber-100 text-amber-800',
      buttonClass: 'bg-amber-500 hover:bg-amber-600'
    },
    CLAIMED: {
      value: 'Claimed',
      label: 'Claimed',
      icon: '✓',
      colorClass: 'bg-emerald-100 text-emerald-800',
      buttonClass: 'bg-emerald-600 hover:bg-emerald-700'
    },
    REJECTED: {
      value: 'Rejected',
      label: 'Rejected',
      icon: '✗',
      colorClass: 'bg-red-100 text-red-800',
      buttonClass: 'bg-red-600 hover:bg-red-700'
    }
  };

  // Global variables for item management
  window.taggedItems = [];
  window.categories = [];
  window.locations = [];
  window.users = [];
  window.currentItemId = null;
  window.currentTab = 'all';

  // ===== UTILITY FUNCTIONS =====
  
  // Check if an item has a valid tag (RFID or QR code)
  function itemHasValidTag(item) {
    if (!item) return false;
    
    // For RFID tags
    const hasValidRfid = item.rfid_tag && 
                       item.rfid_tag !== 'None' && 
                       item.rfid_tag !== '' &&
                       item.rfid_tag !== 'null' &&
                       item.rfid_tag !== 'undefined';
                       
    // For QR codes (unique_code)
    const hasValidQR = item.unique_code && 
                     item.unique_code !== '' &&
                     item.unique_code !== 'null' &&
                     item.unique_code !== 'undefined';
                     
    return hasValidRfid || hasValidQR;
  }
  
  // Get appropriate status display for an item
  function getItemStatusDisplay(item) {
    if (!item) return null;
    
    const hasTag = itemHasValidTag(item);
    
    // Determine actual display status based on a combination of status field and tag presence
    let statusDisplay;
    
    switch(item.status) {
      case STATUS_TYPES.REGISTERED.value:
        statusDisplay = STATUS_TYPES.REGISTERED;
        break;
        
      case STATUS_TYPES.APPROVED.value:
        // If approved but no tag, show as awaiting QR code
        statusDisplay = hasTag ? STATUS_TYPES.COMPLETED : STATUS_TYPES.APPROVED;
        break;
        
      case STATUS_TYPES.COMPLETED.value:
        statusDisplay = STATUS_TYPES.COMPLETED;
        break;
        
      case STATUS_TYPES.UNCLAIMED.value:
        statusDisplay = STATUS_TYPES.UNCLAIMED;
        break;
        
      case STATUS_TYPES.CLAIMED.value:
        statusDisplay = STATUS_TYPES.CLAIMED;
        break;
        
      case STATUS_TYPES.REJECTED.value:
        statusDisplay = STATUS_TYPES.REJECTED;
        break;
        
      default:
        // Default fallback
        statusDisplay = {
          value: item.status || 'Unknown',
          label: item.status || 'Unknown',
          icon: '?',
          colorClass: 'bg-gray-100 text-gray-800',
          buttonClass: 'bg-gray-600 hover:bg-gray-700'
        };
    }
    
    return statusDisplay;
  }
  
  // Format date in a readable format
  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  }
  
  // Show notification to the user
  function showNotification(message, type = "info") {
    // Remove any existing notifications to prevent stacking
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification fixed top-6 right-6 p-4 rounded-lg shadow-lg z-50 transform transition-all duration-500 translate-x-full';
    
    // Set notification type styling
    let icon, bgColor, textColor;
    switch(type) {
      case 'success':
        icon = '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
        bgColor = 'bg-green-100';
        textColor = 'text-green-800';
        break;
      case 'error':
        icon = '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
        bgColor = 'bg-red-100';
        textColor = 'text-red-800';
        break;
      default:
        icon = '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
        bgColor = 'bg-blue-100';
        textColor = 'text-blue-800';
    }
    
    notification.className += ` ${bgColor} ${textColor}`;
    notification.innerHTML = `
      <div class="flex items-center">
        ${icon}
        <div class="flex-1">${message}</div>
        <button class="ml-4 text-gray-500 hover:text-gray-700 focus:outline-none" onclick="this.parentElement.parentElement.remove()">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
      notification.classList.add('translate-x-0');
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      notification.classList.remove('translate-x-0');
      notification.classList.add('translate-x-full');
      
      // Remove from DOM after animation completes
      setTimeout(() => notification.remove(), 500);
    }, 5000);
  }
  
  // ===== DATA FETCHING =====
  
  // Fetch all tagged items from the server
  async function fetchTaggedItems() {
    try {
      // Show loading state
      const container = document.getElementById("items-container");
      if (container) {
        container.innerHTML = `
          <div class="col-span-full flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p class="text-gray-500 text-lg">Loading items...</p>
          </div>
        `;
      }
      
      const response = await fetch("/api/tagged-items");
      if (!response.ok) {
        throw new Error(`Failed to fetch items: ${response.statusText}`);
      }
      const data = await response.json();
      
      // Ensure data is in the expected format
      if (Array.isArray(data)) {
        window.taggedItems = data;
      } else if (data.items && Array.isArray(data.items)) {
        window.taggedItems = data.items;
      } else {
        window.taggedItems = [];
        console.error("Invalid tagged items data format");
      }
      
      console.log(`Loaded ${window.taggedItems.length} tagged items`);
      return window.taggedItems;
    } catch (error) {
      console.error("Error fetching tagged items:", error);
      showNotification("Failed to load items. Please refresh the page.", "error");
      
      // Show error message in the items container
      const container = document.getElementById("items-container");
      if (container) {
        container.innerHTML = `
          <div class="col-span-full flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm">
            <svg class="w-16 h-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-red-500 text-lg mb-1">Error loading items</p>
            <p class="text-gray-500 text-sm">Please refresh the page to try again</p>
            <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Refresh Page
            </button>
          </div>
        `;
      }
      
      // Return empty array to prevent errors in dependent code
      return [];
    }
  }
  
  // Fetch categories from the server
  async function fetchCategories() {
    try {
      const response = await fetch("/api/categories");
      if (!response.ok) {
        throw new Error(`Failed to fetch categories: ${response.statusText}`);
      }
      const data = await response.json();
      window.categories = data;
      
      // Populate category dropdown
      const categoryDropdown = document.getElementById("category");
      if (categoryDropdown) {
        categoryDropdown.innerHTML = '<option value="">Select Category</option>';
        
        window.categories.forEach(category => {
          const option = document.createElement("option");
          option.value = category.id;
          option.textContent = category.name;
          categoryDropdown.appendChild(option);
        });
      }
      
      return window.categories;
    } catch (error) {
      console.error("Error fetching categories:", error);
      return [];
    }
  }
  
  // Fetch locations from the server
  async function fetchLocations() {
    try {
      const response = await fetch("/api/locations");
      if (!response.ok) {
        throw new Error(`Failed to fetch locations: ${response.statusText}`);
      }
      const data = await response.json();
      window.locations = data;
      
      // Populate location filter dropdown
      const locationFilter = document.getElementById("location-filter");
      if (locationFilter) {
        locationFilter.innerHTML = '<option value="">📍 By Location</option>';
        
        window.locations.forEach(location => {
          // For filter dropdown
          const filterOption = document.createElement("option");
          filterOption.value = location.name;
          filterOption.textContent = location.name;
          locationFilter.appendChild(filterOption);
        });
        
        // Add change event for filter
        locationFilter.addEventListener("change", filterItems);
      }
      
      return window.locations;
    } catch (error) {
      console.error("Error fetching locations:", error);
      return [];
    }
  }
  
  // Fetch users from the server
  async function fetchUsers() {
    try {
      const response = await fetch("/api/users");
      if (!response.ok) {
        throw new Error(`Failed to fetch users: ${response.statusText}`);
      }
      const data = await response.json();
      window.users = data;
      
      return window.users;
    } catch (error) {
      console.error("Error fetching users:", error);
      return [];
    }
  }
  
  // ===== TAB AND FILTERING =====
  
  // Filter items based on selected tab
  function switchTab(tabName) {
    console.log("Unified switchTab called with tab:", tabName);
    window.currentTab = tabName;
    
    try {
      // Update tab UI
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-blue-600');
        btn.classList.add('border-transparent', 'text-gray-500');
      });
      
      const tabElement = document.getElementById(`tab-${tabName}`);
      if (tabElement) {
        tabElement.classList.remove('border-transparent', 'text-gray-500');
        tabElement.classList.add('border-blue-500', 'text-blue-600');
      }
      
      // Ensure we have valid data
      if (!window.taggedItems || !Array.isArray(window.taggedItems)) {
        console.error("taggedItems is not properly defined");
        showNotification("Error loading items. Please refresh the page.", "error");
        return;
      }
      
      // Apply filters based on selected tab
      let filteredItems = [];
      
      if (tabName === 'all') {
        // Show all items
        filteredItems = window.taggedItems;
      } 
      else if (tabName === 'official') {
        // Show only official/tagged items
        filteredItems = window.taggedItems.filter(item => {
          // Item is official if:
          // 1. It's Completed (always considered tagged)
          // 2. It's Approved AND has a valid tag
          return item.status === STATUS_TYPES.COMPLETED.value || 
                (item.status === STATUS_TYPES.APPROVED.value && itemHasValidTag(item));
        });
      } 
      else if (tabName === 'pending') {
        // Show only pending items awaiting approval or tagging
        filteredItems = window.taggedItems.filter(item => {
          // Item is pending if:
          // 1. It's Registered (awaiting approval)
          // 2. It's Approved BUT doesn't have a valid tag yet
          return item.status === STATUS_TYPES.REGISTERED.value || 
                (item.status === STATUS_TYPES.APPROVED.value && !itemHasValidTag(item));
        });
      }
      
      // Apply additional filters from UI if they exist
      const search = document.getElementById("search")?.value?.toLowerCase() || "";
      const status = document.getElementById("filter-status")?.value || "";
      const location = document.getElementById("location-filter")?.value || "";
      
      if (search || status || location) {
        filteredItems = filteredItems.filter(item => {
          return (search === "" ||
                  (item.description && item.description.toLowerCase().includes(search)) ||
                  (item.category && item.category.toLowerCase().includes(search)) ||
                  (item.location && item.location.toLowerCase().includes(search)) ||
                  (item.rfid_tag && item.rfid_tag.toLowerCase().includes(search))) &&
                 (status === "" || item.status === status) &&
                 (location === "" || item.location === location);
        });
      }
      
      // Display the filtered items
      renderItems(filteredItems);
    } catch (error) {
      console.error("Error in switchTab:", error);
      showNotification("Error filtering items. Please refresh the page.", "error");
    }
  }
  
  // Apply additional filters (search, status, location)
  function filterItems() {
    if (window.currentTab) {
      switchTab(window.currentTab);
    } else {
      switchTab('all');
    }
  }
  
  // ===== ITEM RENDERING =====
  
  // Render items to the page
  function renderItems(items) {
    const container = document.getElementById("items-container");
    if (!container) {
      console.error("Items container not found");
      return;
    }
    
    // Clear the container first
    container.innerHTML = "";

    if (!items || items.length === 0) {
      container.innerHTML = `
        <div class="col-span-full flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm">
          <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-gray-500 text-lg mb-1">No tagged items found</p>
          <p class="text-gray-400 text-sm">Try adjusting your search or filters</p>
        </div>
      `;
      return;
    }
    
    // Create and append items
    items.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "bg-white rounded-xl shadow-md transition-all duration-300 hover:shadow-lg hover:translate-y-[-4px] overflow-hidden flex flex-col h-full opacity-0";
      card.style.animation = `slideIn 0.4s ease-out ${index * 0.05}s forwards`;
      
      // Get proper status display
      const statusDisplay = getItemStatusDisplay(item);
      
      // Add special styling for pending items
      if (item.status === STATUS_TYPES.REGISTERED.value) {
        card.classList.add("border-2", "border-blue-400");
      } else if (item.status === STATUS_TYPES.APPROVED.value && !itemHasValidTag(item)) {
        card.classList.add("border-2", "border-amber-400");
      } else if (itemHasValidTag(item)) {
        card.classList.add("border-2", "border-green-400");
      }
      
      // Determine tag display text
      let tagStatusText;
      if (itemHasValidTag(item)) {
        tagStatusText = item.rfid_tag ? `RFID: ${item.rfid_tag}` : (item.unique_code ? `QR: ${item.unique_code}` : "Tagged");
      } else {
        tagStatusText = "Needs Tag";
      }
      
      card.innerHTML = `
        <div class="relative">
          <img class="w-full h-48 object-cover" src="${item.image_file ? "/uploads/" + item.image_file : "/static/default-item.jpg"}" alt="${item.category} image" onerror="this.src='/static/default-item.jpg'">
          <!-- Primary status badge in top right -->
          <div class="absolute top-2 right-2">
            <span class="px-2.5 py-1 rounded-full text-xs font-bold ${statusDisplay.colorClass} flex items-center">
              <span class="mr-1">${statusDisplay.icon}</span> ${statusDisplay.label}
            </span>
          </div>
          
          <!-- Show student submission badge if applicable -->
          ${item.status === STATUS_TYPES.REGISTERED.value ? 
            `<div class="absolute bottom-14 left-0 bg-blue-600 text-white px-3 py-1 rounded-tr-lg font-medium text-xs">
               Student Submission
             </div>` : ''}
             
          <div class="absolute bottom-0 w-full bg-gradient-to-t from-black/70 to-transparent p-3">
            <h3 class="font-bold text-white text-lg">${item.category}</h3>
          </div>
        </div>
        <div class="p-4 flex-grow flex flex-col">
          <p class="text-gray-700 mb-3 line-clamp-2 flex-grow">${item.description}</p>
          <div class="text-gray-600 text-sm space-y-2">
            <p class="flex items-center"><span class="flex-shrink-0 w-5 h-5 mr-1.5 flex items-center justify-center text-blue-500">📍</span> ${item.location}</p>
            <p class="flex items-center"><span class="flex-shrink-0 w-5 h-5 mr-1.5 flex items-center justify-center text-blue-500">📅</span> ${formatDate(item.date_reported)}</p>
            <p class="flex items-center"><span class="flex-shrink-0 w-5 h-5 mr-1.5 flex items-center justify-center text-blue-500">👤</span> 
              <span>${item.owner_name || 'No owner'}</span>
            </p>
            <p class="flex items-center"><span class="flex-shrink-0 w-5 h-5 mr-1.5 flex items-center justify-center text-blue-500">🏷️</span> 
              <span class="font-mono">${tagStatusText}</span>
            </p>
          </div>
          ${item.status === STATUS_TYPES.REGISTERED.value ? 
          `<div class="flex gap-2 mt-3">
             <button class="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm py-2 px-3 rounded transition-colors approve-btn flex items-center justify-center" data-id="${item.id}">
               <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
               </svg>
               Approve
             </button>
             <button class="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm py-2 px-3 rounded transition-colors reject-btn flex items-center justify-center" data-id="${item.id}">
               <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
               </svg>
               Reject
             </button>
           </div>` : ''}
          <button class="mt-3 w-full ${statusDisplay.buttonClass} text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 view-details-btn flex items-center justify-center" data-id="${item.id}">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            View Details
          </button>
        </div>
      `;

      container.appendChild(card);
    });

    // Attach event listeners to buttons
    document.querySelectorAll(".view-details-btn").forEach(btn => {
      btn.addEventListener("click", function() {
        const itemId = this.getAttribute("data-id");
        console.log("View Details button clicked for item ID:", itemId);
        const item = items.find(i => i.id == itemId);
        if (item) {
          if (typeof window.openDetailModal === 'function') {
            window.openDetailModal(item);
          } else {
            console.error("openDetailModal function is not available");
            // Fallback: Try to directly show the modal
            const modal = document.getElementById("itemModal");
            if (modal) {
              // Set current item ID
              window.currentItemId = itemId;
              
              // Update the modal content directly
              document.getElementById("modal-title").textContent = item.category || 'Item Details';
              document.getElementById("modal-image").src = item.image_file ? "/uploads/" + item.image_file : "/static/default-item.jpg";
              document.getElementById("modal-category").textContent = item.category || '';
              document.getElementById("modal-description").textContent = item.description || '';
              document.getElementById("modal-location").textContent = item.location || '';
              document.getElementById("modal-date").textContent = formatDate(item.date_reported);
              
              const tagDisplay = document.getElementById("modal-rfid");
              if (tagDisplay) {
                tagDisplay.textContent = item.rfid_tag || 'Not tagged';
              }
              
              // Show the modal
              modal.classList.remove("hidden");
              modal.classList.add("flex");
            }
          }
        } else {
          console.error("Item not found with ID:", itemId);
        }
      });
    });
    
    // Attach event listeners to approval/rejection buttons
    document.querySelectorAll(".approve-btn").forEach(btn => {
      btn.addEventListener("click", function(e) {
        e.stopPropagation();
        const itemId = this.getAttribute("data-id");
        if (itemId) {
          window.currentItemId = itemId;
          updateItemStatus("Approved");
        }
      });
    });
    
    document.querySelectorAll(".reject-btn").forEach(btn => {
      btn.addEventListener("click", function(e) {
        e.stopPropagation();
        const itemId = this.getAttribute("data-id");
        if (itemId) {
          window.currentItemId = itemId;
          if (confirm("Are you sure you want to reject this submission?")) {
            updateItemStatus("Rejected");
          }
        }
      });
    });
  }
  
  // ===== UPDATE STATUS =====
  
  // Update item status via API
  async function updateItemStatus(newStatus) {
    if (!window.currentItemId) {
      console.error("No item ID selected for status update");
      showNotification("Error: No item selected", "error");
      return;
    }
    
    try {
      console.log(`Updating item ${window.currentItemId} to status: ${newStatus}`);
      
      const response = await fetch(`/api/item-status/${window.currentItemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to update status to ${newStatus}`);
      }
      
      const result = await response.json();
      showNotification(`Item ${result.message}`, "success");
      
      // Update the item in our local array
      const itemIndex = window.taggedItems.findIndex(i => i.id == window.currentItemId);
      if (itemIndex !== -1) {
        window.taggedItems[itemIndex].status = newStatus;
      }
      
      // Close modal if open
      const modal = document.getElementById("itemModal");
      if (modal && modal.classList.contains("flex")) {
        closeModal();
      }
      
      // Refresh the current tab view
      switchTab(window.currentTab || 'all');
      
    } catch (error) {
      console.error("Error updating item status:", error);
      showNotification(error.message, "error");
    }
  }
  
  // ===== MODAL HANDLING =====
  
  // Enhance detail modal with consistent status display
  function enhanceDetailModal() {
    if (typeof window.openDetailModal === 'function') {
      console.log("Enhancing detail modal with consistent status display");
      
      // Store reference to original function
      const originalOpenDetailModal = window.openDetailModal;
      
      // Override with enhanced version
      window.openDetailModal = function(item) {
        // Call original function
        originalOpenDetailModal(item);
        
        // Set currentItemId for status updates
        window.currentItemId = item.id;
        
        // Update status display
        const statusDisplay = getItemStatusDisplay(item);
        const statusElem = document.getElementById("modal-status");
        
        if (statusElem) {
          statusElem.textContent = statusDisplay.label;
          statusElem.className = "px-2 py-1 rounded text-sm font-medium " + statusDisplay.colorClass;
        }
        
        // Update tag display
        const tagDisplay = document.getElementById("modal-rfid");
        if (tagDisplay) {
          if (itemHasValidTag(item)) {
            if (item.rfid_tag && item.rfid_tag !== 'None' && item.rfid_tag !== '') {
              tagDisplay.textContent = `RFID: ${item.rfid_tag}`;
            } else if (item.unique_code && item.unique_code !== '') {
              tagDisplay.textContent = `QR Code: ${item.unique_code}`;
            } else {
              tagDisplay.textContent = 'Tagged';
            }
          } else {
            tagDisplay.textContent = 'Not tagged yet';
          }
        }
        
        // Set up status action buttons
        updateStatusButtons(item.status);
        
        // Make sure the modal is visible
        const modal = document.getElementById("itemModal");
        if (modal) {
          modal.classList.remove("hidden");
          modal.classList.add("flex");
        }
      };
    } else {
      // If openDetailModal doesn't exist in the window scope, create it
      window.openDetailModal = function(item) {
        console.log("Using fallback openDetailModal function");
        // Set currentItemId for status updates
        window.currentItemId = item.id;
        
        // Get proper status display
        const statusDisplay = getItemStatusDisplay(item);
        
        // Set modal elements
        document.getElementById("modal-title").textContent = item.category;
        document.getElementById("modal-image").src = item.image_file ? "/uploads/" + item.image_file : "/static/default-item.jpg";
        document.getElementById("modal-category").textContent = item.category;
        document.getElementById("modal-description").textContent = item.description;
        document.getElementById("modal-location").textContent = item.location || 'Unknown location';
        document.getElementById("modal-date").textContent = formatDate(item.date_reported);
        
        // Set status information
        const statusElem = document.getElementById("modal-status");
        if (statusElem) {
          statusElem.textContent = statusDisplay.label;
          statusElem.className = "px-2 py-1 rounded text-sm font-medium " + statusDisplay.colorClass;
        }
        
        // Update tag display
        const tagDisplay = document.getElementById("modal-rfid");
        if (tagDisplay) {
          if (itemHasValidTag(item)) {
            if (item.rfid_tag && item.rfid_tag !== 'None' && item.rfid_tag !== '') {
              tagDisplay.textContent = `RFID: ${item.rfid_tag}`;
            } else if (item.unique_code && item.unique_code !== '') {
              tagDisplay.textContent = `QR Code: ${item.unique_code}`;
            } else {
              tagDisplay.textContent = 'Tagged';
            }
          } else {
            tagDisplay.textContent = 'Not tagged yet';
          }
        }
        
        // Owner details
        if (document.getElementById("modal-owner-name")) {
          document.getElementById("modal-owner-name").textContent = item.owner_name || "N/A";
        }
        if (document.getElementById("modal-owner-email")) {
          document.getElementById("modal-owner-email").textContent = item.owner_email || "N/A";
        }
        if (document.getElementById("modal-owner-student-id")) {
          document.getElementById("modal-owner-student-id").textContent = item.owner_student_id || "N/A";
        }
        if (document.getElementById("modal-owner-contact")) {
          document.getElementById("modal-owner-contact").textContent = item.owner_contact || "N/A";
        }
        
        // Update student submission section visibility
        const studentSubmissionSection = document.getElementById("student-submission-section");
        const isPendingSubmission = item.status === "Registered";
        
        if (studentSubmissionSection) {
          if (isPendingSubmission) {
            studentSubmissionSection.classList.remove("hidden");
            
            // Update submission metadata if available
            const submissionDate = document.getElementById("submission-date");
            if (submissionDate) {
              submissionDate.textContent = formatDate(item.date_reported);
            }
          } else {
            studentSubmissionSection.classList.add("hidden");
          }
        }
        
        // Set up status action buttons
        updateStatusButtons(item.status);
        
        // Show modal
        const modal = document.getElementById("itemModal");
        if (modal) {
          modal.classList.remove("hidden");
          modal.classList.add("flex");
        }
      };
    }
    
    // Check if closeModal function exists, if not, create it
    if (typeof window.closeModal !== 'function') {
      window.closeModal = function() {
        const modal = document.getElementById("itemModal");
        if (modal) {
          modal.classList.remove("flex");
          modal.classList.add("hidden");
        }
      };
    }
  }
  
  // Enhanced status button update function
  function updateStatusButtons(status) {
    console.log("Updating status buttons for:", status);
    
    // Get action buttons container
    const actionButtons = document.getElementById("status-action-buttons");
    if (!actionButtons) return;
    
    // Hide buttons by default
    actionButtons.classList.add("hidden");
    
    // Get individual buttons
    const approveBtn = document.getElementById("approve-btn");
    const completeBtn = document.getElementById("complete-btn");
    
    // First hide all buttons
    if (approveBtn) approveBtn.classList.add("hidden");
    if (completeBtn) completeBtn.classList.add("hidden");
    
    // Show appropriate buttons based on status
    if (status === "Registered") {
      // Enable approve buttons
      actionButtons.classList.remove("hidden");
      
      if (approveBtn) {
        approveBtn.classList.remove("hidden");
        approveBtn.onclick = () => updateItemStatus("Approved");
      }
    } 
    else if (status === "Approved") {
      // Enable complete buttons
      actionButtons.classList.remove("hidden");
      
      if (completeBtn) {
        completeBtn.classList.remove("hidden");
        completeBtn.classList.add("flex");
        completeBtn.innerHTML = `
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Mark as Tagged
        `;
        completeBtn.onclick = () => updateItemStatus("Completed");
      }
    }
  }
  
  // ===== INITIALIZATION =====
  
  // Set up search handlers
  function setupSearchHandlers() {
    const searchInput = document.getElementById("search");
    if (searchInput) {
      searchInput.addEventListener("input", function() {
        // Debounce to prevent excessive filtering
        clearTimeout(searchInput.timeout);
        searchInput.timeout = setTimeout(filterItems, 300);
      });
    }
    
    const statusFilter = document.getElementById("filter-status");
    if (statusFilter) {
      statusFilter.addEventListener("change", filterItems);
    }
  }

  // Initialize data and event handlers
  async function initializeApp() {
    console.log("Initializing tagItemStatus.js");
    
    try {
      // Make main container visible
      const mainContainer = document.getElementById("mainContainer");
      if (mainContainer) {
        mainContainer.style.opacity = "1";
        mainContainer.classList.remove("opacity-0");
        mainContainer.classList.add("opacity-100");
      }
      
      // Set up search handlers
      setupSearchHandlers();
      
      // Override global tab function
      window.switchTab = switchTab;
      
      // Enhance modal functionalities
      enhanceDetailModal();
      
      // Load data in parallel
      const [items, categories, locations] = await Promise.all([
        fetchTaggedItems(),
        fetchCategories(),
        fetchLocations()
      ]);
      
      // Initialize view with default tab
      if (items.length > 0) {
        window.currentTab = 'all';
        switchTab('all');
      }
      
      // Make sure openDetailModal is accessible from outside the module
      if (typeof window.openDetailModal !== 'function') {
        console.error("openDetailModal function not properly set in global scope!");
      } else {
        console.log("openDetailModal successfully installed in global scope");
      }
      
      console.log("TagTrack initialization complete");
    } catch (error) {
      console.error("Error initializing app:", error);
      showNotification("Failed to initialize application. Please refresh the page.", "error");
    }
  }
  
  // Wait for document to be fully loaded before initializing
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeApp);
  } else {
    // Document already loaded
    initializeApp();
  }
})(); 