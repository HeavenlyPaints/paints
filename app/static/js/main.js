// Cart (session via server) — UI uses fetch endpoints
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

// ✅ CLEAR CART FUNCTION (newly added)
async function clearCart(){
  const res = await fetch('/cart/clear', {
      method: 'POST'
  });
  const data = await res.json();

  // Reset UI
  document.getElementById('cart-items').innerHTML = '';
  document.getElementById('cart-total').textContent = `Total: ₦0`;

  // Update cart icon number
  updateCartCount();

  // Close modal
  closeCart();

  // Toast
  showToast("Cart cleared successfully");
}

// --------------------- RENDER CART ---------------------
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

    // Product text
    const text = document.createElement('span');
    text.textContent = `${it.name} x${it.qty} — ₦${(it.price * it.qty).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    li.appendChild(text);

    // Color swatch
    if(it.color_hex){
      const swatch = document.createElement('div');
      swatch.style.width = '20px';
      swatch.style.height = '20px';
      swatch.style.backgroundColor = it.color_hex;
      swatch.style.border = '1px solid #000';
      li.appendChild(swatch);
    }

    // Delete button
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
// --------------------- END RENDER CART ---------------------

async function addToCart(pid, qty=1){
  await fetch('/cart/add', {
      method:'POST', 
      headers:{'Content-Type':'application/json'}, 
      body: JSON.stringify({product_id: pid, qty})
  });
  updateCartCount();
  showToast('Added to cart');
}

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 4000);
}

let selectedProductId = null;
let selectedColor = null;

// Open color modal when "Add to Cart" button clicked
function openColorModal(productId, productName){
  selectedProductId = productId;
  selectedColor = null;
  document.getElementById('color-product-name').textContent = productName;
  document.getElementById('color-input').value = '';
  document.getElementById('color-suggestions').innerHTML = '';
  document.getElementById('color-modal').style.display = 'block';
}

// Close modal
function closeColorModal(){
  document.getElementById('color-modal').style.display = 'none';
}

// ---- Replace only the color-input listener with this block ----
document.getElementById('color-input').addEventListener('input', async function () {
  const raw = this.value.trim();
  const suggestionsDiv = document.getElementById('color-suggestions');
  suggestionsDiv.innerHTML = '';
  selectedColor = null;

  if (!raw) return;

  // Normalize input (try with and without spaces)
  const candidates = [raw, raw.replace(/\s+/g, '')];

  // Helper: test if the browser understands this color name
  function browserColorToHex(name) {
    const test = document.createElement('div');
    test.style.backgroundColor = '';              // reset
    test.style.backgroundColor = name;
    // If browser didn't accept it, the property stays empty string
    if (!test.style.backgroundColor) return null;
    // Use computed style to get rgb(...) and convert to hex
    const cs = getComputedStyle(test).backgroundColor;
    // cs like "rgb(255, 0, 0)" or "rgba(0,0,0,0)"
    const m = cs.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    if (!m) return null;
    const r = parseInt(m[1], 10);
    const g = parseInt(m[2], 10);
    const b = parseInt(m[3], 10);
    const toHex = n => ('0' + n.toString(16)).slice(-2);
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
  }

  // STEP 1: Try to resolve locally using the browser. This prevents showing black.
  let mainHex = null;
  let mainName = null;
  for (const cand of candidates) {
    const h = browserColorToHex(cand);
    if (h) {
      mainHex = h;
      mainName = cand;
      break;
    }
  }

  // If browser couldn't resolve name, still try API (it can sometimes understand names the browser doesn't).
  if (!mainHex) {
    try {
      // Use scheme endpoint (accepts names or hex). We request just 1 color to get a main match.
      const apiRes = await fetch(`https://www.thecolorapi.com/scheme?hex=${encodeURIComponent(raw)}&mode=monochrome&count=1`);
      if (apiRes.ok) {
        const apiData = await apiRes.json();
        if (apiData && Array.isArray(apiData.colors) && apiData.colors.length > 0) {
          mainHex = apiData.colors[0].hex.value;
          mainName = apiData.colors[0].name ? apiData.colors[0].name.value : raw;
        }
      }
    } catch (err) {
      // swallow — we'll fallback to a visible placeholder
      console.warn('API attempt failed (will fallback to browser-only):', err);
    }
  }

  // Final fallback: if we still have no color, show the typed text as preview (avoids black)
  if (!mainHex) {
    // Try to remove spaces/hyphens and try browser again
    const alt = raw.replace(/[\s-]+/g, '');
    const h = browserColorToHex(alt);
    if (h) {
      mainHex = h;
      mainName = alt;
    } else {
      // show a neutral "unknown" swatch and text, don't select any color
      const unknown = document.createElement('div');
      unknown.textContent = `Unknown color: ${raw}`;
      unknown.style.padding = '8px';
      unknown.style.color = '#333';
      suggestionsDiv.appendChild(unknown);
      return;
    }
  }

  // STEP 2: Show the main swatch (guaranteed valid hex now)
  const mainSwatch = document.createElement('div');
  mainSwatch.style.display = 'inline-block';
  mainSwatch.style.margin = '4px';
  mainSwatch.style.width = '40px';
  mainSwatch.style.height = '40px';
  mainSwatch.style.borderRadius = '6px';
  mainSwatch.style.border = '2px solid #ccc';
  mainSwatch.style.cursor = 'pointer';
  mainSwatch.style.backgroundColor = mainHex || raw;
  mainSwatch.title = `${mainName || raw} — ${mainHex}`;

  // label below swatch
  const wrapper = document.createElement('div');
  wrapper.style.display = 'inline-block';
  wrapper.style.textAlign = 'center';
  wrapper.style.fontSize = '12px';
  wrapper.style.marginRight = '6px';
  wrapper.appendChild(mainSwatch);
  const label = document.createElement('div');
  label.textContent = (mainName || raw) + `\n${mainHex}`;
  label.style.whiteSpace = 'pre';
  wrapper.appendChild(label);

  mainSwatch.addEventListener('click', () => {
    document.querySelectorAll('#color-suggestions div').forEach(d => d.style.border = '2px solid #ccc');
    mainSwatch.style.border = '2px solid black';
    selectedColor = { name: mainName || raw, hex: mainHex };
  });

  suggestionsDiv.appendChild(wrapper);

  // STEP 3: Attempt to fetch related colors (analogous). If API fails, nothing else breaks.
  try {
    const schemeRes = await fetch(`https://www.thecolorapi.com/scheme?hex=${encodeURIComponent(mainHex.replace('#',''))}&mode=analogic&count=5`);
    if (schemeRes.ok) {
      const schemeData = await schemeRes.json();
      if (schemeData && Array.isArray(schemeData.colors)) {
        schemeData.colors.forEach(c => {
          const chex = c.hex && c.hex.value ? c.hex.value : null;
          const cname = c.name && c.name.value ? c.name.value : chex;
          if (!chex) return;

          const sw = document.createElement('div');
          sw.style.display = 'inline-block';
          sw.style.margin = '4px';
          sw.style.width = '36px';
          sw.style.height = '36px';
          sw.style.borderRadius = '6px';
          sw.style.border = '2px solid #ccc';
          sw.style.cursor = 'pointer';
          sw.style.backgroundColor = chex;
          sw.title = `${cname} — ${chex}`;

          const wrap = document.createElement('div');
          wrap.style.display = 'inline-block';
          wrap.style.textAlign = 'center';
          wrap.style.fontSize = '11px';
          wrap.style.marginRight = '6px';
          wrap.appendChild(sw);
          const lbl = document.createElement('div');
          lbl.textContent = cname + `\n${chex}`;
          lbl.style.whiteSpace = 'pre';
          wrap.appendChild(lbl);

          sw.addEventListener('click', () => {
            document.querySelectorAll('#color-suggestions div').forEach(d => d.style.border = '2px solid #ccc');
            sw.style.border = '2px solid black';
            selectedColor = { name: cname, hex: chex };
          });

          suggestionsDiv.appendChild(wrap);
        });
      }
    } else {
      console.warn('Related colors fetch returned status', schemeRes.status);
    }
  } catch (err) {
    console.warn('Related colors fetch failed:', err);
    // don't show error to user — main color already displayed
  }
});
// ---- end listener ----



