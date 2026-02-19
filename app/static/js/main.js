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
  const res = await fetch('/cart/clear', {
      method: 'POST'
  });
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

async function addToCart(pid, qty=1, color=null){

  const payload = {
    product_id: pid,
    qty: qty,
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



function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 4000);
}

let selectedProductId = null;
let selectedColor = null;
let colorBank = [];



async function loadColors() {
    if (colorBank.length) return;

    for (let i = 0; i < 8; i++) {
        try {
            const res = await fetch(
              `https://www.thecolorapi.com/scheme?count=100&mode=analogic&hex=${Math.floor(Math.random()*16777215).toString(16)}`
            );
            const data = await res.json();

            data.colors.forEach(c => {
                colorBank.push({
                    name: c.name.value,
                    hex: c.hex.value,
                    img: c.image.bare
                });
            });
        } catch {}
    }
}


function openColorPicker(productId) {
    selectedProductId = productId;
    document.getElementById("colorModal").style.display = "block";
    loadColors();
}


function searchColors() {
    const query = document.getElementById("colorSearch").value.toLowerCase();
    const results = document.getElementById("colorResults");
    results.innerHTML = "";

    if (!query) return;

    colorBank
      .filter(c => c.name.toLowerCase().includes(query))
      .slice(0, 30)
      .forEach(color => {
          const div = document.createElement("div");
          div.className = "color-item";
          div.innerHTML = `
              <img src="${color.img}">
              <span>${color.name}</span>
          `;
          div.onclick = () => selectColor(color);
          results.appendChild(div);
      });
}


function selectColor(color){
    if(!selectedProductId) return;
    addToCart(selectedProductId, 1, color);
    closeColorModal();
}



function closeColorModal() {
    document.getElementById("colorModal").style.display = "none";
    document.getElementById("colorSearch").value = "";
    document.getElementById("colorResults").innerHTML = "";
}




function openColorModal(productId, productName){
  selectedProductId = productId;
  selectedColor = null;
  document.getElementById('color-modal-title').textContent = productName;
  document.getElementById('color-input').value = '';
  document.getElementById('color-suggestions').innerHTML = '';
  document.getElementById('color-modal').style.display = 'block';
}


function closeColorModal(){
  document.getElementById('color-modal').style.display = 'none';
  selectedProductId = null;
  selectedColor = null;
}


