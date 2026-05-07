// ==========================================
// 1. CART LOGIC
// ==========================================
async function updateCartCount(){
  const res = await fetch('/cart');
  const data = await res.json();
  const count = data.cart.reduce((s,i)=>s+i.qty,0);
  document.getElementById('cart-count').textContent = count;
}
updateCartCount();

function openCart(){ 
  document.getElementById('cart-modal').style.display='block'; 
  renderCart(); 
}

function closeCart(){ 
  document.getElementById('cart-modal').style.display='none'; 
}

async function clearCart(){
  const res = await fetch('/cart/clear', { method: 'POST' });
  const data = await res.json();
  document.getElementById('cart-items').innerHTML = '';
  document.getElementById('cart-total').textContent = `Total: ₦0`;
  updateCartCount();
  closeCart();
  showToast("Cart cleared successfully");
}

async function renderCart(){
  const res = await fetch('/cart');
  const data = await res.json();
  const ul = document.getElementById('cart-items');
  ul.innerHTML = '';
  let total = 0;

  data.cart.forEach(it => {
    const li = document.createElement('li');
    li.style.display = 'flex';
    li.style.alignItems = 'center';
    li.style.gap = '10px';

    const text = document.createElement('span');
    text.textContent = `${it.name} x${it.qty} — ₦${(it.price * it.qty).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    li.appendChild(text);

    if(it.product_type){
      const type = document.createElement('div');
      type.style.fontSize = '12px';
      type.style.opacity = '0.7';
      type.textContent = `Type: ${it.product_type}`;
      li.appendChild(type);
    }

    const colorWrapper = document.createElement('div');
    colorWrapper.style.display = 'flex';
    colorWrapper.style.alignItems = 'center';
    colorWrapper.style.gap = '6px';

    if(it.color_hex){
      const swatch = document.createElement('div');
      swatch.style.width = '16px';
      swatch.style.height = '16px';
      swatch.style.borderRadius = '4px';
      swatch.style.backgroundColor = it.color_hex;
      swatch.style.border = '1px solid #000';
      colorWrapper.appendChild(swatch);
    }

    const cname = document.createElement('span');
    cname.textContent = it.color_name ? it.color_name : "No color selected";
    colorWrapper.appendChild(cname);
    li.appendChild(colorWrapper);

    const del = document.createElement('button');
    del.textContent = 'Delete';
    del.onclick = async ()=>{
      await fetch('/cart/remove', {
          method:'POST', 
          headers:{'Content-Type':'application/json'}, 
          body: JSON.stringify({product_id: it.product_id})
      });
      renderCart(); 
      updateCartCount();
    };
    li.appendChild(del);

    ul.appendChild(li);
    total += it.price * it.qty;
  });

  document.getElementById('cart-total').textContent = 
    `Total: ₦${total.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
}

async function addToCart(pid, qty=1, color=null, unit=null){
  const payload = {
    product_id: pid,
    qty: qty,
    unit: unit,
    color_name: color ? color.name : null,
    color_hex: color ? color.hex : null
  };

  const res = await fetch('/cart/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
  });

  const data = await res.json();
  if(data.status){
    updateCartCount();
    showToast('Added to cart');
  }
}

function confirmQuantity(){
  const qty  = parseFloat(document.getElementById("qty-input").value);
  const unit = document.getElementById("unit-input").value;

  if(!qty || qty <= 0){
    alert("Enter valid quantity");
    return;
  }

  window.selectedQty = qty;
  window.selectedUnit = unit;
  openColorModal(window.qtyProductId || null, "Select Color");

  if(typeof closeQtyModal === 'function') closeQtyModal();
}

function showToast(message) {
  const toast = document.getElementById('toast');
  if(!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 4000);
}

function proceedToCheckout(){
  window.location.href='/checkout';
}


// ==========================================
// 2. NEW SMART COLOR SELECTION LOGIC (API POWERED)
// ==========================================
let globalColorCatalog = [];

// Fetch the Global Color API instantly in the background
fetch('https://raw.githubusercontent.com/bahamas10/css-color-names/master/css-color-names.json')
    .then(response => response.json())
    .then(data => {
        for (const [colorName, hexCode] of Object.entries(data)) {
            globalColorCatalog.push({
                name: colorName.charAt(0).toUpperCase() + colorName.slice(1), 
                hex: hexCode.toUpperCase()
            });
        }
        console.log("Global Color API Loaded:", globalColorCatalog.length, "colors ready.");
    })
    .catch(err => console.error("Failed to load Color API:", err));

let pendingCartItem = {
    id: null,
    name: "",
    qty: 1,
    unit: "buckets",
    colorName: "",
    colorHex: ""
};

window.openColorModal = function(productId, productName) {
    if(event) event.preventDefault();
    
    pendingCartItem.id = productId;
    pendingCartItem.name = productName;
    pendingCartItem.qty = window.selectedQty || 1;
    pendingCartItem.unit = window.selectedUnit || "buckets";
    pendingCartItem.colorName = "";
    pendingCartItem.colorHex = "";

    const nameEl = document.getElementById('color-product-name');
    if(nameEl) nameEl.innerText = productName;
    
    const inputEl = document.getElementById('color-input');
    if(inputEl) inputEl.value = "";
    
    const suggestionsBox = document.getElementById('color-suggestions');
    if(suggestionsBox) suggestionsBox.innerHTML = "";
    
    // Reset the Preview Screen Safely
    const largePreview = document.getElementById('live-color-preview');
    const largeName = document.getElementById('live-color-name');
    if (largePreview) {
        largePreview.style.backgroundColor = "transparent";
        largePreview.style.borderColor = "#eaeaea";
    }
    if (largeName) {
        largeName.innerText = "Search to preview a color";
    }

    const modal = document.getElementById('color-modal');
    if(modal) modal.style.display = "block"; 
};

window.closeColorModal = function() {
    const modal = document.getElementById('color-modal');
    if(modal) modal.style.display = "none";
};

// Live Engine for Typing & Rendering
const colorInputEl = document.getElementById('color-input');
if (colorInputEl) {
    colorInputEl.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        const suggestionsBox = document.getElementById('color-suggestions');
        const largePreview = document.getElementById('live-color-preview');
        const largeName = document.getElementById('live-color-name'); // Might be missing in HTML, handled safely now
        
        suggestionsBox.innerHTML = "";

        if (query.length === 0) {
            if(largePreview) {
                largePreview.style.backgroundColor = "transparent";
                largePreview.style.borderColor = "#eaeaea";
            }
            if(largeName) largeName.innerText = "Search to preview a color";
            return;
        }

        // 1. Is it a valid global color code?
        const tempDiv = document.createElement("div");
        tempDiv.style.color = query;
        if (tempDiv.style.color !== "") {
            if(largePreview) {
                largePreview.style.backgroundColor = query;
                largePreview.style.borderColor = "#333";
            }
            if(largeName) largeName.innerText = query.toUpperCase();
            
            pendingCartItem.colorName = query;
            pendingCartItem.colorHex = query; 
        } else {
            if(largePreview) {
                largePreview.style.backgroundColor = "transparent";
                largePreview.style.borderColor = "#eaeaea";
            }
            if(largeName) largeName.innerText = "Searching...";
        }

        // 2. Build the Grid of Square + Name Combos with Hardcoded Inline CSS (Bulletproof)
        const matches = globalColorCatalog.filter(c => c.name.toLowerCase().includes(query)).slice(0, 30);

        // Ensure the grid layout is applied to the suggestions box
        suggestionsBox.style.display = "grid";
        suggestionsBox.style.gridTemplateColumns = "repeat(auto-fill, minmax(80px, 1fr))";
        suggestionsBox.style.gap = "15px";

        matches.forEach(color => {
            const wrapper = document.createElement('div');
            wrapper.style.display = "flex";
            wrapper.style.flexDirection = "column";
            wrapper.style.alignItems = "center";
            wrapper.style.gap = "6px";
            wrapper.style.cursor = "pointer";
            wrapper.style.transition = "transform 0.15s ease";
            
            const square = document.createElement('div');
            square.style.width = "100%";
            square.style.aspectRatio = "1/1";
            square.style.backgroundColor = color.hex;
            square.style.border = "3px solid #bbb";
            square.style.borderRadius = "12px";
            square.style.boxShadow = "0 4px 8px rgba(0,0,0,0.15)";
            square.style.transition = "border-color 0.15s ease, box-shadow 0.15s ease";
            
            const label = document.createElement('span');
            label.style.fontSize = "0.75em";
            label.style.fontWeight = "bold";
            label.style.textAlign = "center";
            label.style.color = "#333";
            label.innerText = color.name;

            wrapper.appendChild(square);
            wrapper.appendChild(label);

            // Hover effects
            wrapper.onmouseover = () => {
                wrapper.style.transform = "scale(1.1)";
                square.style.borderColor = "#000";
                square.style.boxShadow = "0 8px 16px rgba(0,0,0,0.3)";
            };
            wrapper.onmouseout = () => {
                wrapper.style.transform = "scale(1)";
                square.style.borderColor = "#bbb";
                square.style.boxShadow = "0 4px 8px rgba(0,0,0,0.15)";
            };

            // When clicked, send to preview screen
            wrapper.onclick = () => {
                if(largePreview) {
                    largePreview.style.backgroundColor = color.hex;
                    largePreview.style.borderColor = "#333";
                }
                if(largeName) {
                    largeName.innerText = color.name;
                }
                
                document.getElementById('color-input').value = color.name;
                pendingCartItem.colorName = color.name;
                pendingCartItem.colorHex = color.hex;
                
                suggestionsBox.innerHTML = ""; 
            };

            suggestionsBox.appendChild(wrapper);
        });
    });
}

