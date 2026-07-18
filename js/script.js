let currentBookingCtx = null;

// Navigation
function goTo(viewName) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + viewName).classList.add('active');
  document.querySelectorAll('nav a').forEach(a => a.classList.toggle('active', a.dataset.view === viewName));
  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (viewName === 'hotels') loadHotels('hotels-results', '', true);
  if (viewName === 'bookings') loadBookings();
  if (viewName === 'profile') loadProfile();
}

// Hotel cards
function hotelCardHTML(hotel) {
  const roomsHTML = hotel.rooms.map(r => `
    <div class="room">
      <img src="${r.img}" alt="${r.type}">
      <div class="c">
        <h3>${r.type}</h3>
        <div class="price">₹${r.price.toLocaleString('en-IN')} <span>/ night</span></div>
        <button class="btn" onclick='openBookingModal(${hotel.id}, "${r.id}")'>Book Now</button>
      </div>
    </div>`).join('');
  return `
  <div class="hotel">
    <div class="top">
      <img src="${hotel.img}" alt="${hotel.name}">
      <div class="info">
        <h2>${hotel.name} <span class="tag">${hotel.city}</span></h2>
        <p class="amenities">⭐⭐⭐⭐⭐ &nbsp;|&nbsp; WiFi &nbsp;|&nbsp; Pool &nbsp;|&nbsp; Breakfast</p>
      </div>
    </div>
    <div class="rooms">${roomsHTML}</div>
  </div>`;
}

let hotelsCache = [];

async function loadHotels(containerId, destination, isHotelsPage) {
  const el = document.getElementById(containerId);
  el.innerHTML = `<div class="loading">Loading hotels…</div>`;
  try {
    const url = destination ? `/api/hotels?destination=${encodeURIComponent(destination)}` : '/api/hotels';
    const res = await fetch(url);
    const list = await res.json();
    hotelsCache = list;

    if (list.length === 0) {
      el.innerHTML = `<div class="empty"><h3>No hotels found</h3><p>Try a different destination.</p></div>`;
    } else {
      el.innerHTML = list.map(hotelCardHTML).join('');
    }
    if (isHotelsPage) {
      document.getElementById('hotelsResultText').textContent =
        `${list.length} propert${list.length === 1 ? 'y' : 'ies'} found`;
    }
  } catch (err) {
    el.innerHTML = `<div class="empty"><h3>Couldn't load hotels</h3><p>Is the server running?</p></div>`;
  }
}

