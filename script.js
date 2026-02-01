const tool = document.getElementById('floating-tool');
const handle = document.getElementById('dragHandle');
const btn = document.getElementById('btnAnalys');

let isDragging = false;
let currentX, currentY, initialX, initialY;
let xOffset = 0, yOffset = 0;

/* Kéo thả (chuột + cảm ứng) */
handle.addEventListener("mousedown", dragStart);
document.addEventListener("mousemove", drag);
document.addEventListener("mouseup", dragEnd);

handle.addEventListener("touchstart", dragStart, { passive: false });
document.addEventListener("touchmove", drag, { passive: false });
document.addEventListener("touchend", dragEnd);

function dragStart(e) {
    if (e.type === "touchstart") {
        initialX = e.touches[0].clientX - xOffset;
        initialY = e.touches[0].clientY - yOffset;
    } else {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
    }
    isDragging = true;
}

function drag(e) {
    if (!isDragging) return;
    e.preventDefault();

    if (e.type === "touchmove") {
        currentX = e.touches[0].clientX - initialX;
        currentY = e.touches[0].clientY - initialY;
    } else {
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
    }

    xOffset = currentX;
    yOffset = currentY;
    tool.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
}

function dragEnd() {
    isDragging = false;
}

/* Phân tích MD5 */
btn.addEventListener("click", analyzeLogic);

function analyzeLogic() {
    const input = document.getElementById('md5Input').value.trim();
    const resDiv = document.getElementById('result');

    if (input.length < 5) {
        resDiv.innerText = "SAI MÃ";
        resDiv.style.color = "yellow";
        return;
    }

    resDiv.innerText = "TÍNH TOÁN...";
    resDiv.style.color = "#fff";

    setTimeout(() => {
        let total = 0;
        for (let char of input) {
            total += char.charCodeAt(0);
        }

        const lastChar = input.slice(-1);
        const isLastCharNumber = !isNaN(parseInt(lastChar));

        if ((total % 2 === 0 && isLastCharNumber) ||
            (total % 2 !== 0 && !isLastCharNumber)) {
            resDiv.innerText = "DỰ ĐOÁN: XỈU";
            resDiv.style.color = "#00ffff";
        } else {
            resDiv.innerText = "DỰ ĐOÁN: TÀI";
            resDiv.style.color = "#ff4444";
        }
    }, 500);
}