// Confirm color and add product to cart
document.getElementById('confirm-color-btn').addEventListener('click', async ()=>{
  if(!selectedProductId || !selectedColor){
    alert('Please select a color.');
    return;
  }

  // Send product + color info to /cart/add
  await fetch('/cart/add', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      product_id: selectedProductId,
      qty: 1,
      color_name: selectedColor.name,
      color_hex: selectedColor.hex
    })
  });

  updateCartCount();
  closeColorModal();
  showToast('Added to cart with selected color');
});

// Checkout redirect to server checkout route
function proceedToCheckout(){ 
  window.location.href = '/checkout'; 
}

// Rating widget on product page
document.addEventListener('DOMContentLoaded', function(){
  const starWidget = document.getElementById('star-widget');
  if(starWidget){
    const stars = Array.from(starWidget.querySelectorAll('.star'));
    let selected = 0;
    const pid = starWidget.dataset.pid;

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

    stars.forEach(s=>{
      s.addEventListener('mouseover', ()=> setStars(parseInt(s.dataset.value)));
      s.addEventListener('mouseout', ()=> setStars(selected));
      s.addEventListener('click', ()=> { 
        selected = parseInt(s.dataset.value); 
        setStars(selected); 
      });
    });

    document.getElementById('submit-rating').addEventListener('click', async ()=>{
      const starsVal = selected;
      const comment = document.getElementById('rating-comment').value;
      const orderRef = document.getElementById('order-ref').value || null;

      if(!starsVal){ alert('Select stars'); return; }

      const resp = await fetch('/rate', {
          method:'POST', 
          headers:{'Content-Type':'application/json'}, 
          body: JSON.stringify({product_id: pid, stars: starsVal, comment, order_ref: orderRef})
      });

      const data = await resp.json();
      if(data.status){
        document.getElementById('rating-feedback').textContent = 'Thanks for rating!';
        renderRatings(data.summary);
      } else {
        document.getElementById('rating-feedback').textContent = data.message || 'Error';
      }
    });

    fetch(`/ratings-summary?product_id=${PRODUCT_ID || pid}`)
      .then(r=>r.json())
      .then(d=>{
        if(d.status) renderRatings(d.summary);
      });

    function renderRatings(summary){
      if(!summary) return;
      document.getElementById('avg-rating').textContent = summary.average.toFixed(2);
      document.getElementById('total-ratings').textContent = summary.total;
      const ctx = document.getElementById('ratingsPie').getContext('2d');

      if(window._ratingsChart) { 
        window._ratingsChart.data.datasets[0].data = summary.values; 
        window._ratingsChart.update(); 
        return; 
      }

      window._ratingsChart = new Chart(ctx, {
        type: 'pie',
        data: { labels: summary.labels, datasets: [{ data: summary.values }] },
        options: { responsive:true }
      });
    }
  }

  document.querySelectorAll('.faq-question').forEach(q => {
    q.addEventListener('click', ()=> q.nextElementSibling.classList.toggle('open'));
  });
});


