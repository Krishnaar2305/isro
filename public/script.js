const hist = document.getElementById("history");
const ana = document.getElementById("analysis");
const curr = document.getElementById("curr");
const currImg = document.getElementById("currGraph")
const uploadBtn = document.getElementById("upload")
const uploadForm = document.getElementById("uploadForm");

// const readTxt = async (name) => {
//     const resp = await fetch(`./arrayTxt/${name}`);
//     if (!resp.ok) {
//         throw new Error('Network response was not ok');
//     }
//     const text = await resp.text(); // Use .text() for reading .txt files
//     return text.split(' ').map(Number); // Convert lines to an array of numbers
// };

// let i = 0;
// if(!localStorage.getItem("size")){
//     localStorage.setItem("size", 0);
// }
// else{
//     i = parseInt(localStorage.getItem("size"));
// }


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

// uploadBtn.addEventListener("click", () => {
//     i++;
//     localStorage.setItem("size", i)
//     currImg.src = `./history/img${i}.png`
// })

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent page refresh

    const formData = new FormData(uploadForm);
    
    // Use fetch to send the form data to your server
    try {
        const response = await fetch(uploadForm.action, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Handle the response (you might want to show a success message)
        const result = await response.json();
        console.log(result); // Process the result from the server

        // Assuming the server responds with the image path
        currImg.src = result.imagePath; // Update this based on your server response
    } catch (error) {
        console.error('Error uploading file:', error);
        // Display an error message to the user
    }
});