// Confirm Button Add to Cart
const confirmColorBtn = document.getElementById('confirm-color-btn');
if (confirmColorBtn) {
    confirmColorBtn.addEventListener('click', async () => {
        if (!pendingCartItem.colorName) {
            alert("Please search for a valid color or click a square to select one.");
            return;
        }

        try {
            await addToCart(
                pendingCartItem.id,
                pendingCartItem.qty,
                { name: pendingCartItem.colorName, hex: pendingCartItem.colorHex },
                pendingCartItem.unit
            );

            closeColorModal();
            
            if (typeof renderCart === 'function') renderCart();
            if (typeof recalculateCartTotalUI === 'function') recalculateCartTotalUI();
            
        } catch (err) {
            console.error(err);
            alert('Error adding product to cart.');
        }
    });
}


// ==========================================
// 3. RATING SYSTEM & FAQS
// ==========================================
document.addEventListener('DOMContentLoaded', function(){
  const starWidget = document.getElementById('star-widget');
  
  if(starWidget){
    const stars = Array.from(starWidget.querySelectorAll('.star'));
    let selected = 0;
    
    // Safely grab the product ID from the HTML data attribute
    const pid = starWidget.dataset.pid || (typeof PRODUCT_ID !== 'undefined' ? PRODUCT_ID : null);

    // Function to visually fill the stars
    function setStars(val){
      stars.forEach(s => { 
        if(parseInt(s.dataset.value) <= val){
          s.classList.add('active'); 
          s.textContent='★'; 
        } else { 
          s.classList.remove('active'); 
          s.textContent='☆'; 
        } 
      });
    }

    // Add hover and click effects to the stars
    stars.forEach(s => {
      s.addEventListener('mouseover', () => setStars(parseInt(s.dataset.value)));
      s.addEventListener('mouseout', () => setStars(selected));
      s.addEventListener('click', () => { 
        selected = parseInt(s.dataset.value); 
        setStars(selected); 
      });
    });

    // Handle the actual submission
    const submitBtn = document.getElementById('submit-rating');
    if(submitBtn) {
        submitBtn.addEventListener('click', async () => {
          const starsVal = selected;
          
          // SAFELY grab the inputs to prevent silent JavaScript crashes
          const commentEl = document.getElementById('rating-comment');
          const comment = commentEl ? commentEl.value.trim() : "";
          
          const orderRefEl = document.getElementById('order-ref');
          const orderRef = orderRefEl ? orderRefEl.value.trim() : null;

          if(!starsVal){ 
              alert('Please select a star rating first.'); 
              return; 
          }

          if(!pid) {
              alert('Error: Product ID is missing from the page.');
              return;
          }

          // UI feedback while sending to server
          const feedbackEl = document.getElementById('rating-feedback');
          if(feedbackEl) {
              feedbackEl.style.color = "#007bff"; // Blue for loading
              feedbackEl.textContent = 'Submitting your rating...';
          }
          submitBtn.disabled = true;

          try {
              const resp = await fetch('/rate', {
                  method: 'POST', 
                  headers: {'Content-Type': 'application/json'}, 
                  // Send null for order_ref if the box is empty, so the backend doesn't crash
                  body: JSON.stringify({
                      product_id: pid, 
                      stars: starsVal, 
                      comment: comment, 
                      order_ref: orderRef || null 
                  })
              });

              const data = await resp.json();
              
              if(data.status){
                // Success!
                if(feedbackEl) {
                    feedbackEl.style.color = "green";
                    feedbackEl.textContent = 'Thanks for your rating!';
                }
                
                // Clear the input boxes so they don't submit twice
                if(commentEl) commentEl.value = ""; 
                if(orderRefEl) orderRefEl.value = ""; 
                
                // Update the visual charts with the new math
                renderRatings(data.summary);
              } else {
                // Failed (Likely because order wasn't delivered yet)
                if(feedbackEl) {
                    feedbackEl.style.color = "red";
                    feedbackEl.textContent = data.message || 'Error saving rating.';
                }
                alert(data.message || 'Error saving rating. Ensure your order reference is valid and marked as delivered.');
              }
          } catch(err) {
              console.error("Rating submission error:", err);
              if(feedbackEl) {
                  feedbackEl.style.color = "red";
                  feedbackEl.textContent = "Failed to connect to the server.";
              }
          } finally {
              // Re-enable the button
              submitBtn.disabled = false;
          }
        });
    }

    // Fetch initial ratings summary when the page loads
    if(pid) {
        fetch(`/ratings-summary?product_id=${pid}`)
          .then(r => r.json())
          .then(d => {
            if(d.status) renderRatings(d.summary);
          })
          .catch(err => console.error("Error fetching ratings summary:", err));
    }

    // Safely update the DOM and Chart.js with the new math
    function renderRatings(summary){
        if(!summary) return;
        
        const avgRatingEl = document.getElementById('avg-rating');
        if(avgRatingEl) avgRatingEl.textContent = summary.average.toFixed(2);
        
        const totalRatingsEl = document.getElementById('total-ratings');
        if(totalRatingsEl) totalRatingsEl.textContent = summary.total;
        
        const avg = Math.round(summary.average);
        setStars(avg);
        selected = avg; // Lock the stars visually to the average
        
        const canvasEl = document.getElementById('ratingsPie');
        if (canvasEl) {
            const ctx = canvasEl.getContext('2d');
            if(window._ratingsChart) { 
                // Update existing chart
                window._ratingsChart.data.datasets[0].data = summary.values; 
                window._ratingsChart.update(); 
                return; 
            }

            // Create new chart (Make sure Chart.js is imported in your HTML)
            if(typeof Chart !== 'undefined') {
                window._ratingsChart = new Chart(ctx, {
                    type: 'pie',
                    data: { 
                        labels: summary.labels, 
                        datasets: [{ 
                            data: summary.values, 
                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'] 
                        }] 
                    },
                    options: { responsive:true }
                });
            }
        }
    }
  }

  // FAQs Toggle Logic
  document.querySelectorAll('.faq-question').forEach(q => {
    q.addEventListener('click', ()=> {
        q.nextElementSibling.classList.toggle('open');
    });
  });
});