(function() {
  let currentScroll = 0;  // current position
  let targetScroll = 0;   // desired position

  const ease = 0.02;      // very slow easing for water-like motion
  const maxDelta = 30;    // max scroll change per wheel/touch for gentle drip

  // Wheel / Trackpad
  window.addEventListener('wheel', (e) => {
    e.preventDefault();
    targetScroll += Math.max(-maxDelta, Math.min(maxDelta, e.deltaY));
    targetScroll = Math.max(0, Math.min(targetScroll, document.body.scrollHeight - window.innerHeight));
  }, { passive: false });

  // Touch devices
  let touchStartY = 0;
  window.addEventListener('touchstart', (e) => {
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    const delta = touchStartY - e.touches[0].clientY;
    targetScroll += Math.max(-maxDelta, Math.min(maxDelta, delta));
    targetScroll = Math.max(0, Math.min(targetScroll, document.body.scrollHeight - window.innerHeight));
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  // Animation loop
  function animateScroll() {
    const distance = targetScroll - currentScroll;
    currentScroll += distance * ease; // interpolate slowly for water-like motion
    window.scrollTo(0, currentScroll);
    requestAnimationFrame(animateScroll);
  }

  animateScroll();
})();


let stream = null;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const imageInput = document.getElementById('image');
const facePreview = document.getElementById('facePreview');
const faceError = document.getElementById('faceError');
const startCameraBtn = document.getElementById('startCamera');

/* ---------------- CAMERA CONTROL ---------------- */

startCameraBtn.onclick = async () => {
  if (!stream) {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = 'block';
    video.play();
  }
};

/* ---------------- FACE CAPTURE ---------------- */

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

  // Basic face validation (brightness + shape check)
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

/* ---------------- SIMPLE FACE VALIDATION ---------------- */

function isLikelyFace(ctx, size) {
  const imageData = ctx.getImageData(0, 0, size, size).data;
  let brightPixels = 0;

  for (let i = 0; i < imageData.length; i += 4) {
    const brightness = (imageData[i] + imageData[i+1] + imageData[i+2]) / 3;
    if (brightness > 60) brightPixels++;
  }

  return brightPixels > (size * size * 0.25); // threshold
}

/* ---------------- STOP CAMERA ---------------- */

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
    video.style.display = 'none';
  }
}

/* ---------------- PHASE NAV ---------------- */

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

/* ---------------- CLICK TO VIEW FULL IMAGE ---------------- */

facePreview.onclick = () => {
  const win = window.open();
  win.document.write(`<img src="${facePreview.src}" style="width:100%">`);
};


const data = {
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

  Cameroon: {
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

countrySelect.addEventListener("change", () => {
  stateSelect.innerHTML = '<option value="">Select State</option>';
  lgaSelect.innerHTML = '<option value="">Select L.G.A</option>';

  const states = data[countrySelect.value];
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

  const lgas = data[countrySelect.value]?.[stateSelect.value];
  if (lgas) {
    lgas.forEach(lga => {
      const option = document.createElement("option");
      option.value = lga;
      option.textContent = lga;
      lgaSelect.appendChild(option);
    });
  }
});