document.getElementById('color-input').addEventListener('input', async function(){
  const raw = this.value.trim();
  const suggestionsDiv = document.getElementById('color-suggestions');
  suggestionsDiv.innerHTML = '';
  selectedColor = null;

  if(!raw) return;

  const candidates = [raw, raw.replace(/\s+/g, '')];

  function browserColorValid(nameOrHex){
    const test = document.createElement('div');
    test.style.backgroundColor = '';
    test.style.backgroundColor = nameOrHex;
    return !!test.style.backgroundColor;
  }

  let mainColor=null, mainName=null, mainHex=null;

  for(const c of candidates){
    if(browserColorValid(c)){
      mainColor = c; mainName=c;
      const div = document.createElement('div');
      div.style.backgroundColor = c;
      const cs = getComputedStyle(div).backgroundColor;
      const m = cs.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
      if(m){
        const toHex = n=>('0'+n.toString(16)).slice(-2);
        mainHex = `#${toHex(parseInt(m[1],10))}${toHex(parseInt(m[2],10))}${toHex(parseInt(m[3],10))}`.toUpperCase();
      }
      break;
    }
  }


  if(!mainColor){
    try{
      const res = await fetch(`https://www.thecolorapi.com/scheme?hex=${encodeURIComponent(raw.replace('#',''))}&mode=monochrome&count=1`);
      if(res.ok){
        const data = await res.json();
        if(data?.colors?.length){
          mainHex = data.colors[0].hex?.value || '#CCCCCC';
          mainName = data.colors[0].name?.value || raw;
          mainColor = browserColorValid(mainName) ? mainName : mainHex;
        }
      }
    }catch{}
  }


  if(!mainColor){
    mainColor = '#CCCCCC';
    mainHex = '#CCCCCC';
    mainName = raw;
  }


  const wrapper = document.createElement('div');
  wrapper.style.display = 'inline-block';
  wrapper.style.margin='4px';
  wrapper.style.textAlign='center';
  wrapper.style.fontSize='12px';

  const sw = document.createElement('div');
  sw.style.width='40px';
  sw.style.height='40px';
  sw.style.borderRadius='6px';
  sw.style.border='2px solid #ccc';
  sw.style.cursor='pointer';
  sw.style.backgroundColor=mainColor;
  sw.title=`${mainName} — ${mainHex}`;
  sw.addEventListener('click', ()=>{
    document.querySelectorAll('#color-suggestions div > div').forEach(d=>d.style.border='2px solid #ccc');
    sw.style.border='2px solid black';
    selectedColor={name:mainName, hex:mainHex};
  });

  const lbl = document.createElement('div');
  lbl.style.whiteSpace='pre';
  lbl.textContent=`${mainName}\n${mainHex}`;

  wrapper.appendChild(sw);
  wrapper.appendChild(lbl);
  suggestionsDiv.appendChild(wrapper);


  try{
    const schemeRes = await fetch(`https://www.thecolorapi.com/scheme?hex=${mainHex.replace('#','')}&mode=analogic&count=5`);
    if(schemeRes.ok){
      const schemeData = await schemeRes.json();
      schemeData.colors?.forEach(c=>{
        const chex=c.hex?.value;
        const cname=c.name?.value||chex;
        if(!chex) return;

        const wrap = document.createElement('div');
        wrap.style.display='inline-block';
        wrap.style.textAlign='center';
        wrap.style.fontSize='11px';
        wrap.style.marginRight='6px';

        const sw2 = document.createElement('div');
        sw2.style.width='36px';
        sw2.style.height='36px';
        sw2.style.borderRadius='6px';
        sw2.style.border='2px solid #ccc';
        sw2.style.cursor='pointer';
        sw2.style.backgroundColor=browserColorValid(cname)?cname:chex;
        sw2.title=`${cname} — ${chex}`;
        sw2.addEventListener('click', ()=>{
          document.querySelectorAll('#color-suggestions div > div').forEach(d=>d.style.border='2px solid #ccc');
          sw2.style.border='2px solid black';
          selectedColor={name:cname, hex:chex};
        });

        const lbl2 = document.createElement('div');
        lbl2.style.whiteSpace='pre';
        lbl2.textContent=`${cname}\n${chex}`;

        wrap.appendChild(sw2);
        wrap.appendChild(lbl2);
        suggestionsDiv.appendChild(wrap);
      });
    }
  }catch{}
});


document.getElementById('confirm-color-btn').addEventListener('click', async () => {
  if (!selectedProductId || !selectedColor) {
    alert('Please select a color.');
    return;
  }

  try {

    await addToCart(selectedProductId, 1, selectedColor);


    closeColorModal();

    if (typeof showToast === 'function') showToast('Added to cart with selected color');
  } catch (err) {
    console.error(err);
    alert('Error adding product to cart.');
  }
});



function proceedToCheckout(){
  window.location.href='/checkout';
}




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



let stream = null;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const imageInput = document.getElementById('image');
const facePreview = document.getElementById('facePreview');
const faceError = document.getElementById('faceError');
const startCameraBtn = document.getElementById('startCamera');



startCameraBtn.onclick = async () => {
  if (!stream) {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = 'block';
    video.play();
  }
};


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


async function verifyPickup(code, btn) {
    try {
        const res = await fetch('/verify-pickup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pickup_code: code })
        });
        const data = await res.json();
        alert(data.message);

        if (data.success) {
            const row = btn.closest('tr');
            row.querySelector('.delivered-status').textContent = 'Yes';
            btn.disabled = true;
            btn.textContent = 'Verified';
        }
    } catch (err) {
        console.error(err);
        alert('Error verifying pickup code');
    }
}