// ==========================================
// 4. SMOOTH SCROLLING
// ==========================================
(function () {
  if (window.matchMedia("(max-width: 768px)").matches) {
    return;
  }

  let currentScroll = window.scrollY;
  let targetScroll = window.scrollY;

  const ease = 0.06;
  const maxDelta = 120;

  window.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();

      targetScroll += e.deltaY;
      targetScroll = Math.max(
        0,
        Math.min(
          targetScroll,
          document.documentElement.scrollHeight - window.innerHeight
        )
      );
    },
    { passive: false }
  );

  function animateScroll() {
    currentScroll += (targetScroll - currentScroll) * ease;
    window.scrollTo(0, currentScroll);
    requestAnimationFrame(animateScroll);
  }

  animateScroll();
})();


// ==========================================
// 5. CAMERA & FACE CAPTURE LOGIC
// ==========================================
let stream = null;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const imageInput = document.getElementById('image');
const facePreview = document.getElementById('facePreview');
const faceError = document.getElementById('faceError');
const startCameraBtn = document.getElementById('startCamera');

if (startCameraBtn) {
    startCameraBtn.onclick = async () => {
      if (!stream) {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        video.play();
      }
    };
}

function capture() {
  if (!stream) return;

  const size = 300;
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, size, size);
  ctx.save();
  ctx.beginPath();
  ctx.arc(size/2, size/2, size/2, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();
  ctx.drawImage(video, 0, 0, size, size);
  ctx.restore();

  const dataURL = canvas.toDataURL('image/png');

  if (!isLikelyFace(ctx, size)) {
    faceError.style.display = 'block';
    return;
  }

  faceError.style.display = 'none';
  imageInput.value = dataURL;

  facePreview.src = dataURL;
  facePreview.style.display = 'block';

  stopCamera();
}

