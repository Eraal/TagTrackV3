/* Script changes for listTagItem.html */

// Filter items based on selected tab
function switchTab(tabName) {
  console.log("switchTab called with tab:", tabName);
  window.currentTab = tabName;
  
  try {
    // Update tab UI
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('border-blue-500', 'text-blue-600');
      btn.classList.add('border-transparent', 'text-gray-500');
    });
    
    document.getElementById(`tab-${tabName}`).classList.remove('border-transparent', 'text-gray-500');
    document.getElementById(`tab-${tabName}`).classList.add('border-blue-500', 'text-blue-600');
    
    console.log("Tab UI updated for:", tabName);
    // Filter items based on tab
    let filteredItems = [];
    
    if (!window.taggedItems || !Array.isArray(window.taggedItems)) {
      console.error("taggedItems is not defined or not an array");
      return;
    }
    
    console.log("Total items:", window.taggedItems.length);
    
    if (tabName === 'all') {
      filteredItems = window.taggedItems;
    } else if (tabName === 'official') {
      // Official items are those that are Approved or Completed and have either:
      // 1. An assigned RFID tag
      // 2. A generated QR code (unique_code)
      filteredItems = window.taggedItems.filter(item => 
        (item.status === 'Approved' || item.status === 'Completed') && 
        (
          (item.rfid_tag && item.rfid_tag !== 'None' && item.rfid_tag !== '') || 
          (item.unique_code && item.unique_code !== '')
        )
      );
    } else if (tabName === 'pending') {
      // Pending items are those with "Registered" status (awaiting approval)
      // These are student submissions that have not yet been approved
      filteredItems = window.taggedItems.filter(item => 
        item.status === 'Registered'
      );
    }
    
    // Apply existing filters on the filtered set
    const search = document.getElementById("search")?.value?.toLowerCase() || "";
    const status = document.getElementById("filter-status")?.value || "";
    const location = document.getElementById("location-filter")?.value || "";
    
    if (search || status || location) {
      filteredItems = filteredItems.filter(item => {
        return (search === "" ||
                item.description.toLowerCase().includes(search) ||
                item.category.toLowerCase().includes(search) ||
                item.location.toLowerCase().includes(search) ||
                (item.rfid_tag && item.rfid_tag.toLowerCase().includes(search))) &&
               (status === "" || item.status === status) &&
               (location === "" || item.location === location);
      });
    }
    
    console.log(`Filtered to ${filteredItems.length} items for tab: ${tabName}`);
    
    // Display the filtered items immediately 
    renderItems(filteredItems);
  } catch (e) {
    console.error("Error in switchTab:", e);
  }
}