// Search
document.getElementById('searchForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const dest = document.getElementById('searchDestination').value.trim();
  const checkin = document.getElementById('checkin').value;
  const checkout = document.getElementById('checkout').value;

  if (checkin && checkout && checkout <= checkin) {
    alert('Check-out date must be after the check-in date.');
    return;
  }

  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-hotels').classList.add('active');
  document.querySelectorAll('nav a').forEach(a => a.classList.toggle('active', a.dataset.view === 'hotels'));
  loadHotels('hotels-results', dest, true);
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

function clearFilter() {
  document.getElementById('searchDestination').value = '';
  loadHotels('hotels-results', '', true);
}

// Booking modal
function openBookingModal(hotelId, roomId) {
  const hotel = hotelsCache.find(h => h.id === hotelId);
  const room = hotel.rooms.find(r => r.id === roomId);
  currentBookingCtx = { hotel, room };

  document.getElementById('modalRoomTitle').textContent = room.type;
  document.getElementById('modalHotelName').textContent = `${hotel.name}, ${hotel.city}`;
  document.getElementById('modalRate').textContent = '₹' + room.price.toLocaleString('en-IN');
  document.getElementById('modalNights').value = 1;

  fetch('/api/profile').then(r => r.json()).then(p => {
    document.getElementById('modalGuestName').value = p && p.name ? p.name : '';
  }).catch(() => {});

  updateModalTotal();
  document.getElementById('bookingOverlay').classList.add('active');
}

function updateModalTotal() {
  if (!currentBookingCtx) return;
  let nights = parseInt(document.getElementById('modalNights').value) || 1;
  if (nights < 1) nights = 1;
  document.getElementById('modalTotal').textContent =
    '₹' + (currentBookingCtx.room.price * nights).toLocaleString('en-IN');
}
document.getElementById('modalNights').addEventListener('input', updateModalTotal);

function closeModal() {
  document.getElementById('bookingOverlay').classList.remove('active');
  currentBookingCtx = null;
}

async function confirmBooking() {
  const name = document.getElementById('modalGuestName').value.trim();
  const nights = parseInt(document.getElementById('modalNights').value) || 1;
  if (!name) { alert('Please enter the guest name.'); return; }
  if (nights < 1) { alert('Nights must be at least 1.'); return; }

  const { hotel, room } = currentBookingCtx;
  const payload = {
    hotel_id: hotel.id, hotel_name: hotel.name, city: hotel.city,
    room_id: room.id, room_type: room.type, room_price: room.price,
    nights, guest_name: name
  };

  try {
    const res = await fetch('/api/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) { alert(data.error || 'Could not create booking.'); return; }

    closeModal();
    goTo('bookings');
  } catch (err) {
    alert('Network error — is the server running?');
  }
}

// Bookings list
function bookingCardHTML(b) {
  const roomImg = 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80';
  return `
    <div class="booking-card">
      <img src="${roomImg}" alt="${b.room_type}">
      <div>
        <h3>${b.room_type} — ${b.hotel_name}, ${b.city}</h3>
        <div class="meta">Guest: ${b.guest_name}<br>${b.nights} night(s) &nbsp;•&nbsp; Total: ₹${b.total.toLocaleString('en-IN')}</div>
        <span class="status ${b.status}">${b.status === 'confirmed' ? 'Confirmed' : 'Cancelled'}</span>
      </div>
      <div>
        ${b.status === 'confirmed' ? `<button class="btn danger" onclick="cancelBooking(${b.id})">Cancel</button>` : ''}
      </div>
    </div>`;
}

async function loadBookings() {
  const el = document.getElementById('bookings-list');
  el.innerHTML = `<div class="loading">Loading bookings…</div>`;
  try {
    const res = await fetch('/api/bookings');
    const bookings = await res.json();
    if (bookings.length === 0) {
      el.innerHTML = `<div class="empty"><h3>No bookings yet</h3><p>Book a room from the Hotels page to see it here.</p></div>`;
      updateBookingBadge(0);
      return;
    }
    el.innerHTML = bookings.map(bookingCardHTML).join('');
    updateBookingBadge(bookings.filter(b => b.status === 'confirmed').length);
  } catch (err) {
    el.innerHTML = `<div class="empty"><h3>Couldn't load bookings</h3><p>Is the server running?</p></div>`;
  }
}

async function cancelBooking(id) {
  if (!confirm('Cancel this booking?')) return;
  try {
    await fetch(`/api/bookings/${id}/cancel`, { method: 'POST' });
    loadBookings();
  } catch (err) {
    alert('Network error — could not cancel booking.');
  }
}

function updateBookingBadge(activeCount) {
  const badge = document.getElementById('bookingCount');
  if (activeCount > 0) { badge.style.display = 'inline-block'; badge.textContent = activeCount; }
  else { badge.style.display = 'none'; }
}

// Contact form
document.getElementById('contactForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  let valid = true;
  const name = document.getElementById('cName').value.trim();
  const email = document.getElementById('cEmail').value.trim();
  const message = document.getElementById('cMessage').value.trim();
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  toggleError('err-cName', !name); if (!name) valid = false;
  toggleError('err-cEmail', !emailRe.test(email)); if (!emailRe.test(email)) valid = false;
  toggleError('err-cMessage', !message); if (!message) valid = false;
  if (!valid) return;

  try {
    const res = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, message })
    });
    const data = await res.json();
    if (!res.ok) { alert(data.error || 'Could not send message.'); return; }

    document.getElementById('contactSuccess').style.display = 'block';
    this.reset();
    setTimeout(() => document.getElementById('contactSuccess').style.display = 'none', 4000);
  } catch (err) {
    alert('Network error — is the server running?');
  }
});

// Profile form
async function loadProfile() {
  try {
    const res = await fetch('/api/profile');
    const p = await res.json();
    document.getElementById('pName').value = p.name || '';
    document.getElementById('pEmail').value = p.email || '';
    document.getElementById('pPhone').value = p.phone || '';
  } catch (err) {}
}

document.getElementById('profileForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  let valid = true;
  const name = document.getElementById('pName').value.trim();
  const email = document.getElementById('pEmail').value.trim();
  const phone = document.getElementById('pPhone').value.trim();
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const phoneRe = /^\d{10}$/;

  toggleError('err-pName', !name); if (!name) valid = false;
  toggleError('err-pEmail', !emailRe.test(email)); if (!emailRe.test(email)) valid = false;
  toggleError('err-pPhone', !phoneRe.test(phone)); if (!phoneRe.test(phone)) valid = false;
  if (!valid) return;

  try {
    const res = await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone })
    });
    const data = await res.json();
    if (!res.ok) { alert(data.error || 'Could not save profile.'); return; }

    document.getElementById('profileSuccess').style.display = 'block';
    setTimeout(() => document.getElementById('profileSuccess').style.display = 'none', 4000);
  } catch (err) {
    alert('Network error — is the server running?');
  }
});

function toggleError(id, show) {
  document.getElementById(id).style.display = show ? 'block' : 'none';
}

// Init
(function init() {
  const today = new Date();
  const tomorrow = new Date(today); tomorrow.setDate(today.getDate() + 1);
  const dayAfter = new Date(today); dayAfter.setDate(today.getDate() + 2);
  document.getElementById('checkin').value = tomorrow.toISOString().split('T')[0];
  document.getElementById('checkout').value = dayAfter.toISOString().split('T')[0];
  document.getElementById('checkin').min = today.toISOString().split('T')[0];

  loadHotels('home-results', '', false);

  fetch('/api/bookings').then(r => r.json()).then(list => {
    updateBookingBadge(list.filter(b => b.status === 'confirmed').length);
  }).catch(() => {});
})();
