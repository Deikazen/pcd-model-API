const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const previewBox = document.getElementById("previewBox");
const imagePreview = document.getElementById("imagePreview");
const analyzeBtn = document.getElementById("analyzeBtn");
const resetBtn = document.getElementById("resetBtn");

const loader = document.getElementById("loader");
const placeholder = document.getElementById("placeholder");
const predictionBox = document.getElementById("predictionBox");
const statsGrid = document.getElementById("statsGrid");

const predictionValue = document.getElementById("predictionValue");
const areaValue = document.getElementById("areaValue");
const perimeterValue = document.getElementById("perimeterValue");
const crackCount = document.getElementById("crackCount");

const markedPreview = document.querySelector(".marked-preview");
const markedImage = document.getElementById("markedImage");
const markedPlaceholder = document.getElementById("markedPlaceholder");

const damagedWallImage = document.getElementById("damagedWallImage");
const damagedPlaceholder = document.getElementById("damagedPlaceholder");

const cursorGlow = document.getElementById("cursorGlow");

const stepImages = {
  resized: document.getElementById("step-resized"),
  grayscale: document.getElementById("step-grayscale"),
  blurred: document.getElementById("step-blurred"),
  canny: document.getElementById("step-canny"),
  binary: document.getElementById("step-binary"),
};

let selectedFile = null;

/* =========================
   Cursor glow interaction
========================= */

document.addEventListener("mousemove", (event) => {
  if (!cursorGlow) return;

  cursorGlow.style.left = `${event.clientX}px`;
  cursorGlow.style.top = `${event.clientY}px`;
});

/* =========================
   3D tilt card interaction
========================= */

document.querySelectorAll(".tilt-card").forEach((card) => {
  card.addEventListener("mousemove", (event) => {
    const rect = card.getBoundingClientRect();

    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -5;
    const rotateY = ((x - centerX) / centerX) * 5;

    const percentX = (x / rect.width) * 100;
    const percentY = (y / rect.height) * 100;

    card.style.setProperty("--mx", `${percentX}%`);
    card.style.setProperty("--my", `${percentY}%`);
    card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-3px)`;
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg)";
  });
});

/* =========================
   Upload interaction
========================= */

dropZone.addEventListener("click", () => {
  fileInput.click();
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");

  if (event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0];
    fileInput.files = event.dataTransfer.files;
    handleFile(file);
  }
});

fileInput.addEventListener("change", (event) => {
  if (event.target.files.length > 0) {
    handleFile(event.target.files[0]);
  }
});

function handleFile(file) {
  if (!file.type.startsWith("image/")) {
    alert("File harus berupa gambar.");
    return;
  }

  selectedFile = file;

  const reader = new FileReader();

  reader.onload = (event) => {
    const imageUrl = event.target.result;

    imagePreview.src = imageUrl;
    previewBox.style.display = "block";
    previewBox.classList.remove("scanning");

    dropZone.style.display = "none";
    analyzeBtn.style.display = "block";
    resetBtn.style.display = "block";

    damagedWallImage.src = imageUrl;
    damagedWallImage.style.display = "block";
    damagedPlaceholder.style.display = "none";

    resetResultOnly();
  };

  reader.readAsDataURL(file);
}

/* =========================
   Analyze image
========================= */

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Pilih gambar dulu.");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedFile);

  setLoadingState();

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.status !== "success") {
      throw new Error(data.detail || "Analisis gagal.");
    }

    showResult(data);
  } catch (error) {
    console.error(error);
    alert("Gagal analisis gambar. Pastikan backend masih running.");
    resetUI();
  }
});

function setLoadingState() {
  analyzeBtn.style.display = "none";
  placeholder.style.display = "none";
  predictionBox.style.display = "none";
  statsGrid.style.display = "none";

  loader.style.display = "grid";
  previewBox.classList.add("scanning");

  markedImage.style.display = "none";
  markedImage.src = "";
  markedPreview.classList.remove("has-image");
  markedPlaceholder.style.display = "block";
  markedPlaceholder.innerText = "Sedang mencari area kerusakan...";
}

function showResult(data) {
  const prediction = data.prediction;
  const type = prediction.split(" ")[0];

  loader.style.display = "none";
  previewBox.classList.remove("scanning");

  predictionValue.textContent = prediction;
  predictionValue.className = `prediction-value color-${type}`;
  predictionBox.style.display = "block";
  predictionBox.classList.add("reveal");

  animateNumber(areaValue, Number(data.details.total_area), 2);
  animateNumber(perimeterValue, Number(data.details.total_perimeter), 2);
  animateNumber(crackCount, Number(data.details.crack_count), 0);

  statsGrid.style.display = "grid";
  statsGrid.classList.add("reveal");

  setMarkedImage(data);
  setPipelineImages(data);

  resetBtn.style.display = "block";
}

function setMarkedImage(data) {
  const marked =
    data.steps.marked ||
    data.steps.binary ||
    data.steps.canny;

  if (!marked) {
    markedPlaceholder.style.display = "block";
    markedPlaceholder.innerText = "Gambar tanda kerusakan belum tersedia.";
    return;
  }

  markedImage.src = "data:image/jpeg;base64," + marked;
  markedImage.style.display = "block";
  markedPlaceholder.style.display = "none";
  markedPreview.classList.add("has-image");
}

function setPipelineImages(data) {
  const steps = data.steps;

  setStepImage(stepImages.resized, steps.resized);
  setStepImage(stepImages.grayscale, steps.grayscale);
  setStepImage(stepImages.blurred, steps.blurred);
  setStepImage(stepImages.canny, steps.canny);
  setStepImage(stepImages.binary, steps.binary);
}

function setStepImage(imgElement, base64) {
  if (!imgElement || !base64) return;

  imgElement.src = "data:image/jpeg;base64," + base64;
  imgElement.parentElement.classList.add("has-image");
}

/* =========================
   Reset
========================= */

resetBtn.addEventListener("click", () => {
  resetUI();
});

function resetUI() {
  selectedFile = null;
  fileInput.value = "";

  dropZone.style.display = "grid";
  previewBox.style.display = "none";
  previewBox.classList.remove("scanning");
  imagePreview.src = "";

  analyzeBtn.style.display = "none";
  resetBtn.style.display = "none";

  damagedWallImage.src = "";
  damagedWallImage.style.display = "none";
  damagedPlaceholder.style.display = "block";

  resetResultOnly();
}

function resetResultOnly() {
  loader.style.display = "none";

  placeholder.style.display = "grid";
  placeholder.innerText = "Waiting for image analysis...";

  predictionBox.style.display = "none";
  statsGrid.style.display = "none";

  predictionValue.textContent = "WAITING";
  predictionValue.className = "prediction-value";

  areaValue.textContent = "0.00";
  perimeterValue.textContent = "0.00";
  crackCount.textContent = "0";

  markedImage.src = "";
  markedImage.style.display = "none";
  markedPreview.classList.remove("has-image");
  markedPlaceholder.style.display = "block";
  markedPlaceholder.innerText = "Hasil tanda kerusakan akan muncul di sini.";

  Object.values(stepImages).forEach((img) => {
    if (!img) return;
    img.src = "";
    img.parentElement.classList.remove("has-image");
  });
}

/* =========================
   Number animation
========================= */

function animateNumber(element, target, decimals = 0) {
  const duration = 900;
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    const easeOut = 1 - Math.pow(1 - progress, 3);
    const currentValue = start + (target - start) * easeOut;

    element.textContent = currentValue.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}