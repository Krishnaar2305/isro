const hist = document.getElementById("history");
const ana = document.getElementById("analysis");
const curr = document.getElementById("curr");

const readTxt = async (name) => {
    const resp = await fetch(`./arrayTxt/${name}`);
    if (!resp.ok) {
        throw new Error('Network response was not ok');
    }
    const text = await resp.text(); // Use .text() for reading .txt files
    return text.split(' ').map(Number); // Convert lines to an array of numbers
};

let i = 0; // Initialize i outside of the loop
const histdata = [];
let read = false;
const fetchData = async () => {
    while (!read) {
        try {
            const data = await readTxt(`test${i}.txt`); // Make sure to add .txt if needed
            if(isNaN(data[0])) read = true
            histdata.push(data);
            i++; // Increment i
        } catch (error) {
            console.error(`Error reading file test${i}.txt:`, error);
            read = true
        }
    }
    histdata.pop()
};

document.addEventListener("DOMContentLoaded", fetchData);
console.log(histdata)
// Function to generate the History section with dynamic buttons
const genHist = () => {
    let str1 = `
        <h2>History</h2>
        <div class="file-list">
            <div class="file-item">
                <span>File Name</span>
            </div>
        </div>
        <div id="history">`;

    // Dynamically add buttons for each historical data file
    histdata.forEach(elem => {
        str1 += `<button class="pastGraphs">${elem}</button><br>`;
    });

    str1 += `</div>`;
    return str1;
}

// Function to generate the Upload section
const genUpload = () => {
    return `
        <div id="form" class="upload-section">
            <h2>Upload Data</h2>
            <form id="uploadForm" enctype="multipart/form-data" method="POST" action="/api/upload">
                <label for="fileInput">Choose a file:</label>
                <input type="file" id="fileInput" name="datafile" accept=".ascii,.fits,.xls" required>
                <button type="submit" id="upload" class="menu-item">Upload</button>
            </form>
        </div>`;
}

// Event listener for toggling content sections
document.addEventListener("click", (event) => {
    if (event.target === hist) {
        curr.innerHTML = genHist(); // Correctly call genHist()
        hist.classList.add("active");
        ana.classList.remove("active");
    } else if (event.target === ana) {
        curr.innerHTML = genUpload(); // Correctly call genUpload()
        ana.classList.add("active");
        hist.classList.remove("active");
    }
});