function isLikelyFace(ctx, size) {
  const imageData = ctx.getImageData(0, 0, size, size).data;
  let brightPixels = 0;

  for (let i = 0; i < imageData.length; i += 4) {
    const brightness = (imageData[i] + imageData[i+1] + imageData[i+2]) / 3;
    if (brightness > 60) brightPixels++;
  }
  return brightPixels > (size * size * 0.25);
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
    video.style.display = 'none';
  }
}

function validateFaceAndProceed() {
  if (!imageInput.value) {
    faceError.style.display = 'block';
    return;
  }
  nextPhase(4);
}

function nextPhase(current) {
  document.getElementById(`phase${current}`).style.display = 'none';
  document.getElementById(`phase${current + 1}`).style.display = 'block';
}

function prevPhase(current) {
  document.getElementById(`phase${current}`).style.display = 'none';
  document.getElementById(`phase${current - 1}`).style.display = 'block';
}

if (facePreview) {
    facePreview.onclick = () => {
      const win = window.open();
      win.document.write(`<img src="${facePreview.src}" style="width:100%">`);
    };
}


// ==========================================
// 6. LOCATION DATA DROPDOWNS
// ==========================================
const locationData = {
  Nigeria: {
    "Abia": ["Aba North","Aba South","Arochukwu","Bende","Ikwuano","Isiala Ngwa North","Isiala Ngwa South","Isuikwuato","Obi Ngwa","Ohafia","Osisioma","Ugwunagbo","Ukwa East","Ukwa West","Umuahia North","Umuahia South","Umu Nneochi"],
  "Adamawa": ["Demsa","Fufore","Ganaye","Ganye","Girei","Gombi","Guyuk","Hong","Jada","Lamurde","Madagali","Maiha","Mayo Belwa","Michika","Mubi North","Mubi South","Numan","Shelleng","Song","Toungo","Yola North","Yola South"],
  "Akwa Ibom": ["Abak","Eastern Obolo","Eket","Esit Eket","Essien Udim","Etim Ekpo","Etinan","Ibeno","Ibesikpo Asutan","Ibiono Ibom","Ika","Ikono","Ikot Abasi","Ikot Ekpene","Ini","Itu","Mbo","Mkpat Enin","Nsit Atai","Nsit Ibom","Nsit Ubium","Obot Akara","Okobo","Onna","Oron","Oruk Anam","Udung Uko","Ukanafun","Uruan","Urue-Offong/Oruko","Uyo"],
  "Anambra": ["Aguata","Anambra East","Anambra West","Anaocha","Awka North","Awka South","Ayamelum","Dunukofia","Ekwusigo","Idemili North","Idemili South","Ihiala","Njikoka","Nnewi North","Nnewi South","Ogbaru","Onitsha North","Onitsha South","Orumba North","Orumba South","Oyi"],
  "Bauchi": ["Alkaleri","Bauchi","Bogoro","Damban","Darazo","Dass","Ganjuwa","Giade","Itas/Gadau","Jamaare","Katagum","Kirfi","Misau","Ningi","Shira","Tafawa Balewa","Toro","Warji","Zaki"],
  "Bayelsa": ["Brass","Ekeremor","Kolokuma/Opokuma","Nembe","Ogbia","Sagbama","Southern Ijaw","Yenagoa"],
  "Benue": ["Ado","Agatu","Apa","Buruku","Gboko","Guma","Gwer East","Gwer West","Katsina-Ala","Konshisha","Kwande","Logo","Makurdi","Ogbadibo","Ohimini","Oju","Okpokwu","Otukpo","Tarka","Ukum","Ushongo","Vandeikya"],
  "Borno": ["Abadam","Bama","Bayo","Biu","Chibok","Damboa","Dikwa","Gubio","Guzamala","Gwoza","Hawul","Jere","Kaga","Kala/Balge","Konduga","Kukawa","Kwaya Kusar","Mafa","Magumeri","Maiduguri","Marte","Mobbar","Monguno","Ngala","Nganzai","Shani"],
  "Cross River": ["Akpabuyo","Akamkpa","Bakassi","Bekwara","Biase","Boki","Calabar Municipal","Calabar South","Etung","Ikom","Obanliku","Obubra","Obudu","Odukpani","Ogoja","Yakuur","Yala"],
  "Delta": ["Aniocha North","Aniocha South","Bomadi","Burutu","Ethiope East","Ethiope West","Ika North East","Ika South","Isoko North","Isoko South","Ndokwa East","Ndokwa West","Okpe","Oshimili North","Oshimili South","Patani","Sapele","Udu","Ughelli North","Ughelli South","Ukwuani","Uvwie","Warri North","Warri South","Warri South West"],
  "Ebonyi": ["Abakaliki","Afikpo North","Afikpo South","Ebonyi","Ezza North","Ezza South","Ikwo","Ishielu","Ivo","Ohaozara","Ohaukwu","Onicha"],
  "Edo": ["Akoko-Edo","Egor","Esan Central","Esan North-East","Esan South-East","Esan West","Etsako Central","Etsako East","Etsako West","Igueben","Ikpoba-Okha","Oredo","Orhionmwon","Ovia North-East","Ovia South-West","Owan East","Owan West","Uhunmwonde"],
  "Ekiti": ["Ado-Ekiti","Ekiti East","Ekiti South-West","Ekiti West","Emure","Gbonyin","Ido-Osi","Ijero","Ikere","Ikole","Irepodun/Ifelodun","Ise/Orun","Moba","Oye"],
  "Enugu": ["Aninri","Awgu","Enugu East","Enugu North","Enugu South","Ezeagu","Igbo Etiti","Igbo Eze North","Igbo Eze South","Isi Uzo","Nkanu East","Nkanu West","Nsukka","Oji River","Udenu","Udi","Uzo-Uwani"],
  "Gombe": ["Akko","Balanga","Billiri","Dukku","Funakaye","Gombe","Kaltungo","Kwami","Nafada","Shongom","Yamaltu/Deba"],
  "Imo": ["Aboh Mbaise","Ahiazu Mbaise","Ehime Mbano","Ezinihitte","Ideato North","Ideato South","Ihitte/Uboma","Ikeduru","Isiala Mbano","Isu","Mbaitoli","Ngor Okpala","Njaba","Nkwerre","Nwangele","Obowo","Oguta","Ohaji/Egbema","Onuimo","Orlu","Orsu","Oru East","Owerri Municipal","Owerri North","Owerri West","Ukwa East","Ukwa West","Unuimo","Umuaka"],
  "Jigawa": ["Auyo","Babura","Biriniwa","Birnin Kudu","Buji","Dutse","Gagarawa","Garki","Gumel","Guri","Gwaram","Gwiwa","Hadejia","Jahun","Kafin Hausa","Kaugama","Kazaure","Kiri Kasama","Kiyawa","Maigatari","Malam Madori","Miga","Ringim","Roni","Sule Tankarkar","Taura","Yankwashi"],
  "Kaduna": ["Birnin Gwari","Chikun","Giwa","Igabi","Ikara","Jaba","Jema'a","Kachia","Kaduna North","Kaduna South","Kagarko","Kajuru","Kaura","Kauru","Kubau","Kudan","Lere","Makarfi","Sabon Gari","Sanga","Soba","Zangon Kataf","Zaria"],
  "Kano": ["Ajingi","Albasu","Bagwai","Bebeji","Bichi","Bunkure","Dala","Dambatta","Dawakin Kudu","Dawakin Tofa","Doguwa","Fagge","Gabasawa","Garko","Garun Mallam","Gaya","Gezawa","Gwale","Gwarzo","Kabo","Kano Municipal","Kumbotso","Kunchi","Kura","Madobi","Makoda","Minjibir","Nasarawa","Rano","Rimin Gado","Rogo","Shanono","Sumaila","Takai","Tarauni","Tofa","Tsanyawa","Tudun Wada","Ungogo","Warawa","Wudil"],
  "Katsina": ["Bakori","Batagarawa","Batsari","Baure","Bindawa","Charanchi","Dandume","Danja","Dutsi","Dutsin Ma","Faskari","Funtua","Ingawa","Jibia","Kafur","Kaita","Kankara","Kankia","Kusada","Mai'Adua","Malumfashi","Mani","Mashi","Matazu","Musawa","Rimi","Sabuwa","Safana","Sandamu","Zango"],
  "Kebbi": ["Aliero","Arewa Dandi","Argungu","Augie","Bagudo","Birnin Kebbi","Bunza","Dandi","Fakai","Gwandu","Jega","Kalgo","Koko/Besse","Maiyama","Ngaski","Sakaba","Shanga","Suru","Wasagu/Danko","Yauri"],
  "Kogi": ["Adavi","Ajaokuta","Ankpa","Bassa","Dekina","Ibaji","Idah","Igalamela-Odolu","Ijumu","Ikare","Kabba/Bunu","Kogi","Lokoja","Mopa-Muro","Ofu","Ogori/Magongo","Okehi","Okene","Olamaboro","Omala","Yagba East","Yagba West","Mopa-Muro"],
  "Kwara": ["Asa","Baruten","Edu","Ekiti","Ifelodun","Ilorin East","Ilorin West","Irepodun","Isin","Kaiama","Moro","Offa","Oke Ero","Oyun","Patigi"],
  "Lagos": ["Agege","Ajeromi-Ifelodun","Alimosho","Amuwo-Odofin","Apapa","Badagry","Epe","Eti-Osa","Ibeju-Lekki","Ifako-Ijaiye","Ikeja","Ikorodu","Kosofe","Lagos Island","Lagos Mainland","Mushin","Ojo","Oshodi-Isolo","Shomolu","Surulere"],
  "Nasarawa": ["Akwanga","Awe","Doma","Karu","Keana","Keffi","Kokona","Lafia","Nasarawa","Nasarawa Egon","Obi","Toto","Wamba"],
  "Niger": ["Agaie","Agwara","Bida","Borgu","Bosso","Chanchaga","Edati","Gbako","Katcha","Kontagora","Lapai","Lavun","Magama","Mariga","Mokwa","Muya","Paikoro","Rafi","Rijau","Shiroro","Suleja","Tafa","Wushishi"],
  "Ogun": ["Abeokuta North","Abeokuta South","Ado-Odo/Ota","Ewekoro","Ijebu East","Ijebu North","Ijebu North East","Ijebu Ode","Ikenne","Imeko Afon","Ipokia","Obafemi-Owode","Odeda","Odogbolu","Remo North","Shagamu","Yewa North","Yewa South"],
  "Ondo": ["Akoko North-East","Akoko North-West","Akoko South-East","Akoko South-West","Ese Odo","Idanre","Ifedore","Ilaje","Ile Oluji/Okeigbo","Irele","Odigbo","Okitipupa","Ondo East","Ondo West","Ose","Owo"],
  "Osun": ["Aiyedaade","Aiyedire","Atakunmosa East","Atakunmosa West","Boluwaduro","Boripe","Ede North","Ede South","Egbedore","Ejigbo","Ife Central","Ife East","Ife North","Ife South","Ifedayo","Ifelodun","Ila","Ilesa East","Ilesa West","Irepodun","Irewole","Isokan","Iwo","Obokun","Odo-Otin","Ola-Oluwa","Olorunda","Oriade","Orolu","Osogbo"],
  "Oyo": ["Afijio","Akinyele","Atiba","Atisbo","Egbeda","Ibadan North","Ibadan North-East","Ibadan North-West","Ibadan South-East","Ibadan South-West","Ibarapa Central","Ibarapa East","Ibarapa North","Irepo","Iseyin","Itesiwaju","Iwajowa","Kajola","Lagelu","Ogo Oluwa","Ogbomosho North","Ogbomosho South","Olorunsogo","Oluyole","Ona Ara","Orelope","Orire","Oyo East","Oyo West","Saki East","Saki West","Surulere","Irepo"],
  "Plateau": ["Bokkos","Barkin Ladi","Bassa","Batu","Bokkos","Jos East","Jos North","Jos South","Kanam","Kanke","Langtang North","Langtang South","Mangu","Mikang","Pankshin","Qua'an Pan","Riyom","Shendam","Wase"],
  "Rivers": ["Abua/Odual","Ahoada East","Ahoada West","Akuku-Toru","Andoni","Asari-Toru","Bonny","Degema","Eleme","Emohua","Etche","Gokana","Ikwerre","Khana","Obio/Akpor","Ogba/Egbema/Ndoni","Ogu/Bolo","Okrika","Omuma","Opobo/Nkoro","Oyigbo","Port Harcourt","Tai"],
  "Sokoto": ["Binji","Bodinga","Dange Shuni","Gada","Goronyo","Gudu","Gwadabawa","Illela","Isa","Kebbe","Kware","Rabah","Sabon Birni","Shagari","Silame","Sokoto North","Sokoto South","Tambuwal","Tangaza","Tureta","Wamako","Wurno","Yabo"],
  "Taraba": ["Ardo Kola","Bali","Donga","Gashaka","Gassol","Ibi","Jalingo","Karim Lamido","Kurmi","Lau","Sardauna","Takum","Ussa","Wukari","Yorro","Zing"],
  "Yobe": ["Bade","Bursari","Damaturu","Fika","Fune","Gashua","Gujba","Gulani","Jakusko","Karasuwa","Machina","Nangere","Nguru","Potiskum","Tarmuwa","Yunusari","Yusufari"],
  "Zamfara": ["Anka","Bakura","Birnin Magaji","Bukkuyum","Chafe","Gummi","Gusau","Kaura Namoda","Maradun","Shinkafi","Talata Mafara","Tsafe","Zurmi"],
  },
  Ghana: {
    "Greater Accra": ["Accra Metropolitan","Tema Metropolitan"],
    "Ashanti": ["Kumasi Metropolitan"]
  },
  Cameroine: {
    "Littoral": ["Wouri"],
    "Centre": ["Mfoundi"]
  },
  Niger: {
    "Niamey": ["Niamey I","Niamey II","Niamey III"]
  },
  Benin: {
    "Littoral": ["Cotonou"],
    "Atlantique": ["Abomey-Calavi"]
  },
  Chad: {
    "N'Djamena": ["N'Djamena"]
  }
};