// Update item status via API call
async function updateItemStatus(newStatus) {
  if (!currentItemId) {
    console.error("No item ID selected for status update");
    return;
  }
  
  console.log(`Updating item ${currentItemId} to status: ${newStatus}`);
  
  try {
    const response = await fetch(`/api/item-status/${currentItemId}`, {
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
    
    // Success - update UI
    const result = await response.json();
    showNotification(result.message, "success");
    
    // Update the item in our local array
    const itemIndex = taggedItems.findIndex(i => i.id == currentItemId);
    if (itemIndex !== -1) {
      taggedItems[itemIndex].status = newStatus;
      
      // Update modal display
      const statusElem = document.getElementById("modal-status");
      statusElem.textContent = newStatus;
      
      // Update status color/class
      statusElem.className = "px-2 py-1 rounded text-sm font-medium";
      
      if (newStatus === "Registered") {
        statusElem.className += " bg-blue-100 text-blue-800";
      } else if (newStatus === "Approved") {
        statusElem.className += " bg-green-100 text-green-800";
      } else if (newStatus === "Completed") {
        statusElem.className += " bg-purple-100 text-purple-800";
      } else if (newStatus === "Unclaimed") {
        statusElem.className += " bg-amber-100 text-amber-800";
      } else if (newStatus === "Claimed") {
        statusElem.className += " bg-emerald-100 text-emerald-800";
      }
      
      // Show/hide appropriate buttons
      updateStatusButtons(newStatus);
    }
    
    // Re-render the items list to reflect changes
    // This will also respect the current tab filtering
    setTimeout(() => {
      console.log("Refreshing items with current tab:", currentTab);
      if (typeof window.switchTab === 'function') {
        window.switchTab(currentTab || 'all');
      } else if (typeof window.filterByTab === 'function') {
        window.filterByTab(currentTab || 'all');
      } else {
        console.error("No tab switching function available");
        // Fallback to reloading all items
        window.fetchTaggedItems();
      }
    }, 500);
    
  } catch (error) {
    console.error("Error updating item status:", error);
    showNotification(error.message, "error");
  }
}

// Control status button visibility based on current status
function updateStatusButtons(status) {
  console.log("Updating status buttons for:", status);
  
  // Get the main status action buttons div
  const statusActionDivs = document.querySelectorAll("#status-action-buttons");
  
  // Get individual buttons
  const approveBtn = document.getElementById("approve-btn");
  const completeBtn = document.getElementById("complete-btn");
  const approveButton = document.getElementById("approve-button");
  const completeButton = document.getElementById("complete-button");
  
  // First hide all buttons
  statusActionDivs.forEach(div => div.classList.add("hidden"));
  
  if (approveBtn) approveBtn.classList.add("hidden");
  if (completeBtn) completeBtn.classList.add("hidden");
  
  // Show appropriate buttons based on status
  if (status === "Registered") {
    // Enable approve buttons
    statusActionDivs.forEach(div => div.classList.remove("hidden"));
    
    if (approveButton) {
      approveButton.classList.remove("hidden");
      approveButton.onclick = () => updateItemStatus("Approved");
    }
    
    if (completeButton) completeButton.classList.add("hidden");
    
    if (approveBtn) {
      approveBtn.classList.remove("hidden");
      approveBtn.onclick = () => updateItemStatus("Approved");
    }
    
    console.log("Showing approve buttons");
  } 
  else if (status === "Approved") {
    // Enable complete buttons
    statusActionDivs.forEach(div => div.classList.remove("hidden"));
    
    if (approveButton) approveButton.classList.add("hidden");
    
    if (completeButton) {
      completeButton.classList.remove("hidden");
      completeButton.onclick = () => updateItemStatus("Completed");
    }
    
    if (completeBtn) {
      completeBtn.classList.remove("hidden");
      completeBtn.onclick = () => updateItemStatus("Completed");
    }
    
    console.log("Showing complete buttons");
  }
  // For all other statuses, keep buttons hidden
}

// Make these functions globally available
window.switchTab = switchTab;
window.updateItemStatus = updateItemStatus;
window.updateStatusButtons = updateStatusButtons;

document.addEventListener("DOMContentLoaded", function () {
    // Initialize currentTab
    currentTab = 'all';
    
    // Show main container with fade-in effect - ensure it's always visible
    const mainContainer = document.getElementById("mainContainer");
    if (mainContainer) {
      mainContainer.style.opacity = "1";
      mainContainer.classList.remove("opacity-0");
      mainContainer.classList.add("opacity-100");
      console.log("Made container visible");
    }
    
    // Fetch all required data with proper initialization
    Promise.all([
      fetchTaggedItems(),
      fetchCategories(),
      fetchLocations(),
      fetchUsers()
    ]).then(() => {
      // Once all data is loaded, ensure items are rendered with correct statuses
      if (window.taggedItems && window.taggedItems.length > 0) {
        console.log("All data loaded, initializing view...");
        switchTab('all');
      }
    }).catch(err => {
      console.error("Error initializing data:", err);
    });
    
    // Setup event listeners
    document.getElementById("itemForm").addEventListener("submit", handleItemFormSubmit);
    document.getElementById("editItemBtn").addEventListener("click", handleEditButtonClick);
    
    // Add event listeners for the modal approve and reject buttons
    const modalApproveBtn = document.getElementById("modal-approve-btn");
    if (modalApproveBtn) {
      modalApproveBtn.addEventListener("click", function() {
        if (currentItemId) {
          updateItemStatus("Approved");
        }
      });
    }
    
    const modalRejectBtn = document.getElementById("modal-reject-btn");
    if (modalRejectBtn) {
      modalRejectBtn.addEventListener("click", function() {
        if (currentItemId) {
          if (confirm("Are you sure you want to reject this student submission?")) {
            updateItemStatus("Rejected");
          }
        }
      });
    }
    
    // Let the onclick attributes handle tab switching
    console.log("DOM loaded, tab functionality initialized");
    
    // Image preview functionality
    document.getElementById("image").addEventListener("change", function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          document.getElementById("imagePreview").src = e.target.result;
          document.getElementById("imagePreviewContainer").classList.remove("hidden");
        }
        reader.readAsDataURL(file);
      }
    });
  });
