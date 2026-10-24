// Language support: English and Bahasa Malaysia. Owner: Member 5 (texts), Member 4 (wiring).
//
// To translate a string: add a key to BOTH dictionaries below, then use t("key") in JS, or
// data-i18n="key" on an element in index.html. {name}-style placeholders are filled from t()'s
// second argument. A missing Malay text falls back to English, so nothing ever shows blank.
//
// Skill, role, course and career-area names come from the data files and stay in English.
// The Malay texts were drafted for the prototype: a fluent speaker should review them.

const KEY = "rpg:lang";

let lang = "en";
try { if (localStorage.getItem(KEY) === "ms") lang = "ms"; } catch {}

const T = {
  en: {
    "lang.label": "Language",
    "lang.note": "",
    "mock.badge": "Mock data: not real trends",
    "asof": "Data as of {date} ({source})",
    "scenario.label": "Disruption scenario",
    "scenario.slow": "Slow",
    "scenario.moderate": "Moderate",
    "scenario.fast": "Fast",
    "scenario.note.slow": "Slow: AI adoption is gradual, so most roles change little in the next few years.",
    "scenario.note.moderate": "Moderate: AI adoption grows steadily and some tasks shift to AI-assisted work.",
    "scenario.note.fast": "Fast: AI adoption accelerates and many tasks change quickly.",
    "estimates": "These are estimates, not predictions.",
    "area.label": "Career area",
    "area.auto": "Best match for my skills",
    "area.loadError": "Couldn't load the career areas.",
    "area.needs": "Your skills don't point to one career area yet. Pick an area above, or tick a few more specific skills.",
    "area.matched": "Matched from your skills: {area}.",
    "area.second": " {area} is a close second; switch above if it fits you better.",
    "tree.aria": "Skill tree",
    "tree.loading": "Loading your skill tree…",
    "tree.error": "Couldn't load the skill tree. Check that the server is running.",
    "tree.retry": "Try again",
    "tree.needsArea": "Choose a career area above to see your skill tree.",
    "class.yours": "Your starting class",
    "class.note": "Based on the skills you started with. It never limits which roles are open to you.",
    "stats.level": "Level",
    "stats.trained": "Skills trained",
    "stats.badges": "SDG badges",
    "xp.aria": "XP to next level",
    "refresh.button": "Refresh data",
    "reset.button": "Reset progress",
    "detail.empty": "Select a node to see details.",
    "profile.title": "Your character",
    "profile.name": "Adventurer name",
    "profile.placeholder": "A nickname is enough",
    "profile.note": "Saved only in this browser. No account and no personal details needed: please use a nickname.",
    "profile.export": "Download profile (JSON)",
    "profile.delete": "Delete saved data",
    "intake.title": "Choose your starting class",
    "intake.kitNote": "Each class is a sample starting kit: a typical job and its skills.",
    "intake.kitInfo": "{name}, {title}. Background: {role}, {hours} hours a week to study. Sample data, not a real person.",
    "intake.customInfo": "Your profile: {n} skills ticked, {hours} hours a week to study.",
    "intake.describe": "Or describe yourself",
    "intake.sampleNote": "Use sample information. We do not store it.",
    "intake.hours": "Hours per week you can study:",
    "intake.use": "Use this profile",
    "cv.summary": "Fill the checklist from a CV (optional)",
    "cv.note": "Paste CV text, load a .txt file, or try a sample. Use invented CVs only. The text is checked on the server and never stored; emails and phone numbers are removed first.",
    "cv.try": "Try a sample",
    "cv.choose": "Choose a sample CV",
    "cv.fileAria": "Load a CV as a .txt file",
    "cv.textAria": "CV text",
    "cv.scan": "Find my skills",
    "cv.onlyTxt": "Only .txt files for now. Paste the text instead.",
    "cv.empty": "Paste some CV text first.",
    "cv.reading": "Reading…",
    "cv.error": "Couldn't read the CV. Try again or tick skills yourself.",
    "cv.ticked": "Ticked {n} skills",
    "cv.removed": "; removed {n} contact details first.",
    "cv.found": "Found and ticked",
    "cv.possible": "Possible: tick if they fit you",
    "cv.review": "Check the ticks in the list below, then press \"Use this profile\". You decide; the reader only suggests.",
    "cv.note.negation": "mentioned after a negation such as 'no' or 'without'",
    "cv.note.intent": "mentioned as something being learned or wanted, not yet used",
    "cv.note.similar": "similar wording, not the exact phrase",
    "radar.title": "Future Skills Radar",
    "radar.note": "Scenario: {scenario}. These are estimates, not predictions. Job-posting data mostly covers German and European postings, so figures may not reflect the Malaysian job market directly.",
    "radar.rising": "Rising",
    "radar.declining": "Declining",
    "radar.noData": "No data yet",
    "radar.mockSource": "Mock data, no source yet",
    "path.title": "Pathway",
    "path.empty": "Select a role in the tree and choose \"Show pathway\".",
    "path.notVerified": "(not yet verified, not counted)",
    "path.noCourse": "No course in the catalogue yet",
    "path.allDone": "You already have every skill for this role.",
    "path.total": "Verified total: {hours} h, RM{cost}. Skills without a verified course: {gaps}.",
    "footer": "Personas are synthetic. Every number cites its source and date. Job data: <a href=\"https://www.arbeitnow.com\">Arbeitnow</a> and <a href=\"https://remotive.com\">Remotive</a>. Research data: arXiv. Occupation references: O*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration, used under <a href=\"https://creativecommons.org/licenses/by/4.0/\">CC BY 4.0</a>, adapted by us. This tool supports your career decisions; you make them.",
  },
  ms: {
    "lang.label": "Bahasa",
    "lang.note": "Nama kemahiran, peranan dan kursus kekal dalam Bahasa Inggeris.",
    "mock.badge": "Data contoh: bukan trend sebenar",
    "asof": "Data setakat {date} ({source})",
    "scenario.label": "Senario gangguan AI",
    "scenario.slow": "Perlahan",
    "scenario.moderate": "Sederhana",
    "scenario.fast": "Pantas",
    "scenario.note.slow": "Perlahan: penggunaan AI berlaku secara beransur-ansur, jadi kebanyakan peranan berubah sedikit dalam beberapa tahun akan datang.",
    "scenario.note.moderate": "Sederhana: penggunaan AI berkembang secara berterusan dan sesetengah tugas beralih kepada kerja yang dibantu AI.",
    "scenario.note.fast": "Pantas: penggunaan AI meningkat dengan cepat dan banyak tugas berubah dengan pantas.",
    "estimates": "Ini ialah anggaran, bukan ramalan.",
    "area.label": "Bidang kerjaya",
    "area.auto": "Padanan terbaik untuk kemahiran saya",
    "area.loadError": "Bidang kerjaya tidak dapat dimuatkan.",
    "area.needs": "Kemahiran anda belum menunjuk kepada satu bidang kerjaya. Pilih bidang di atas, atau tanda beberapa kemahiran yang lebih khusus.",
    "area.matched": "Dipadankan daripada kemahiran anda: {area}.",
    "area.second": " {area} hampir sama; tukar di atas jika lebih sesuai dengan anda.",
    "tree.aria": "Pokok kemahiran",
    "tree.loading": "Memuatkan pokok kemahiran anda…",
    "tree.error": "Pokok kemahiran tidak dapat dimuatkan. Pastikan pelayan sedang berjalan.",
    "tree.retry": "Cuba lagi",
    "tree.needsArea": "Pilih bidang kerjaya di atas untuk melihat pokok kemahiran anda.",
    "class.yours": "Kelas permulaan anda",
    "class.note": "Berdasarkan kemahiran yang anda ada pada permulaan. Ia tidak mengehadkan peranan yang terbuka kepada anda.",
    "stats.level": "Tahap",
    "stats.trained": "Kemahiran dilatih",
    "stats.badges": "Lencana SDG",
    "xp.aria": "XP ke tahap seterusnya",
    "refresh.button": "Muat semula data",
    "reset.button": "Set semula kemajuan",
    "detail.empty": "Pilih satu nod untuk melihat butiran.",
    "profile.title": "Watak anda",
    "profile.name": "Nama pengembara",
    "profile.placeholder": "Nama samaran sudah memadai",
    "profile.note": "Disimpan dalam pelayar ini sahaja. Tiada akaun dan tiada butiran peribadi diperlukan: sila gunakan nama samaran.",
    "profile.export": "Muat turun profil (JSON)",
    "profile.delete": "Padam data yang disimpan",
    "intake.title": "Pilih kelas permulaan anda",
    "intake.kitNote": "Setiap kelas ialah kit permulaan contoh: satu pekerjaan biasa dan kemahirannya.",
    "intake.kitInfo": "{name}, {title}. Latar belakang: {role}, {hours} jam seminggu untuk belajar. Data contoh, bukan orang sebenar.",
    "intake.customInfo": "Profil anda: {n} kemahiran ditanda, {hours} jam seminggu untuk belajar.",
    "intake.describe": "Atau terangkan diri anda",
    "intake.sampleNote": "Gunakan maklumat contoh. Kami tidak menyimpannya.",
    "intake.hours": "Jam seminggu yang boleh anda gunakan untuk belajar:",
    "intake.use": "Guna profil ini",
    "cv.summary": "Isi senarai semak daripada CV (pilihan)",
    "cv.note": "Tampal teks CV, muat naik fail .txt, atau cuba contoh. Gunakan CV rekaan sahaja. Teks diperiksa di pelayan dan tidak pernah disimpan; e-mel dan nombor telefon dibuang dahulu.",
    "cv.try": "Cuba contoh",
    "cv.choose": "Pilih CV contoh",
    "cv.fileAria": "Muat naik CV sebagai fail .txt",
    "cv.textAria": "Teks CV",
    "cv.scan": "Cari kemahiran saya",
    "cv.onlyTxt": "Hanya fail .txt buat masa ini. Sila tampal teksnya.",
    "cv.empty": "Tampal teks CV dahulu.",
    "cv.reading": "Sedang membaca…",
    "cv.error": "CV tidak dapat dibaca. Cuba lagi atau tanda kemahiran sendiri.",
    "cv.ticked": "{n} kemahiran ditanda",
    "cv.removed": "; {n} butiran hubungan dibuang dahulu.",
    "cv.found": "Dijumpai dan ditanda",
    "cv.possible": "Mungkin: tanda jika sesuai dengan anda",
    "cv.review": "Semak tanda dalam senarai di bawah, kemudian tekan \"Guna profil ini\". Anda yang memutuskan; pembaca hanya mencadangkan.",
    "cv.note.negation": "disebut selepas penafian seperti 'tiada' atau 'tanpa'",
    "cv.note.intent": "disebut sebagai sesuatu yang sedang dipelajari atau diingini, belum digunakan",
    "cv.note.similar": "perkataan yang serupa, bukan frasa yang tepat",
    "radar.title": "Radar Kemahiran Masa Depan",
    "radar.note": "Senario: {scenario}. Ini ialah anggaran, bukan ramalan. Data iklan kerja kebanyakannya daripada Jerman dan Eropah, jadi angka mungkin tidak mencerminkan pasaran kerja Malaysia secara langsung.",
    "radar.rising": "Meningkat",
    "radar.declining": "Menurun",
    "radar.noData": "Belum ada data",
    "radar.mockSource": "Data contoh, belum ada sumber",
    "path.title": "Laluan pembelajaran",
    "path.empty": "Pilih satu peranan dalam pokok dan tekan \"Show pathway\".",
    "path.notVerified": "(belum disahkan, tidak dikira)",
    "path.noCourse": "Belum ada kursus dalam katalog",
    "path.allDone": "Anda sudah mempunyai semua kemahiran untuk peranan ini.",
    "path.total": "Jumlah yang disahkan: {hours} jam, RM{cost}. Kemahiran tanpa kursus yang disahkan: {gaps}.",
    "footer": "Persona adalah rekaan. Setiap angka menyatakan sumber dan tarikhnya. Data pekerjaan: <a href=\"https://www.arbeitnow.com\">Arbeitnow</a> dan <a href=\"https://remotive.com\">Remotive</a>. Data penyelidikan: arXiv. Rujukan pekerjaan: O*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration, digunakan di bawah <a href=\"https://creativecommons.org/licenses/by/4.0/\">CC BY 4.0</a>, diubah suai oleh kami. Alat ini menyokong keputusan kerjaya anda; anda yang membuat keputusan.",
  },
};

export function getLang() { return lang; }

export function t(key, vars = {}) {
  const text = (T[lang] && T[lang][key]) ?? T.en[key] ?? key;
  return text.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? ""));
}

// Fill static page text: data-i18n (text), data-i18n-html (trusted dictionary HTML, e.g. the
// footer links), data-i18n-aria and data-i18n-placeholder.
export function applyStatic(root = document) {
  document.documentElement.lang = lang === "ms" ? "ms" : "en";
  root.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  root.querySelectorAll("[data-i18n-html]").forEach((el) => { el.innerHTML = t(el.dataset.i18nHtml); });
  root.querySelectorAll("[data-i18n-aria]").forEach((el) => el.setAttribute("aria-label", t(el.dataset.i18nAria)));
  root.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  document.querySelectorAll("#lang button").forEach((b) => {
    const on = b.dataset.lang === lang;
    b.classList.toggle("on", on);
    b.setAttribute("aria-pressed", String(on));
  });
}

// Switching reloads the page so every panel renders in the new language. Progress for the
// starting classes is kept (it is saved in this browser).
export function setLang(next) {
  if (next === lang) return;
  try { localStorage.setItem(KEY, next); } catch {}
  location.reload();
}