const countrySelect = document.getElementById("country");
const stateSelect = document.getElementById("state");
const lgaSelect = document.getElementById("lga");

if (countrySelect && stateSelect && lgaSelect) {
    countrySelect.addEventListener("change", () => {
      stateSelect.innerHTML = '<option value="">Select State</option>';
      lgaSelect.innerHTML = '<option value="">Select L.G.A</option>';

      const states = locationData[countrySelect.value];
      if (states) {
        Object.keys(states).forEach(state => {
          const option = document.createElement("option");
          option.value = state;
          option.textContent = state;
          stateSelect.appendChild(option);
        });
      }
    });

    stateSelect.addEventListener("change", () => {
      lgaSelect.innerHTML = '<option value="">Select L.G.A</option>';

      const lgas = locationData[countrySelect.value]?.[stateSelect.value];
      if (lgas) {
        lgas.forEach(lga => {
          const option = document.createElement("option");
          option.value = lga;
          option.textContent = lga;
          lgaSelect.appendChild(option);
        });
      }
    });
}

// ==========================================
// 7. PICKUP VERIFICATION
// ==========================================
async function verifyPickup(code, btn) {
    try {
        const res = await fetch('/admin/verify-pickup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pickup_code: code })
        });
        const data = await res.json();
        alert(data.message);

        if (data.success) {
            const row = btn.closest('tr');
            if (row) {
               const statusCell = row.querySelector('.delivered-status');
               if (statusCell) statusCell.textContent = 'Yes';
            }
            btn.disabled = true;
            btn.textContent = 'Verified';
        }
    } catch (err) {
        console.error(err);
        alert('Error verifying pickup code');
    }
}
